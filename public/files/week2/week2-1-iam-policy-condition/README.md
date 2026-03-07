# IAM 실습 파일

이 패키지는 AWS IAM 역할 및 정책 실습을 위한 JSON 정책 파일들입니다.

## 📦 포함된 파일

### IAM Role Lab
- `assume-role-policy.json` - AssumeRole 권한 정책

### IAM Policy Lab
- `mfa-policy.json` - MFA 강제 정책
- `ip-restriction-policy.json` - IP 제한 정책
- `time-based-policy.json` - 시간 기반 정책
- `README.md` - 이 파일

## 🚀 사용 방법

### 1. AssumeRole 정책 (2-1 실습)

**사용 전 수정**:
- `ACCOUNT_ID`를 실제 AWS 계정 ID로 변경

**적용 방법**:
1. IAM 콘솔 > Users > 사용자 선택
2. Permissions 탭 > Add permissions > Create inline policy
3. JSON 탭에서 내용 붙여넣기
4. 정책 이름: `AssumeS3ReadOnlyRolePolicy`

### 2. MFA 강제 정책 (2-2 실습)

**사용 전 수정**:
- `YOUR_BUCKET_NAME`을 실제 버킷 이름으로 변경

**정책 설명**:
- ✅ 버킷 목록 조회: MFA 없이 가능
- ✅ 객체 읽기: MFA 없이 가능
- ❌ 객체 삭제: MFA 필수

**적용 방법**:
1. IAM 콘솔 > Policies > Create policy
2. JSON 탭에서 내용 붙여넣기
3. 정책 이름: `S3MFADeletePolicy`
4. 사용자에게 정책 연결

### 3. IP 제한 정책 (2-2 실습)

**사용 전 수정**:
- `YOUR_BUCKET_NAME`을 실제 버킷 이름으로 변경
- `YOUR_IP_ADDRESS`를 본인 IP 주소로 변경

**IP 주소 확인**:
```bash
curl https://checkip.amazonaws.com
```

**정책 설명**:
- 지정된 IP 주소에서만 S3 접근 허용
- 다른 IP에서는 접근 거부

### 4. 시간 기반 정책 (2-2 실습)

**사용 전 수정**:
- `YOUR_BUCKET_NAME`을 실제 버킷 이름으로 변경
- 날짜/시간을 원하는 범위로 변경

**정책 설명**:
- 지정된 시간 범위 내에만 S3 접근 허용
- UTC 시간 기준 (한국 시간 -9시간)

## 📋 AWS CLI로 AssumeRole 테스트

### 1. 역할 맡기

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/S3ReadOnlyRole \
  --role-session-name test-session
```

**Response**:
```json
{
  "Credentials": {
    "AccessKeyId": "ASIA...",
    "SecretAccessKey": "...",
    "SessionToken": "...",
    "Expiration": "2024-01-27T12:00:00Z"
  }
}
```

### 2. 임시 자격증명 설정

```bash
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

### 3. S3 접근 테스트

```bash
# 버킷 목록 조회 (성공)
aws s3 ls

# 객체 읽기 (성공)
aws s3 cp s3://your-bucket/file.txt .

# 객체 쓰기 (실패 - 읽기 전용 역할)
aws s3 cp file.txt s3://your-bucket/
```

## 🔍 Condition 키 레퍼런스

### 글로벌 Condition 키

| 키 | 설명 | 예시 |
|---|------|------|
| `aws:CurrentTime` | 현재 시간 | `2024-01-27T10:00:00Z` |
| `aws:SourceIp` | 요청 IP 주소 | `203.0.113.0/24` |
| `aws:MultiFactorAuthPresent` | MFA 인증 여부 | `true` / `false` |
| `aws:UserAgent` | User Agent | `aws-cli/2.0` |
| `aws:SecureTransport` | HTTPS 사용 여부 | `true` / `false` |

### S3 전용 Condition 키

| 키 | 설명 |
|---|------|
| `s3:x-amz-acl` | ACL 설정 |
| `s3:prefix` | 객체 접두사 |
| `s3:delimiter` | 구분자 |

## 💡 실습 팁

1. **정책 테스트**: IAM Policy Simulator 사용
2. **IP 확인**: `curl https://checkip.amazonaws.com`
3. **UTC 시간**: 한국 시간 - 9시간
4. **MFA 설정**: IAM 사용자 > Security credentials > MFA

## 🔗 추가 리소스

- [IAM Policy 문법](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_policies_grammar.html)
- [Condition 키 레퍼런스](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_policies_condition-keys.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)
- [AssumeRole API](https://docs.aws.amazon.com/ko_kr/STS/latest/APIReference/API_AssumeRole.html)
