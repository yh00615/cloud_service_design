"""
AWS Lambda 함수: 예약 불가 알림 발송

이 Lambda 함수는 EventBridge에서 TableUnavailable 이벤트를 수신하여
SNS를 통해 예약 불가 알림을 발송합니다.

주요 기능:
    1. TableUnavailable 이벤트 수신 및 파싱
    2. SNS Topic을 통한 알림 메시지 발송
    3. 알림 발송 결과 로깅

환경 변수:
    SNS_TOPIC_ARN (str): SNS Topic ARN (알림 발송용)

트리거:
    EventBridge 규칙 (TableUnavailable 이벤트)
"""

import json
import boto3
import os
from datetime import datetime

# AWS 서비스 클라이언트 초기화
sns = boto3.client('sns')

# 환경 변수에서 SNS Topic ARN 가져오기
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def lambda_handler(event, context):
    """
    TableUnavailable 이벤트를 수신하여 SNS 알림을 발송하는 Lambda 함수
    
    EventBridge에서 전달된 TableUnavailable 이벤트를 분석하고,
    SNS Topic을 통해 예약 불가 알림을 발송합니다.
    
    Args:
        event (dict): EventBridge에서 전달된 TableUnavailable 이벤트
            - detail (dict): 예약 상세 정보
                - restaurantId (str): 레스토랑 ID
                - reservationId (str): 예약 ID
                - timeSlot (str): 예약 시간대 (날짜#시간 형식)
                - partySize (int): 인원 수
                - availableSlots (int): 예약 가능한 슬롯 수
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
        availability_detail = event['detail']
        restaurant_id = availability_detail['restaurantId']
        reservation_id = availability_detail['reservationId']
        time_slot = availability_detail['timeSlot']
        party_size = availability_detail['partySize']
        available_slots = availability_detail['availableSlots']
        
        print(f"Sending notification for reservation: {reservation_id}")
        
        # 알림 메시지 제목 생성
        subject = f"[QuickTable] 예약 불가 알림 - 예약 {reservation_id}"
        
        # 알림 메시지 본문 생성
        message = create_notification_message(
            restaurant_id=restaurant_id,
            reservation_id=reservation_id,
            time_slot=time_slot,
            party_size=party_size,
            available_slots=available_slots
        )
        
        # SNS를 통해 알림 발송
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'restaurantId': {
                    'DataType': 'String',
                    'StringValue': restaurant_id
                },
                'reservationId': {
                    'DataType': 'String',
                    'StringValue': reservation_id
                },
                'timeSlot': {
                    'DataType': 'String',
                    'StringValue': time_slot
                }
            }
        )
        
        # SNS 응답 확인
        message_id = response.get('MessageId')
        print(f"Notification sent successfully: MessageId={message_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notification sent successfully',
                'messageId': message_id,
                'restaurantId': restaurant_id,
                'reservationId': reservation_id
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
        print(f"Error sending notification: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }


def create_notification_message(restaurant_id, reservation_id, time_slot, party_size, available_slots):
    """
    알림 메시지 본문을 생성하는 헬퍼 함수
    
    Args:
        restaurant_id (str): 레스토랑 ID
        reservation_id (str): 예약 ID
        time_slot (str): 예약 시간대 (날짜#시간 형식)
        party_size (int): 인원 수
        available_slots (int): 예약 가능한 슬롯 수
    
    Returns:
        str: 알림 메시지 본문
    """
    # 현재 시간 (ISO 8601 형식)
    current_time = datetime.utcnow().isoformat()
    
    # timeSlot을 날짜와 시간으로 분리
    date_part, time_part = time_slot.split('#')
    
    # 상태 메시지 구성
    if available_slots == 0:
        status_message = "해당 시간대에 예약 가능한 테이블이 없습니다."
    else:
        status_message = f"요청하신 인원({party_size}명)에 비해 예약 가능한 테이블({available_slots}개)이 부족합니다."
    
    # 메시지 본문 생성
    message = f"""
QuickTable 예약 불가 알림

{status_message}

예약 정보:
- 예약 ID: {reservation_id}
- 레스토랑 ID: {restaurant_id}
- 예약 날짜: {date_part}
- 예약 시간: {time_part}
- 요청 인원: {party_size}명
- 예약 가능 테이블: {available_slots}개

조치 사항:
다른 시간대를 선택하시거나 인원을 조정하여 다시 예약을 시도해주세요.

발생 시간: {current_time}

---
이 알림은 QuickTable 레스토랑 예약 시스템에서 자동으로 발송되었습니다.
    """.strip()
    
    return message
