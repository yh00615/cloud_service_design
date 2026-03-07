# Week 11 실습 파일 안내

## 📦 포함된 파일

### Week 11-2: AWS Glue Crawler 및 Amazon Athena 쿼리 실습

**파일**: `week11-2-datalake-lab.yaml`

**생성 리소스**:
- **S3 Buckets** (3개)
  - Raw Data Bucket: 원본 데이터 저장
  - Processed Data Bucket: 처리된 데이터 저장
  - Query Results Bucket: Athena 쿼리 결과 저장
- **Glue Database**: 데이터 카탈로그 데이터베이스
- **Glue Crawler**: 데이터 스키마 자동 탐지
- **Athena Workgroup**: 쿼리 실행 환경
- **샘플 데이터**: 고객 이탈 데이터(CSV), 판매 데이터(JSON)

**리소스 이름 충돌 방지**:
- StudentId 파라미터를 사용하여 학번으로 고유성 보장
- 예: `week11-raw-20240001-ap-northeast-2`

**샘플 데이터**:
- `customer-churn.csv`: 고객 이탈 분석 데이터 (10개 레코드)
- `sales.json`: 판매 데이터 (JSON Lines 형식, 5개 레코드)

---

### Week 11-3: AWS Glue를 활용한 데이터 파이프라인 구축 실습

**파일**: `week11-3-data-pipeline-lab.yaml`

**생성 리소스**:
- **S3 Buckets** (3개)
  - Data Bucket: 원본 및 처리된 데이터 저장
  - Scripts Bucket: Glue ETL 스크립트 저장
  - Temp Bucket: 임시 파일 저장 (1일 후 자동 삭제)
- **Glue Database**: 파이프라인 데이터베이스
- **Glue Crawler**: 원본 데이터 스키마 탐지
- **Glue ETL Job**: 데이터 변환 작업
- **Lambda Function**: 파이프라인 트리거
- **EventBridge Rule**: S3 이벤트 감지
- **샘플 데이터**: 거래 데이터(CSV)
- **샘플 스크립트**: Glue ETL 스크립트(Python)

**파이프라인 흐름**:
1. 새 파일이 `s3://data-bucket/raw/`에 업로드
2. EventBridge가 S3 이벤트 감지
3. Lambda 함수가 Glue Crawler 시작
4. Crawler가 데이터 카탈로그 업데이트
5. Glue ETL Job 실행 (수동 또는 자동)
6. 처리된 데이터가 `s3://data-bucket/processed/`에 저장

**샘플 데이터**:
- `transactions.csv`: 거래 데이터 (10개 레코드)
- `etl-script.py`: Glue ETL 스크립트 (학생이 수정 가능)

---

## 🚀 사용 방법

### 1. CloudFormation 스택 생성

```bash
# AWS CLI로 스택 생성 (Week 11-2 예시)
aws cloudformation create-stack \
  --stack-name week11-2-lab-20240001 \
  --template-body file://week11-2-datalake-lab.yaml \
  --parameters ParameterKey=StudentId,ParameterValue=20240001 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-2
```

**중요 파라미터**:
- `StudentId`: 학번 또는 고유 식별자 (소문자, 숫자, 하이픈만 사용, 5-20자)
  - 예: `20240001`, `student01`, `john-doe`
  - 이 값으로 S3 버킷 및 Glue Database 이름이 생성됩니다

### 2. 스택 생성 확인

```bash
# 스택 상태 확인
aws cloudformation describe-stacks \
  --stack-name week11-2-lab-20240001 \
  --region ap-northeast-2

# 출력값 확인
aws cloudformation describe-stacks \
  --stack-name week11-2-lab-20240001 \
  --query 'Stacks[0].Outputs' \
  --region ap-northeast-2
```

### 3. 리소스 정리

```bash
# 스택 삭제 (모든 리소스 자동 삭제)
aws cloudformation delete-stack \
  --stack-name week11-2-lab-20240001 \
  --region ap-northeast-2
```

---

## 📋 리소스 이름 규칙

### Week 11-2 (Data Lake)

| 리소스 | 이름 패턴 | 예시 |
|--------|----------|------|
| Raw Data Bucket | `week11-raw-{StudentId}-{Region}` | `week11-raw-20240001-ap-northeast-2` |
| Processed Data Bucket | `week11-processed-{StudentId}-{Region}` | `week11-processed-20240001-ap-northeast-2` |
| Query Results Bucket | `week11-query-{StudentId}-{Region}` | `week11-query-20240001-ap-northeast-2` |
| Glue Database | `week11_db_{StudentId}` | `week11_db_20240001` |
| Glue Crawler | `week11-crawler-{StudentId}` | `week11-crawler-20240001` |
| Athena Workgroup | `week11-workgroup-{StudentId}` | `week11-workgroup-20240001` |

