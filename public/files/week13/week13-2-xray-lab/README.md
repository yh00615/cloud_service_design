# Week 13-2: AWS X-Ray를 활용한 서버리스 애플리케이션 추적

## 포함 파일

- `week13-2-xray-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 QuickTable 환경 자동 생성: Reservations 테이블, CreateReservation/GetReservations AWS Lambda 함수, Amazon API Gateway, AWS X-Ray 추적 활성화)
- `create_reservation.py` - AWS X-Ray SDK가 통합된 예약 생성 AWS Lambda 함수 코드
- `get_reservations.py` - AWS X-Ray SDK가 통합된 예약 조회 AWS Lambda 함수 코드

## 관련 태스크

- 태스크 0: 실습 환경 구축 (AWS CloudFormation 스택 생성으로 QuickTable API 인프라 자동 배포)
- 태스크 1: AWS Lambda 함수 코드 확인 (AWS X-Ray SDK 통합 패턴 확인)
- 태스크 2: AWS X-Ray 추적 활성화 확인 (AWS Lambda 함수의 Active tracing 설정 확인)
- 태스크 3~4: API 호출 및 트레이스 생성 (예약 생성/조회 API 호출하여 AWS X-Ray 트레이스 데이터 생성)
- 태스크 5~6: 서비스 맵 확인 및 트레이스 분석
- 태스크 7: AWS X-Ray Insights 및 Analytics 활용
