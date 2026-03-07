"""
AWS Lambda 함수: Rekognition 자동 이미지 분석 시스템

이 Lambda 함수는 S3에 업로드된 이미지를 Amazon Rekognition을 사용하여
자동으로 분석하고 결과를 DynamoDB에 저장합니다.

주요 기능:
    1. 얼굴 인식 및 감정 분석
    2. 객체 및 장면 탐지
    3. 이미지 내 텍스트 추출 (OCR)
    4. 분석 결과를 DynamoDB에 저장

환경 변수:
    DYNAMODB_TABLE (str): 분석 결과를 저장할 DynamoDB 테이블 이름

트리거:
    S3 이벤트 (input-images/ 폴더에 이미지 업로드 시)

출력:
    DynamoDB 테이블에 다음 정보 저장:
        - image_key: S3 객체 키
        - timestamp: 분석 시간
        - bucket: S3 버킷 이름
        - analyses: 분석 결과 (JSON)

작성자: AWS 실습 가이드
버전: 1.0.0
"""

import json
import boto3
import os
from datetime import datetime

# AWS 클라이언트 초기화
rekognition = boto3.client('rekognition')  # Rekognition 이미지 분석
dynamodb = boto3.resource('dynamodb')  # DynamoDB 데이터 저장
s3 = boto3.client('s3')  # S3 객체 접근


def lambda_handler(event, context):
    """
    S3 이벤트를 처리하고 이미지를 분석하는 Lambda 핸들러
    
    S3에 이미지가 업로드되면 자동으로 트리거되어 Rekognition으로
    얼굴, 객체, 텍스트를 분석하고 결과를 DynamoDB에 저장합니다.
    
    Args:
        event (dict): S3 이벤트 정보
            - Records[0].s3.bucket.name: S3 버킷 이름
            - Records[0].s3.object.key: S3 객체 키
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공)
            - body (str): JSON 형식의 분석 결과
    
    Example:
        >>> event = {
        ...     'Records': [{
        ...         's3': {
        ...             'bucket': {'name': 'my-bucket'},
        ...             'object': {'key': 'input-images/photo.jpg'}
        ...         }
        ...     }]
        ... }
        >>> result = lambda_handler(event, None)
        >>> print(result['statusCode'])
        200
    """
    # S3 이벤트에서 버킷과 키 추출
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # 처리 시작 로그
    print(f"Processing image: {bucket}/{key}")
    
    # 이미지 분석 결과 저장용 딕셔너리 초기화
    results = {
        'bucket': bucket,  # S3 버킷 이름
        'key': key,  # S3 객체 키
        'timestamp': datetime.now().isoformat(),  # 분석 시간 (ISO 8601 형식)
        'analyses': {}  # 분석 결과 저장
    }
    
    try:
        # 1. 얼굴 분석 (Face Detection)
        # 이미지에서 얼굴을 감지하고 감정, 연령, 성별 등을 분석
        face_response = rekognition.detect_faces(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            Attributes=['ALL']  # 모든 얼굴 속성 분석 (감정, 연령, 성별, 안경 등)
        )
        
        # 얼굴 분석 결과 저장
        results['analyses']['faces'] = {
            'count': len(face_response['FaceDetails']),  # 감지된 얼굴 수
            'details': face_response['FaceDetails']  # 각 얼굴의 상세 정보
        }
        
        # 얼굴 감지 성공 로그
        print(f"Detected {len(face_response['FaceDetails'])} faces")
        
    except Exception as e:
        # 얼굴 분석 실패 시 오류 로그 및 저장
        print(f"Face detection error: {str(e)}")
        results['analyses']['faces'] = {'error': str(e)}
    
    try:
        # 2. 객체 및 장면 탐지 (Label Detection)
        # 이미지에서 객체, 장면, 활동을 탐지
        label_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,  # 최대 10개 레이블 반환
            MinConfidence=70  # 신뢰도 70% 이상만 반환
        )
        
        # 레이블 탐지 결과 저장
        results['analyses']['labels'] = {
            'count': len(label_response['Labels']),  # 감지된 레이블 수
            'details': label_response['Labels']  # 각 레이블의 상세 정보
        }
        
        # 레이블 탐지 성공 로그
        print(f"Detected {len(label_response['Labels'])} labels")
        
    except Exception as e:
        # 레이블 탐지 실패 시 오류 로그 및 저장
        print(f"Label detection error: {str(e)}")
        results['analyses']['labels'] = {'error': str(e)}
    
    try:
        # 3. 텍스트 추출 (Text Detection / OCR)
        # 이미지에서 텍스트를 추출 (한글, 영어 등 다양한 언어 지원)
        text_response = rekognition.detect_text(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        # 텍스트 추출 결과 저장
        results['analyses']['text'] = {
            'count': len(text_response['TextDetections']),  # 감지된 텍스트 항목 수
            'details': text_response['TextDetections']  # 각 텍스트의 상세 정보
        }
        
        # 텍스트 추출 성공 로그
        print(f"Detected {len(text_response['TextDetections'])} text items")
        
    except Exception as e:
        # 텍스트 추출 실패 시 오류 로그 및 저장
        print(f"Text detection error: {str(e)}")
        results['analyses']['text'] = {'error': str(e)}
    
    # DynamoDB에 결과 저장
    # 환경 변수에서 테이블 이름 가져오기
    table_name = os.environ.get('DYNAMODB_TABLE')
    
    if table_name:
        try:
            # DynamoDB 테이블 객체 가져오기
            table = dynamodb.Table(table_name)
            
            # 분석 결과를 DynamoDB에 저장
            table.put_item(Item={
                'image_key': key,  # Partition Key: S3 객체 키
                'timestamp': results['timestamp'],  # Sort Key: 분석 시간
                'bucket': bucket,  # S3 버킷 이름
                'analyses': json.dumps(results['analyses'])  # 분석 결과 (JSON 문자열)
            })
            
            # DynamoDB 저장 성공 로그
            print(f"Results saved to DynamoDB: {table_name}")
            
        except Exception as e:
            # DynamoDB 저장 실패 시 오류 로그
            # 저장 실패해도 함수는 계속 실행 (분석 결과는 반환)
            print(f"DynamoDB save error: {str(e)}")
    else:
        # 환경 변수가 설정되지 않은 경우 경고 로그
        print("Warning: DYNAMODB_TABLE environment variable not set")
    
    # 성공 응답 반환
    return {
        'statusCode': 200,
        'body': json.dumps(results, default=str)  # datetime 객체를 문자열로 변환
    }
