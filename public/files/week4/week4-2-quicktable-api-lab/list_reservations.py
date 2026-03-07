"""
AWS Lambda 함수: QuickTable 예약 목록 조회

이 Lambda 함수는 QuickTable 레스토랑 예약 시스템에서
사용자의 예약 목록을 조회합니다.

주요 기능:
    1. Cognito Authorizer에서 사용자 ID 추출.
    2. DynamoDB에서 사용자의 모든 예약 조회.
    3. 예약 목록 반환.

환경 변수:
    TABLE_NAME (str): DynamoDB 테이블 이름

트리거:
    API Gateway GET /reservations
"""

import json
import boto3
import os
from boto3.dynamodb.conditions import Key

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """
    예약 목록 조회 Lambda 함수
    
    Cognito Authorizer에서 전달된 사용자 정보를 사용하여
    해당 사용자의 모든 예약을 조회합니다.
    
    Args:
        event (dict): API Gateway 이벤트 (Cognito Authorizer 정보 포함)
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공) 또는 500 (오류)
            - body (str): JSON 형식의 예약 목록 또는 오류 메시지
    """
    try:
        # 1. Cognito Authorizer에서 사용자 ID 추출
        # API Gateway Authorizer가 검증한 사용자 정보는 event['requestContext']['authorizer']['claims']에 포함됨
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # 2. DynamoDB에서 사용자의 예약 조회 (Query 사용)
        # userId가 파티션 키이므로 Query로 효율적으로 조회 가능
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        
        # 3. 조회 결과 추출
        reservations = response.get('Items', [])
        
        # 4. 성공 응답 반환
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'count': len(reservations),
                'reservations': reservations
            })
        }
        
    except Exception as e:
        # 오류 처리
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
