"""
QuickTable 예약 생성 Lambda 함수 (AWS X-Ray SDK 통합)

이 함수는 QuickTable 레스토랑 예약 시스템에서 새로운 예약을 생성하고
Amazon DynamoDB에 저장합니다. AWS X-Ray SDK를 사용하여 커스텀
서브세그먼트, 어노테이션, 메타데이터를 기록합니다.

주요 기능:
    1. API Gateway에서 전달된 예약 정보 파싱
    2. 입력 데이터 검증 (서브세그먼트: validate_input)
    3. DynamoDB에 예약 데이터 저장 (서브세그먼트: create_dynamodb_item)
    4. 각 단계에 어노테이션/메타데이터 기록

환경 변수:
    TABLE_NAME (str): DynamoDB 테이블 이름

트리거:
    API Gateway POST /reservations

AWS X-Ray 추적 항목:
    - 어노테이션: operation, restaurantName, date, reservation_id, status
    - 메타데이터: request_body, reservation_data
    - 서브세그먼트: validate_input, create_dynamodb_item
"""

import json
import boto3
import os
import uuid
from datetime import datetime
from aws_xray_sdk.core import patch_all, xray_recorder

# boto3 DynamoDB 호출 자동 추적
patch_all()

# DynamoDB 테이블 초기화
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """
    예약 생성 핸들러

    API Gateway 프록시 통합으로 전달된 요청을 처리하여
    새로운 예약을 생성하고 DynamoDB에 저장합니다.

    Args:
        event (dict): API Gateway 프록시 이벤트
            - body (str): JSON 형식의 예약 정보
                - userId (str): 사용자 ID (기본값: 'anonymous')
                - restaurantName (str): 레스토랑 이름
                - date (str): 예약 날짜 (YYYY-MM-DD)
                - time (str): 예약 시간 (HH:MM)
                - partySize (int): 인원 수
                - phoneNumber (str): 연락처
        context: Lambda 실행 컨텍스트

    Returns:
        dict: HTTP 응답
            - statusCode (int): 200 (성공) 또는 500 (오류)
            - headers (dict): CORS 헤더 포함
            - body (str): JSON 형식의 응답
    """
    try:
        # 요청 본문 파싱
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('userId', 'anonymous')
        date_str = body.get('date', '')
        time_str = body.get('time', '')

        # 예약 ID 생성 (RSV-날짜-랜덤8자리)
        reservation_id = f"RSV-{date_str.replace('-', '')}-{uuid.uuid4().hex[:8]}"

        # 서브세그먼트: 입력 데이터 검증
        subsegment = xray_recorder.begin_subsegment('validate_input')
        subsegment.put_annotation('operation', 'create')
        subsegment.put_annotation('restaurantName', body.get('restaurantName', ''))
        subsegment.put_annotation('date', date_str)
        subsegment.put_metadata('request_body', body)
        xray_recorder.end_subsegment()

        # 서브세그먼트: DynamoDB에 예약 저장
        subsegment = xray_recorder.begin_subsegment('create_dynamodb_item')
        item = {
            'userId': user_id,
            'reservationId': reservation_id,
            'restaurantName': body.get('restaurantName', ''),
            'date': date_str,
            'time': time_str,
            'partySize': int(body.get('partySize', 1)),
            'phoneNumber': body.get('phoneNumber', ''),
            'status': 'confirmed',
            'createdAt': datetime.utcnow().isoformat()
        }
        subsegment.put_annotation('reservation_id', reservation_id)
        subsegment.put_annotation('status', 'confirmed')
        subsegment.put_metadata('reservation_data', item)

        # DynamoDB PutItem 호출 (patch_all()에 의해 자동 추적됨)
        table.put_item(Item=item)
        xray_recorder.end_subsegment()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Reservation created',
                'reservationId': reservation_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
