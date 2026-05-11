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

이 실습에서는 AWS Config를 활성화하여 AWS 리소스의 구성 변경을 추적하고, 관리형 규칙을 생성하여 규정 준수를 자동으로 평가합니다. 규정 위반 리소스를 식별하고 수정하는 과정을 실습하며, 자동 알림 설정과 Conformance Pack 배포를 통해 조직 수준의 규정 준수 관리 방법을 학습합니다.

> [!CONCEPT] AWS Config란?
>
> AWS Config는 AWS 리소스의 구성을 **지속적으로 기록하고 평가**하는 서비스입니다.
>
> - **구성 기록**: 리소스의 설정 변경 이력을 자동으로 추적합니다.
> - **규칙 평가**: 관리형 규칙으로 리소스가 보안 정책을 준수하는지 자동 평가합니다.
> - **규정 준수 대시보드**: 전체 리소스의 준수/위반 상태를 한눈에 확인합니다.
> - **자동 수정**: 위반 감지 시 SSM Automation으로 자동 알림 또는 수정을 수행합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 1: AWS Config 설정

### 태스크 1.0: Amazon SNS 토픽 사전 생성

> [!NOTE]
> AWS Config 설정 시 SNS 토픽을 동시에 생성하면 IAM 역할 생성 순서 문제로 에러가 발생할 수 있습니다.
> 이를 방지하기 위해 SNS 토픽을 먼저 생성한 후 Config 설정에서 선택합니다.

1. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
2. 상단 검색창에 `SNS`를 입력하고 **Simple Notification Service**를 선택합니다.
3. 왼쪽 메뉴에서 **Topics**를 선택합니다.
4. [[Create topic]] 버튼을 클릭합니다.
   <img src="/images/week12/12-2-task1-step4-create-topic.png" alt="Create topic 버튼 클릭" class="guide-img-md" />

