---
title: 'AWS Config 규칙 생성 및 모니터링'
week: 12
session: 2
awsServices:
  - AWS Config
learningObjectives:
  - AWS Config의 개념과 규정 준수 모니터링의 중요성을 이해할 수 있습니다.
  - AWS Config를 활성화하고 리소스 구성 변경을 기록할 수 있습니다.
  - 관리형 규칙을 추가하여 Amazon S3 버킷 암호화를 검증할 수 있습니다.
  - 규정 준수 대시보드를 확인하고 비준수 리소스를 수정할 수 있습니다.

prerequisites:
  - AWS 리소스 기본 개념 이해
  - 규정 준수 (Compliance) 개념 이해
  - AWS IAM 정책 기본 지식
---

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.
>
> **예상 비용** (ap-northeast-2 리전 기준):
>
> | 리소스           | 타입                | 비용                            |
> | ---------------- | ------------------- | ------------------------------- |
> | AWS Config       | Configuration Items | 월 $0.003/항목 (처음 100,000개) |
> | AWS Config Rules | 규칙 평가           | 월 $0.001/평가 (처음 100,000개) |
> | Amazon S3        | 스토리지            | 월 $0.025/GB                    |
> | Amazon SNS       | 알림                | 월 $0.50/백만 건                |
> | Conformance Pack | 배포                | 월 $0.001/평가                  |
> | **총 예상**      |                     | **월 약 $2-5**                  |

## 태스크 1: AWS Config 설정

### 태스크 1.1: AWS Config 활성화 및 기본 설정

1. AWS Management Console에 로그인한 후 상단 검색창에 `Config`을 입력하고 선택합니다.
2. 처음 사용하는 경우 [[Get started]] 버튼을 클릭합니다.
3. **Settings** 페이지에서 다음을 설정합니다:
	- **Recording strategy**: `Record specific resource types`
	- **Resource types**: 다음 리소스 타입을 선택합니다:
		- `AWS::Amazon S3::Bucket`
     - `AWS::Amazon EC2::Instance`
     - `AWS::Amazon EC2::SecurityGroup`
     - `AWS::AWS IAM::User`
     - `AWS::AWS IAM::Role`
   - **Include global resources**: 체크합니다 (AWS IAM 리소스 추적을 위해 필수).

`Record all resource types`는 모든 AWS 리소스를 추적하여 비용이 많이 발생하므로, 실습에서는 `Record specific resource types`를 선택하여 필요한 리소스만 추적합니다.

### 태스크 1.2: Delivery 설정

4. **Delivery method** 섹션에서:
	- **Amazon S3 bucket**: [[Create a bucket]] 선택
	- 버킷 이름이 자동 생성됩니다 (형식: `config-bucket-{계정ID}-{리전}`)
	- **Amazon SNS topic**: `Stream configuration changes and notifications to an Amazon SNS topic` 체크
   - [[Create a topic]] 선택
   - 토픽 이름이 자동 생성됩니다 (형식: `config-topic-{계정ID}`)
5. [[Next]] 버튼을 클릭합니다.

### 태스크 1.3: AWS IAM 역할 설정 및 활성화

6. **AWS Config role** 섹션에서 `Create AWS Config service-linked role`을 선택합니다.
7. [[Next]] 버튼을 클릭합니다.
8. **AWS Config rules** 페이지에서 규칙을 선택하지 않고 [[Next]] 버튼을 클릭합니다 (규칙은 태스크 3에서 개별적으로 생성).
9. 설정을 검토하고 [[Confirm]] 버튼을 클릭합니다.

> [!NOTE]
> AWS Config 활성화 후 초기 스냅샷 생성에 수 분이 소요되며, Amazon SNS 토픽도 이 시점에 생성됩니다.

### 태스크 1.4: Amazon SNS 이메일 구독 확인

AWS Config 설정을 완료한 후 Amazon SNS 이메일 구독을 확인합니다.

10. Amazon SNS 콘솔로 이동합니다.
11. 왼쪽 메뉴에서 **Subscriptions**를 선택합니다.
12. AWS Config가 생성한 구독을 찾습니다 (Status: "Pending confirmation").
13. 이메일 받은편지함을 확인합니다.
14. "AWS Notification - Subscription Confirmation" 제목의 이메일을 엽니다.
15. 이메일 본문의 **Confirm subscription** 링크를 클릭합니다.
16. 브라우저에서 "Subscription confirmed!" 메시지를 확인합니다.
17. Amazon SNS 콘솔로 돌아가 페이지를 새로고침합니다.
18. 구독 상태가 "Confirmed"로 변경되었는지 확인합니다.

