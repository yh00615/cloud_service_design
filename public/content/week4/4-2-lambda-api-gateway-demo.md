---
title: 'Amazon API Gateway 인증 구성'
week: 4
session: 2
awsServices:
  - AWS Lambda
  - Amazon API Gateway
  - Amazon Cognito
learningObjectives:
  - Amazon Cognito User Pool을 생성하고 구성할 수 있습니다.
  - Amazon API Gateway Authorizer를 생성하고 메서드에 연결할 수 있습니다.
  - Amazon Cognito 사용자를 생성하고 인증 토큰을 획득할 수 있습니다.
  - 인증된 API 요청을 테스트하고 검증할 수 있습니다.

prerequisites:
  - Week 3 Amazon VPC 및 네트워킹 이해.
  - REST API 기본 개념 이해.
---

이 실습에서는 QuickTable 레스토랑 예약 시스템의 백엔드 API에 사용자 인증을 추가합니다. Amazon Cognito User Pool을 생성하여 사용자 등록 및 로그인 시스템을 구축하고, Amazon API Gateway Authorizer를 설정하여 JWT 토큰 기반 인증을 구현합니다. 인증된 사용자만 자신의 예약 데이터에 접근할 수 있도록 보호합니다.

> [!NOTE]
> 이 실습에서는 Amazon API Gateway, AWS Lambda, Amazon DynamoDB 등 사전 인프라가 AWS CloudFormation 템플릿으로 제공됩니다. 학생이 직접 수행하는 것은 Amazon Cognito 생성, Authorizer 설정, 인증 테스트입니다.
>
> **리전**: 이 실습은 `ap-northeast-2` (서울) 리전에서 진행됩니다.

> [!DOWNLOAD]
> [week4-2-quicktable-api-lab.zip](/files/week4/week4-2-quicktable-api-lab.zip)
>
> - `week4-2-quicktable-api-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB, AWS Lambda, Amazon API Gateway 자동 생성)
> - `create_reservation.py` - 예약 생성 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
> - `list_reservations.py` - 예약 조회 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week4-2-quicktable-api-lab.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 서버리스 API 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

**Amazon DynamoDB 테이블: Reservations**

- **파티션 키**: `userId` (String) - Amazon Cognito 사용자 ID
- **정렬 키**: `reservationId` (String) - UUID 형식 예약 ID
- **속성**: restaurantName, date, time, partySize, phoneNumber, status, createdAt

**AWS Lambda 함수: CreateReservation**

- **트리거**: Amazon API Gateway POST /reservations
- **입력 파라미터**: restaurantName, date, time, partySize, phoneNumber
- **자동 생성**: userId (Amazon Cognito 토큰에서 추출), reservationId (UUID), status (pending), createdAt
- **권한**: Amazon DynamoDB PutItem

**AWS Lambda 함수: GetReservations**

- **트리거**: Amazon API Gateway GET /reservations
- **동작**: userId 기반으로 해당 사용자의 예약만 조회
- **권한**: Amazon DynamoDB Query

**Amazon API Gateway: QuickTableAPI**

- **리소스**: /reservations
- **메서드**: POST, GET
- **통합**: AWS Lambda 프록시 통합 (AWS Lambda 함수와 연결)
- **인증**: 없음 (태스크 3에서 Authorizer 추가)

**AWS IAM 역할: AWS Lambda 실행 역할**

- **권한**: Amazon DynamoDB 접근, Amazon CloudWatch Logs 작성

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week4-2-quicktable-api-lab.zip` 파일의 압축을 해제합니다.
2. `week4-2-quicktable-api-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Choose a stack creation method**에서 `With new resources (standard)`를 선택합니다.
6. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
7. **Specify template**에서 `Upload a template file`을 선택합니다.
8. [[Choose file]] 버튼을 클릭한 후 `week4-2-quicktable-api-lab.yaml` 파일을 선택합니다.
9. [[Next]] 버튼을 클릭합니다.
10. **Stack name**에 `week4-2-quicktable-api-lab-stack`을 입력합니다.
11. **Parameters** 섹션에서 기본값을 유지합니다.
12. [[Next]] 버튼을 클릭합니다.
13. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
14. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-2`     |
| `CreatedBy` | `Student` |

15. [[Next]] 버튼을 클릭합니다.
16. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
17. [[Next]] 버튼을 클릭합니다.
18. **Review** 페이지에서 설정을 확인합니다.
19. [[Submit]] 버튼을 클릭합니다.
20. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

21. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
22. **Outputs** 탭을 선택합니다.
23. 출력값들을 확인하고 메모장에 복사합니다:
    - `ApiGatewayInvokeUrl`: Amazon API Gateway Invoke URL (예: https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod)

