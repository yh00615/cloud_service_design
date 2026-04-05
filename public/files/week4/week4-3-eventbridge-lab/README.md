# Week 4-3: Amazon EventBridge 기반 예약 처리 시스템

## 포함 파일

- `week4-3-quicktable-events-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB 테이블, Amazon EventBridge Event Bus, AWS Lambda 함수 3개, AWS Lambda 역할, Amazon SNS Topic 자동 생성)
- `reservation_processor.py` - 예약 생성 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
- `table_availability_checker.py` - 테이블 재고 확인 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
- `notification_sender.py` - 알림 발송 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)

## 관련 태스크

- 태스크 0: 실습 환경 구축 (week4-3-quicktable-events-lab.yaml 사용)