이메일 구독을 확인하지 않으면 태스크 6에서 규정 위반 알림을 받을 수 없으므로, 반드시 이메일 받은편지함을 확인하고 구독을 승인합니다.

✅ **태스크 완료**: AWS Config가 활성화되었습니다.

## 태스크 2: 리소스 인벤토리 확인

### 태스크 2.1: 리소스 타입 탐색

19. AWS Config 콘솔에서 **Resources** 메뉴를 선택합니다.
20. **Resource type** 필터에서 다양한 리소스 타입을 확인합니다.
21. 특정 리소스 타입을 선택합니다 (예: `AWS::Amazon S3::Bucket`).
22. 리소스 목록이 표시됩니다.

### 태스크 2.2: 리소스 상세 정보 및 변경 이력 확인

23. 특정 리소스를 클릭하여 상세 정보를 확인합니다.
24. **Resource timeline** 탭에서 변경 이력을 확인합니다 (리소스의 생성 시점, 설정 변경 이력, 변경한 사용자 추적).
25. **Configuration** 탭에서 현재 설정을 확인합니다.
26. **Relationships** 탭에서 관련 리소스를 확인합니다.
27. **Compliance** 탭에서 규정 준수 상태를 확인합니다.

✅ **태스크 완료**: 리소스 인벤토리를 확인했습니다.

## 태스크 3: AWS Config Rules 생성

> [!CONCEPT] AWS Config Rules 개념
> AWS Config Rules를 생성하여 리소스가 조직의 보안 및 규정 준수 정책을 따르는지 자동으로 평가합니다.
>
> **주요 기능**:
>
> - AWS 관리형 규칙 200개 이상 제공
> - 리소스 설정 변경 시 자동 평가
> - 규정 위반 리소스 즉시 식별
> - AWS Lambda 함수로 커스텀 규칙 생성 가능
>
> **평가 대상**:
>
> - Amazon S3 버킷 퍼블릭 액세스 차단
> - 암호화 활성화 여부
> - Amazon EC2 인스턴스 AWS Systems Manager 관리
> - AWS IAM 비밀번호 정책
> - 보안 그룹 포트 설정

### 태스크 3.1: Amazon S3 퍼블릭 읽기 금지 규칙 생성

28. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
29. [[Add rule]] 버튼을 클릭합니다.
30. **Select rule type**에서 `Add AWS managed rule`을 선택합니다.
31. 검색창에 `s3-bucket-public-read-prohibited`를 입력합니다.
32. 해당 규칙을 선택하고 [[Next]] 버튼을 클릭합니다.
33. **Name**은 기본값을 유지합니다.
34. **Trigger** 섹션에서:
	- **Trigger type**: `Configuration changes`
	- **Resources**: `AWS::Amazon S3::Bucket`

AWS Config는 선택한 규칙에 따라 적절한 Trigger type을 자동으로 설정합니다. `Configuration changes`는 리소스 설정이 변경될 때마다 평가하며, `Periodic`은 주기적으로 평가합니다 (예: 24시간마다). 대부분의 관리형 규칙은 Configuration changes를 사용합니다.

