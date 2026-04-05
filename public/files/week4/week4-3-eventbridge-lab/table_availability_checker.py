"""
AWS Lambda 함수: 테이블 재고 확인 및 TableUnavailable 이벤트 발행

이 Lambda 함수는 EventBridge에서 ReservationCreated 이벤트를 수신하여
RestaurantAvailability 테이블에서 예약 가능한 슬롯을 확인하고,
슬롯이 부족하면 TableUnavailable 이벤트를 발행합니다.

주요 기능:
    1. ReservationCreated 이벤트 수신 및 파싱
    2. DynamoDB RestaurantAvailability 테이블에서 예약 가능 슬롯 확인
    3. partySize vs availableSlots 비교
    4. 슬롯 부족 시 TableUnavailable 이벤트 발행

환경 변수:
    RESTAURANT_AVAILABILITY_TABLE (str): DynamoDB RestaurantAvailability 테이블 이름
    EVENT_BUS_NAME (str): EventBridge Event Bus 이름

트리거:
    EventBridge 규칙 (ReservationCreated 이벤트)
"""

import json
import boto3
import os
from datetime import datetime

# AWS 서비스 클라이언트 초기화
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# 환경 변수에서 테이블 이름 및 Event Bus 이름 가져오기
RESTAURANT_AVAILABILITY_TABLE = os.environ['RESTAURANT_AVAILABILITY_TABLE']
EVENT_BUS_NAME = os.environ['EVENT_BUS_NAME']

# DynamoDB 테이블 객체
availability_table = dynamodb.Table(RESTAURANT_AVAILABILITY_TABLE)


def lambda_handler(event, context):
    """
    ReservationCreated 이벤트를 수신하여 테이블 재고를 확인하는 Lambda 함수
    
    EventBridge에서 전달된 ReservationCreated 이벤트를 분석하고,
    RestaurantAvailability 테이블에서 예약 가능한 슬롯을 확인합니다.
    partySize가 availableSlots를 초과하면 TableUnavailable 이벤트를 발행합니다.
    
    Args:
        event (dict): EventBridge에서 전달된 ReservationCreated 이벤트
            - detail (dict): 예약 상세 정보
                - reservationId (str): 예약 ID
                - restaurantId (str): 레스토랑 ID
                - timeSlot (str): 예약 시간대 (날짜#시간 형식)
                - partySize (int): 인원 수
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공)
            - body (str): JSON 형식의 처리 결과
    """
    # 이벤트 전체 내용을 로그에 출력 (디버깅용)
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # EventBridge 이벤트에서 예약 정보 추출
        reservation_detail = event['detail']
        reservation_id = reservation_detail['reservationId']
        restaurant_id = reservation_detail['restaurantId']
        time_slot = reservation_detail['timeSlot']
        party_size = reservation_detail['partySize']
        
        print(f"Checking table availability for restaurant: {restaurant_id}, timeSlot: {time_slot}, reservation: {reservation_id}")
        
        # DynamoDB에서 레스토랑 예약 가능 슬롯 조회
        response = availability_table.get_item(
            Key={
                'restaurantId': restaurant_id,
                'timeSlot': time_slot
            }
        )
        
        # 예약 가능 슬롯 정보가 없는 경우
        if 'Item' not in response:
            print(f"No availability data found for restaurant: {restaurant_id}, timeSlot: {time_slot}")
            
            # TableUnavailable 이벤트 발행 (슬롯 정보 없음)
            publish_table_unavailable_event(
                restaurant_id=restaurant_id,
                reservation_id=reservation_id,
                time_slot=time_slot,
                party_size=party_size,
                available_slots=0
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No availability data found',
                    'restaurantId': restaurant_id,
                    'timeSlot': time_slot,
                    'availabilityStatus': 'NO_DATA'
                })
            }
        
        # 예약 가능 슬롯 정보 추출
        availability_item = response['Item']
        available_slots = int(availability_item.get('availableSlots', 0))
        
        print(f"Available slots for {restaurant_id} at {time_slot}: {available_slots}")
        
        # 예약 가능 슬롯 부족 확인
        if party_size > available_slots:
            print(f"Table unavailable: party size ({party_size}) exceeds available slots ({available_slots})")
            
            # TableUnavailable 이벤트 발행
            publish_table_unavailable_event(
                restaurant_id=restaurant_id,
                reservation_id=reservation_id,
                time_slot=time_slot,
                party_size=party_size,
                available_slots=available_slots
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Table unavailable',
                    'restaurantId': restaurant_id,
                    'timeSlot': time_slot,
                    'partySize': party_size,
                    'availableSlots': available_slots,
                    'availabilityStatus': 'UNAVAILABLE'
                })
            }
        
        # 예약 가능 슬롯 충분
        print(f"Table available: party size ({party_size}) within available slots ({available_slots})")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Table availability check completed',
                'restaurantId': restaurant_id,
                'timeSlot': time_slot,
                'partySize': party_size,
                'availableSlots': available_slots,
                'availabilityStatus': 'AVAILABLE'
            })
        }
        
    except KeyError as e:
        # 필수 필드 누락 오류
        print(f"Missing required field in event: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Bad Request',
                'message': f'Missing required field: {str(e)}'
            })
        }
        
    except Exception as e:
        # 기타 오류
        print(f"Error checking table availability: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


def publish_table_unavailable_event(restaurant_id, reservation_id, time_slot, party_size, available_slots):
    """
    EventBridge에 TableUnavailable 이벤트를 발행하는 헬퍼 함수
    
    Args:
        restaurant_id (str): 레스토랑 ID
        reservation_id (str): 예약 ID
        time_slot (str): 예약 시간대 (날짜#시간 형식)
        party_size (int): 인원 수
        available_slots (int): 예약 가능한 슬롯 수
    """
    try:
        # 현재 시간 (ISO 8601 형식)
        current_time = datetime.utcnow().isoformat()
        
        # EventBridge에 발행할 이벤트 데이터
        event_detail = {
            'restaurantId': restaurant_id,
            'reservationId': reservation_id,
            'timeSlot': time_slot,
            'partySize': party_size,
            'availableSlots': available_slots,
            'timestamp': current_time
        }
        
        # EventBridge에 TableUnavailable 이벤트 발행
        response = eventbridge.put_events(
            Entries=[
                {
                    'Source': 'availability.service',
                    'DetailType': 'TableUnavailable',
                    'Detail': json.dumps(event_detail),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        
        # EventBridge 응답 확인
        if response['FailedEntryCount'] > 0:
            print(f"Failed to publish TableUnavailable event: {response}")
        else:
            print(f"TableUnavailable event published for reservation: {reservation_id}")
            
    except Exception as e:
        print(f"Error publishing TableUnavailable event: {str(e)}")