> [!IMPORTANT]
> 이 출력값은 태스크 4.1에서 환경 변수로 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon Cognito User Pool 생성

이 태스크에서는 Amazon Cognito User Pool을 생성하여 사용자 인증 시스템을 구축합니다.

> [!CONCEPT] Amazon Cognito User Pool
> Amazon Cognito User Pool은 사용자 등록, 로그인, 비밀번호 관리 등의 인증 기능을 제공하는 완전 관리형 서비스입니다. 이메일 기반 로그인, 비밀번호 정책, 사용자 자가 등록 등을 설정할 수 있으며, App Client를 통해 애플리케이션에서 User Pool에 접근할 수 있습니다.

### 태스크 1.1: User Pool 생성 시작 및 로그인 설정

24. AWS Management Console 상단 검색창에 `Cognito`을 입력하고 선택합니다.
25. [[Create user pool]] 버튼을 클릭합니다.
26. **Amazon Cognito user pool sign-in options**에서 `Email`을 체크합니다.
27. [[Next]] 버튼을 클릭합니다.

### 태스크 1.2: 보안 설정

> [!IMPORTANT]
> **Amazon Cognito 콘솔 UI 변경 안내:**
>
> 이 가이드는 **New experience (2024년 이후 기본)** 기준으로 작성되었습니다.
>
> **New experience (2024년 이후 기본):**
>
> - 단계별로 설정을 진행하며, 각 섹션이 명확히 구분되어 있습니다.
> - 이 가이드의 단계를 그대로 따라하면 됩니다.
>
> **Legacy experience를 사용하는 경우:**
>
> - 모든 설정이 한 페이지에 표시됩니다.
> - 각 섹션을 찾아 동일한 설정을 적용하면 됩니다.

28. **Password policy**에서 `Amazon Cognito defaults`를 선택합니다.
29. **Multi-factor authentication**에서 `No MFA`를 선택합니다.
30. **User account recovery**는 기본값을 유지합니다.
31. [[Next]] 버튼을 클릭합니다.

💡 **참고**: 실습 환경에서는 MFA를 비활성화하지만, 프로덕션 환경에서는 보안을 위해 활성화하는 것이 권장됩니다.

### 태스크 1.3: 사용자 등록 설정

> [!IMPORTANT]
> **Amazon Cognito 콘솔 UI 변경 안내:**
>
> 이 가이드는 **New experience (2024년 이후 기본)** 기준으로 작성되었습니다.
>
> **New experience (2024년 이후 기본):**
>
> - **Self-service sign-up** 섹션에서 `Enable self-registration`을 체크합니다.
>
> **Legacy experience를 사용하는 경우:**
>
> - **Sign-up experience** 섹션에서 `Allow users to sign themselves up`을 체크합니다.

32. **Self-service sign-up**에서 `Enable self-registration`을 체크합니다.
33. **Attribute verification and user account confirmation**은 기본값을 유지합니다.
34. **Required attributes**에서 `name`을 체크합니다.
35. [[Next]] 버튼을 클릭합니다.

### 태스크 1.4: 이메일 및 User Pool 생성

36. **Email**에서 `Send email with Amazon Cognito`를 선택합니다.
37. [[Next]] 버튼을 클릭합니다.
38. **User pool name**에 `QuickTableUserPool`을 입력합니다.
39. **Hosted authentication pages**는 체크하지 않습니다.

> [!IMPORTANT]
> **Hosted authentication pages 옵션 위치:**
>
> **New experience (2024년 이후 기본):**
>
> - **Hosted authentication pages** 체크박스가 User Pool 이름 입력 섹션 아래에 있습니다.
> - 이 옵션을 체크하지 않으면 Amazon Cognito Hosted UI가 생성되지 않습니다.
>
> **Legacy experience를 사용하는 경우:**
>
> - **App integration** 섹션에서 `Use the Amazon Cognito Hosted UI` 옵션을 찾습니다.
> - 이 옵션을 체크하지 않습니다.
>
> 이 실습에서는 Hosted UI를 사용하지 않으므로 체크하지 않습니다.

40. **Initial app client** 섹션에서 다음을 설정합니다:
	- **App client name**에 `QuickTableAppClient`를 입력합니다.
	- **Client secret**에서 `Don't generate a client secret`를 선택합니다.
41. 아래로 스크롤하여 **Advanced app client settings** 섹션을 확장합니다.
42. **Authentication flows** 섹션에서 `ALLOW_USER_PASSWORD_AUTH`를 체크합니다.