35. **Parameters** 섹션은 기본값을 유지합니다 (파라미터 없음).
36. [[Next]] 버튼을 클릭합니다.
37. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-2`    |
| `CreatedBy` | `Student` |

38. 설정을 검토하고 [[Add rule]] 버튼을 클릭합니다.

이 규칙은 Amazon S3 버킷이 퍼블릭 읽기 액세스를 허용하는지 확인합니다. 퍼블릭 액세스가 허용된 버킷은 "Noncompliant"로 표시됩니다.

### 태스크 3.2: 추가 보안 규칙 생성

다음 4개 규칙을 동일한 방법으로 생성하며, 각 규칙마다 위와 동일한 태그 3개(`Project=AWS-Lab`, `Week=12-2`, `CreatedBy=Student`)를 추가합니다.

39. `s3-bucket-server-side-encryption-enabled` 규칙을 생성합니다:
    - [[Add rule]] 버튼 클릭
    - 규칙 검색 및 선택
    - **Parameters**: 기본값 유지 (파라미터 없음 - 모든 암호화 방식 허용)
    - **Tags**: 위와 동일한 태그 3개 추가
    - [[Add rule]] 클릭

40. `ec2-instance-managed-by-systems-manager` 규칙을 생성합니다:
    - [[Add rule]] 버튼 클릭
    - 규칙 검색 및 선택
    - **Parameters**: 기본값 유지 (파라미터 없음)
    - **Tags**: 위와 동일한 태그 3개 추가
    - [[Add rule]] 클릭

> [!NOTE]
> 실습 환경에 Amazon EC2 인스턴스가 없는 경우 이 규칙은 "Not applicable" 또는 "Insufficient data"로 표시될 수 있으며, 이는 정상입니다. 이 규칙은 Amazon EC2 인스턴스가 AWS Systems Manager에 의해 관리되는지 확인하는 규칙으로, 평가 대상 리소스가 없으면 해당 상태로 표시됩니다.

41. `iam-password-policy` 규칙을 생성합니다:
    - [[Add rule]] 버튼 클릭
    - 규칙 검색 및 선택
    - **Parameters** 섹션에서 다음을 입력:
        - **RequireUppercaseCharacters**: `"true"` (문자열 형식)
        - **RequireLowercaseCharacters**: `"true"` (문자열 형식)
        - **MinimumPasswordLength**: `"8"` (문자열 형식)
        - 나머지 파라미터는 기본값 유지
    - **Tags**: 위와 동일한 태그 3개 추가
    - [[Add rule]] 클릭

이 규칙의 파라미터 값은 반드시 문자열 형식(`"true"`, `"8"`)으로 입력해야 합니다. Boolean 값(`true`)이나 숫자 값(`8`)을 직접 입력하면 규칙 평가 시 오류가 발생할 수 있습니다.

42. `vpc-sg-open-only-to-authorized-ports` 규칙을 생성합니다:
    - [[Add rule]] 버튼 클릭
    - 규칙 검색 및 선택
    - **Parameters** 섹션에서:
        - **authorizedTcpPorts**: `443,80` 입력
    - **Tags**: 위와 동일한 태그 3개 추가
    - [[Add rule]] 클릭

> [!NOTE]
> **AWS Config Rules 유형 및 평가 결과**:
>
> **규칙 유형**:
>
> - **AWS Managed Rules**: AWS가 제공하는 200개 이상의 사전 정의 규칙
> - **Custom Rules**: AWS Lambda 함수로 구현하는 조직 특화 규칙
> - **Trigger Type**: Configuration changes (변경 시) 또는 Periodic (주기적 평가)
>
> **평가 결과**:
>
> - **Compliant**: 규정 준수
> - **Noncompliant**: 규정 위반
> - **Not applicable**: 해당 없음
> - **Insufficient data**: 데이터 부족

✅ **태스크 완료**: AWS Config Rules가 생성되었습니다.

## 태스크 4: 테스트 버킷 생성

이 태스크에서는 규정 위반을 테스트하기 위한 Amazon S3 버킷을 생성합니다. 이 버킷은 퍼블릭 액세스를 허용하도록 설정하여 AWS Config Rules가 위반을 감지하도록 합니다.

43. Amazon S3 콘솔로 이동합니다.
44. [[Create bucket]] 버튼을 클릭합니다.
45. **Bucket name**에 `config-test-bucket-{계정ID}`를 입력합니다.

> [!NOTE]
> `{계정ID}` 부분은 본인의 AWS 계정 ID로 대체합니다. 예: `config-test-bucket-123456789012`

46. **Region**에서 `Asia Pacific (Seoul) ap-northeast-2`를 선택합니다.
47. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-2`    |
| `CreatedBy` | `Student` |

48. [[Create bucket]] 버튼을 클릭합니다.
49. 생성한 버킷을 선택합니다.
50. **Permissions** 탭을 선택합니다.
51. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
52. **Block all public access**를 체크 해제합니다.
53. [[Save changes]] 버튼을 클릭합니다.
54. 확인 창에서 `confirm`을 입력하고 [[Confirm]] 버튼을 클릭합니다.

퍼블릭 액세스를 허용하면 AWS Config가 규정 위반을 감지합니다. 이는 계정 수준 설정이 아닌 버킷 수준 설정이므로, 다른 버킷에는 영향을 주지 않습니다.

> [!NOTE]
> AWS Config가 새 버킷을 감지하고 규칙을 평가하는 데 수 분이 소요됩니다. 잠시 기다린 후 태스크 5를 진행합니다.

✅ **태스크 완료**: 테스트 버킷이 생성되었습니다.

## 태스크 5: 규정 준수 평가 확인 및 위반 리소스 수정

