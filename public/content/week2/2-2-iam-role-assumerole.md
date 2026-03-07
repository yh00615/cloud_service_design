---
title: 'AWS STS AssumeRole을 활용한 역할 전환'
week: 2
session: 2
awsServices:
  - AWS IAM
  - AWS STS
learningObjectives:
  - Amazon S3 읽기 전용 역할을 생성하고 신뢰 정책을 구성할 수 있습니다.
  - 최소 권한 사용자에게 특정 역할을 맡을 수 있는 AssumeRole 권한을 부여할 수 있습니다.
  - AWS CLI에서 AWS STS AssumeRole로 역할을 전환할 수 있습니다.
  - 임시 자격증명으로 리소스에 접근하여 역할 동작을 확인할 수 있습니다.
prerequisites:
  - AWS 계정 및 AWS IAM 사용자
  - AWS CloudShell 접근 가능한 환경 (또는 AWS CLI 설치 및 구성)
  - AWS IAM 기본 개념 이해
---

이 실습에서는 **AWS IAM 역할**의 개념을 이해하고 **AssumeRole API**를 활용하여 **임시 자격증명**을 획득하는 방법을 학습합니다. 먼저 **Amazon S3 읽기 전용 역할**을 생성하고 **신뢰 정책**(Trust Policy)과 **권한 정책**(Permission Policy)의 차이를 이해합니다. **AWS CLI**를 사용하여 **AssumeRole API**를 호출하고 **임시 보안 자격증명**을 획득한 후, 이를 사용하여 **Amazon S3 버킷**에 접근합니다.

> [!DOWNLOAD]
> [week2-2-iam-role-assumerole.zip](/files/week2/week2-2-iam-role-assumerole.zip)
>
> - `week2-2-iam-role-assumerole.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 IAM 사용자, S3 버킷 자동 생성)
> - `assume-role-policy.json` - AssumeRole 권한 정책 JSON (태스크 4에서 사용)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week2-2-iam-role-assumerole.yaml 사용)
> - 태스크 4: IAM 사용자에게 AssumeRole 권한 부여 (assume-role-policy.json 사용)

> [!WARNING]
> 이 실습에서 생성하는 AWS IAM 역할은 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 AWS IAM 사용자와 테스트용 Amazon S3 버킷을 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **AWS IAM 사용자**: `lab-user` (콘솔 로그인 가능, AssumeRole 테스트용)
- **Amazon S3 버킷**: 역할 권한 테스트용

> [!NOTE]
> lab-user는 콘솔 로그인이 가능하도록 초기 비밀번호가 설정됩니다. 첫 로그인 시 비밀번호 변경이 필요합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week2-2-iam-role-assumerole.zip` 파일의 압축을 해제합니다.
2. `week2-2-iam-role-assumerole.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week2-2-iam-role-assumerole.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week2-2-iam-role-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다.
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 기본값을 유지합니다.
13. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
14. [[Next]] 버튼을 클릭합니다.
15. **Review** 페이지에서 설정을 확인합니다.
16. [[Submit]] 버튼을 클릭합니다.
17. 스택 생성이 시작됩니다.
18. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.

> [!NOTE]
> 스택 생성에 1-2분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. **Outputs** 탭을 선택합니다.
20. 출력값들을 확인하고 메모장에 복사합니다:
    - `LabUserName`: lab-user
    - `LabUserConsoleLoginUrl`: 콘솔 로그인 URL
    - `LabUserInitialPassword`: 초기 비밀번호 (ChangeMe123!)
    - `TestBucketName`: iam-role-lab-{계정ID}

> [!IMPORTANT]
> 이 출력값들은 태스크 4-6에서 사용됩니다. 반드시 메모장에 저장합니다.
>
> **다음 단계**: 새 시크릿 창(또는 시크릿 모드)을 열고 `LabUserConsoleLoginUrl`로 접속하여 lab-user로 로그인합니다.
>
> - 사용자 이름: `lab-user`
> - 비밀번호: `ChangeMe123!` (또는 스택 생성 시 설정한 비밀번호)
> - 첫 로그인 시 새 비밀번호로 변경해야 합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon S3 읽기 전용 역할 생성

이 태스크에서는 **AWS IAM 역할**을 생성하고 **신뢰 정책**(Trust Policy)을 구성합니다. **신뢰 정책**(Trust Policy)은 "누가 이 역할을 맡을 수 있는가"를 정의하며, **AWS 계정**을 신뢰 주체로 지정하면 같은 계정 내의 **AWS IAM 사용자**나 **서비스**가 이 역할을 맡을 수 있습니다.

21. AWS Management Console에 로그인한 후 상단 검색창에 `IAM`을 입력하고 선택합니다.
22. 왼쪽 메뉴에서 **Roles**를 선택합니다.
23. [[Create role]] 버튼을 클릭합니다.
24. **Trusted entity type**에서 `AWS account`를 선택합니다.

> [!NOTE]
> **Trusted entity type** 옵션은 다음과 같습니다:
>
> - AWS service (첫 번째)
> - **AWS account** (두 번째) ← 이 옵션을 선택합니다
> - Web identity (세 번째)
> - SAML 2.0 federation (네 번째)
> - Custom trust policy (다섯 번째)

25. **An AWS account**에서 `This account`를 선택합니다.

> [!NOTE]
> 콘솔 버전에 따라 "This account (계정ID)" 또는 "This account"로 표시될 수 있습니다.  
> 현재 계정을 선택하는 옵션을 선택합니다.

26. **Account ID**에 현재 계정 ID가 표시되는지 확인합니다.

> [!NOTE]
> **Account ID** 필드에 12자리 숫자가 자동으로 표시됩니다. 이는 현재 로그인한 AWS 계정의 ID입니다.

27. [[Next]] 버튼을 클릭합니다.
28. **Add permissions** 페이지로 이동합니다.

> [!NOTE]
> "This account"를 선택하면 같은 계정 내의 AWS IAM 사용자가 이 역할을 맡을 수 있습니다. 다음 단계에서 이 역할에 권한을 부여합니다.

✅ **태스크 완료**: 신뢰 정책이 구성되었습니다.

## 태스크 2: 권한 정책 연결

이 태스크에서는 **권한 정책**(Permission Policy)을 역할에 연결합니다. **권한 정책**(Permission Policy)은 "이 역할이 무엇을 할 수 있는가"를 정의하며, **AWS 관리형 정책**인 **AmazonS3ReadOnlyAccess**를 사용하면 **Amazon S3 버킷**과 객체를 조회할 수 있지만 생성, 수정, 삭제는 할 수 없습니다.

29. **Permissions policies** 검색창에 `S3`를 입력합니다.
30. 검색 결과에서 `AmazonS3ReadOnlyAccess` 정책을 찾습니다.
31. `AmazonS3ReadOnlyAccess` 정책 왼쪽의 체크박스를 선택합니다.

> [!NOTE]
> 체크박스를 선택하면 체크 표시가 나타나고, 화면 하단에 "1 policy selected"라고 표시됩니다.

32. [[Next]] 버튼을 클릭합니다.
33. **Name, review, and create** 페이지로 이동합니다.
34. **Role name**에 `S3ReadOnlyRole`을 입력합니다.
35. **Description**에 `Role for read-only access to Amazon S3 buckets`를 입력합니다.
36. 아래로 스크롤하여 **Step 1: Select trusted entities** 섹션을 확인합니다.

> [!NOTE]
> **Trusted entities** 섹션에 "Trust policy"가 표시되고, 신뢰 정책 요약이 보입니다.  
> 콘솔 버전에 따라 JSON 전체가 표시되거나 요약 형태로 표시될 수 있습니다.  
> JSON 전체를 보려면 역할 생성 후 **Trust relationships** 탭에서 확인할 수 있습니다.

예상되는 신뢰 정책 JSON: 여기서 `123456789012`는 현재 계정 ID로 자동으로 채워집니다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}
```