### Week 11-3 (Data Pipeline)

| 리소스 | 이름 패턴 | 예시 |
|--------|----------|------|
| Data Bucket | `week11-data-{StudentId}-{Region}` | `week11-data-20240001-ap-northeast-2` |
| Scripts Bucket | `week11-scripts-{StudentId}-{Region}` | `week11-scripts-20240001-ap-northeast-2` |
| Temp Bucket | `week11-temp-{StudentId}-{Region}` | `week11-temp-20240001-ap-northeast-2` |
| Glue Database | `week11_pipeline_{StudentId}` | `week11_pipeline_20240001` |
| Glue Crawler | `week11-pipeline-crawler-{StudentId}` | `week11-pipeline-crawler-20240001` |
| Glue ETL Job | `week11-etl-job-{StudentId}` | `week11-etl-job-20240001` |
| Lambda Function | `week11-3-pipeline-lab-PipelineTrigger-{StudentId}` | `week11-3-pipeline-lab-PipelineTrigger-20240001` |

---

## 💡 주의사항

### 1. StudentId 파라미터 규칙
- **필수**: 소문자, 숫자, 하이픈(-)만 사용
- **길이**: 5-20자
- **예시**: `20240001`, `student01`, `john-doe`
- **금지**: 대문자, 특수문자, 공백

### 2. 리소스 이름 충돌 방지
- 여러 학생이 같은 AWS 계정을 사용하는 경우, 각자 고유한 StudentId를 사용해야 합니다
- StudentId가 같으면 리소스 이름이 충돌하여 스택 생성이 실패합니다

### 3. 비용 관리
- **Glue Crawler**: 실행 시간당 과금 (DPU 기준)
- **Glue ETL Job**: 실행 시간당 과금 (DPU 기준)
- **Athena**: 스캔한 데이터 양에 따라 과금
- **S3**: 저장 용량 및 요청 수에 따라 과금
- **실습 종료 후 반드시 스택을 삭제하세요!**

### 4. 샘플 데이터 자동 업로드
- CloudFormation 스택 생성 시 Lambda Custom Resource가 샘플 데이터를 자동으로 업로드합니다
- 별도로 데이터를 업로드할 필요가 없습니다
- 스택 생성 완료 후 S3 콘솔에서 데이터를 확인할 수 있습니다

### 5. 리소스 정리
- CloudFormation 스택을 삭제하면 모든 리소스가 자동으로 삭제됩니다
- S3 버킷에 데이터가 있어도 자동으로 삭제됩니다 (DeletionPolicy 설정)
- 수동으로 생성한 리소스는 별도로 삭제해야 합니다

---

## 🔍 문제 해결

### 스택 생성 실패: "Bucket already exists"
**원인**: 동일한 StudentId를 사용하는 다른 스택이 이미 존재합니다.

**해결**:
1. 다른 StudentId를 사용하거나
2. 기존 스택을 삭제한 후 다시 생성하세요

### Glue Crawler 실행 실패
**원인**: S3 버킷에 데이터가 없거나 권한이 부족합니다.

**해결**:
1. S3 콘솔에서 샘플 데이터가 업로드되었는지 확인
2. Glue Crawler IAM Role의 권한 확인
3. CloudWatch Logs에서 오류 메시지 확인

### Athena 쿼리 실패
**원인**: Glue Crawler가 실행되지 않았거나 테이블이 생성되지 않았습니다.

**해결**:
1. Glue 콘솔에서 Crawler를 실행
2. Glue Database에 테이블이 생성되었는지 확인
3. Athena Workgroup 설정 확인

### Lambda 함수 실행 실패 (Week 11-3)
**원인**: EventBridge Rule이 활성화되지 않았거나 권한이 부족합니다.

**해결**:
1. EventBridge 콘솔에서 Rule 상태 확인
2. Lambda 함수 권한 확인
3. CloudWatch Logs에서 오류 메시지 확인

---

## 📚 추가 리소스

### AWS 공식 문서
- [AWS Glue 개발자 가이드](https://docs.aws.amazon.com/glue/)
- [Amazon Athena 사용자 가이드](https://docs.aws.amazon.com/athena/)
- [AWS CloudFormation 사용자 가이드](https://docs.aws.amazon.com/cloudformation/)

### 샘플 코드
- [AWS Glue ETL 스크립트 예시](https://github.com/aws-samples/aws-glue-samples)
- [Athena 쿼리 예시](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/code-samples.html)

---

**작성일**: 2025-02-07  
**버전**: 1.0.0