> [!IMPORTANT]
> **ALLOW_USER_PASSWORD_AUTH 설정 위치:**
>
> 이 가이드는 **New experience (2024년 이후 기본)** 기준으로 작성되었습니다.
>
> **New experience (2024년 이후 기본):**
>
> 1. User Pool 생성 마지막 단계에서 **Advanced app client settings** 섹션을 확장합니다.
> 2. **Authentication flows** 섹션에서 `ALLOW_USER_PASSWORD_AUTH`를 체크합니다.
>
> **Legacy experience를 사용하는 경우:**
>
> 1. User Pool 생성 후 **App integration** 탭을 선택합니다.
> 2. **App clients and analytics** 섹션에서 App Client를 선택합니다.
> 3. [[Edit]] 버튼을 클릭합니다.
> 4. **Authentication flows** 섹션에서 `ALLOW_USER_PASSWORD_AUTH`를 체크합니다.
>
> 이 설정을 활성화하지 않으면 태스크 4에서 `initiate-auth` 명령어가 "USER_PASSWORD_AUTH flow not enabled" 오류로 실패합니다.

43. 아래로 스크롤하여 **Tags - optional** 섹션을 확장합니다.
44. [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-2`     |
| `CreatedBy` | `Student` |

45. [[Next]] 버튼을 클릭합니다.
46. 설정을 검토한 후 [[Create user pool]] 버튼을 클릭합니다.

✅ **태스크 완료**: Amazon Cognito User Pool이 생성되었습니다.

## 태스크 2: User Pool ID 및 Client ID 확인

이 태스크에서는 생성된 Amazon Cognito User Pool의 ID와 App Client ID를 확인하여 Amazon API Gateway Authorizer 설정에 사용할 수 있도록 준비합니다.

47. Amazon Cognito 콘솔의 User Pool 목록에서 `QuickTableUserPool`을 클릭합니다.
48. **User pool overview**에서 **User pool ID**를 복사하여 메모장에 저장합니다.
49. **App integration** 탭을 선택합니다.
50. **App clients and analytics** 섹션에서 `QuickTableAppClient`를 선택합니다.
51. **Client ID**를 복사하여 메모장에 저장합니다.

> [!TIP]
> 이 두 값을 메모장에 저장합니다. 이후 실습에서 동일한 값을 계속 사용합니다.

✅ **태스크 완료**: User Pool ID와 Client ID가 확인되었습니다.

## 태스크 3: Amazon API Gateway Authorizer 생성 및 메서드 연결

이 태스크에서는 Amazon API Gateway에 Amazon Cognito Authorizer를 설정하고 POST 및 GET 메서드에 연결하여 인증된 사용자만 API에 접근할 수 있도록 보호합니다.

> [!CONCEPT] Amazon API Gateway Authorizer
> Amazon Cognito Authorizer는 API 요청의 Authorization 헤더에서 JWT 토큰을 자동으로 검증합니다. 토큰 검증에는 Amazon Cognito User Pool의 공개 키가 사용되며, 토큰의 서명, 만료 시간, 발급자 등을 확인합니다. 유효한 토큰인 경우에만 AWS Lambda 함수를 호출하고, 사용자 정보를 AWS Lambda 함수에 전달합니다.

### 태스크 3.1: Authorizer 생성

52. 상단 검색창에 `API Gateway`을 입력하고 선택합니다.
53. API 목록에서 `Week4-2-QuickTableAPI`를 선택합니다.
54. 왼쪽 메뉴에서 **Authorizers**를 선택합니다.
55. [[Create authorizer]] 버튼을 클릭합니다.
56. **Authorizer name**에 `CognitoAuthorizer`를 입력합니다.
57. **Type**에서 `Amazon Cognito`를 선택합니다.
58. **Amazon Cognito user pool**에서 `QuickTableUserPool`을 선택합니다.
59. **Token source**에 `Authorization`을 입력합니다.
60. [[Create authorizer]] 버튼을 클릭합니다.

> [!NOTE]
> Token source는 API 요청에서 JWT 토큰을 추출할 HTTP 헤더 이름입니다. "Authorization" 헤더에서 토큰을 가져옵니다.

### 태스크 3.2: POST 메서드에 Authorizer 연결

61. 왼쪽 메뉴에서 **Resources**를 선택합니다.
62. `/reservations` 리소스를 확장합니다.
63. `POST` 메서드를 선택합니다.
64. **Method Request** 섹션에서 [[Edit]] 버튼을 클릭합니다.

> [!TIP]
> **Method Request Edit 버튼 위치**: POST 메서드를 선택하면 오른쪽에 메서드 실행 흐름이 표시됩니다. **Method Request** 박스 오른쪽 상단에 [[Edit]] 버튼이 있습니다. 만약 보이지 않으면 페이지를 아래로 스크롤하거나 브라우저 창을 확대합니다.

65. **Authorization**에서 `CognitoAuthorizer`를 선택합니다.
66. [[Save]] 버튼을 클릭합니다.

### 태스크 3.3: GET 메서드에 Authorizer 연결

67. `/reservations` 리소스에서 `GET` 메서드를 선택합니다.
68. **Method Request** 섹션에서 [[Edit]] 버튼을 클릭합니다.

> [!TIP]
> **Method Request Edit 버튼 위치**: GET 메서드를 선택하면 오른쪽에 메서드 실행 흐름이 표시됩니다. **Method Request** 박스 오른쪽 상단에 [[Edit]] 버튼이 있습니다. 만약 보이지 않으면 페이지를 아래로 스크롤하거나 브라우저 창을 확대합니다.

69. **Authorization**에서 `CognitoAuthorizer`를 선택합니다.
70. [[Save]] 버튼을 클릭합니다.

### 태스크 3.4: API 재배포

71. [[Deploy API]] 버튼을 클릭합니다.

> [!TIP]
> **Deploy API 버튼 위치**: 화면 오른쪽 상단에 주황색 [[Deploy API]] 버튼이 있습니다. Resources 페이지에서 메서드를 선택한 상태에서 보입니다. 만약 보이지 않으면 페이지를 위로 스크롤하거나 브라우저 창을 확대합니다.

72. **Stage**에서 `prod`를 선택합니다.
73. [[Deploy]] 버튼을 클릭합니다.

> [!IMPORTANT]
> Amazon API Gateway는 변경 사항을 스테이지에 배포해야 적용됩니다. Authorizer를 연결한 후 반드시 재배포해야 인증이 작동합니다.

✅ **태스크 완료**: API 메서드에 인증이 설정되고 재배포되었습니다.

## 태스크 4: Amazon Cognito 사용자 생성 및 인증 토큰 획득

이 태스크에서는 Amazon Cognito User Pool에 테스트 사용자를 생성하고 인증 토큰을 획득합니다.

> [!CONCEPT] JWT 토큰 기반 인증
> Amazon Cognito는 사용자 로그인 시 3가지 JWT 토큰을 발급합니다:
>
> - **IdToken**: 사용자 정보를 포함하며, Amazon API Gateway Authorizer에서 사용됩니다.
> - **AccessToken**: 리소스 접근 권한을 나타냅니다.
> - **RefreshToken**: 만료된 토큰을 갱신하는 데 사용됩니다.
>
> API 호출 시 Authorization 헤더에 IdToken을 포함하면, Amazon API Gateway Authorizer가 자동으로 검증하고 AWS Lambda 함수에 사용자 정보를 전달합니다.

### 태스크 4.1: AWS CloudShell 환경 변수 설정

74. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.
75. CloudShell이 시작될 때까지 기다립니다.
76. 다음 명령어로 환경 변수를 설정합니다:

```bash
# Client ID 설정 (태스크 2에서 복사한 값으로 변경)
export CLIENT_ID="YOUR_CLIENT_ID"

# User Pool ID 설정 (태스크 2에서 복사한 값으로 변경)
export USER_POOL_ID="YOUR_USER_POOL_ID"

# API URL 설정 (태스크 0에서 복사한 Invoke URL로 변경)
export API_URL="https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod"

# 테스트 이메일 설정 (공유 환경에서 충돌 방지)
export TEST_EMAIL="test@example.com"
```

> [!IMPORTANT]
> `YOUR_CLIENT_ID`, `YOUR_USER_POOL_ID`, `API_URL`을 실제 값으로 변경합니다.
> 환경 변수를 사용하면 이후 명령어에서 긴 값을 반복 입력하지 않아도 됩니다.
>
> **공유 환경에서 이메일 충돌 방지**: 여러 학생이 동일한 AWS 계정을 공유하는 경우, `TEST_EMAIL` 환경 변수를 고유한 값으로 변경합니다 (예: `test-yourname@example.com`).

> [!WARNING]
> **CloudShell 세션 타임아웃 안내**: CloudShell 세션이 약 20분 동안 비활성 상태이면 자동으로 종료됩니다.
> 세션이 재시작된 경우, 이 태스크의 환경 변수 설정과 태스크 4.3의 토큰 획득을 다시 수행해야 합니다.

77. 환경 변수가 올바르게 설정되었는지 확인합니다:

```bash
echo "Client ID: $CLIENT_ID"
echo "User Pool ID: $USER_POOL_ID"
echo "API URL: $API_URL"
echo "Test Email: $TEST_EMAIL"
```

### 태스크 4.2: 사용자 생성 및 확인

78. 다음 명령어로 사용자를 생성합니다:

```bash
aws cognito-idp sign-up \
  --client-id $CLIENT_ID \
  --username $TEST_EMAIL \
  --password Test1234! \
  --user-attributes Name=name,Value=TestUser \
  --region ap-northeast-2
```

> [!OUTPUT]
>
> ```json
> {
>   "UserConfirmed": false,
>   "UserSub": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
> }
> ```

> [!WARNING]
> 이 실습에서는 학습 목적으로 비밀번호를 평문으로 사용합니다. 프로덕션 환경에서는 절대 비밀번호를 평문으로 노출하지 않으며, 환경 변수나 AWS Secrets Manager를 사용하여 안전하게 관리합니다.

> [!NOTE]
> **Amazon Cognito 기본 비밀번호 정책**: 최소 8자, 대문자·소문자·숫자·특수문자 포함이 필요합니다.
> `Test1234!`는 이 정책을 충족합니다 (대문자 T, 소문자 est, 숫자 1234, 특수문자 !).

> [!NOTE]
> **공유 환경에서 이메일 충돌 가능성**: 여러 학생이 동일한 AWS 계정을 공유하는 경우, 동일한 이메일 주소로 사용자를 생성하면 "UsernameExistsException" 오류가 발생할 수 있습니다. 이 경우 태스크 4.1에서 `TEST_EMAIL` 환경 변수를 고유한 값으로 변경합니다:
>
> - `export TEST_EMAIL="test-yourname@example.com"` (예: `test-john@example.com`)
> - `export TEST_EMAIL="test-123@example.com"` (임의의 숫자 추가)
>
> 환경 변수를 변경한 후 이 태스크의 명령어를 다시 실행하면 고유한 이메일로 사용자가 생성됩니다.

79. 사용자를 확인합니다:

```bash
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id $USER_POOL_ID \
  --username $TEST_EMAIL \
  --region ap-northeast-2
```

> [!NOTE]
> 이 명령어는 성공 시 출력이 없습니다. 오류 메시지가 표시되지 않으면 정상적으로 완료된 것입니다.

> [!NOTE]
> `admin-confirm-sign-up` 명령어는 이메일 인증 단계를 건너뛰고 사용자를 즉시 활성화합니다. 실습 환경에서는 편의를 위해 이메일 인증을 생략하지만, 프로덕션 환경에서는 이메일 인증을 통해 사용자 신원을 확인하는 것이 권장됩니다.

### 태스크 4.3: 인증 토큰 획득

80. 다음 명령어로 로그인하여 인증 토큰을 획득하고 환경 변수에 저장합니다:

```bash
export ID_TOKEN=$(aws cognito-idp initiate-auth \
  --client-id $CLIENT_ID \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=$TEST_EMAIL,PASSWORD=Test1234! \
  --region ap-northeast-2 \
  --query 'AuthenticationResult.IdToken' \
  --output text)
```

81. IdToken이 올바르게 저장되었는지 확인합니다:

```bash
echo "ID Token (first 50 characters): ${ID_TOKEN:0:50}..."
```

> [!OUTPUT]
>
> ```
> ID Token (first 50 characters): eyJraWQiOiJxxx...
> ```

> [!NOTE]
> IdToken은 매우 긴 문자열(수백~수천 자)입니다. 환경 변수 `$ID_TOKEN`에 저장하면 이후 API 호출 시 편리하게 사용할 수 있습니다.

> [!WARNING]
> **IdToken 만료 안내**: IdToken은 기본적으로 1시간 후 만료됩니다.
> 태스크 5에서 "The incoming token has expired" 오류가 발생하면, 이 태스크의 `initiate-auth` 명령어를 다시 실행하여 새 토큰을 획득합니다.

✅ **태스크 완료**: 사용자가 생성되고 인증 토큰을 획득했습니다.

## 태스크 5: 인증된 API 호출 테스트

이 태스크에서는 Amazon Cognito에서 받은 IdToken을 사용하여 보호된 API를 호출하고, 인증이 정상적으로 작동하는지 확인합니다.

### 태스크 5.1: 예약 생성 테스트

82. CloudShell에서 다음 명령어를 실행하여 예약을 생성합니다:

```bash
curl -X POST $API_URL/reservations \
  -H "Authorization: $ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "강남 맛집", "date": "2026-03-20", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}'
```

> [!NOTE]
> **날짜 형식 안내**: `"date": "2026-03-20"` 부분을 실제 날짜로 변경합니다.
>
> - 예: `"date": "2026-04-15"` (2026년 4월 15일)
> - 현재 날짜 이후의 날짜를 입력하는 것이 자연스럽습니다.

> [!TIP]
> JSON 출력을 보기 좋게 포맷팅하려면 `| python3 -m json.tool`을 추가합니다:
>
> ```bash
> curl -X POST $API_URL/reservations \
>   -H "Authorization: $ID_TOKEN" \
>   -H "Content-Type: application/json" \
>   -d '{"restaurantName": "강남 맛집", "date": "2026-03-20", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}' \
>   | python3 -m json.tool
> ```

> [!NOTE]
> 환경 변수 `$API_URL`과 `$ID_TOKEN`을 사용하므로 값을 직접 입력할 필요가 없습니다.

> [!OUTPUT]
>
> ```json
> {
>   "userId": "<cognito-user-id>",
>   "reservationId": "<uuid-format>",
>   "restaurantName": "강남 맛집",
>   "date": "<입력한 날짜>",
>   "time": "18:00",
>   "partySize": 4,
>   "phoneNumber": "010-1234-5678",
>   "status": "pending",
>   "createdAt": "<current-timestamp>"
> }
> ```

> [!NOTE]
> **출력값 설명**:
>
> - `userId`: Amazon Cognito에서 자동으로 생성된 고유 사용자 ID (UUID 형식)
> - `reservationId`: 자동 생성된 예약 ID (UUID 형식, 예: `550e8400-e29b-41d4-a716-446655440000`)
> - `date`: 요청 시 입력한 날짜가 그대로 반환됩니다 (예: `2026-03-20`)
> - `createdAt`: 실제 실행 시점의 타임스탬프 (ISO 8601 형식, 예: `2026-02-18T05:30:00.123Z`)
>
> `date`와 `createdAt`은 실행 시점에 따라 달라지므로 예상 출력과 다를 수 있습니다.

### 태스크 5.2: 예약 목록 조회 테스트

83. 다음 명령어로 예약 목록을 조회합니다:

```bash
curl -X GET $API_URL/reservations \
  -H "Authorization: $ID_TOKEN"
```

> [!OUTPUT]
>
> ```json
> [
>   {
>     "userId": "<cognito-user-id>",
>     "reservationId": "<uuid-format>",
>     "restaurantName": "강남 맛집",
>     "date": "<입력한 날짜>",
>     "time": "18:00",
>     "partySize": 4,
>     "phoneNumber": "010-1234-5678",
>     "status": "pending",
>     "createdAt": "<current-timestamp>"
>   }
> ]
> ```

> [!NOTE]
> **출력값 설명**:
>
> - `userId`: Amazon Cognito에서 자동으로 생성된 고유 사용자 ID (UUID 형식)
> - `reservationId`: 자동 생성된 예약 ID (UUID 형식, 예: `550e8400-e29b-41d4-a716-446655440000`)
> - `date`: 태스크 5.1에서 입력한 날짜가 그대로 반환됩니다 (예: `2026-03-20`)
> - `createdAt`: 실제 실행 시점의 타임스탬프 (ISO 8601 형식, 예: `2026-02-18T05:30:00.123Z`)
>
> `date`와 `createdAt`은 실행 시점에 따라 달라지므로 예상 출력과 다를 수 있습니다.

### 태스크 5.3: 인증 없이 API 호출 테스트

84. Authorization 헤더 없이 API를 호출합니다:

```bash
curl -X GET $API_URL/reservations
```

> [!OUTPUT]
>
> ```json
> { "message": "Unauthorized" }
> ```

> [!NOTE]
> Authorization 헤더가 없으면 Amazon API Gateway Authorizer가 요청을 거부하고 401 Unauthorized 응답을 반환합니다.

### 태스크 5.4: 잘못된 토큰으로 API 호출 테스트

85. 잘못된 토큰으로 API를 호출합니다:

```bash
curl -X GET $API_URL/reservations \
  -H "Authorization: invalid.token.here"
```

> [!OUTPUT]
>
> ```json
> { "message": "Unauthorized" }
> ```

> [!NOTE]
> Amazon API Gateway Authorizer는 토큰의 서명을 Amazon Cognito User Pool의 공개 키로 검증합니다. 잘못된 토큰은 검증에 실패하므로 요청이 거부됩니다.

✅ **태스크 완료**: 인증된 API 호출이 정상적으로 작동합니다.

## 마무리

다음을 성공적으로 수행했습니다:

- QuickTable 레스토랑 예약 시스템의 백엔드 API를 구축했습니다
- Amazon Cognito User Pool을 생성하고 사용자 인증 시스템을 구축했습니다
- Amazon API Gateway Authorizer를 설정하여 JWT 토큰 기반 인증을 구현했습니다
- 인증된 사용자만 자신의 예약 데이터에 접근할 수 있도록 보호했습니다
- 예약 생성 및 조회 API를 테스트하여 인증 흐름을 검증했습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

---

## 1단계: Tag Editor로 생성된 리소스 확인

실습에서 생성한 모든 리소스를 Tag Editor로 확인합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `4-2`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 이 실습에서 생성한 AWS Lambda, Amazon DynamoDB, Amazon API Gateway 등의 리소스가 표시됩니다. Amazon Cognito User Pool과 Amazon CloudWatch Logs는 태그가 없어 표시되지 않지만, 다음 단계에서 삭제합니다.

> [!TIP]
> Tag Editor는 리소스 확인 용도로만 사용하며, 실제 삭제는 다음 단계에서 수행합니다.

---

## 2단계: 리소스 삭제

다음 두 가지 방법 중 하나를 선택하여 리소스를 삭제할 수 있습니다.

### 옵션 1: AWS 콘솔에서 수동 삭제 (권장)

> [!TIP]
> AWS 관리 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 권장합니다.
>
> AWS CLI 명령어에 익숙한 경우 아래 [옵션 2](#option-2)를 사용하면 더 빠르게 삭제할 수 있습니다.

**Amazon Cognito User Pool 삭제**

7. Amazon Cognito 콘솔로 이동합니다.
8. User Pool 목록에서 `QuickTableUserPool`을 선택합니다.
9. [[Delete]] 버튼을 클릭합니다.
10. 확인 창에 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon Cognito User Pool 삭제는 즉시 완료됩니다.

**Amazon CloudWatch Log Groups 삭제**

11. Amazon CloudWatch 콘솔로 이동합니다.
12. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
13. 다음 Log Group들을 선택합니다:
	- `/aws/lambda/Week4-2-CreateReservation`
	- `/aws/lambda/Week4-2-GetReservations`
14. **Actions** > `Delete log group(s)`를 선택합니다.
15. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Log Groups는 AWS Lambda 함수 실행 시 자동 생성되며, AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동 삭제가 필요합니다.

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 위 [옵션 1](#option-1)을 참고합니다.

16. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
17. CloudShell이 열리면 다음 명령어를 실행합니다:

```bash
# Amazon Cognito User Pool 삭제
USER_POOL_ID=$(aws cognito-idp list-user-pools \
  --region ap-northeast-2 \
  --max-results 60 \
  --query 'UserPools[?Name==`QuickTableUserPool`].Id' \
  --output text)

if [ -n "$USER_POOL_ID" ]; then
  echo "삭제 중: Amazon Cognito User Pool $USER_POOL_ID"
  aws cognito-idp delete-user-pool \
    --region ap-northeast-2 \
    --user-pool-id $USER_POOL_ID
  echo "Amazon Cognito User Pool 삭제 완료"
else
  echo "삭제할 Amazon Cognito User Pool이 없습니다"
fi

# Amazon CloudWatch Log Groups 삭제
LOG_GROUPS=$(aws logs describe-log-groups \
  --region ap-northeast-2 \
  --log-group-name-prefix "/aws/lambda/Week4-2-" \
  --query 'logGroups[].logGroupName' \
  --output text)

if [ -n "$LOG_GROUPS" ]; then
  for LOG_GROUP in $LOG_GROUPS; do
    echo "삭제 중: $LOG_GROUP"
    aws logs delete-log-group \
      --region ap-northeast-2 \
      --log-group-name $LOG_GROUP
  done
  echo "Amazon CloudWatch Log Groups 삭제 완료"
else
  echo "삭제할 Amazon CloudWatch Log Groups가 없습니다"
fi
```

> [!NOTE]
> 스크립트는 Amazon Cognito User Pool과 Amazon CloudWatch Log Groups를 자동으로 찾아 삭제합니다. 삭제는 즉시 완료됩니다.

---

## 3단계: AWS CloudFormation 스택 삭제

마지막으로 AWS CloudFormation 스택을 삭제하여 나머지 모든 리소스를 정리합니다.

18. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
19. 스택 목록에서 `week4-2-quicktable-api-lab-stack` 스택을 검색합니다.
20. `week4-2-quicktable-api-lab-stack` 스택의 체크박스를 선택합니다.

> [!NOTE]
> 스택이 선택되면 체크박스에 체크 표시가 나타나고, 상단의 [[Delete]] 버튼이 활성화됩니다.

21. [[Delete]] 버튼을 클릭합니다.
22. 확인 창에서 [[Delete]] 버튼을 다시 클릭하여 삭제를 확인합니다.

> [!NOTE]
> 확인 후 스택 목록 페이지로 이동합니다.

23. `week4-2-quicktable-api-lab-stack` 스택의 **Status** 열을 확인합니다.

> [!NOTE]
> 스택 삭제가 시작되면 **Status**가 "DELETE_IN_PROGRESS"로 표시됩니다. AWS CloudFormation이 생성한 모든 리소스를 역순으로 삭제합니다.

24. 스택을 클릭하여 상세 페이지로 이동합니다.
25. **Events** 탭을 선택합니다.

> [!NOTE]
> **Events** 탭에는 리소스 삭제 과정이 실시간으로 표시됩니다. Amazon DynamoDB 테이블, AWS Lambda 함수, Amazon API Gateway, AWS IAM 역할 등이 순차적으로 삭제됩니다. 삭제에 3-5분이 소요됩니다.

26. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택이 완전히 삭제되면 스택 목록에서 사라집니다. 만약 "DELETE_FAILED"가 표시되면 **Events** 탭에서 오류 원인을 확인하고, Amazon DynamoDB 테이블을 수동으로 삭제한 후 스택 삭제를 다시 시도합니다.

27. 스택 목록 페이지로 돌아가서 `week4-2-quicktable-api-lab-stack` 스택이 목록에서 사라졌는지 확인합니다.

> [!NOTE]
> 스택이 목록에 표시되지 않으면 성공적으로 삭제된 것입니다.

---

## 4단계: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

28. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
29. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
30. **Regions**에서 `ap-northeast-2`를 선택합니다.
31. **Resource types**에서 `All supported resource types`를 선택합니다.
32. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `4-2`
33. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon Cognito User Pools](https://docs.aws.amazon.com/ko_kr/cognito/latest/developerguide/cognito-user-identity-pools.html)
- [Amazon API Gateway AWS Lambda Authorizers](https://docs.aws.amazon.com/ko_kr/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [JWT 토큰 구조](https://jwt.io/introduction)

## 📚 참고: Amazon Cognito 인증 아키텍처

### 인증 흐름

**1단계: 사용자 등록 및 확인**

- 사용자가 Amazon Cognito User Pool에 등록합니다.
- 이메일 인증 또는 관리자 확인을 통해 계정을 활성화합니다.

**2단계: 로그인 및 토큰 획득**

- 사용자가 이메일과 비밀번호로 로그인합니다.
- Amazon Cognito가 IdToken, AccessToken, RefreshToken을 발급합니다.

**3단계: API 호출**

- 클라이언트가 Authorization 헤더에 IdToken을 포함하여 API를 호출합니다.
- Amazon API Gateway Authorizer가 토큰을 자동으로 검증합니다.

**4단계: AWS Lambda 실행**

- 토큰이 유효하면 AWS Lambda 함수를 호출합니다.
- `event['requestContext']['authorizer']['claims']`에 사용자 정보가 포함됩니다.

**5단계: 사용자별 데이터 격리**

- AWS Lambda 함수가 Amazon Cognito 사용자 ID를 추출합니다.
- Amazon DynamoDB에서 해당 사용자의 데이터만 조회/수정합니다.

### JWT 토큰 구조

**IdToken 구성**:

- **Header**: 토큰 타입 및 서명 알고리즘 (RS256)
- **Payload**: 사용자 정보 (sub, email, name 등)
- **Signature**: Amazon Cognito User Pool의 RSA 프라이빗 키로 서명 (검증 시 Amazon Cognito가 공개하는 공개 키 사용)

**주요 Claim**:

- `sub`: Amazon Cognito 사용자 ID (고유 식별자)
- `email`: 사용자 이메일 주소
- `name`: 사용자 이름
- `exp`: 토큰 만료 시간 (Unix timestamp)
- `iss`: 토큰 발급자 (Amazon Cognito User Pool URL)

### 보안 모범 사례

**토큰 관리**:

- IdToken은 메모리(변수) 또는 HttpOnly 쿠키에 저장하는 것이 권장됩니다. LocalStorage/SessionStorage는 XSS 공격에 노출될 수 있어 보안에 취약합니다.
- 토큰 만료 시 RefreshToken을 사용하여 갱신합니다.
- HTTPS를 사용하여 토큰 전송 시 암호화합니다.

**User Pool 설정**:

- 프로덕션 환경에서는 MFA를 활성화합니다.
- 강력한 비밀번호 정책을 설정합니다.
- 계정 복구 옵션을 구성합니다.

**Amazon API Gateway 설정**:

- Authorizer 캐싱을 활성화하여 성능을 향상시킵니다 (기본 300초).
- CORS를 적절히 설정하여 허용된 도메인만 접근하도록 합니다.
- Amazon CloudWatch Logs를 활성화하여 인증 실패를 모니터링합니다.

> [!NOTE]
> **Authorizer 캐싱**: Amazon API Gateway는 기본적으로 Authorizer 결과를 300초(5분) 동안 캐싱합니다. 이는 동일한 토큰으로 반복 요청 시 Amazon Cognito 검증을 생략하여 성능을 향상시킵니다. 캐싱 설정은 이 실습 범위를 벗어나지만, 프로덕션 환경에서는 보안과 성능의 균형을 고려하여 TTL을 조정할 수 있습니다.