37. **Step 2: Add permissions** 섹션에서 `AmazonS3ReadOnlyAccess` 정책이 연결되어 있는지 확인합니다.

> [!NOTE]
> 신뢰 정책은 누가 이 역할을 맡을 수 있는지 정의하고, 권한 정책은 역할이 무엇을 할 수 있는지 정의합니다.

38. 아래로 스크롤하여 **Tags - optional** 섹션을 찾습니다.
39. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-2`     |
| `CreatedBy` | `Student` |

40. [[Create role]] 버튼을 클릭합니다.
41. 역할 생성이 완료되면 **Roles** 페이지로 자동 이동합니다.
42. 화면 상단에 녹색 배너로 "Role S3ReadOnlyRole created"라는 성공 메시지가 표시됩니다.
43. 역할 목록에서 `S3ReadOnlyRole`을 검색하여 생성된 역할을 확인합니다.

> [!NOTE]
> 역할 목록에서 **Role name** 열에 `S3ReadOnlyRole`이 표시됩니다. 이 역할을 클릭하면 상세 정보를 확인할 수 있습니다.

✅ **태스크 완료**: Amazon S3 읽기 전용 역할이 생성되었습니다.

## 태스크 3: 역할 ARN 확인

이 태스크에서는 생성된 역할의 **ARN**(Amazon Resource Name)을 확인합니다. **ARN**(Amazon Resource Name)은 AWS 리소스를 고유하게 식별하는 값으로, **AssumeRole API**를 호출할 때 필수 파라미터로 사용됩니다. 형식은 `arn:aws:iam::계정ID:role/역할이름`이며, 이 값을 복사하여 저장해두면 **CLI**나 **SDK**에서 역할을 맡을 때 사용할 수 있습니다.

44. 역할 목록에서 `S3ReadOnlyRole`을 검색합니다.
45. 검색 결과에서 `S3ReadOnlyRole`을 클릭합니다.
46. 역할 상세 페이지가 열립니다.
47. 페이지 상단의 **Summary** 섹션을 확인합니다.
48. **ARN** 필드를 찾습니다.

> [!NOTE]
> **ARN** 필드는 **Summary** 섹션의 상단에 위치하며, `arn:aws:iam::123456789012:role/S3ReadOnlyRole` 형식으로 표시됩니다.  
> ARN 오른쪽에 복사 아이콘이 있습니다.

49. ARN 오른쪽의 복사 아이콘을 클릭하여 ARN 값을 복사합니다.
50. 메모장을 열고 복사한 ARN을 붙여넣습니다.
51. 메모장에 "S3ReadOnlyRole ARN:"이라는 레이블을 추가하여 저장합니다.

> [!NOTE]
> ARN은 AWS 리소스를 고유하게 식별하는 값으로, AssumeRole 시 필요합니다. 다음 태스크에서 이 ARN을 사용합니다. AWS IAM은 글로벌 서비스이므로 리전 필드가 비어있어 콜론이 연속으로 두 개(`::`)가 나타나는 것이 정상입니다.

ARN 형식 예시: `arn:aws:iam::123456789012:role/S3ReadOnlyRole`

✅ **태스크 완료**: 역할 ARN이 확인되었습니다.

## 태스크 4: AWS IAM 사용자에게 AssumeRole 권한 부여

이 태스크에서는 **lab-user**에게 **sts:AssumeRole** 권한을 부여합니다. 이 권한은 **인라인 정책**으로 사용자에게 직접 연결하며, 정책에서 **Resource 요소**로 맡을 수 있는 역할을 명시적으로 지정합니다. 이를 통해 사용자가 특정 역할만 맡을 수 있도록 제한하여 **보안**을 강화합니다.

> [!NOTE]
> 이 태스크는 **lab-user로 로그인한 시크릿 창**에서 진행하거나, 관리자 권한이 있는 원래 창에서 진행할 수 있습니다.
> lab-user는 IAMReadOnlyAccess 권한만 있어 자신에게 정책을 추가할 수 없으므로, **관리자 권한이 있는 원래 창**에서 진행하는 것을 권장합니다.

52. AWS IAM 콘솔로 이동합니다.
53. 왼쪽 메뉴에서 **Users**를 선택합니다.
54. 사용자 목록에서 `lab-user`를 검색합니다.
55. `lab-user`를 클릭합니다.

56. 사용자 상세 페이지에서 **Permissions** 탭을 선택합니다.
57. **Permissions policies** 섹션에서 [[Add permissions]] 버튼을 클릭합니다.
58. 드롭다운 메뉴가 나타나면 [[Create inline policy]]를 선택합니다.
59. **Specify permissions** 페이지가 열립니다.
60. **JSON** 탭 또는 토글을 선택합니다.

> [!NOTE]
> 콘솔 버전에 따라 "JSON" 탭, "JSON" 토글, 또는 "Switch to JSON editor" 버튼으로 표시될 수 있습니다. JSON 편집기로 전환하는 옵션을 선택합니다.

61. 기존 정책 코드를 모두 삭제한 후 다음 정책을 입력합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::YOUR_ACCOUNT_ID:role/S3ReadOnlyRole"
    }
  ]
}
```