이 태스크에서는 생성한 AWS Config Rules의 평가 결과를 확인하고 규정을 위반한 리소스를 식별합니다. 각 규칙의 준수 상태(Compliant, Noncompliant, Not applicable, Insufficient data)를 검토하고, 위반 리소스의 상세 정보와 위반 시점을 파악합니다. Compliance timeline을 통해 리소스가 언제부터 규정을 위반했는지 추적하고, Configuration 탭에서 현재 설정을 확인하여 어떤 부분이 정책을 위반하는지 분석합니다. 위반 사항을 수정한 후 AWS Config가 자동으로 재평가하여 준수 상태로 변경되는 것을 확인하고, 규정 준수 대시보드에서 전체 준수율과 위반 리소스 통계를 모니터링할 수 있습니다.

### 태스크 5.1: 규정 준수 평가 확인

55. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
56. 생성한 규칙 목록을 확인합니다.
57. 각 규칙의 **Compliance** 상태를 확인합니다.
58. `Noncompliant` 상태인 규칙을 클릭합니다.
59. **Resources in scope** 섹션에서 위반 리소스를 확인합니다.
60. 위반 리소스를 클릭하여 상세 정보를 확인합니다.
61. **Compliance timeline**에서 언제부터 위반되었는지 확인합니다.
62. **Configuration** 탭에서 현재 설정을 확인합니다.

### 태스크 5.2: 위반 리소스 수정

63. `s3-bucket-public-read-prohibited` 규칙을 선택합니다.
64. **Resources in scope** 섹션에서 위반 리소스(버킷 이름)를 확인합니다.

> [!OUTPUT]
>
> ```
> Rule: s3-bucket-public-read-prohibited
> Resource: config-test-bucket-123456789012
> Status: Noncompliant
> Reason: Bucket has public read access
> First detected: [실습 시점 날짜/시간]
> ```

65. 새 브라우저 탭을 열고 Amazon S3 콘솔로 이동합니다.
66. 위반 버킷(`config-test-bucket-{계정ID}`)을 선택합니다.
67. **Permissions** 탭을 선택합니다.
68. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
69. **Block all public access**를 체크합니다.
70. [[Save changes]] 버튼을 클릭합니다.
71. 확인 창에서 `confirm`을 입력합니다.
72. [[Confirm]] 버튼을 클릭합니다.

> [!NOTE]
> 퍼블릭 액세스 차단 설정이 적용되었습니다. 이제 AWS Config가 자동으로 재평가합니다.

73. AWS Config 콘솔 탭으로 이동합니다.
74. `s3-bucket-public-read-prohibited` 규칙 페이지를 새로고침합니다.
75. [[Re-evaluate]] 버튼을 클릭하여 즉시 재평가를 트리거합니다.
76. 페이지를 새로고침하여 준수 상태 변경을 확인합니다.
77. **Resources in scope** 섹션에서 버킷의 **Compliance** 상태가 "Compliant"로 변경되었는지 확인합니다.

규칙 재평가는 수 분이 소요될 수 있습니다. 페이지를 여러 번 새로고침하여 상태 변경을 확인합니다.

> [!OUTPUT]
>
> ```
> Rule: s3-bucket-public-read-prohibited
> Resource: config-test-bucket-123456789012
> Status: Compliant
> Last evaluated: [재평가 시점 날짜/시간]
> ```

> [!NOTE]
> 규정 준수 대시보드

- **Compliance Summary**: 전체 규칙 수, 준수/위반 규칙 수, 준수율
- **Resource Compliance**: 리소스별 준수 상태 및 위반 목록
- **Compliance Timeline**: 시간에 따른 준수 상태 변화 추적

✅ **태스크 완료**: 규정 준수 평가 결과를 확인했습니다.

## 태스크 6: 규정 위반 자동 알림 설정

이 태스크에서는 규정 위반이 감지되면 자동으로 Amazon SNS를 통해 알림을 전송하는 기능을 설정합니다. AWS Systems Manager Automation 문서를 사용하여 위반 감지 시 즉시 보안 팀에 알림을 보내고, 위반 리소스 정보와 위반 사유를 포함한 상세 메시지를 전달할 수 있습니다. Automatic remediation을 활성화하면 위반 감지 즉시 알림이 전송되며, Manual remediation을 선택하면 검토 후 수동으로 트리거할 수 있습니다. 재시도 로직을 설정하여 실패 시 최대 5회까지 자동으로 재시도하고, 실행 로그를 통해 알림 전송의 성공 여부를 추적할 수 있습니다. 이를 통해 규정 준수 위반을 신속하게 감지하고 보안 팀이 즉시 대응할 수 있도록 지원합니다.

