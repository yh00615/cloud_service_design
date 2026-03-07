# Week 6-3: CloudFormation 변경 세트 실습 파일

이 폴더에는 CloudFormation 변경 세트 생성 및 적용 실습에 필요한 파일들이 포함되어 있습니다.

## 📁 포함된 파일

### 1. s3-bucket-versioning.yaml
**용도**: 태스크 2에서 사용  
**설명**: S3 버킷에 버전 관리와 태그를 추가하는 템플릿

**주요 변경 사항**:
- 버전 관리 활성화 (VersioningConfiguration)
- 태그 추가 (Environment, Purpose)

**사용 시점**: 변경 세트를 생성하여 기존 스택을 안전하게 업데이트할 때

### 2. stack-policy.json
**용도**: 태스크 5에서 사용  
**설명**: S3 버킷의 교체와 삭제를 차단하는 스택 정책

**정책 내용**:
- S3 버킷의 Replace와 Delete 작업 차단
- 다른 모든 Update 작업은 허용

**사용 시점**: 중요한 리소스를 실수로 삭제하거나 교체하지 않도록 보호할 때

### 3. s3-bucket-rename.yaml
**용도**: 태스크 5.3에서 사용  
**설명**: 버킷 이름을 변경하여 리소스 교체를 시도하는 템플릿 (테스트용)

**주요 특징**:
- BucketName 속성 추가 (리소스 교체 발생)
- 스택 정책이 이를 차단하는지 테스트

**사용 시점**: 스택 정책이 올바르게 작동하는지 검증할 때

## 🎯 실습 흐름

```
1. 기본 스택 생성
   └─ AWS 제공 템플릿 사용

2. 변경 세트 생성
   └─ s3-bucket-versioning.yaml 사용
   └─ 변경 사항 검토

3. 변경 세트 실행
   └─ 스택 업데이트

4. 스택 정책 적용
   └─ stack-policy.json 사용

5. 스택 정책 테스트
   └─ s3-bucket-rename.yaml 사용
   └─ 교체 차단 확인

6. 드리프트 감지
   └─ 수동 변경 탐지
```

## 💡 주요 학습 포인트

### 변경 세트 (Change Set)
- 스택 업데이트 전 변경 사항을 미리 확인
- 리소스 교체 여부 확인 가능
- 안전한 프로덕션 배포

### 스택 정책 (Stack Policy)
- 중요 리소스 보호
- 실수로 인한 삭제/교체 방지
- 한 번 설정하면 제거 불가

### 드리프트 감지 (Drift Detection)
- 템플릿과 실제 리소스 비교
- 수동 변경 탐지
- 인프라 일관성 유지

## ⚠️ 주의사항

1. **스택 정책 설정 후**:
   - 스택 정책은 제거할 수 없습니다
   - 더 제한적인 정책으로만 업데이트 가능
   - 신중하게 설정하세요

2. **리소스 교체**:
   - Replacement: True인 경우 데이터 손실 가능
   - 반드시 변경 세트로 확인 후 실행
   - 백업 필수

3. **드리프트 감지**:
   - 자동으로 수정하지 않음
   - 관리자가 수동으로 처리 필요
   - 정기적으로 확인 권장

## 🔗 관련 AWS 문서

- [변경 세트 사용](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)
- [스택 정책](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html)
- [드리프트 감지](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html)

## 📝 실습 가이드

전체 실습 가이드는 다음 위치에서 확인할 수 있습니다:
`/content/week6/6-3-cloudformation-changeset.md`
