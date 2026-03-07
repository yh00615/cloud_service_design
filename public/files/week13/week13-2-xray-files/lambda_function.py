"""
AWS Lambda 함수: X-Ray 분산 추적 데모

이 Lambda 함수는 AWS X-Ray SDK를 사용하여 분산 추적을 구현합니다.
서비스 맵, 트레이스, 세그먼트, 서브세그먼트를 생성하여
애플리케이션의 성능과 병목 지점을 분석할 수 있습니다.

주요 기능:
    1. X-Ray SDK를 사용한 자동 추적
    2. DynamoDB 호출 추적
    3. 외부 HTTP 요청 추적
    4. 커스텀 서브세그먼트 생성
    5. 메타데이터 및 어노테이션 추가

환경 변수:
    TABLE_NAME (str): DynamoDB 테이블 이름 (선택사항)

트리거:
    API Gateway (HTTP 요청)
"""

import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS X-Ray SDK 임포트
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# AWS SDK 자동 패치 (boto3 호출 자동 추적)
patch_all()

import boto3
from botocore.exceptions import ClientError

# DynamoDB 클라이언트 생성 (X-Ray가 자동으로 추적)
dynamodb = boto3.resource('dynamodb')

# 환경 변수에서 테이블 이름 가져오기
TABLE_NAME = os.environ.get('TABLE_NAME', 'xray-demo-table')


def lambda_handler(event: dict, context: Any) -> dict:
    """
    X-Ray 추적이 활성화된 Lambda 핸들러 함수
    
    API Gateway에서 전달된 요청을 처리하고,
    X-Ray를 사용하여 모든 작업을 추적합니다.
    
    Args:
        event (dict): API Gateway 이벤트
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공)
            - body (str): JSON 형식의 응답
    """
    
    # 요청 정보를 X-Ray 세그먼트에 추가
    segment = xray_recorder.current_segment()
    segment.put_annotation('function_name', context.function_name)
    segment.put_annotation('request_id', context.request_id)
    
    # 이벤트 정보 로깅
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # HTTP 메서드 확인
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # 경로별 처리
        if path == '/health':
            return handle_health_check()
        elif path == '/data':
            if http_method == 'GET':
                return handle_get_data()
            elif http_method == 'POST':
                body = json.loads(event.get('body', '{}'))
                return handle_post_data(body)
        elif path == '/process':
            return handle_process_data()
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Not Found',
                    'path': path
                })
            }
    
    except Exception as e:
        # 오류를 X-Ray에 기록
        segment.put_annotation('error', str(e))
        logger.error(f"Error: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Internal Server Error',
                'error': str(e)
            })
        }


def handle_health_check() -> dict:
    """
    헬스 체크 엔드포인트
    
    X-Ray 서브세그먼트를 생성하여 헬스 체크 작업을 추적합니다.
    
    Returns:
        dict: HTTP 200 응답
    """
    
    # 커스텀 서브세그먼트 생성
    subsegment = xray_recorder.begin_subsegment('health_check')
    
    try:
        # 메타데이터 추가
        subsegment.put_metadata('check_time', datetime.now().isoformat())
        subsegment.put_annotation('status', 'healthy')
        
        # 간단한 지연 시뮬레이션
        time.sleep(0.1)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })
        }
    
    finally:
        # 서브세그먼트 종료
        xray_recorder.end_subsegment()


def handle_get_data() -> dict:
    """
    DynamoDB에서 데이터 조회
    
    X-Ray가 자동으로 DynamoDB 호출을 추적합니다.
    
    Returns:
        dict: HTTP 200 응답 (데이터 목록)
    """
    
    # 커스텀 서브세그먼트 생성
    subsegment = xray_recorder.begin_subsegment('get_data_from_dynamodb')
    
    try:
        # 어노테이션 추가
        subsegment.put_annotation('operation', 'scan')
        subsegment.put_annotation('table_name', TABLE_NAME)
        
        # DynamoDB 테이블 참조
        table = dynamodb.Table(TABLE_NAME)
        
        # 데이터 스캔 (X-Ray가 자동으로 추적)
        response = table.scan(Limit=10)
        items = response.get('Items', [])
        
        # 메타데이터 추가
        subsegment.put_metadata('item_count', len(items))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'items': items,
                'count': len(items)
            }, default=str)
        }
    
    except ClientError as e:
        # DynamoDB 오류 처리
        error_code = e.response['Error']['Code']
        subsegment.put_annotation('error_code', error_code)
        
        logger.error(f"DynamoDB Error: {error_code}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Failed to get data',
                'error': error_code
            })
        }
    
    finally:
        # 서브세그먼트 종료
        xray_recorder.end_subsegment()