> [!NOTE]
> 이 실습에서는 Amazon SNS 알림만 전송하도록 설정합니다. 프로덕션 환경에서는 `AWS-DisableS3BucketPublicReadWrite`, `AWS-EnableS3BucketEncryption` 등의 Automation 문서를 사용하여 실제로 리소스를 자동 수정할 수 있습니다. 자동 수정 기능은 신중하게 테스트한 후 적용해야 하며, 중요한 리소스에는 Manual remediation을 권장합니다.

### 태스크 6.1: Amazon SNS 알림 자동 전송 설정

78. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
79. 규칙을 선택합니다 (예: `s3-bucket-public-read-prohibited`).
80. **Actions** 드롭다운에서 `Manage remediation`을 선택합니다.
81. **Remediation action** 섹션에서:
	- **Select remediation method**: `Automatic remediation`
	- **Remediation action details**: `AWS-PublishSNSNotification` 선택
82. **Resource ID parameter** 드롭다운에서 아무것도 선택하지 않거나, 기본값을 유지합니다.

> [!WARNING]
> **Resource ID parameter**에 `TopicArn`을 매핑하면 Amazon SNS 토픽 ARN 대신 위반 리소스 ID가 들어가게 되어 실행이 실패합니다. Resource ID parameter는 사용하지 않고, Parameters 섹션에서 TopicArn을 직접 입력해야 합니다.

83. **Parameters** 섹션에서:
	- **TopicArn**: Amazon SNS 토픽 ARN 입력 (태스크 1에서 생성한 토픽)
	- **Message**: `Amazon S3 bucket public access compliance violation detected`

> [!IMPORTANT]
> **AWS IAM 역할 설정**:
>
> AWS-PublishSNSNotification SSM Automation 문서를 실행하려면 AWS Config Remediation이 Amazon SNS Publish 권한을 가진 AWS IAM 역할을 사용해야 합니다.
>
> **Auto remediation AWS IAM role** 섹션에서:
>
> - 기존 역할이 있으면 Amazon SNS Publish 권한이 포함된 역할을 선택합니다
> - 또는 [[Create a role]] 버튼을 클릭하여 새 역할을 생성합니다
>
> **필요한 최소 권한**:
>
> ```json
> {
>   "Effect": "Allow",
>   "Action": "sns:Publish",
>   "Resource": "arn:aws:sns:ap-northeast-2:{계정ID}:config-topic-*"
> }
> ```
>
> 역할 없이 저장하면 Remediation 실행 시 AccessDenied 오류가 발생합니다.

84. **Auto remediation**을 활성화합니다.
85. **Retry attempts**: `5`를 입력합니다.
86. [[Save changes]] 버튼을 클릭합니다.

> [!NOTE]
> **AWS-PublishSNSNotification 제약사항**:
>
> - 이 SSM Automation 문서는 고정된 메시지만 전송합니다.
> - 동적 플레이스홀더(`{ResourceId}` 등)는 지원하지 않습니다.
> - 위반 리소스 정보를 포함한 동적 메시지가 필요한 경우, 커스텀 AWS Lambda 함수를 사용해야 합니다.

### 태스크 6.2: 자동 알림 테스트

87. Amazon S3 콘솔로 이동합니다.
88. `config-test-bucket-{계정ID}` 버킷을 선택합니다.
89. **Permissions** 탭을 선택합니다.
90. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
91. **Block all public access**를 체크 해제합니다.
92. [[Save changes]] 버튼을 클릭합니다.
93. 확인 창에서 `confirm`을 입력하고 [[Confirm]] 버튼을 클릭합니다.

> [!NOTE]
> 테스트를 위해 퍼블릭 액세스를 다시 허용합니다. AWS Config가 위반을 감지하면 자동으로 Remediation이 트리거됩니다.

94. AWS Config 콘솔로 이동합니다.
95. **Rules** 메뉴에서 `s3-bucket-public-read-prohibited` 규칙을 선택합니다.
96. 페이지를 새로고침하여 위반 리소스를 확인합니다.
97. **Resources in scope**에서 위반 리소스(`config-test-bucket-{계정ID}`)를 확인합니다.
98. Amazon SNS 이메일 알림이 수신되었는지 확인합니다.

> [!NOTE]
> 퍼블릭 액세스를 다시 해제한 후 AWS Config가 변경을 감지 → 규칙 재평가 → Noncompliant 판정 → Remediation 트리거 → Amazon SNS 알림 전송까지의 전체 흐름에 5-10분이 소요될 수 있습니다. 페이지를 여러 번 새로고침하여 상태 변경을 확인합니다.