> [!TIP]
> 다운로드한 ZIP 파일의 `assume-role-policy.json`에도 동일한 정책이 포함되어 있습니다. 파일을 열어서 복사하여 붙여넣을 수도 있습니다.

> [!IMPORTANT]
> `YOUR_ACCOUNT_ID`를 실제 계정 ID로 변경해야 합니다.  
> 계정 ID는 태스크 3에서 복사한 ARN에서 확인할 수 있습니다 (예: `arn:aws:iam::123456789012:role/S3ReadOnlyRole`에서 `123456789012` 부분).
>
> **권장 방법**: 태스크 3에서 복사한 ARN 전체를 Resource 값으로 사용합니다. 메모장에 저장한 ARN을 그대로 복사하여 붙여넣으면 오류를 방지할 수 있습니다.

> [!TROUBLESHOOTING]
> **문제**: 정책 저장 시 "Invalid ARN" 또는 "Malformed policy document" 오류가 발생합니다
>
> **일반적인 원인**:
>
> 1. **계정 ID 미변경**: `YOUR_ACCOUNT_ID`를 실제 계정 ID로 변경하지 않았습니다
> 2. **ARN 형식 오류**: 콜론(`:`)이나 슬래시(`/`)가 누락되었거나 잘못된 위치에 있습니다
> 3. **역할 이름 오타**: `S3ReadOnlyRole` 대신 다른 이름을 입력했습니다
> 4. **공백 포함**: ARN에 불필요한 공백이 포함되었습니다
>
> **해결 방법**:
>
> 1. 태스크 3에서 복사한 ARN을 메모장에서 확인합니다
> 2. ARN 전체를 복사하여 `"Resource"` 값에 붙여넣습니다
> 3. 올바른 형식: `arn:aws:iam::123456789012:role/S3ReadOnlyRole`
> 4. JSON 문법 검증: 중괄호, 대괄호, 쉼표, 따옴표가 올바른지 확인합니다

62. JSON 편집기에서 `YOUR_ACCOUNT_ID` 부분을 찾아 실제 계정 ID로 교체합니다.
63. 정책이 올바르게 작성되었는지 확인합니다.

> [!TIP]
> 정책 예시 (계정 ID가 123456789012인 경우):
>
> ```json
> {
>   "Version": "2012-10-17",
>   "Statement": [
>     {
>       "Effect": "Allow",
>       "Action": "sts:AssumeRole",
>       "Resource": "arn:aws:iam::123456789012:role/S3ReadOnlyRole"
>     }
>   ]
> }
> ```