5. **Type**에서 `Standard`를 선택합니다.
6. **Name**에 `config-topic`을 입력합니다.
7. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-2`    |
| `CreatedBy` | `Student` |

8. [[Create topic]] 버튼을 클릭합니다.
   <img src="/images/week12/12-2-task1-step8-create-topic-done.png" alt="Create topic 완료" class="guide-img-md" />

### 태스크 1.1: AWS Config 활성화 및 기본 설정

9. 상단 검색창에 `Config`을 입력하고 선택합니다.
10. 처음 사용하는 경우 [[Get started]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step10-get-started.png" alt="Config Get started 버튼 클릭" class="guide-img-md" />

11. **Step 1: Settings** 페이지에서 **Recording method** 섹션을 확인합니다.
12. **Recording strategy**에서 `Specific resource types`를 선택합니다.

> [!NOTE]
> `All resource types with customizable overrides`는 수백 개 이상의 모든 AWS 리소스를 추적하여 비용이 많이 발생합니다. 실습에서는 `Specific resource types`를 선택하여 필요한 리소스만 추적합니다.

13. **Resource types to record** 섹션에서 다음 리소스 타입을 검색하여 추가하고, 각각 **Frequency**를 `Continuous`로 선택합니다:
    - `AWS S3 Bucket`
    - `AWS EC2 Instance`
    - `AWS EC2 SecurityGroup`
    - `AWS IAM User`
    - `AWS IAM Role`
    - `AWS Config ResourceCompliance`

    <img src="/images/week12/12-2-task1-step13-resource-types.png" alt="Resource types 설정" class="guide-img-md" />

> [!NOTE]
> `AWS Config ResourceCompliance`는 리소스의 규정 준수 상태 변화를 기록하는 리소스 타입입니다.
> 이 타입을 추가하지 않으면 리소스 Timeline에서 Compliance 이벤트가 기록되지 않아 "Stopped recording changes to compliance events" 메시지가 표시됩니다.

> [!NOTE]
> **Continuous**는 리소스 설정이 변경될 때마다 즉시 기록합니다. **Daily**는 하루에 한 번만 기록하므로 비용은 절감되지만 변경 감지가 지연됩니다.

### 태스크 1.2: IAM 역할 및 Delivery 설정

14. **Data governance** 섹션에서 **IAM role for AWS Config**를 확인합니다.
15. `Create AWS Config service-linked role`을 선택합니다.

> [!TIP]
> 이 실습을 다시 진행하거나 이전 시도에서 IAM 역할이 남아있는 경우, `Use an existing AWS Config service-linked role`이 표시됩니다. 그대로 선택하면 됩니다.

16. **Delivery channel** 섹션에서:
    - **Amazon S3 bucket**: `Create a bucket` 선택 (버킷 이름은 기본값 사용 또는 원하는 이름으로 변경, 예: `config-bucket-{StudentId}`)
    - **Amazon SNS topic**: `Stream configuration changes and notifications to an Amazon SNS topic` 체크
    - `Choose a topic from your account` 선택 → 태스크 1.0에서 생성한 `config-topic` 선택

> [!TIP]
> 이전 시도에서 S3 버킷이 남아있는 경우, `Choose a bucket from your account`를 선택하고 기존 버킷을 사용합니다.

17. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step17-next.png" alt="Delivery channel 설정 후 Next" class="guide-img-md" />

### 태스크 1.3: Rules 설정 및 활성화

18. **Step 2: Rules** 페이지에서 규칙을 선택하지 않고 [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step18-rules-next.png" alt="Rules 페이지 Next" class="guide-img-sm" />

> [!NOTE]
> 규칙은 태스크 3에서 개별적으로 생성합니다. 여기서 규칙을 선택하면 불필요한 규칙이 추가될 수 있습니다.

19. **Step 3: Review** 페이지에서 설정을 검토합니다.
20. [[Confirm]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step20-confirm.png" alt="Review 후 Confirm 클릭" class="guide-img-md" />

> [!TROUBLESHOOTING]
> Confirm 시 에러가 발생하면 IAM 역할이나 S3 버킷이 부분적으로 생성된 상태일 수 있습니다.
> 이 경우 페이지를 새로고침한 후 처음부터 다시 설정합니다.
> 이미 생성된 리소스는 위 TIP을 참고하여 기존 것을 선택합니다.

> [!NOTE]
> AWS Config 활성화 후 초기 스냅샷 생성에 수 분이 소요됩니다.

### 태스크 1.4: Amazon SNS 이메일 구독 생성

AWS Config 설정에서 생성한 Amazon SNS 토픽에 이메일 구독을 추가합니다. 태스크 6에서 규정 위반 알림을 수신하려면 이 단계가 필요합니다.

21. 상단 검색창에 `SNS`를 입력하고 **Simple Notification Service**를 선택합니다.
22. 왼쪽 메뉴에서 **Topics**를 선택합니다.
23. 태스크 1.0에서 생성한 `config-topic` 토픽을 선택합니다.
24. [[Create subscription]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step24-create-subscription.png" alt="Create subscription 버튼 클릭" class="guide-img-md" />

25. **Protocol**에서 `Email`을 선택합니다.
26. **Endpoint**에 알림을 수신할 이메일 주소를 입력합니다.
27. [[Create subscription]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task1-step27-subscription-created.png" alt="Subscription 생성 완료" class="guide-img-md" />

    <img src="/images/week12/12-2-task1-step27-subscription-email.png" alt="구독 확인 이메일" class="guide-img-md" />

28. 이메일 받은편지함을 확인합니다.
29. "AWS Notification - Subscription Confirmation" 제목의 이메일을 엽니다.
30. 이메일 본문의 **Confirm subscription** 링크를 클릭합니다.

    <img src="/images/week12/12-2-task1-step30-confirm-link.png" alt="Confirm subscription 링크 클릭" class="guide-img-sm" />

> [!TIP]
> 확인 링크 클릭 시 구독이 자동 취소되는 경우, 링크를 우클릭하여 [시크릿 창에서 링크 열기]를 선택하면 정상적으로 구독이 완료됩니다.

31. 브라우저에서 "Subscription confirmed!" 메시지를 확인합니다.

    <img src="/images/week12/12-2-task1-step31-confirmed.png" alt="Subscription confirmed 메시지" class="guide-img-sm" />

32. Amazon SNS 콘솔로 돌아가 왼쪽 메뉴에서 **Subscriptions**를 선택합니다.
33. 구독 상태가 "Confirmed"로 변경되었는지 확인합니다.

    <img src="/images/week12/12-2-task1-step33-status-confirmed.png" alt="구독 상태 Confirmed 확인" class="guide-img-md" />

> [!IMPORTANT]
> 이메일 구독을 확인하지 않으면 태스크 6에서 규정 위반 알림을 받을 수 없습니다. 반드시 이메일 받은편지함을 확인하고 구독을 승인합니다.

✅ **태스크 완료**: AWS Config가 활성화되었습니다.

## 태스크 2: 리소스 인벤토리 확인

### 태스크 2.1: 리소스 타입 탐색

34. AWS Config 콘솔에서 **Resources** 메뉴를 선택합니다.
35. **Resource type** 필터에서 다양한 리소스 타입을 확인합니다.
36. 특정 리소스 타입을 선택합니다 (예: `AWS S3 Bucket`).

    <img src="/images/week12/12-2-task2-step36-resources.png" alt="Config Resources 리소스 타입 선택" class="guide-img-md" />

37. [[Apply]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task2-step37-resource-type.png" alt="Resource type 필터 결과" class="guide-img-md" />

> [!OUTPUT]
> 선택한 리소스 타입에 해당하는 리소스 목록이 표시됩니다.

### 태스크 2.2: 리소스 상세 정보 및 변경 이력 확인

38. 특정 리소스를 클릭하여 상세 정보를 확인합니다.

    <img src="/images/week12/12-2-task2-step38-select-resource.png" alt="S3 Bucket 리소스 선택" class="guide-img-md" />

39. **Resource timeline** 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task2-step39-apply.png" alt="Resource timeline 버튼 클릭" class="guide-img-md" />

    <img src="/images/week12/12-2-task2-step39-resource-timeline.png" alt="Resource timeline 변경 이력" class="guide-img-md" />

40. 리소스의 변경 이력을 확인합니다.
41. 리소스 상세 페이지에서 현재 설정(Configuration)을 확인합니다.

42. **View Configuration Item (JSON)** 을 펼쳐 전체 설정을 JSON 형식으로 확인합니다.

43. 하단의 **Rules applied** 탭에서 적용된 규칙과 규정 준수 상태를 확인합니다.

> [!NOTE]
> 현재 AWS Config 콘솔에서는 리소스 상세 페이지 상단에 설정 정보가 표시되고, 하단에 **Rules applied** | **Tags** 탭이 있습니다.  
> Relationships(관련 리소스)는 Resource timeline의 Configuration events에서 확인할 수 있습니다.

✅ **태스크 완료**: 리소스 인벤토리를 확인했습니다.

## 태스크 3: AWS Config Rules 생성

> [!CONCEPT] AWS Config Rules 개념
> AWS Config Rules를 생성하여 리소스가 조직의 보안 및 규정 준수 정책을 따르는지 자동으로 평가합니다.
>
> **주요 기능**:
>
> - AWS 관리형 규칙 수백 개 이상 제공
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

44. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
45. [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task2-step45-rules-applied.png" alt="Rules applied 탭 확인" class="guide-img-md" />

46. **Select rule type**에서 `Add AWS managed rule`을 선택합니다.

47. 검색창에 `s3-bucket-public-read-prohibited`를 입력합니다.

    <img src="/images/week12/12-2-task3-step47-add-rule.png" alt="Add rule 버튼 클릭" class="guide-img-md" />

48. 해당 규칙을 선택하고 [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task3-step48-select-rule-type.png" alt="Add AWS managed rule 선택" class="guide-img-md" />

> [!NOTE]
> **Name**은 기본값을 유지합니다.

49. **Evaluation mode**, **Trigger type**, **Scope of changes**, **Resources** 섹션은 기본값을 유지합니다.

> [!NOTE]
> **Trigger type**의 `When configuration changes`는 리소스 설정이 변경될 때마다 평가하며, `Periodic`은 주기적으로 평가합니다 (예: 24시간마다).
> 대부분의 관리형 규칙은 Configuration changes를 사용합니다.

> [!NOTE]
> **Parameters** 섹션은 기본값을 유지합니다 (파라미터 없음).

50. **Rule tags** 섹션에서 [[Add another row]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-2`    |
| `CreatedBy` | `Student` |

51. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task3-step51-evaluation-mode.png" alt="Evaluation mode 기본값 유지" class="guide-img-md" />

52. 설정을 검토하고 [[Save]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task3-step52-rule-tags.png" alt="Rule tags 추가" class="guide-img-md" />

이 규칙은 Amazon S3 버킷이 퍼블릭 읽기 액세스를 허용하는지 확인합니다. 퍼블릭 액세스가 허용된 버킷은 "Noncompliant"로 표시됩니다.

### 태스크 3.2: 추가 보안 규칙 생성

다음 4개 규칙을 동일한 방법으로 생성하며, 각 규칙마다 위와 동일한 태그 3개(`Project=AWS-Lab`, `Week=12-2`, `CreatedBy=Student`)를 추가합니다.

53. `s3-bucket-server-side-encryption-enabled` 규칙을 동일한 방법으로 생성합니다:
    - [[Add rule]] > `Add AWS managed rule` > 규칙 검색 및 선택 > [[Next]]
    - **Parameters**: 기본값 유지
    - **Rule tags**: 위와 동일한 태그 3개 추가
    - [[Next]] → [[Save]] 클릭
      <img src="/images/week12/12-2-task3-step53-next.png" alt="S3 암호화 규칙 Review and Save" class="guide-img-md" />

54. `ec2-instance-managed-by-systems-manager` 규칙을 동일한 방법으로 생성합니다:
    - [[Add rule]] > `Add AWS managed rule` > 규칙 검색 및 선택 > [[Next]]
    - **Parameters**: 기본값 유지
    - **Rule tags**: 위와 동일한 태그 3개 추가
    - [[Next]] → [[Save]] 클릭
      <img src="/images/week12/12-2-task3-step54-save.png" alt="EC2 Systems Manager 규칙 Save" class="guide-img-md" />

> [!NOTE]
> 실습 환경에 Amazon EC2 인스턴스가 없는 경우 이 규칙은 "Not applicable" 또는 "Insufficient data"로 표시될 수 있으며, 이는 정상입니다.

55. `iam-password-policy` 규칙을 동일한 방법으로 생성합니다:
    - [[Add rule]] > `Add AWS managed rule` > 규칙 검색 및 선택 > [[Next]]
    - **Parameters** 섹션에서 **MinimumPasswordLength**를 `8`로 변경하고 나머지는 기본값 유지
    - **Rule tags**: 위와 동일한 태그 3개 추가
    - [[Next]] → [[Save]] 클릭
      <img src="/images/week12/12-2-task3-step55-encryption-rule.png" alt="IAM Password Policy 규칙 Save" class="guide-img-md" />

> [!NOTE]
> iam-password-policy 규칙의 기본 파라미터:
>
> | Key                        | Value                | 설명                    |
> | -------------------------- | -------------------- | ----------------------- |
> | MaxPasswordAge             | 90                   | 비밀번호 만료 기간 (일) |
> | MinimumPasswordLength      | 8 (기본 14에서 변경) | 최소 비밀번호 길이      |
> | PasswordReusePrevention    | 24                   | 재사용 방지 횟수        |
> | RequireLowercaseCharacters | true                 | 소문자 필수             |
> | RequireNumbers             | true                 | 숫자 필수               |
> | RequireSymbols             | true                 | 특수문자 필수           |
> | RequireUppercaseCharacters | true                 | 대문자 필수             |

56. `vpc-sg-open-only-to-authorized-ports` 규칙을 동일한 방법으로 생성합니다:
    - [[Add rule]] > `Add AWS managed rule` > 규칙 검색 및 선택 > [[Next]]
    - **Parameters** 섹션에서:
      - **authorizedTcpPorts**: `443,80` 입력
      - **authorizedUdpPorts**: 비워둡니다 (optional)
    - **Rule tags**: 위와 동일한 태그 3개 추가
    - [[Next]] → [[Save]] 클릭
      <img src="/images/week12/12-2-task3-step56-ec2-rule.png" alt="VPC Security Group 규칙 Save" class="guide-img-md" />

> [!NOTE]
> **AWS Config Rules 유형 및 평가 결과**:
>
> **규칙 유형**:
>
> - **AWS Managed Rules**: AWS가 제공하는 수백 개 이상의 사전 정의 규칙
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

57. Amazon S3 콘솔로 이동합니다.
58. [[Create bucket]] 버튼을 클릭합니다.
59. **AWS Region**이 `Asia Pacific (Seoul) ap-northeast-2`로 설정되어 있는지 확인합니다.
60. **Bucket name**에 `config-test-bucket-{StudentId}`를 입력합니다.

> [!NOTE]
> `{StudentId}` 부분은 본인의 학번 또는 고유 식별자로 변경합니다. 예: `config-test-bucket-20240001`
> Bucket namespace는 기본값(Global namespace)을 사용합니다.

61. **Block Public Access settings for this bucket** 섹션에서 **Block all public access** 체크를 해제합니다.
62. 체크 해제 시 나타나는 경고 확인란에 체크합니다.

    <img src="/images/week12/12-2-task4-step62-bucket-name.png" alt="S3 버킷 이름 입력" class="guide-img-md" />

> [!WARNING]
> 퍼블릭 액세스를 허용하면 AWS Config가 규정 위반을 감지합니다.
> 이는 버킷 수준 설정이므로 다른 버킷에는 영향을 주지 않습니다.

63. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-2`    |
| `CreatedBy` | `Student` |

64. [[Create bucket]] 버튼을 클릭합니다.
65. 생성한 버킷을 선택합니다.

66. **Permissions** 탭을 선택합니다.
67. **Bucket policy** 섹션에서 [[Edit]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task4-step67-select-bucket.png" alt="생성한 S3 버킷 선택" class="guide-img-md" />

68. 다음 정책을 입력합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadTest",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::config-test-bucket-{StudentId}/*"
    }
  ]
}
```

> [!NOTE]
> `{StudentId}` 부분은 본인의 버킷 이름에 맞게 변경합니다.
> Block public access 해제만으로는 규정 위반으로 감지되지 않습니다. 버킷 정책으로 실제 퍼블릭 읽기를 허용해야 AWS Config가 Noncompliant로 판정합니다.

69. [[Save changes]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task4-step69-bucket-policy-edit.png" alt="Bucket policy Edit 클릭" class="guide-img-md" />

> [!NOTE]
> AWS Config가 새 버킷을 감지하고 규칙을 평가하는 데 수 분이 소요됩니다. 잠시 기다린 후 태스크 5를 진행합니다.

✅ **태스크 완료**: 테스트 버킷이 생성되었습니다.

## 태스크 5: 규정 준수 평가 확인 및 위반 리소스 수정

이 태스크에서는 생성한 AWS Config Rules의 평가 결과를 확인하고 규정을 위반한 리소스를 식별합니다. 각 규칙의 준수 상태(Compliant, Noncompliant, Not applicable, Insufficient data)를 검토하고, 위반 리소스의 상세 정보와 위반 시점을 파악합니다. Compliance timeline을 통해 리소스가 언제부터 규정을 위반했는지 추적하고, Configuration 탭에서 현재 설정을 확인하여 어떤 부분이 정책을 위반하는지 분석합니다. 위반 사항을 수정한 후 AWS Config가 자동으로 재평가하여 준수 상태로 변경되는 것을 확인하고, 규정 준수 대시보드에서 전체 준수율과 위반 리소스 통계를 모니터링할 수 있습니다.

### 태스크 5.1: 규정 준수 평가 확인

70. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
71. 각 규칙의 **Compliance** 상태를 확인합니다.

    <img src="/images/week12/12-2-task4-step71-save-changes.png" alt="Bucket policy Save changes" class="guide-img-md" />

72. `Noncompliant` 상태인 `s3-bucket-public-read-prohibited` 규칙을 클릭합니다.

73. **Resources in scope** 섹션에서 위반 리소스를 확인합니다.

    <img src="/images/week12/12-2-task5-step73-compliance-status.png" alt="Rules Compliance 상태 확인" class="guide-img-md" />

74. 위반 리소스를 클릭하여 상세 정보 페이지로 이동합니다.

    <img src="/images/week12/12-2-task5-step74-noncompliant-rule.png" alt="Noncompliant 규칙 클릭" class="guide-img-md" />

75. 우측 상단의 [[Resource Timeline]] 버튼을 클릭합니다.
76. 리소스의 변경 이력과 규정 준수 상태 변화를 시간순으로 확인합니다.

    <img src="/images/week12/12-2-task5-step76-resource-detail.png" alt="위반 리소스 상세 정보" class="guide-img-md" />

### 태스크 5.2: 위반 리소스 수정

77. `s3-bucket-public-read-prohibited` 규칙을 선택합니다.
78. **Resources in scope** 섹션에서 필터가 `Noncompliant`로 설정되어 있는지 확인하고, 위반 리소스를 확인합니다.

> [!OUTPUT]
>
> ```
> ID: config-test-bucket-{StudentId}
> Type: S3 Bucket
> Compliance: Noncompliant
> Annotation: The S3 bucket policy allows public read access
> ```

79. 새 브라우저 탭을 열고 Amazon S3 콘솔로 이동합니다.
80. 위반 버킷(`config-test-bucket-{StudentId}`)을 선택합니다.

81. **Permissions** 탭을 선택합니다.
82. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task6-step82-select-bucket.png" alt="위반 버킷 선택" class="guide-img-md" />

83. **Block all public access**를 체크합니다.
84. [[Save changes]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task6-step84-edit-block-access.png" alt="Block public access Edit" class="guide-img-md" />

85. 확인 창에서 `confirm`을 입력합니다.
86. [[Confirm]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task6-step86-save-changes.png" alt="Block public access Save changes" class="guide-img-sm" />

    <img src="/images/week12/12-2-task6-step86-confirm.png" alt="Block public access 확인" class="guide-img-md" />

> [!NOTE]
> 퍼블릭 액세스 차단 설정이 적용되었습니다. 이제 AWS Config가 자동으로 재평가합니다.

87. AWS Config 콘솔 탭으로 이동합니다.

88. `s3-bucket-public-read-prohibited` 규칙 페이지를 새로고침합니다.
89. 우측 상단 [[Actions]] 드롭다운에서 **Re-evaluate**를 선택하여 즉시 재평가를 트리거합니다.

    <img src="/images/week12/12-2-task6-step89-compliant.png" alt="Compliant 상태 확인" class="guide-img-md" />

90. 페이지를 새로고침하여 준수 상태 변경을 확인합니다.
91. **Resources in scope** 섹션에서 버킷의 **Compliance** 상태가 "Compliant"로 변경되었는지 확인합니다.

    <img src="/images/week12/12-2-task6-step91-re-evaluate.png" alt="Actions Re-evaluate 선택" class="guide-img-md" />

규칙 재평가는 수 분이 소요될 수 있습니다. 페이지를 여러 번 새로고침하여 상태 변경을 확인합니다.

> [!OUTPUT]
>
> ```
> ID: config-test-bucket-{StudentId}
> Type: S3 Bucket
> Compliance: Compliant
> ```

> [!NOTE]
> AWS Config 콘솔의 **Dashboard** 메뉴에서 전체 규칙의 준수/위반 현황을 한눈에 확인할 수 있습니다.

✅ **태스크 완료**: 규정 준수 평가 결과를 확인했습니다.

## 태스크 6: 규정 위반 자동 알림 설정

이 태스크에서는 규정 위반이 감지되면 자동으로 Amazon SNS를 통해 알림을 전송하는 기능을 설정합니다. AWS Systems Manager Automation 문서를 사용하여 위반 감지 시 즉시 보안 팀에 알림을 보내고, 위반 리소스 정보와 위반 사유를 포함한 상세 메시지를 전달할 수 있습니다. Automatic remediation을 활성화하면 위반 감지 즉시 알림이 전송되며, Manual remediation을 선택하면 검토 후 수동으로 트리거할 수 있습니다. 재시도 로직을 설정하여 실패 시 최대 5회까지 자동으로 재시도하고, 실행 로그를 통해 알림 전송의 성공 여부를 추적할 수 있습니다. 이를 통해 규정 준수 위반을 신속하게 감지하고 보안 팀이 즉시 대응할 수 있도록 지원합니다.

> [!NOTE]
> 이 실습에서는 Amazon SNS 알림만 전송하도록 설정합니다. 프로덕션 환경에서는 `AWS-DisableS3BucketPublicReadWrite`, `AWS-EnableS3BucketEncryption` 등의 Automation 문서를 사용하여 실제로 리소스를 자동 수정할 수 있습니다. 자동 수정 기능은 신중하게 테스트한 후 적용해야 하며, 중요한 리소스에는 Manual remediation을 권장합니다.

### 태스크 6.0: Remediation용 IAM 역할 생성

AWS Config Remediation이 SNS 알림을 전송하려면 SSM Automation이 사용할 IAM 역할이 필요합니다.

92. 상단 검색창에 `IAM`을 입력하고 선택합니다.

93. 왼쪽 메뉴에서 **Roles**를 선택합니다.
94. [[Create role]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task7-step94-iam-roles.png" alt="IAM Roles 페이지" class="guide-img-md" />

95. **Trusted entity type**에서 `AWS service`를 선택합니다.

96. **Use case**에서 `Systems Manager`를 선택합니다.
97. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task7-step97-trusted-entity.png" alt="Trusted entity type 선택" class="guide-img-md" />

98. **Permissions policies** 검색창에 `AmazonSNSFullAccess`를 입력하고 체크합니다.
99. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-task7-step99-next.png" alt="Use case 선택 후 Next" class="guide-img-md" />

100.  **Role name**에 `config-remediation-sns-role`을 입력합니다.
101.  [[Create role]] 버튼을 클릭합니다.
      <img src="/images/week12/12-2-task7-step101-permissions.png" alt="Permissions policies 선택 후 Next" class="guide-img-md" />

102.  생성된 역할을 클릭하여 **ARN**을 복사합니다 (형식: `arn:aws:iam::{계정ID}:role/config-remediation-sns-role`).

> [!NOTE]
> 이 실습에서는 편의상 `AmazonSNSFullAccess` 정책을 사용합니다.
> 프로덕션 환경에서는 `sns:Publish` 권한만 포함한 최소 권한 정책을 사용하는 것을 권장합니다.

### 태스크 6.1: Amazon SNS 알림 자동 전송 설정

103. AWS Config 콘솔에서 **Rules** 메뉴를 선택합니다.
104. `s3-bucket-public-read-prohibited` 규칙을 선택합니다.
105. **Actions** 드롭다운에서 `Manage remediation`을 선택합니다.
     <img src="/images/week12/12-2-task6-step105-manage-remediation.png" alt="Actions > Manage remediation 선택" class="guide-img-md" />

106. **Select remediation method**에서 `Automatic remediation`을 선택합니다.
107. **Remediation action details**에서 **Choose remediation action** 드롭다운에서 `AWS-PublishSNSNotification`을 선택합니다.
108. **Rate Limits**, **Resource ID parameter** 섹션은 기본값을 유지합니다.
109. **Parameters** 섹션에서 다음 값을 입력합니다:

| Parameter                | Value                                                                                                 |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| **TopicArn**             | 태스크 1.0에서 생성한 `config-topic`의 ARN (형식: `arn:aws:sns:ap-northeast-2:{계정ID}:config-topic`) |
| **Message**              | `Amazon S3 bucket public access compliance violation detected`                                        |
| **AutomationAssumeRole** | 태스크 6.0에서 생성한 `config-remediation-sns-role`의 ARN                                             |

> [!NOTE]
> AutomationAssumeRole은 필수 항목입니다. 태스크 6.0에서 복사한 역할 ARN을 입력합니다.

110. [[Save changes]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task6-step110-save-changes.png" alt="Save changes 버튼 클릭" class="guide-img-md" />
     <img src="/images/week12/12-2-task6-step110-save-changes-2.png" alt="Remediation 설정 확인" class="guide-img-md" />
     <img src="/images/week12/12-2-task6-step110-save-changes-3.png" alt="Remediation 설정 완료" class="guide-img-md" />

> [!NOTE]
> **AWS-PublishSNSNotification 제약사항**:
>
> - 이 SSM Automation 문서는 고정된 메시지만 전송합니다.
> - 동적 플레이스홀더(`{ResourceId}` 등)는 지원하지 않습니다.
> - 위반 리소스 정보를 포함한 동적 메시지가 필요한 경우, 커스텀 AWS Lambda 함수를 사용해야 합니다.

### 태스크 6.2: 자동 알림 테스트

111. Amazon S3 콘솔로 이동합니다.
112. `config-test-bucket-{StudentId}` 버킷을 선택합니다.
113. **Permissions** 탭을 선택합니다.
114. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
115. **Block all public access**를 체크 해제합니다.
116. [[Save changes]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task6-step116-save-changes.png" alt="Save changes 버튼 클릭" class="guide-img-md" />
117. 확인 창에서 `confirm`을 입력하고 [[Confirm]] 버튼을 클릭합니다.

> [!NOTE]
> 테스트를 위해 퍼블릭 액세스를 다시 허용합니다. AWS Config가 위반을 감지하면 자동으로 Remediation이 트리거됩니다.

118. AWS Config 콘솔로 이동합니다.
119. **Rules** 메뉴에서 `s3-bucket-public-read-prohibited` 규칙을 선택합니다.
120. 페이지를 새로고침하여 위반 리소스를 확인합니다.
121. **Resources in scope**에서 위반 리소스(`config-test-bucket-{StudentId}`)를 확인합니다.
122. Amazon SNS 이메일 알림이 수신되었는지 확인합니다.

> [!NOTE]
> 퍼블릭 액세스를 다시 해제한 후 AWS Config가 변경을 감지 → 규칙 재평가 → Noncompliant 판정 → Remediation 트리거 → Amazon SNS 알림 전송까지의 전체 흐름에 5-10분이 소요될 수 있습니다. 페이지를 여러 번 새로고침하여 상태 변경을 확인합니다.

123. Amazon S3 콘솔로 이동합니다.
124. `config-test-bucket-{StudentId}` 버킷을 선택합니다.
125. **Permissions** 탭을 선택합니다.
126. **Block public access (bucket settings)** 섹션에서 [[Edit]] 버튼을 클릭합니다.
127. **Block all public access**를 체크합니다.
128. [[Save changes]] 버튼을 클릭합니다.
129. 확인 창에서 `confirm`을 입력하고 [[Confirm]] 버튼을 클릭합니다.

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

130. AWS Config 콘솔에서 **Conformance packs** 메뉴를 선택합니다.
131. [[Deploy conformance pack]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task7-step131-deploy-conformance.png" alt="Deploy conformance pack 버튼 클릭" class="guide-img-md" />

132. **Step 1: Specify template** 페이지에서 **Conformance pack template**은 `Use sample template`이 선택되어 있는지 확인합니다.
133. **Sample template** 드롭다운에서 `Operational Best Practices for Amazon S3`를 선택합니다.
     <img src="/images/week12/12-2-task7-step133-sample-template.png" alt="Sample template 선택" class="guide-img-md" />

134. [[Next]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task7-step134-next.png" alt="Specify template Next" class="guide-img-md" />

135. **Step 2: Specify conformance pack details** 페이지에서 **Conformance pack name**에 `demo-s3-best-practices`를 입력합니다.
136. **Parameters** 섹션은 기본값을 유지합니다.
137. [[Next]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task7-step137-next.png" alt="Conformance pack details Next" class="guide-img-md" />
138. **Step 3: Review and deploy** 페이지에서 설정을 확인합니다.
139. [[Deploy conformance pack]] 버튼을 클릭합니다.
     <img src="/images/week12/12-2-task7-step139-deploy.png" alt="Deploy conformance pack 클릭" class="guide-img-md" />

> [!NOTE]
> 배포에 수 분이 소요됩니다. 배포 상태가 "CREATE_COMPLETE"로 변경될 때까지 기다립니다.

140. 배포 완료 후 Deployment status가 **Completed**인지 확인합니다.
     <img src="/images/week12/12-2-task7-step140-completed.png" alt="Deployment status Completed" class="guide-img-md" />

141. `demo-s3-best-practices`를 클릭하여 상세 페이지로 이동합니다.
     <img src="/images/week12/12-2-task7-step141-detail.png" alt="Conformance pack 상세 페이지" class="guide-img-md" />
142. **Compliance score** 섹션에서 전체 준수율을 확인합니다.

> [!NOTE]
> 배포 직후에는 Compliance score가 INSUFFICIENT DATA로 표시될 수 있습니다. 규칙 평가가 완료되면 점수가 업데이트됩니다.

143. **Rules** 섹션에서 포함된 규칙 목록과 각 규칙의 Compliance 상태(Compliant/Noncompliant)를 확인합니다.

> [!NOTE]
> Conformance Pack에 포함된 규칙 중 Noncompliant가 많을 수 있습니다. 이는 실습 환경에서 모든 S3 모범 사례를 적용하지 않았기 때문이며 정상입니다.

> [!NOTE]
> Conformance Pack 활용
>
> - **템플릿 기반**: YAML 형식으로 여러 AWS Config Rules를 패키지화
> - **AWS 제공 템플릿**: Operational Best Practices, PCI-DSS, HIPAA, CIS Benchmarks 등
> - **조직 전체 배포**: AWS Organizations와 통합하여 모든 계정에 일괄 적용 가능

✅ **태스크 완료**: Conformance Pack이 배포되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Config를 활성화하고 리소스 추적을 시작했습니다.
- 리소스 인벤토리와 변경 이력을 확인했습니다.
- AWS Config Rules를 생성하여 규정 준수를 자동 평가했습니다.
- 위반 리소스를 식별하고 수정했습니다.
- 규정 위반 시 자동 알림 기능을 설정했습니다.
- Conformance Pack으로 여러 규칙을 일괄 배포했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 단계 1: 생성된 리소스 확인 (Tag Editor)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `12-2`
6. [[Search resources]] 버튼을 클릭합니다.
   <img src="/images/week12/12-2-cleanup-step6-tag-search.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!OUTPUT]
> 이 실습에서 태그를 추가한 리소스(테스트 버킷, AWS Config Rules 5개)가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.
> AWS Config가 자동 생성한 Amazon S3 버킷, Amazon SNS 토픽, Conformance Pack 등은 태그를 추가하지 않았으므로 Tag Editor에 표시되지 않습니다. 이러한 리소스는 각 서비스 콘솔에서 직접 삭제해야 합니다.

### 단계 2: 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
8. Conformance Pack을 삭제합니다:

```bash
aws configservice delete-conformance-pack --conformance-pack-name demo-s3-best-practices
```

<img src="/images/week12/12-2-cleanup-step8-cli-conformance.png" alt="Conformance Pack 삭제 CLI" class="guide-img-md" />
> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws configservice describe-conformance-packs --conformance-pack-names demo-s3-best-practices
> ```
>
> `NoSuchConformancePackException` 오류가 나오면 삭제 완료입니다.
>
> <img src="/images/week12/12-2-cleanup-step8-cli-verify.png" alt="삭제 확인 CLI 결과" class="guide-img-md" />

9. Remediation 설정을 제거하고 AWS Config Rules를 삭제합니다:

```bash
# Remediation 제거
aws configservice delete-remediation-configuration --config-rule-name s3-bucket-public-read-prohibited

# Rules 삭제
for RULE in s3-bucket-public-read-prohibited s3-bucket-server-side-encryption-enabled ec2-instance-managed-by-systems-manager iam-password-policy vpc-sg-open-only-to-authorized-ports; do
  aws configservice delete-config-rule --config-rule-name ${RULE}
  echo "Deleted: ${RULE}"
done
```

<img src="/images/week12/12-2-cleanup-step9-cli-rules.png" alt="Rules 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> for RULE in s3-bucket-public-read-prohibited s3-bucket-server-side-encryption-enabled ec2-instance-managed-by-systems-manager iam-password-policy vpc-sg-open-only-to-authorized-ports; do
>   aws configservice describe-config-rules --config-rule-names ${RULE} 2>&1 | grep -q "NoSuchConfigRuleException" && echo "${RULE}: 삭제 완료" || echo "${RULE}: 아직 존재"
> done
> ```
>
> 모두 "삭제 완료"로 표시되면 정상입니다.
>
> <img src="/images/week12/12-2-cleanup-step9-cli-rules-verify.png" alt="Rules 삭제 확인 CLI 결과" class="guide-img-md" />

10. Configuration Recorder와 Delivery Channel을 삭제합니다:

```bash
aws configservice stop-configuration-recorder --configuration-recorder-name default
aws configservice delete-configuration-recorder --configuration-recorder-name default
aws configservice delete-delivery-channel --delivery-channel-name default
```

<img src="/images/week12/12-2-cleanup-step10-cli-recorder.png" alt="Configuration Recorder 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws configservice describe-configuration-recorders --query "ConfigurationRecorders[*].name" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

11. 테스트 버킷을 삭제합니다:

```bash
STUDENT_ID="20240001"
aws s3 rm s3://config-test-bucket-${STUDENT_ID} --recursive
aws s3 rb s3://config-test-bucket-${STUDENT_ID}
```

<img src="/images/week12/12-2-cleanup-step11-cli-s3.png" alt="테스트 버킷 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 `aws s3 ls | grep config-test-bucket`를 실행합니다. 출력이 없으면 삭제 완료입니다.

12. AWS Config 데이터 버킷을 삭제합니다:

```bash
CONFIG_BUCKET=$(aws s3 ls | grep config-bucket | awk '{print $3}')
if [ -n "${CONFIG_BUCKET}" ]; then
  aws s3 rm s3://${CONFIG_BUCKET} --recursive
  aws s3 rb s3://${CONFIG_BUCKET}
  echo "Deleted: ${CONFIG_BUCKET}"
fi
```

<img src="/images/week12/12-2-cleanup-step12-cli-config-bucket.png" alt="Config 데이터 버킷 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 `aws s3 ls | grep config-bucket`를 실행합니다. 출력이 없으면 삭제 완료입니다.

13. Amazon SNS 토픽을 삭제합니다:

```bash
TOPIC_ARN=$(aws sns list-topics --query "Topics[?contains(TopicArn,'config-topic')].TopicArn" --output text)
for ARN in ${TOPIC_ARN}; do
  aws sns delete-topic --topic-arn ${ARN}
  echo "Deleted: ${ARN}"
done
```

<img src="/images/week12/12-2-cleanup-step13-cli-sns.png" alt="SNS 토픽 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 `aws sns list-topics --query "Topics[?contains(TopicArn,'config-topic')]" --output text`를 실행합니다. 출력이 없으면 삭제 완료입니다.

14. Remediation용 IAM 역할을 삭제합니다 (태스크 6.0에서 생성한 경우):

```bash
ROLE_NAME="config-remediation-sns-role"
if aws iam get-role --role-name ${ROLE_NAME} 2>/dev/null; then
  POLICIES=$(aws iam list-attached-role-policies --role-name ${ROLE_NAME} --query "AttachedPolicies[*].PolicyArn" --output text)
  for POLICY in ${POLICIES}; do
    aws iam detach-role-policy --role-name ${ROLE_NAME} --policy-arn ${POLICY}
  done
  aws iam delete-role --role-name ${ROLE_NAME}
  echo "Deleted: ${ROLE_NAME}"
fi
```

<img src="/images/week12/12-2-cleanup-step14-cli-iam.png" alt="IAM 역할 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 `aws iam get-role --role-name config-remediation-sns-role`를 실행합니다. `NoSuchEntity` 오류가 나오면 삭제 완료입니다.

15. 옵션 1 완료 후 아래 **단계 3: 삭제 확인**으로 이동합니다.

<a id="option-2"></a>

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

**Conformance Pack 삭제**

16. AWS Config 콘솔로 이동합니다.
17. 왼쪽 메뉴에서 **Conformance packs**를 선택합니다.
18. `demo-s3-best-practices` Conformance Pack을 선택합니다.
19. **Actions** 드롭다운에서 `Delete`를 선택합니다.
    <img src="/images/week12/12-2-cleanup-step19-delete-conformance.png" alt="Conformance Pack Delete" class="guide-img-md" />
20. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week12/12-2-cleanup-step20-confirm-delete.png" alt="삭제 확인" class="guide-img-sm" />

**AWS Config Rules 삭제**

> [!IMPORTANT]
> Remediation 설정이 활성화된 상태에서 AWS Config Rule을 삭제하면 오류가 발생할 수 있습니다. 반드시 Remediation을 먼저 제거한 후 Rule을 삭제해야 합니다.

> [!NOTE]
> Conformance Pack을 삭제하면 해당 Pack에 포함된 규칙들은 자동으로 삭제됩니다. 여기서는 직접 생성한 규칙만 삭제합니다.

21. AWS Config 콘솔에서 왼쪽 메뉴의 **Rules**를 선택합니다.
22. Remediation이 설정된 규칙(`s3-bucket-public-read-prohibited`)을 클릭합니다.
23. **Remediation action** 섹션에서 [[Delete]] 버튼을 클릭합니다.
24. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.
25. 왼쪽 메뉴에서 **Rules**를 선택합니다.
26. 삭제할 규칙을 선택하고 **Actions** > `Delete rule`을 선택합니다.
    <img src="/images/week12/12-2-cleanup-step26-delete-rule.png" alt="Delete rule 선택" class="guide-img-md" />
27. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.
28. 직접 생성한 모든 규칙에 대해 반복합니다:
    <img src="/images/week12/12-2-cleanup-step28-confirm-rule.png" alt="Rule 삭제 확인" class="guide-img-sm" />
    - `s3-bucket-public-read-prohibited`
    - `s3-bucket-server-side-encryption-enabled`
    - `ec2-instance-managed-by-systems-manager`
    - `iam-password-policy`
    - `vpc-sg-open-only-to-authorized-ports`

**Configuration Recorder 중지 및 삭제**

29. 왼쪽 메뉴에서 **Settings**를 선택합니다.
30. **Recorder** 섹션에서 [[Stop recording]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step30-stop-recording.png" alt="Stop recording 확인" class="guide-img-sm" />

31. 확인 창에서 [[Confirm]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step31-confirm-stop.png" alt="Stop recording 확인" class="guide-img-sm" />

32. AWS Management Console 상단의 CloudShell 아이콘을 클릭하고 다음 명령어를 실행합니다:

```bash
aws configservice delete-configuration-recorder --configuration-recorder-name default
aws configservice delete-delivery-channel --delivery-channel-name default
```

<img src="/images/week12/12-2-cleanup-step32-cloudshell.png" alt="CloudShell 실행" class="guide-img-md" />
<img src="/images/week12/12-2-cleanup-step32-delete-recorder.png" alt="Configuration Recorder 및 Delivery Channel 삭제 CLI" class="guide-img-md" />

> [!NOTE]
> Configuration Recorder와 Delivery Channel은 AWS 콘솔에서 직접 삭제할 수 없으므로 AWS CLI를 사용합니다.

**테스트 버킷 삭제**

33. Amazon S3 콘솔로 이동합니다.
34. `config-test-bucket-{StudentId}` 버킷을 선택합니다.
35. [[Empty]] 버튼을 클릭합니다.
36. 확인 창에서 `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
37. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
38. 확인 창에서 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

**AWS Config 데이터 버킷 삭제**

39. AWS Config가 생성한 버킷을 찾습니다 (이름: `config-bucket-{계정ID}`).
40. 위와 동일한 방법으로 버킷을 비우고 삭제합니다.

**Amazon SNS 토픽 삭제**

41. Amazon SNS 콘솔로 이동합니다.
42. 왼쪽 메뉴에서 **Topics**를 선택합니다.
43. `config-topic` 토픽을 선택합니다.
44. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step44-delete-sns.png" alt="SNS 토픽 삭제" class="guide-img-md" />
45. 확인 창에서 `delete me`를 입력하고 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step45-confirm-sns.png" alt="SNS 토픽 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> Amazon SNS 토픽을 삭제하면 연결된 모든 구독도 자동으로 삭제됩니다.

**Remediation IAM 역할 삭제 (태스크 6.0에서 생성한 경우)**

46. AWS IAM 콘솔로 이동합니다.
47. 왼쪽 메뉴에서 **Roles**를 선택합니다.
48. `config-remediation-sns-role` 역할을 선택합니다.
49. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step49-delete-role.png" alt="IAM 역할 삭제" class="guide-img-md" />
50. 확인 창에서 역할 이름을 입력하고 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step50-delete-iam.png" alt="IAM 역할 삭제 확인" class="guide-img-sm" />

### 단계 3: 삭제 확인

51. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
52. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
53. **Regions**에서 `ap-northeast-2`를 선택합니다.
54. **Resource types**에서 `All supported resource types`를 선택합니다.
55. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `12-2`
56. [[Search resources]] 버튼을 클릭합니다.
    <img src="/images/week12/12-2-cleanup-step56-verify.png" alt="삭제 확인 검색 결과" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

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
- Detective: 리소스 생성 후 평가 (기본)

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