99. Amazon S3 콘솔로 이동합니다.
100. `config-test-bucket-{계정ID}` 버킷을 선택합니다.
101. **Permissions** 탭을 선택합니다.
102. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
103. **Block all public access**를 체크합니다.
104. [[Save changes]] 버튼을 클릭합니다.
105. 확인 창에서 `confirm`을 입력하고 [[Confirm]] 버튼을 클릭합니다.

테스트 후 퍼블릭 액세스를 다시 차단하여 보안을 유지합니다.

> [!NOTE]
> **Automatic Remediation**: 위반 감지 즉시 SSM Automation 문서를 실행하여 자동 알림을 전송합니다. 실패 시 최대 5회 재시도합니다.
>
> **Manual Remediation**: 검토 후 수동으로 트리거하여 민감한 작업에 적합합니다.

✅ **태스크 완료**: 자동 알림이 설정되었습니다.

## 태스크 7: Conformance Pack 배포

이 태스크에서는 여러 AWS Config Rules를 묶어서 한 번에 배포하는 Conformance Pack을 사용합니다. Conformance Pack은 YAML 형식의 템플릿으로 여러 규칙을 패키지화하여 일관된 규정 준수 정책을 적용할 수 있습니다. AWS가 제공하는 Operational Best Practices 템플릿(Amazon S3, Security, PCI-DSS, HIPAA, CIS Benchmarks 등)을 사용하거나 커스텀 템플릿을 생성할 수 있습니다. AWS Organizations와 통합하여 조직의 모든 계정에 Conformance Pack을 일괄 배포하고, 중앙에서 규정 준수 상태를 모니터링할 수 있습니다. 배포 후 포함된 모든 규칙의 준수 상태를 한눈에 확인하고, 전체 준수율을 추적하여 보안 및 규정 준수 수준을 지속적으로 개선할 수 있습니다.

> [!NOTE]
> Conformance Pack에 포함된 규칙 중 일부는 이미 태스크 3에서 개별적으로 생성한 규칙과 중복될 수 있습니다. 이는 정상적인 동작이며, Conformance Pack은 여러 규칙을 패키지로 관리하기 위한 것입니다. 중복된 규칙은 동일한 리소스를 평가하지만, 각각 독립적으로 관리됩니다.

106. AWS Config 콘솔에서 **Conformance packs** 메뉴를 선택합니다.
107. [[Deploy conformance pack]] 버튼을 클릭합니다.
108. **Select template**에서 샘플 템플릿을 선택합니다:
	- `Operational Best Practices for Amazon S3`
	- 또는 `Operational Best Practices for Security`
109. **Conformance pack name**에 `demo-s3-best-practices`를 입력합니다.
110. **Parameters** 섹션에서 필요한 파라미터를 입력합니다 (선택사항).
111. [[Deploy conformance pack]] 버튼을 클릭합니다.
112. 배포 상태를 확인합니다 (수 분 소요).
113. 배포 완료 후 **Conformance pack details**를 확인합니다.
114. **Rules** 탭에서 포함된 규칙 목록을 확인합니다.
115. **Compliance** 탭에서 전체 준수 상태를 확인합니다.

> [!NOTE]
> Conformance Pack 활용

- **템플릿 기반**: YAML 형식으로 여러 AWS Config Rules를 패키지화
- **AWS 제공 템플릿**: Operational Best Practices, PCI-DSS, HIPAA, CIS Benchmarks 등
- **조직 전체 배포**: AWS Organizations와 통합하여 모든 계정에 일괄 적용 가능

✅ **태스크 완료**: Conformance Pack이 배포되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Config를 활성화하고 리소스 추적을 시작했습니다
- 리소스 인벤토리와 변경 이력을 확인했습니다
- AWS Config Rules를 생성하여 규정 준수를 자동 평가했습니다
- 위반 리소스를 식별하고 수정했습니다
- 규정 위반 시 자동 알림 기능을 설정했습니다
- Conformance Pack으로 여러 규칙을 일괄 배포했습니다

### 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

#### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `12-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 태그를 추가한 리소스(테스트 버킷, AWS Config Rules 5개)가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.
>
> AWS Config가 자동 생성한 Amazon S3 버킷, Amazon SNS 토픽, Conformance Pack 등은 태그를 추가하지 않았으므로 Tag Editor에 표시되지 않습니다. 이러한 리소스는 각 서비스 콘솔에서 직접 삭제해야 합니다.

