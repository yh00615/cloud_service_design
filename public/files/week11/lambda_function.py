"""
AWS Lambda 함수: S3 데이터 파이프라인 자동 처리

이 Lambda 함수는 S3에 업로드된 CSV 파일을 자동으로 처리하여
판매 데이터를 분석하고 통계를 계산합니다.

환경 변수:
    없음 (S3 이벤트에서 버킷과 키 정보를 받음)

트리거:
    S3 Object Created 이벤트 (raw-data/*.csv)

출력:
    CloudWatch Logs에 처리 결과 출력
    - 총 주문 수
    - 총 매출
    - 평균 주문 금액

작성자: AWS 실습 가이드
버전: 1.0.0
"""

import json
import boto3
import csv
from io import StringIO

# S3 클라이언트 초기화
s3 = boto3.client('s3')


def lambda_handler(event, context):
    """
    Lambda 함수의 메인 핸들러
    
    S3에 업로드된 CSV 파일을 읽고 판매 데이터를 분석합니다.
    각 주문의 매출(수량 × 가격)을 계산하여 총 주문 수, 총 매출,
    평균 주문 금액을 산출합니다.
    
    Args:
        event (dict): S3 이벤트 정보
            - Records[0].s3.bucket.name: S3 버킷 이름
            - Records[0].s3.object.key: S3 객체 키 (파일 경로)
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): HTTP 상태 코드 (200: 성공)
            - body (str): JSON 형식의 처리 결과
                - total_orders: 총 주문 수
                - total_sales: 총 매출
                - average_order_value: 평균 주문 금액
    
    Example:
        >>> event = {
        ...     'Records': [{
        ...         's3': {
        ...             'bucket': {'name': 'my-bucket'},
        ...             'object': {'key': 'raw-data/sales.csv'}
        ...         }
        ...     }]
        ... }
        >>> result = lambda_handler(event, None)
        >>> print(result['statusCode'])
        200
    """
    # S3 이벤트에서 버킷과 키 정보 추출
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # 처리 시작 로그 출력
    print(f"Processing file: s3://{bucket}/{key}")
    
    # S3에서 파일 읽기
    # get_object()는 파일 내용을 바이트 스트림으로 반환
    response = s3.get_object(Bucket=bucket, Key=key)
    
    # 바이트 스트림을 UTF-8 문자열로 디코딩
    content = response['Body'].read().decode('utf-8')
    
    # CSV 파싱
    # StringIO를 사용하여 문자열을 파일처럼 처리
    # DictReader는 첫 번째 행을 헤더로 사용하여 딕셔너리 형태로 각 행을 반환
    csv_reader = csv.DictReader(StringIO(content))
    
    # 데이터 처리: 총 매출 계산
    total_sales = 0  # 총 매출 누적 변수
    order_count = 0  # 주문 수 카운터
    
    # CSV의 각 행을 순회하며 매출 계산
    for row in csv_reader:
        # 수량과 가격을 정수로 변환
        # CSV에서 읽은 값은 문자열이므로 int()로 변환 필요
        quantity = int(row['quantity'])
        price = int(row['price'])
        
        # 주문 매출 = 수량 × 가격
        total_sales += quantity * price
        
        # 주문 수 증가
        order_count += 1
    
    # 결과 계산
    # 평균 주문 금액 = 총 매출 / 주문 수
    # 주문이 없는 경우 0으로 처리 (ZeroDivisionError 방지)
    result = {
        'total_orders': order_count,
        'total_sales': total_sales,
        'average_order_value': total_sales / order_count if order_count > 0 else 0
    }
    
    # 처리 완료 로그 출력 (JSON 형식)
    print(f"Processing complete: {json.dumps(result)}")
    
    # HTTP 200 응답 반환
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