64. [[Next]] 버튼을 클릭합니다.
65. **Review and create** 페이지로 이동합니다.
66. **Policy name**에 `AssumeS3ReadOnlyRolePolicy`를 입력합니다.
67. [[Create policy]] 버튼을 클릭합니다.
68. 정책 생성이 완료되면 사용자의 **Permissions** 탭으로 자동 이동합니다.
69. 화면 상단에 녹색 배너로 "Policy AssumeS3ReadOnlyRolePolicy created"라는 성공 메시지가 표시됩니다.
70. **Permissions policies** 섹션에서 `AssumeS3ReadOnlyRolePolicy`가 추가되었는지 확인합니다.

> [!NOTE]
> **Permissions policies** 섹션에 `AssumeS3ReadOnlyRolePolicy`가 표시되고, **Policy Type** 열에 "Customer inline"으로 표시됩니다. 이는 사용자에게 직접 연결된 인라인 정책임을 의미합니다.

✅ **태스크 완료**: AssumeRole 권한이 부여되었습니다.

## 태스크 5: AWS CLI로 AssumeRole 수행

이 태스크에서는 **lab-user로 로그인한 시크릿 창**에서 **AWS CloudShell**을 사용하여 **AssumeRole API**를 호출하고 **임시 자격증명**을 획득합니다. **AssumeRole**은 **STS**(Security Token Service)의 API로, 역할을 맡으면 **AccessKeyId**, **SecretAccessKey**, **SessionToken**으로 구성된 임시 자격증명을 받습니다. 이 자격증명은 기본 1시간 동안 유효하며, 역할의 Maximum session duration 설정에서 최대 12시간까지 연장할 수 있습니다.

> [!IMPORTANT]
> 이 태스크는 **lab-user로 로그인한 시크릿 창**에서 진행합니다.
>
> 1. 새 시크릿 창(또는 시크릿 모드)을 엽니다.
> 2. 태스크 0의 Outputs에서 복사한 `LabUserConsoleLoginUrl`로 접속합니다.
> 3. 사용자 이름: `lab-user`, 비밀번호: 태스크 0에서 확인한 초기 비밀번호
> 4. 첫 로그인 시 새 비밀번호로 변경합니다.

> [!NOTE]
> 이 실습에서 생성한 역할은 Maximum session duration을 변경하지 않았으므로 최대 세션 시간은 1시간입니다.  
> 역할 설정에서 Maximum session duration을 늘리면 최대 12시간까지 연장할 수 있습니다.

71. **lab-user로 로그인한 시크릿 창**에서 AWS Management Console 상단 오른쪽의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell은 AWS CLI가 사전 설치되어 있고 현재 로그인한 AWS IAM 사용자 자격증명이 자동으로 구성된 브라우저 기반 셸 환경입니다.  
> 첫 실행 시 환경 초기화에 1-2분이 소요될 수 있습니다. 환경이 준비될 때까지 기다립니다.

72. 현재 자격증명을 확인합니다:

```bash
aws sts get-caller-identity
```

> [!OUTPUT]
>
> ```json
> {
>   "UserId": "AIDAI...",
>   "Account": "123456789012",
>   "Arn": "arn:aws:iam::123456789012:user/lab-user"
> }
> ```

73. 현재 사용자로 Amazon S3 버킷 목록 조회를 시도합니다:

```bash
aws s3 ls
```

> [!OUTPUT]
>
> ```bash
> An error occurred (AccessDenied) when calling the ListBuckets operation: Access Denied
> ```

> [!NOTE]
> **AccessDenied** 오류가 나타나는 것이 정상입니다. 현재 사용자는 `sts:AssumeRole` 권한만 가지고 있고, Amazon S3 접근 권한은 없습니다.  
> 다음 단계에서 AssumeRole을 통해 S3ReadOnlyRole 역할을 맡으면 Amazon S3 읽기 권한을 얻을 수 있습니다.

74. 메모장에 저장한 역할 ARN을 확인합니다.
75. 다음 명령어를 입력하되, 역할 ARN 부분을 태스크 3에서 복사한 실제 ARN으로 교체합니다:

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/S3ReadOnlyRole \
  --role-session-name s3-readonly-session
