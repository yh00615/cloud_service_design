"""
AWS Lambda 함수: 레스토랑 예약 생성 및 EventBridge 이벤트 발행

이 Lambda 함수는 QuickTable 레스토랑 예약 시스템에서 예약 데이터를
DynamoDB Reservations 테이블에 저장한 후 EventBridge에 ReservationCreated 이벤트를 발행합니다.

주요 기능:
    1. 예약 데이터 검증 및 DynamoDB 저장
    2. date/time 필드를 timeSlot 형식으로 변환 (날짜#시간)
    3. EventBridge에 ReservationCreated 이벤트 발행
    4. 예약 생성 결과 반환

환경 변수:
    RESERVATIONS_TABLE (str): DynamoDB Reservations 테이블 이름
    EVENT_BUS_NAME (str): EventBridge Event Bus 이름

트리거:
    수동 실행 또는 API Gateway
"""

import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# AWS 서비스 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# 환경 변수에서 테이블 이름 및 Event Bus 이름 가져오기
RESERVATIONS_TABLE = os.environ['RESERVATIONS_TABLE']
EVENT_BUS_NAME = os.environ['EVENT_BUS_NAME']

# DynamoDB 테이블 객체
reservations_table = dynamodb.Table(RESERVATIONS_TABLE)


def lambda_handler(event, context):
    """
    예약을 생성하고 EventBridge에 ReservationCreated 이벤트를 발행하는 Lambda 함수
    
    Args:
        event (dict): Lambda 이벤트 객체
            - reservationId (str): 예약 ID
            - userId (str): 사용자 ID
            - restaurantId (str): 레스토랑 ID
            - date (str): 예약 날짜 (YYYY-MM-DD)
            - time (str): 예약 시간 (HH:MM)
            - partySize (int): 인원 수
            - phoneNumber (str): 전화번호
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공) 또는 500 (실패)
            - body (str): JSON 형식의 처리 결과
    """
    # 이벤트 전체 내용을 로그에 출력 (디버깅용)
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # 예약 데이터 추출
        reservation_id = event['reservationId']
        user_id = event['userId']
        restaurant_id = event['restaurantId']
        date = event['date']
        time = event['time']
        party_size = event['partySize']
        phone_number = event['phoneNumber']
        
        # date와 time을 timeSlot 형식으로 변환 (날짜#시간)
        time_slot = f"{date}#{time}"
        
        # 현재 시간 (ISO 8601 형식)
        current_time = datetime.utcnow().isoformat()
        
        # DynamoDB에 저장할 예약 데이터
        reservation_item = {
            'reservationId': reservation_id,
            'userId': user_id,
            'restaurantId': restaurant_id,
            'date': date,
            'time': time,
            'timeSlot': time_slot,
            'partySize': party_size,
            'phoneNumber': phone_number,
            'status': 'pending',
            'createdAt': current_time,
            'updatedAt': current_time
        }
        
        # DynamoDB에 예약 데이터 저장
        reservations_table.put_item(Item=reservation_item)
        print(f"Reservation saved to DynamoDB: {reservation_id}")
        
        # EventBridge에 발행할 이벤트 데이터
        event_detail = {
            'reservationId': reservation_id,
            'userId': user_id,
            'restaurantId': restaurant_id,
            'date': date,
            'time': time,
            'timeSlot': time_slot,
            'partySize': party_size,
            'phoneNumber': phone_number,
            'status': 'pending',
            'createdAt': current_time
        }
        
        # EventBridge에 ReservationCreated 이벤트 발행
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'reservation.service',
                    'DetailType': 'ReservationCreated',
                    'Detail': json.dumps(event_detail),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        
        # EventBridge 응답 확인
        if response['FailedEntryCount'] > 0:
            print(f"Failed to publish event: {response}")
            raise Exception("Failed to publish ReservationCreated event")
        
        print(f"ReservationCreated event published: {reservation_id}")
        
        # 성공 응답 반환
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Reservation created successfully',
                'reservationId': reservation_id,
                'status': 'pending'
            })
        }
        
    except KeyError as e:
        # 필수 필드 누락 오류
        print(f"Missing required field: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Bad Request',
                'message': f'Missing required field: {str(e)}'
            })
        }
        
    except Exception as e:
        # 기타 오류
        print(f"Error processing reservation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }
