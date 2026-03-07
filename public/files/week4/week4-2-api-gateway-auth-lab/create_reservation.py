"""
AWS Lambda 함수: QuickTable 예약 생성

이 Lambda 함수는 QuickTable 레스토랑 예약 시스템에서
새로운 예약을 생성하고 DynamoDB에 저장합니다.

주요 기능:
    1. Cognito Authorizer에서 사용자 ID 추출.
    2. 예약 정보 검증 및 UUID 생성.
    3. DynamoDB에 예약 데이터 저장.
    4. 생성된 예약 정보 반환.

환경 변수:
    TABLE_NAME (str): DynamoDB 테이블 이름

트리거:
    API Gateway POST /reservations
"""

import json
import boto3
import os
import uuid
from datetime import datetime

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """
    예약 생성 Lambda 함수
    
    Cognito Authorizer에서 전달된 사용자 정보를 사용하여
    새로운 예약을 생성하고 DynamoDB에 저장합니다.
    
    Args:
        event (dict): API Gateway 이벤트 (Cognito Authorizer 정보 포함)
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공) 또는 400/500 (오류)
            - body (str): JSON 형식의 예약 정보 또는 오류 메시지
    """
    try:
        # 1. Cognito Authorizer에서 사용자 ID 추출
        # API Gateway Authorizer가 검증한 사용자 정보는 event['requestContext']['authorizer']['claims']에 포함됨
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # 2. 요청 본문 파싱
        body = json.loads(event['body'])
        
        # 3. 필수 필드 검증
        required_fields = ['restaurantName', 'date', 'time', 'partySize']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Missing required field: {field}'
                    })
                }
        
        # 4. 예약 ID 생성 (UUID)
        reservation_id = str(uuid.uuid4())
        
        # 5. 예약 데이터 구성
        reservation = {
            'userId': user_id,
            'reservationId': reservation_id,
            'restaurantName': body['restaurantName'],
            'date': body['date'],
            'time': body['time'],
            'partySize': int(body['partySize']),
            'status': 'confirmed',
            'createdAt': datetime.utcnow().isoformat()
        }
        
        # 6. DynamoDB에 저장
        table.put_item(Item=reservation)
        
        # 7. 성공 응답 반환
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(reservation)
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
