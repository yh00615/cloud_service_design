# Week 13-2: CloudWatch 모니터링 실습 파일

이 압축 파일에는 CloudWatch 모니터링 실습에 필요한 파일들이 포함되어 있습니다.

## 포함된 파일

### 1. lambda_function.py
- **용도**: 태스크 12에서 사용
- **설명**: 커스텀 메트릭을 CloudWatch에 전송하는 Lambda 함수
- **사용 방법**: Lambda 콘솔의 코드 편집기에 복사하여 붙여넣기

### 2. cloudwatch-agent-config.json
- **용도**: 태스크 8에서 사용
- **설명**: CloudWatch 에이전트 설정 파일
- **사용 방법**: EC2 인스턴스에 SSH 접속 후 파일 내용을 사용

### 3. lambda-iam-policy.json
- **용도**: 태스크 12에서 사용 (Secrets Manager 실습용)
- **설명**: Lambda 함수가 Secrets Manager와 Parameter Store에 접근하기 위한 IAM 정책
- **사용 방법**: IAM 콘솔에서 인라인 정책 생성 시 JSON 탭에 붙여넣기

## 사용 순서

1. **태스크 8**: cloudwatch-agent-config.json 사용
2. **태스크 12**: lambda_function.py 및 lambda-iam-policy.json 사용

## 주의사항

- 파일을 수정하지 말고 그대로 사용하세요
- 실습 가이드의 단계를 따라 정확한 위치에 파일 내용을 붙여넣으세요
- SSH 접속 시 파일을 직접 업로드하거나 내용을 복사하여 사용할 수 있습니다
