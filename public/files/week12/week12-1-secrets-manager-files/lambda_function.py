import json
import boto3
import pymysql
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    AWS Secrets Manager와 Parameter Store에서 자격증명을 조회하고
    RDS MySQL 데이터베이스에 연결하는 Lambda 함수
    
    환경 변수:
    - SECRET_NAME: Secrets Manager 시크릿 이름
    - PARAMETER_NAME: Parameter Store 파라미터 이름
    - DB_HOST: RDS 엔드포인트
    - DB_PORT: RDS 포트
    """
    # Initialize AWS clients
    secrets_client = boto3.client('secretsmanager')
    ssm_client = boto3.client('ssm')
    
    results = {}
    
    try:
        # 1. Get database credentials from Secrets Manager
        secret_name = os.environ['SECRET_NAME']
        secret_response = secrets_client.get_secret_value(SecretId=secret_name)
        db_credentials = json.loads(secret_response['SecretString'])
        
        results['secrets_manager'] = {
            'secret_name': secret_name,
            'username': db_credentials.get('username'),
            'password_length': len(db_credentials.get('password', '')),
            'status': 'Retrieved successfully'
        }
        
        # 2. Get parameter from Parameter Store
        parameter_name = os.environ['PARAMETER_NAME']
        parameter_response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        
        results['parameter_store'] = {
            'parameter_name': parameter_name,
            'value': parameter_response['Parameter']['Value'],
            'type': parameter_response['Parameter']['Type'],
            'status': 'Retrieved successfully'
        }
        
        # 3. Connect to RDS MySQL database
        db_host = os.environ['DB_HOST']
        db_port = int(os.environ['DB_PORT'])
        db_user = db_credentials['username']
        db_password = db_credentials['password']
        
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()[0]
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
        
        connection.close()
        
        results['database_connection'] = {
            'host': db_host,
            'port': db_port,
            'username': db_user,
            'mysql_version': db_version,
            'current_database': current_db,
            'status': 'Connected successfully'
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(results, indent=2)
        }
        
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'AWS API Error',
                'message': str(e)
            })
        }
    except pymysql.MySQLError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Database Connection Error',
                'message': str(e),
                'partial_results': results
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Unexpected Error',
                'message': str(e),
                'partial_results': results
            })
        }
