# Week 11-3: AWS Glue를 활용한 데이터 파이프라인 구축

## 포함 파일

- `week11-3-data-pipeline-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, AWS IAM 역할, AWS Lambda 함수, EventBridge 규칙, 샘플 데이터 자동 생성)
- `lambda_function.py` - AWS Lambda 함수 소스 코드 (참고용, CloudFormation이 자동 배포)
- `sales-data.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)
- `sales-data-2.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)

## 관련 태스크

- 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿으로 Amazon S3, AWS IAM 역할, AWS Lambda, EventBridge 규칙, 샘플 데이터 자동 생성)
- 태스크 5: 파이프라인 테스트 (sales-data.csv 또는 sales-data-2.csv를 업로드하여 AWS Lambda 자동 트리거 확인)
