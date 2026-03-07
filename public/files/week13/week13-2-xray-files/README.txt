# AWS X-Ray 실습 파일 안내

이 폴더에는 AWS X-Ray를 활용한 서버리스 애플리케이션 추적 실습에 필요한 파일이 포함되어 있습니다.

## 📁 포함 파일

1. **lambda_function.py**
   - X-Ray SDK가 통합된 Lambda 함수 코드
   - 분산 추적, 서브세그먼트, 메타데이터/어노테이션 기능 포함
   - DynamoDB 호출 자동 추적
   - 외부 API 호출 시뮬레이션

2. **lambda-iam-policy.json**
   - Lambda 함수 실행 역할에 연결할 IAM 정책
   - X-Ray 추적 권한 (PutTraceSegments, PutTelemetryRecords)
   - CloudWatch Logs 권한 (로깅용)
   - DynamoDB 권한 (선택사항)

## 🚀 실습 진행 방법

### 1단계: Lambda 함수 생성
- 런타임: Python 3.11
- 함수 이름: xray-demo-function
- lambda_function.py 코드 업로드

### 2단계: X-Ray SDK 설치
Lambda 함수에 X-Ray SDK를 추가해야 합니다.

**방법 1: Lambda 레이어 사용 (권장)**
- AWS에서 제공하는 X-Ray SDK 레이어 사용
- 레이어 ARN: arn:aws:lambda:ap-northeast-2:580247275435:layer:LambdaInsightsExtension:14

**방법 2: 배포 패키지 생성**
```bash
# 로컬에서 패키지 생성
mkdir package
pip install aws-xray-sdk -t package/
cd package
zip -r ../lambda-package.zip .
cd ..
zip -g lambda-package.zip lambda_function.py
```

### 3단계: IAM 권한 설정
lambda-iam-policy.json 파일의 정책을 Lambda 실행 역할에 연결합니다.

### 4단계: X-Ray 추적 활성화
Lambda 함수 설정에서 "Active tracing" 활성화

### 5단계: API Gateway 생성
Lambda 함수를 트리거할 API Gateway 생성

### 6단계: 테스트 및 추적 확인
- API Gateway 엔드포인트 호출
- X-Ray 콘솔에서 서비스 맵 확인
- 트레이스 분석

## 📊 X-Ray 추적 기능

### 자동 추적
- AWS SDK 호출 (boto3)
- HTTP 요청
- SQL 쿼리

### 커스텀 서브세그먼트
- health_check: 헬스 체크 작업
- get_data_from_dynamodb: DynamoDB 조회
- put_data_to_dynamodb: DynamoDB 저장
- process_data: 데이터 처리
- validate: 데이터 검증
- transform: 데이터 변환
- external_api_call: 외부 API 호출

### 메타데이터 및 어노테이션
- 어노테이션: 검색 가능한 키-값 쌍
- 메타데이터: 추가 정보 (검색 불가)

## 🔍 X-Ray 콘솔 사용법

### 서비스 맵
- Lambda 함수와 연결된 서비스 시각화
- DynamoDB, 외부 API 등의 의존성 확인
- 응답 시간 및 오류율 확인

### 트레이스
- 개별 요청의 전체 경로 추적
- 각 서브세그먼트의 실행 시간 확인
- 병목 지점 식별

### X-Ray Insights
- 자동 이상 탐지
- 응답 시간 증가 감지
- 오류율 증가 감지

## 💡 실습 팁

1. **DynamoDB 테이블 생성 (선택사항)**
   - 테이블 이름: xray-demo-table
   - 파티션 키: id (String)
   - 환경 변수 TABLE_NAME 설정

2. **여러 엔드포인트 테스트**
   - /health: 헬스 체크
   - /data (GET): 데이터 조회
   - /data (POST): 데이터 저장
   - /process: 데이터 처리

3. **부하 테스트**
   - 여러 번 API 호출하여 트레이스 수집
   - 서비스 맵에서 평균 응답 시간 확인

4. **오류 시뮬레이션**
   - 잘못된 요청 보내기
   - X-Ray에서 오류 추적 확인

## 📚 참고 자료

- AWS X-Ray 개발자 가이드: https://docs.aws.amazon.com/xray/
- X-Ray SDK for Python: https://docs.aws.amazon.com/xray-sdk-for-python/
- Lambda와 X-Ray 통합: https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/services-xray.html

## ⚠️ 주의사항

- X-Ray 추적은 무료 티어 제공 (월 100,000개 트레이스)
- 초과 시 트레이스당 $0.000005 부과
- 실습 종료 후 Lambda 함수 및 API Gateway 삭제 권장
