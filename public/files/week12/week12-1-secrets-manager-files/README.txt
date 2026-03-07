# Week 12-1: Secrets Manager 자격증명 관리 실습 파일

이 압축 파일에는 Secrets Manager 실습에 필요한 파일들이 포함되어 있습니다.

## 포함된 파일

### 1. lambda_function.py
- **용도**: 태스크 5에서 사용
- **설명**: Secrets Manager와 Parameter Store에서 자격증명을 조회하는 Lambda 함수
- **사용 방법**: Lambda 콘솔의 코드 편집기에 복사하여 붙여넣기

### 2. lambda-iam-policy.json
- **용도**: 태스크 5에서 사용
- **설명**: Lambda 함수가 Secrets Manager, Parameter Store, KMS에 접근하기 위한 IAM 정책
- **사용 방법**: IAM 콘솔에서 인라인 정책 생성 시 JSON 탭에 붙여넣기

## 사용 순서

1. **태스크 5 - 6번**: lambda_function.py를 Lambda 코드 편집기에 붙여넣기
2. **태스크 5 - 13번**: lambda-iam-policy.json을 IAM 인라인 정책에 붙여넣기

## 주요 기능

### lambda_function.py
- Secrets Manager에서 데이터베이스 자격증명 조회
- Secrets Manager에서 API 키 조회
- Parameter Store에서 개별 파라미터 조회
- Parameter Store에서 경로별 파라미터 일괄 조회
- 암호화된 파라미터 자동 복호화

### lambda-iam-policy.json
- `prod/` 경로의 시크릿만 접근 가능 (최소 권한 원칙)
- `prod/` 경로의 파라미터만 접근 가능
- KMS 복호화는 Secrets Manager와 SSM을 통해서만 가능 (보안 강화)

## 주의사항

- 파일을 수정하지 말고 그대로 사용하세요
- 실습 가이드의 단계를 따라 정확한 위치에 파일 내용을 붙여넣으세요
- IAM 정책은 최소 권한 원칙을 따르도록 설계되었습니다