```

> [!IMPORTANT]
> `--role-arn` 값을 반드시 태스크 3에서 복사한 실제 역할 ARN으로 교체해야 합니다. 메모장에 저장한 ARN을 그대로 복사하여 붙여넣습니다.
>
> `--role-session-name`은 세션을 식별하는 이름으로, 원하는 이름을 사용할 수 있습니다. 이 이름은 CloudTrail 로그에 기록되어 누가 역할을 맡았는지 추적하는 데 사용됩니다.

> [!TIP]
> **한 줄 명령어** (줄바꿈 없이 복사하려는 경우):
>
> ```bash
> aws sts assume-role --role-arn arn:aws:iam::123456789012:role/S3ReadOnlyRole --role-session-name s3-readonly-session
> ```
>
> 명령어 예시 (계정 ID가 123456789012인 경우):
>
> ```bash
> aws sts assume-role \
>   --role-arn arn:aws:iam::123456789012:role/S3ReadOnlyRole \
>   --role-session-name s3-readonly-session
> ```

76. Enter 키를 눌러 명령어를 실행합니다.
77. Enter 키를 눌러 명령어를 실행합니다.
78. 출력된 JSON 결과를 확인합니다.

> [!OUTPUT]
>
> ```json
> {
>   "Credentials": {
>     "AccessKeyId": "ASIAZ...",
>     "SecretAccessKey": "wJalrXUtn...",
>     "SessionToken": "FwoGZXIvYXdz...",
>     "Expiration": "2026-02-15T12:00:00Z"
>   },
>   "AssumedRoleUser": {
>     "AssumedRoleId": "AROAI...:s3-readonly-session",
>     "Arn": "arn:aws:sts::123456789012:assumed-role/S3ReadOnlyRole/s3-readonly-session"
>   }
> }
> ```

79. 출력된 JSON에서 `Credentials` 섹션의 세 가지 값을 메모장에 복사합니다:
   - `AccessKeyId`: `ASIAZ...`로 시작하는 값
   - `SecretAccessKey`: 긴 문자열 값
   - `SessionToken`: 매우 긴 문자열 값

> [!WARNING]
> **임시 자격증명 보안 주의사항**: 메모장에 저장한 자격증명 정보는 실습 종료 후 반드시 삭제합니다.  
> 임시 자격증명이라도 유효 기간 동안에는 AWS 리소스에 접근할 수 있으므로 주의가 필요합니다.

> [!NOTE]
> 이 세 가지 값은 다음 태스크에서 환경 변수로 설정할 때 사용됩니다. 정확히 복사하여 메모장에 저장합니다.
>
> **SessionToken 길이 주의**: SessionToken은 매우 긴 문자열(보통 500-1000자 이상)입니다.  
> 복사할 때 전체가 선택되었는지 확인합니다. 일부만 복사하면 다음 태스크에서 "Invalid token" 오류가 발생합니다.  
> 메모장에 붙여넣은 후 스크롤하여 전체 길이를 확인하는 것을 권장합니다.
>
> **SessionToken 복사 시 줄바꿈 주의**: 복사한 값에 줄바꿈이 포함되지 않도록 주의합니다.  
> 메모장에 붙여넣은 후 줄바꿈이 있으면 제거합니다. 줄바꿈이 포함되면 환경 변수 설정 시 오류가 발생합니다.

✅ **태스크 완료**: AssumeRole이 성공적으로 수행되었습니다.

## 태스크 6: 임시 자격증명 사용

이 태스크에서는 **AssumeRole**로 획득한 **임시 자격증명**을 환경 변수로 설정하고 사용합니다. **환경 변수**로 설정하면 **AWS CLI**가 자동으로 이 자격증명을 사용하며, **현재 AWS CloudShell 세션**에서만 유효합니다. CloudShell을 닫거나 환경 변수를 제거하면 원래 자격증명으로 돌아갑니다.

> [!TIP]
> **jq를 활용한 자동 설정 (선택사항)**: 환경 변수를 수동으로 설정하는 대신, jq를 사용하여 자동으로 설정할 수 있습니다. 다음 명령어를 한 줄로 실행합니다:
>
> ```bash
> eval $(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/S3ReadOnlyRole --role-session-name s3-readonly-session | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)"')
> ```
>
> 이 방법을 사용하면 복사/붙여넣기 오류를 방지할 수 있습니다. **단, 역할 ARN은 실제 값으로 교체해야 합니다**.

80. 메모장에 저장한 세 가지 자격증명 값을 확인합니다.
81. 다음 명령어 3줄을 메모장에 복사한 후, 따옴표 안의 값을 실제 자격증명 값으로 교체합니다:

```bash
export AWS_ACCESS_KEY_ID="여기에_AccessKeyId_값_붙여넣기"
export AWS_SECRET_ACCESS_KEY="여기에_SecretAccessKey_값_붙여넣기"
export AWS_SESSION_TOKEN="여기에_SessionToken_값_붙여넣기"
```

> [!IMPORTANT]
> 쉘 명령어의 따옴표(`"`)는 그대로 유지하고, `여기에_값_붙여넣기` 부분만 실제 자격증명 값으로 교체합니다.  
> 자격증명 값 자체에는 추가 따옴표를 넣지 않습니다.
>
> **SessionToken에는 특수문자가 포함되어 있으므로 반드시 따옴표로 감싸야 합니다.** 따옴표를 빼먹으면 명령어가 실패합니다.

> [!TIP]
> 올바른 예시:
>
> ```bash
> export AWS_ACCESS_KEY_ID="ASIAZEXAMPLE123"
> ```
>
> 잘못된 예시:
>
> ```bash
> export AWS_ACCESS_KEY_ID=""ASIAZEXAMPLE123""  # 따옴표 중복 (잘못됨)
> export AWS_ACCESS_KEY_ID=ASIAZEXAMPLE123      # 따옴표 누락 (SessionToken에 특수문자가 포함될 수 있으므로 반드시 따옴표 사용)
> ```
>
> **자주 발생하는 오류:**
>
> - `InvalidAccessKeyId`: Access Key ID를 잘못 복사했거나 공백/줄바꿈이 포함된 경우
> - `InvalidClientTokenId`: SessionToken을 잘못 복사했거나 만료된 경우
> - 값 복사 시 전체가 선택되었는지 확인하고, 메모장에 붙여넣은 후 줄바꿈이 없는지 확인합니다

82. 메모장에서 값을 교체한 3줄의 명령어를 모두 복사합니다.
83. CloudShell에 붙여넣고 Enter 키를 눌러 실행합니다.