#### 방법 2: 수동 삭제

##### Conformance Pack 삭제

8. AWS Config 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Conformance packs**를 선택합니다.
10. `demo-s3-best-practices` Conformance Pack을 선택합니다.
11. [[Delete]] 버튼을 클릭합니다.
12. 확인 창에서 `delete`를 입력합니다.
13. [[Delete]] 버튼을 클릭합니다.

##### AWS Config Rules 삭제

> [!IMPORTANT]
> Remediation 설정이 활성화된 상태에서 AWS Config Rule을 삭제하면 오류가 발생할 수 있습니다. 반드시 Remediation을 먼저 제거한 후 Rule을 삭제해야 합니다.

14. AWS Config 콘솔로 이동합니다.
15. 왼쪽 메뉴에서 **Rules**를 선택합니다.
16. Remediation이 설정된 규칙(`s3-bucket-public-read-prohibited`)을 선택합니다.
17. **Actions** 드롭다운에서 `Manage remediation`을 선택합니다.
18. [[Delete]] 버튼을 클릭하여 Remediation 설정을 제거합니다.
19. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

20. 생성한 규칙을 하나씩 선택합니다.
21. [[Delete rule]] 버튼을 클릭합니다.
22. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
23. 모든 규칙에 대해 반복합니다:
    - `s3-bucket-public-read-prohibited`
    - `s3-bucket-server-side-encryption-enabled`
    - `ec2-instance-managed-by-systems-manager`
    - `iam-password-policy`
    - `vpc-sg-open-only-to-authorized-ports`

##### Configuration Recorder 중지 및 삭제

