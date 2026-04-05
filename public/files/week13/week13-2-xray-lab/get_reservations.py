"""
QuickTable 예약 조회 Lambda 함수 (AWS X-Ray SDK 통합)

이 함수는 QuickTable 레스토랑 예약 시스템에서 사용자의 예약 목록을
조회합니다. AWS X-Ray SDK를 사용하여 커스텀 서브세그먼트, 어노테이션,
메타데이터를 기록합니다.

주요 기능:
    1. DynamoDB에서 사용자의 모든 예약 조회 (서브세그먼트: get_reservations)
    2. 조회 결과에 어노테이션/메타데이터 기록

환경 변수:
    TABLE_NAME (str): DynamoDB 테이블 이름

트리거:
    API Gateway GET /reservations

AWS X-Ray 추적 항목:
    - 어노테이션: operation, user_id
    - 메타데이터: reservation_count, user_id
    - 서브세그먼트: get_reservations
"""

import json
import boto3
import os
from decimal import Decimal
from aws_xray_sdk.core import patch_all, xray_recorder

# boto3 DynamoDB 호출 자동 추적
patch_all()

# DynamoDB 테이블 초기화
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB Decimal 타입을 JSON 직렬화하기 위한 커스텀 인코더

    DynamoDB는 숫자를 Decimal 타입으로 반환하므로,
    JSON 직렬화 시 int로 변환합니다.
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super().default(obj)


def lambda_handler(event, context):
    """
    예약 조회 핸들러

    'anonymous' 사용자의 모든 예약을 DynamoDB에서 조회하여 반환합니다.

    Args:
        event (dict): API Gateway 프록시 이벤트
        context: Lambda 실행 컨텍스트

    Returns:
        dict: HTTP 응답
            - statusCode (int): 200 (성공) 또는 500 (오류)
            - headers (dict): CORS 헤더 포함
            - body (str): JSON 형식의 예약 목록
    """
    try:
        user_id = 'anonymous'

        # 서브세그먼트: DynamoDB 예약 조회
        subsegment = xray_recorder.begin_subsegment('get_reservations')
        subsegment.put_annotation('operation', 'get')
        subsegment.put_annotation('user_id', user_id)

        # DynamoDB Query 호출 (patch_all()에 의해 자동 추적됨)
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        items = response.get('Items', [])

        subsegment.put_metadata('reservation_count', len(items))
        subsegment.put_metadata('user_id', user_id)
        xray_recorder.end_subsegment()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(items, cls=DecimalEncoder)
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