> [!WARNING]
> **환경 변수 히스토리 노출 주의**: `export` 명령어로 설정한 환경 변수는 셸 히스토리에 기록됩니다. `history` 명령어로 자격증명이 노출될 수 있으므로, 실습 종료 후 CloudShell 세션을 종료하거나 `history -c` 명령어로 히스토리를 삭제하는 것을 권장합니다.

84. 현재 자격증명을 다시 확인합니다:

```bash
aws sts get-caller-identity
```

> [!OUTPUT]
>
> ```json
> {
>   "UserId": "AROAI...:s3-readonly-session",
>   "Account": "123456789012",
>   "Arn": "arn:aws:sts::123456789012:assumed-role/S3ReadOnlyRole/s3-readonly-session"
> }
> ```

> [!NOTE]
> Arn이 `assumed-role`로 변경되어 역할을 사용 중임을 나타냅니다.

✅ **태스크 완료**: 임시 자격증명이 설정되었습니다.

## 태스크 7: 권한 테스트

이 태스크에서는 **임시 자격증명**으로 **Amazon S3 권한**을 테스트합니다. **S3ReadOnlyAccess** 정책은 **읽기 권한**만 부여하므로, **버킷 목록 조회**는 성공하지만 **버킷 생성**은 실패합니다. 이를 통해 역할의 **권한 범위**가 올바르게 작동하는지 확인할 수 있습니다.

85. Amazon S3 버킷 목록을 조회합니다 (읽기 권한 - 성공):

```bash
aws s3 ls
```

> [!OUTPUT]
>
> ```
> 2026-02-15 10:30:00 my-bucket-1
> 2026-02-16 14:15:00 my-bucket-2
> ```

> [!NOTE]
> 계정에 Amazon S3 버킷이 없는 경우 빈 출력이 표시됩니다. 이는 정상이며, 읽기 권한이 작동하고 있음을 의미합니다.

86. Amazon S3 버킷 생성을 시도합니다 (쓰기 권한 - 실패):

```bash
aws s3 mb s3://test-bucket-assumerole-YOUR-INITIALS-12345
```

> [!WARNING]
> `YOUR-INITIALS-12345` 부분을 본인의 이니셜(소문자)과 랜덤 숫자로 변경합니다 (예: `test-bucket-assumerole-jdoe-98765`).
>
> **Amazon S3 버킷 명명 규칙:**
>
> - 전 세계적으로 고유해야 합니다.
> - 소문자(a-z), 숫자(0-9), 하이픈(-)만 사용 가능합니다.
> - 대문자, 언더스코어(\_), 특수문자는 사용할 수 없습니다.
> - 3-63자 사이여야 합니다.

> [!OUTPUT]
>
> ```bash
> An error occurred (AccessDenied) when calling the CreateBucket operation: Access Denied
> ```

> [!IMPORTANT]
> **AccessDenied** 오류가 나와야 정상입니다. 이는 S3ReadOnlyAccess 정책이 읽기 권한만 부여하므로 버킷 생성이 거부되었음을 의미합니다.
>
> 만약 `BucketAlreadyExists` 오류가 발생하면 다른 사람이 이미 같은 이름의 버킷을 생성한 것입니다.  
> 만약 `BucketAlreadyOwnedByYou` 오류가 발생하면 본인 계정이 이미 소유한 버킷입니다.  
> 두 경우 모두 다른 버킷 이름으로 다시 시도합니다. `AccessDenied` 오류가 나와야 권한 테스트가 성공한 것입니다.
>
> 이 명령은 AccessDenied로 실패하므로 버킷이 생성되지 않습니다. 별도의 정리가 필요하지 않습니다.

✅ **태스크 완료**: 역할의 권한이 올바르게 작동함을 확인했습니다.

## 태스크 8: 원래 자격증명으로 복귀

이 태스크에서는 **환경 변수**를 제거하여 **원래 AWS IAM 사용자 자격증명**으로 복귀합니다. **임시 자격증명**은 환경 변수로만 설정되었으므로, 변수를 제거하면 **AWS CLI**가 다시 기본 자격증명을 사용합니다.

> [!NOTE]
> **AWS CLI 자격증명 우선순위 (CloudShell 환경)**: AWS CloudShell에서 AWS CLI는 다음 순서로 자격증명을 찾습니다:
>
> 1. 환경 변수 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
> 2. AWS CLI 프로파일 (~/.aws/credentials)
> 3. CloudShell 기본 자격증명 (현재 로그인한 사용자)
>
> CloudShell에서 환경 변수를 설정하면 CloudShell의 기본 자격증명을 오버라이드합니다. 환경 변수를 제거하면 다시 CloudShell의 기본 자격증명이 사용됩니다.
>
> **참고**: 일반 AWS CLI 환경에서는 추가로 다음 우선순위가 있습니다:
>
> - AWS CLI 설정 파일 (~/.aws/config)
> - 컨테이너 자격증명 (Amazon ECS 태스크 역할)
> - Amazon EC2 인스턴스 메타데이터 (Amazon EC2 인스턴스 역할)
>
> 이 실습에서는 CloudShell 환경을 사용하므로 위의 3가지 우선순위만 관련됩니다.

87. 환경 변수를 제거합니다:

```bash
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
```

88. 현재 자격증명을 확인합니다:

```bash
aws sts get-caller-identity
```

> [!OUTPUT]
>
> ```json
> {
>   "UserId": "AIDAI...",
>   "Account": "123456789012",
>   "Arn": "arn:aws:iam::123456789012:user/lab-user"
> }
> ```

✅ **태스크 완료**: 원래 AWS IAM 사용자 자격증명으로 복귀했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS IAM 역할을 생성하고 신뢰 정책을 구성했습니다.
- 권한 정책을 역할에 연결했습니다.
- AssumeRole을 사용하여 임시 자격증명을 획득했습니다.
- 임시 자격증명으로 AWS 서비스에 접근했습니다.
- 역할의 권한 범위를 테스트하고 확인했습니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 보안 위험을 방지합니다.

### 단계 1: Tag Editor로 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `All regions`를 선택합니다.

> [!NOTE]
> AWS IAM은 글로벌 서비스이므로 특정 리전이 아닌 All regions를 선택해야 AWS IAM 역할이 검색됩니다.  
> Week 1-1 실습에서는 리전별 리소스(Amazon S3, AWS Lambda 등)를 검색했으므로 ap-northeast-2를 선택했지만, AWS IAM 리소스는 All regions를 선택해야 합니다.

4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `2-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 AWS IAM 역할이 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 보안 위험을 방지합니다.

### 🗑️ 리소스 정리 프로세스

Tag Editor로 Week 태그 검색 → 리소스 확인 → AWS IAM 리소스 삭제 → AWS CloudFormation 스택 삭제

### 단계 1: Tag Editor로 리소스 확인

8. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
9. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
10. **Regions**에서 `All regions`를 선택합니다.

> [!NOTE]
> AWS IAM은 글로벌 서비스이므로 특정 리전이 아닌 All regions를 선택해야 AWS IAM 역할이 검색됩니다.

11. **Resource types**에서 `All supported resource types`를 선택합니다.
12. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `2-2`
13. [[Search resources]] 버튼을 클릭합니다.
14. 이 실습에서 생성한 AWS IAM 역할이 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: AWS IAM 리소스 삭제

#### AWS IAM 역할 삭제

15. AWS IAM 콘솔로 이동합니다.
16. 왼쪽 메뉴에서 **Roles**를 선택합니다.
17. 역할 목록에서 `S3ReadOnlyRole`을 검색합니다.
18. `S3ReadOnlyRole` 역할 왼쪽의 라디오 버튼을 선택합니다.

> [!NOTE]
> 역할이 선택되면 라디오 버튼에 점이 표시되고, 상단의 [[Delete]] 버튼이 활성화됩니다.

19. [[Delete]] 버튼을 클릭합니다.
20. 확인 창이 나타나면 입력 필드에 `S3ReadOnlyRole`을 입력합니다.

> [!NOTE]
> 역할 이름을 정확히 입력해야 [[Delete]] 버튼이 활성화됩니다.

21. [[Delete]] 버튼을 클릭합니다.
22. 화면 상단에 녹색 배너로 "Role S3ReadOnlyRole deleted successfully"라는 성공 메시지가 표시됩니다.
23. 역할 목록에서 `S3ReadOnlyRole`이 더 이상 표시되지 않는지 확인합니다.

#### AWS IAM 사용자 인라인 정책 삭제

24. 왼쪽 메뉴에서 **Users**를 선택합니다.
25. 사용자 목록에서 이전에 정책을 추가한 사용자를 검색합니다.
26. 해당 사용자를 클릭합니다.
27. **Permissions** 탭을 선택합니다.
28. **Permissions policies** 섹션에서 `AssumeS3ReadOnlyRolePolicy`를 찾습니다.
29. `AssumeS3ReadOnlyRolePolicy` 왼쪽의 체크박스를 선택합니다.

> [!NOTE]
> 체크박스를 선택하면 체크 표시가 나타나고, 상단의 [[Remove]] 버튼이 활성화됩니다.

30. [[Remove]] 버튼을 클릭합니다.
31. 확인 창이 나타나면 [[Remove]] 버튼을 다시 클릭합니다.
32. 화면 상단에 녹색 배너로 "Policy removed successfully"라는 성공 메시지가 표시됩니다.
33. **Permissions policies** 섹션에서 `AssumeS3ReadOnlyRolePolicy`가 더 이상 표시되지 않는지 확인합니다.

### 단계 3: AWS CloudFormation 스택 삭제

34. AWS CloudFormation 콘솔로 이동합니다.
35. 왼쪽 메뉴에서 **Stacks**를 선택합니다.
36. `week2-2-iam-role-stack` 스택을 선택합니다.
37. [[Delete]] 버튼을 클릭합니다.
38. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
39. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 태스크 0에서 생성한 AWS IAM 사용자(lab-user), Access Key, Amazon S3 버킷이 자동으로 삭제됩니다.

### 단계 4: 삭제 확인

모든 리소스가 삭제되었는지 확인합니다.

40. Tag Editor로 이동합니다.
41. **Regions**에서 `All regions`를 선택합니다.
42. **Resource types**에서 `All supported resource types`를 선택합니다.
43. **Tags** 섹션에서 다음 태그를 입력합니다:
   - **Tag key**: `Week`
   - **Optional tag value**: `2-2`
44. [[Search resources]] 버튼을 클릭합니다.
45. 검색 결과가 비어있는지 확인합니다.

> [!NOTE]
> 리소스가 삭제되면 태그도 함께 제거되므로 Tag Editor에서 검색 결과가 비어있으면 정상적으로 삭제된 것입니다. AWS IAM 역할은 Tag Editor에서 검색되지 않을 수 있으므로, AWS CloudFormation 스택으로 생성하지 않은 AWS IAM 역할이 있다면 AWS IAM 콘솔에서 직접 삭제하는 것을 권장합니다.

> [!SUCCESS]
> 검색 결과가 비어있으면 모든 리소스가 정상적으로 삭제되었습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS IAM 역할](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles.html)
- [AssumeRole API](https://docs.aws.amazon.com/ko_kr/STS/latest/APIReference/API_AssumeRole.html)
- [임시 보안 자격 증명](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_temp.html)

## 📚 참고: AWS IAM 역할 및 AssumeRole 개념

### AWS IAM 역할 vs AWS IAM 사용자

**AWS IAM 사용자:**

- 장기 자격증명(Access Key, Secret Key)을 가집니다
- 특정 개인이나 애플리케이션에 할당됩니다
- 자격증명이 유출되면 보안 위험이 높습니다

**AWS IAM 역할:**

- 임시 자격증명을 제공합니다
- 여러 주체(사용자, 서비스, 계정)가 맡을 수 있습니다
- 자격증명이 자동으로 만료되어 보안이 강화됩니다

### 신뢰 정책(Trust Policy)

**목적:**

- 누가 이 역할을 맡을 수 있는지 정의합니다
- Principal 요소로 신뢰할 주체를 지정합니다

> [!NOTE]
> **root Principal 보안 모범 사례**: 실습에서는 편의상 `"AWS": "arn:aws:iam::123456789012:root"`를 사용했지만, 이는 해당 계정의 모든 AWS IAM 엔티티가 역할을 맡을 수 있음을 의미합니다 (적절한 권한이 있는 경우). 프로덕션 환경에서는 특정 사용자나 역할의 ARN을 지정하는 것이 보안 모범 사례입니다.
>
> 예: `"AWS": "arn:aws:iam::123456789012:user/specific-user"`

**예시:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 권한 정책(Permission Policy)

**목적:**

- 역할이 무엇을 할 수 있는지 정의합니다
- AWS 관리형 정책 또는 사용자 지정 정책을 연결합니다

**차이점:**

- 신뢰 정책: "누가" 역할을 맡을 수 있는가
- 권한 정책: 역할이 "무엇을" 할 수 있는가

### AssumeRole 프로세스

**1단계: 역할 맡기 요청**

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/MyRole \
  --role-session-name my-session
```