24. 왼쪽 메뉴에서 **Settings**를 선택합니다.
25. **Recorder** 섹션에서 [[Edit]] 버튼을 클릭합니다.
26. **Recording is on** 토글을 끕니다.
27. [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Configuration Recorder를 중지하면 리소스 변경 추적이 중단되지만, 기존 데이터는 Amazon S3에 유지됩니다.

28. AWS Management Console 상단 오른쪽의 CloudShell 아이콘을 클릭합니다.
29. CloudShell이 열리면 다음 명령어를 실행하여 Configuration Recorder를 삭제합니다:

```bash
aws configservice delete-configuration-recorder --configuration-recorder-name default
```

> [!TIP]
> AWS CloudShell을 사용하면 브라우저에서 바로 AWS CLI 명령어를 실행할 수 있습니다. AWS CLI 설치나 자격 증명 설정이 필요 없으며, 사전 구성된 환경에서 즉시 명령어를 실행할 수 있습니다.

> [!NOTE]
> Configuration Recorder를 삭제해야 Delivery Channel 삭제가 가능합니다.

30. 다음 명령어를 실행하여 Delivery Channel을 삭제합니다:

```bash
aws configservice delete-delivery-channel --delivery-channel-name default
```

> [!NOTE]
> Delivery Channel은 AWS 콘솔에서 직접 삭제할 수 없으므로 AWS CLI를 사용합니다.

### 테스트 버킷 삭제

31. Amazon S3 콘솔로 이동합니다.
32. `config-test-bucket-{계정ID}` 버킷을 선택합니다.
33. [[Empty]] 버튼을 클릭합니다.
34. 확인 창에서 `permanently delete`를 입력합니다.
35. [[Empty]] 버튼을 클릭합니다.
36. 버킷을 다시 선택합니다.
37. [[Delete]] 버튼을 클릭합니다.
38. 확인 창에서 버킷 이름을 입력합니다.
39. [[Delete bucket]] 버튼을 클릭합니다.

### Amazon S3 버킷 삭제 (AWS Config 데이터)

40. AWS Config가 생성한 버킷을 찾습니다 (이름: `config-bucket-{계정ID}`).
41. 버킷을 선택합니다.
42. [[Empty]] 버튼을 클릭합니다.
43. 확인 창에서 `permanently delete`를 입력합니다.
44. [[Empty]] 버튼을 클릭합니다.
45. 버킷을 다시 선택합니다.
46. [[Delete]] 버튼을 클릭합니다.
47. 확인 창에서 버킷 이름을 입력합니다.
48. [[Delete bucket]] 버튼을 클릭합니다.

### Amazon SNS 토픽 및 구독 삭제

49. Amazon SNS 콘솔로 이동합니다.
50. 왼쪽 메뉴에서 **Topics**를 선택합니다.
51. AWS Config가 생성한 토픽을 선택합니다 (이름: `config-topic-{계정ID}`).
52. [[Delete]] 버튼을 클릭합니다.
53. 확인 창에서 `delete me`를 입력합니다.
54. [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon SNS 토픽을 삭제하면 연결된 모든 구독도 자동으로 삭제됩니다.

### Remediation AWS IAM 역할 삭제 (태스크 6.1에서 새 역할을 생성한 경우)

> [!NOTE]
> 태스크 6.1에서 기존 AWS IAM 역할을 선택한 경우 이 단계를 건너뜁니다. 새 역할을 생성한 경우에만 삭제가 필요합니다.

55. AWS IAM 콘솔로 이동합니다.
56. 왼쪽 메뉴에서 **Roles**를 선택합니다.
57. 태스크 6.1에서 생성한 Remediation 역할을 선택합니다.
58. [[Delete]] 버튼을 클릭합니다.
59. 확인 창에서 역할 이름을 입력합니다.
60. [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 태스크 6.1에서 [[Create a role]] 버튼으로 생성한 경우, 역할 이름은 생성 시 직접 지정했거나 자동 생성된 이름입니다. AWS IAM 콘솔에서 생성 날짜를 기준으로 해당 역할을 찾을 수 있습니다.

### Amazon CloudWatch Log Group 삭제 (선택사항)

> [!NOTE]
> AWS Config는 기본적으로 Amazon CloudWatch Logs에 로그를 전송하지 않습니다. 이 단계는 Delivery Channel 설정 시 Amazon CloudWatch Logs를 활성화한 경우에만 필요합니다. 로그 그룹이 존재하지 않으면 이 단계를 건너뜁니다.

61. Amazon CloudWatch 콘솔로 이동합니다.
62. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
63. `/aws/config/` 접두사로 시작하는 로그 그룹이 있는지 확인합니다.
64. 로그 그룹이 존재하는 경우, 해당 로그 그룹을 선택합니다.
65. **Actions** > `Delete log group(s)`를 선택합니다.
66. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS Config 개발자 가이드](https://docs.aws.amazon.com/ko_kr/config/latest/developerguide/WhatIsConfig.html)
- [AWS Config Rules 레퍼런스](https://docs.aws.amazon.com/ko_kr/config/latest/developerguide/managed-rules-by-aws-config.html)
- [Conformance Packs](https://docs.aws.amazon.com/ko_kr/config/latest/developerguide/conformance-packs.html)
- [AWS Config 모범 사례](https://docs.aws.amazon.com/ko_kr/config/latest/developerguide/best-practices.html)

## 📚 참고: AWS Config 핵심 개념

### Configuration Item (CI)

- 리소스의 특정 시점 스냅샷 (JSON 형식)
- 메타데이터, 관계, 설정 포함
- 변경 이력 추적의 기본 단위
- Configuration Snapshot은 Delivery Channel 설정에 따라 주기적으로 Amazon S3에 전달

> [!NOTE]
> **Configuration Snapshot 생성 방식**:
>
> - AWS Config는 리소스 변경 시 즉시 Configuration Item을 생성합니다.
> - Configuration Snapshot(전체 리소스 스냅샷)은 Delivery Channel의 Frequency 설정에 따라 자동으로 Amazon S3에 전달됩니다.
> - 태스크 1.2에서 Delivery Channel을 설정했으므로, 설정한 주기(1시간/3시간/6시간/12시간/24시간)에 따라 자동 스냅샷이 생성됩니다.
> - 수동으로 스냅샷을 트리거할 수도 있습니다.

### AWS Config Rules

**Evaluation Mode**

- Proactive: 리소스 생성 전 평가 (AWS CloudFormation)
- Amazon Detective: 리소스 생성 후 평가 (기본)

**Trigger Type**

- Configuration changes: 변경 시 평가
- Periodic: 주기적 평가

**Compliance Status**

- Compliant: 규정 준수
- Noncompliant: 규정 위반
- Not applicable: 해당 없음
- Insufficient data: 데이터 부족

### Remediation

**Automatic Remediation**

- 위반 감지 즉시 실행
- SSM Automation 문서 사용
- 실패 시 최대 5회 재시도

**Manual Remediation**

- 수동으로 트리거
- 검토 후 실행
- 민감한 작업에 적합

### 규정 준수 프레임워크

**PCI-DSS**: 결제 카드 산업 데이터 보안 표준  
**HIPAA**: 의료 정보 보호법  
**CIS Benchmarks**: 보안 설정 모범 사례  
**GDPR**: 유럽 개인정보 보호 규정