def handle_post_data(body: dict) -> dict:
    """
    DynamoDB에 데이터 저장
    
    X-Ray가 자동으로 DynamoDB 호출을 추적합니다.
    
    Args:
        body (dict): 저장할 데이터
    
    Returns:
        dict: HTTP 201 응답
    """
    
    # 커스텀 서브세그먼트 생성
    subsegment = xray_recorder.begin_subsegment('put_data_to_dynamodb')
    
    try:
        # 어노테이션 추가
        subsegment.put_annotation('operation', 'put_item')
        subsegment.put_annotation('table_name', TABLE_NAME)
        
        # 데이터 검증
        if 'id' not in body or 'data' not in body:
            subsegment.put_annotation('validation', 'failed')
            
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing required fields: id, data'
                })
            }
        
        # DynamoDB 테이블 참조
        table = dynamodb.Table(TABLE_NAME)
        
        # 데이터 저장 (X-Ray가 자동으로 추적)
        item = {
            'id': body['id'],
            'data': body['data'],
            'timestamp': datetime.now().isoformat()
        }
        
        table.put_item(Item=item)
        
        # 메타데이터 추가
        subsegment.put_metadata('item', item)
        subsegment.put_annotation('validation', 'success')
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Data saved successfully',
                'item': item
            }, default=str)
        }
    
    except ClientError as e:
        # DynamoDB 오류 처리
        error_code = e.response['Error']['Code']
        subsegment.put_annotation('error_code', error_code)
        
        logger.error(f"DynamoDB Error: {error_code}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Failed to save data',
                'error': error_code
            })
        }
    
    finally:
        # 서브세그먼트 종료
        xray_recorder.end_subsegment()


def handle_process_data() -> dict:
    """
    데이터 처리 시뮬레이션
    
    여러 서브세그먼트를 생성하여 복잡한 처리 과정을 추적합니다.
    
    Returns:
        dict: HTTP 200 응답
    """
    
    # 메인 처리 서브세그먼트
    subsegment = xray_recorder.begin_subsegment('process_data')
    
    try:
        subsegment.put_annotation('operation', 'process')
        
        # 1단계: 데이터 검증
        validation_result = validate_data()
        
        # 2단계: 데이터 변환
        transformation_result = transform_data()
        
        # 3단계: 외부 API 호출 시뮬레이션
        api_result = call_external_api()
        
        # 결과 집계
        result = {
            'validation': validation_result,
            'transformation': transformation_result,
            'api_call': api_result,
            'timestamp': datetime.now().isoformat()
        }
        
        subsegment.put_metadata('result', result)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    
    finally:
        # 서브세그먼트 종료
        xray_recorder.end_subsegment()


def validate_data() -> dict:
    """
    데이터 검증 서브세그먼트
    
    Returns:
        dict: 검증 결과
    """
    
    subsegment = xray_recorder.begin_subsegment('validate')
    
    try:
        subsegment.put_annotation('step', 'validation')
        
        # 검증 시뮬레이션 (0.2초 지연)
        time.sleep(0.2)
        
        result = {
            'status': 'valid',
            'checks_passed': 5
        }
        
        subsegment.put_metadata('validation_result', result)
        
        return result
    
    finally:
        xray_recorder.end_subsegment()


def transform_data() -> dict:
    """
    데이터 변환 서브세그먼트
    
    Returns:
        dict: 변환 결과
    """
    
    subsegment = xray_recorder.begin_subsegment('transform')
    
    try:
        subsegment.put_annotation('step', 'transformation')
        
        # 변환 시뮬레이션 (0.3초 지연)
        time.sleep(0.3)
        
        result = {
            'status': 'transformed',
            'records_processed': 100
        }
        
        subsegment.put_metadata('transformation_result', result)
        
        return result
    
    finally:
        xray_recorder.end_subsegment()


def call_external_api() -> dict:
    """
    외부 API 호출 서브세그먼트
    
    Returns:
        dict: API 호출 결과
    """
    
    subsegment = xray_recorder.begin_subsegment('external_api_call')
    
    try:
        subsegment.put_annotation('step', 'api_call')
        subsegment.put_annotation('api_endpoint', 'https://api.example.com')
        
        # API 호출 시뮬레이션 (0.5초 지연)
        time.sleep(0.5)
        
        result = {
            'status': 'success',
            'response_time_ms': 500
        }
        
        subsegment.put_metadata('api_result', result)
        
        return result
    
    finally:
        xray_recorder.end_subsegment()