**2단계: 임시 자격증명 수신**

- AccessKeyId (ASIA로 시작 - 임시 자격증명)
- SecretAccessKey
- SessionToken
- Expiration (기본 1시간, 최대 12시간)

> [!NOTE]
> **ASIA vs AKIA 차이**: 임시 자격증명의 Access Key는 `ASIA`로 시작하고, 장기 자격증명(AWS IAM 사용자)은 `AKIA`로 시작합니다. 이를 통해 자격증명 유형을 쉽게 구분할 수 있습니다.

**3단계: 임시 자격증명 사용**

- 환경 변수로 설정하거나
- AWS CLI 프로파일로 구성하거나
- SDK에서 직접 사용합니다

### 사용 사례(Use Cases)

**Cross-Account Access:**

- 다른 AWS 계정의 리소스에 접근할 때 사용합니다
- 계정 간 권한을 안전하게 위임합니다

**Amazon EC2 인스턴스 역할:**

- Amazon EC2 인스턴스가 자동으로 역할을 맡습니다
- 인스턴스 메타데이터에서 임시 자격증명을 가져옵니다

**AWS Lambda 실행 역할:**

- AWS Lambda 함수가 실행될 때 자동으로 역할을 맡습니다
- 함수가 필요한 AWS 서비스에 접근할 수 있습니다

**임시 권한 상승:**

- 일반 사용자가 특정 작업을 위해 임시로 높은 권한을 얻습니다
- MFA를 요구하여 보안을 강화할 수 있습니다

### 보안 모범 사례(Security Best Practices)

**최소 권한 원칙:**

- 역할에 필요한 최소한의 권한만 부여합니다
- 와일드카드(\*) 사용을 최소화합니다

**세션 시간 제한:**

- 짧은 세션 시간을 설정합니다 (기본 1시간)
- 장시간 작업이 필요한 경우에만 연장합니다

**MFA 요구:**

- 민감한 작업을 수행하는 역할에는 MFA를 요구합니다
- Condition 요소에 `aws:MultiFactorAuthPresent`를 사용합니다

**외부 ID 사용:**

- 제3자가 역할을 맡을 때 External ID를 사용합니다
- Confused Deputy 문제를 방지합니다

> [!NOTE]
> **Confused Deputy 문제**: 제3자 서비스가 고객의 역할을 맡을 때, 악의적인 사용자가 다른 고객의 리소스에 접근하도록 속일 수 있는 보안 문제입니다. External ID를 사용하면 이를 방지할 수 있습니다. 자세한 내용은 [AWS 문서](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html)를 참조합니다.
