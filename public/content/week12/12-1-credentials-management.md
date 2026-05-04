---
title: 'AWS Secrets Manager와 AWS Systems Manager를 활용한 자격증명 관리'
week: 12
session: 1
awsServices:
  - AWS Secrets Manager
  - AWS Systems Manager
  - AWS KMS
  - Amazon RDS
  - AWS Lambda
learningObjectives:
  - AWS Secrets Manager에 Amazon RDS 자격증명을 저장하고 자동 로테이션을 설정할 수 있습니다.
  - AWS Systems Manager Parameter Store와 AWS Secrets Manager의 차이점을 이해할 수 있습니다.
  - AWS Lambda 함수에서 AWS Secrets Manager와 AWS Systems Manager Parameter Store를 조회하고 Amazon RDS에 연결할 수 있습니다.
  - 자동 로테이션을 통해 비밀번호를 안전하게 관리할 수 있습니다.

prerequisites:
  - AWS IAM 기본 개념 이해
  - AWS Lambda 기본 사용 경험
  - 암호화 기본 개념 이해
---

이 실습에서는 AWS Secrets Manager의 핵심 기능인 **자동 로테이션**을 학습합니다. Amazon RDS MySQL 데이터베이스를 생성하고, AWS Secrets Manager에 자격증명을 저장한 후, 자동 로테이션을 설정하여 비밀번호를 주기적으로 변경합니다. AWS Lambda 함수에서 AWS Secrets Manager와 AWS Systems Manager Parameter Store를 조회하여 실제 데이터베이스에 연결하는 과정을 실습합니다.

> [!DOWNLOAD]
> [week12-1-secrets-manager-lab.zip](/files/week12/week12-1-secrets-manager-lab.zip)
>
> - `week12-1-secrets-manager-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon RDS, Amazon VPC, AWS Lambda 함수 자동 생성)
> - `lambda_function.py` - AWS Lambda 함수 코드 (참고용)
> - `lambda-iam-policy.json` - AWS Lambda 실행 역할 IAM 정책 (참고용)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation으로 Amazon RDS + AWS Lambda 자동 생성)
> - 태스크 5: AWS Lambda 함수 테스트 (이미 생성된 함수 사용)

> [!CONCEPT] 자격증명 관리 아키텍처
>
> 코드에 자격증명을 하드코딩하면 소스 코드 유출 시 보안 사고로 이어집니다. **중앙 집중식 자격증명 관리**는 이를 해결하는 핵심 아키텍처입니다.
>
> - **AWS Secrets Manager**: 데이터베이스 자격증명 등 민감 정보를 저장하고, **자동 로테이션**으로 비밀번호를 주기적으로 변경합니다.
> - **AWS Systems Manager Parameter Store**: 애플리케이션 설정값을 계층 구조(`/prod/app/config/`)로 관리하며, SecureString으로 암호화를 지원합니다.
> - **AWS KMS**: 두 서비스에서 저장하는 데이터를 암호화하는 키를 관리합니다.
>
> 애플리케이션은 런타임에 AWS Secrets Manager/AWS Systems Manager Parameter Store에서 자격증명을 조회하여 사용합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제**해야 합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 Amazon RDS MySQL 데이터베이스와 AWS Lambda 함수를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon RDS MySQL**: db.t3.micro 인스턴스
- **Amazon VPC**: 프라이빗 서브넷 2개
- **AWS Lambda 함수**: AWS Secrets Manager 및 AWS Systems Manager Parameter Store 조회, Amazon RDS 연결
- **AWS IAM 역할**: AWS Lambda 실행 역할 (AWS Secrets Manager, AWS Systems Manager Parameter Store, AWS KMS 권한 포함)
- **보안 그룹**: AWS Lambda → Amazon RDS 통신

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 생성)은 동일합니다.

1. 다운로드한 `week12-1-secrets-manager-lab.zip` 파일의 압축을 해제합니다.
2. `week12-1-secrets-manager-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

   <img src="/images/week12/12-1-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week12-1-secrets-manager-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week12-1-secrets-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `12-1` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)
    - **DBUsername**: `admin` (기본값 유지)
    - **DBPassword**: `TempPassword123!` (기본값 유지)

> [!NOTE]
> Parameters에서 설정한 태그 값(Project, Week, CreatedBy)은 모든 리소스에 자동으로 적용됩니다. 별도로 Tags 섹션에서 추가할 필요가 없습니다.

11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 10-15분이 소요됩니다 (Amazon RDS 인스턴스 포함). 상태가 "CREATE_IN_PROGRESS"에서 "CREATE_COMPLETE"로 변경될 때까지 기다립니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. **Outputs** 탭을 선택합니다.
19. 출력값들을 메모장에 복사합니다:
    - `DBEndpoint`: Amazon RDS 엔드포인트
    - `DBPort`: Amazon RDS 포트 (3306)
    - `DBUsername`: 데이터베이스 사용자 이름 (admin)
    - `LambdaFunctionName`: AWS Lambda 함수 이름

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: AWS KMS 키 생성

이 태스크에서는 AWS Secrets Manager와 AWS Systems Manager Parameter Store에서 사용할 암호화 키를 생성합니다.

20. 상단 검색창에 `KMS`을 입력하고 선택합니다.
21. 왼쪽 메뉴에서 **Customer managed keys**를 선택합니다.
22. [[Create key]] 버튼을 클릭합니다.

### Step 1: Configure key

23. **Key type**에서 `Symmetric`이 선택되어 있는지 확인합니다.
24. **Key usage**에서 `Encrypt and decrypt`가 선택되어 있는지 확인합니다.

> [!NOTE]
> **Advanced options**의 **Key material origin**은 `KMS - recommended`, **Regionality**는 `Single-region key`를 기본값으로 유지합니다.

25. [[Next]] 버튼을 클릭합니다.

### Step 2: Add labels

26. **Alias**에 `secrets-encryption-key`를 입력합니다.
27. **Description**에 `Encryption key for Secrets Manager and Parameter Store`를 입력합니다.
28. **Tags** 섹션에서 [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

29. [[Next]] 버튼을 클릭합니다.

### Step 3: Define key administrative permissions

30. **Key administrators** 섹션에서 본인의 AWS IAM 사용자를 선택합니다.
31. [[Next]] 버튼을 클릭합니다.

### Step 4: Define key usage permissions

32. **Key users** 섹션에서 AWS CloudFormation이 생성한 AWS Lambda 실행 역할을 선택합니다.
    - 검색창에 `week12-1`을 입력하여 `week12-1-lambda-secrets-role`을 찾아 선택합니다.
33. [[Next]] 버튼을 클릭합니다.

### Step 5: Edit key policy

> [!NOTE]
> 키 정책은 이전 단계에서 설정한 관리자와 사용자 권한이 자동으로 반영됩니다. 수정할 필요가 없습니다.

34. [[Next]] 버튼을 클릭합니다.

### Step 6: Review

35. 설정을 검토하고 [[Finish]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS KMS 키가 생성되었습니다.

## 태스크 2: AWS Secrets Manager에 Amazon RDS 자격증명 저장

이 태스크에서는 AWS Secrets Manager에 Amazon RDS 데이터베이스 자격증명을 저장합니다.

36. 상단 검색창에 `Secrets Manager`을 입력하고 선택합니다.
37. [[Store a new secret]] 버튼을 클릭합니다.
38. **Secret type**에서 `Credentials for Amazon RDS database`를 선택합니다.
39. **User name**에 `admin`을 입력합니다.
40. **Password**에 `LabPassword456!`을 입력합니다.

> [!NOTE]
> Amazon RDS 생성 시 설정한 비밀번호(`TempPassword123!`)와 다른 값을 입력합니다. 로테이션 후 비밀번호가 변경되었는지 확인하기 위해 의도적으로 다른 값을 사용합니다.

41. **Encryption key**에서 `secrets-encryption-key`를 선택합니다.
42. **Database**에서 AWS CloudFormation이 생성한 Amazon RDS 인스턴스를 선택합니다.
    - 인스턴스 ID: `week12-1-mysql-db`

43. [[Next]] 버튼을 클릭합니다.
44. **Secret name**에 `prod/db/mysql/credentials`를 입력합니다.
45. **Description**에 `Production MySQL database credentials`를 입력합니다.
46. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

47. [[Next]] 버튼을 클릭합니다.
48. **Automatic rotation** 토글을 활성화합니다.

> [!IMPORTANT]
> 자동 로테이션은 AWS Secrets Manager의 핵심 기능입니다. 비밀번호를 주기적으로 자동 변경하여 보안을 강화합니다.

49. **Rotation schedule** 섹션에서 다음을 설정합니다:
    - **Schedule expression builder**를 선택합니다.
    - **Time unit**에서 `Hours`를 선택합니다.
    - **Hours**에 `23`을 입력합니다.
    - **Window duration - optional**은 기본값(`4h`)을 유지합니다.
    - **Rotate immediately when the secret is stored** 체크박스가 선택되어 있는지 확인합니다.

> [!NOTE]
> 실습에서는 로테이션을 빠르게 확인하기 위해 23시간으로 설정합니다. 프로덕션 환경에서는 30일(720시간) 이상을 권장합니다.

50. **Rotation function** 섹션에서 다음을 설정합니다:
    - `Create a rotation function`을 선택합니다.
    - **Lambda rotation function** 이름에 `mysql-rotation-lambda`를 입력합니다.
    - **Rotation strategy**에서 `Single user`를 선택합니다.
    - **IAM permissions**에서 `Create default role`을 선택합니다.

> [!NOTE]
> AWS Secrets Manager가 함수 이름 앞에 `SecretsManager` 접두사를 자동으로 추가합니다. 최종 함수 이름은 `SecretsManagermysql-rotation-lambda`가 됩니다.
> `Create default role`을 선택하면 로테이션 함수에 필요한 AWS IAM 역할이 자동으로 생성됩니다.

51. [[Next]] 버튼을 클릭합니다.
52. 설정을 검토합니다.
53. [[Store]] 버튼을 클릭합니다.

> [!NOTE]
> 시크릿 생성 후 "AWS CloudFormation is setting up rotation resources, this can take up to two minutes to complete" 메시지가 표시됩니다. AWS Secrets Manager가 로테이션 AWS Lambda 함수를 자동으로 생성하고 있으며, **2분 정도 기다린 후** 페이지를 새로고침합니다.

✅ **태스크 완료**: Amazon RDS 자격증명이 저장되고 자동 로테이션이 설정되었습니다.

## 태스크 3: 자동 로테이션 테스트

이 태스크에서는 자동 로테이션을 즉시 실행하여 비밀번호가 변경되는 과정을 확인합니다.

54. `prod/db/mysql/credentials` 시크릿을 선택합니다.
55. **Rotation** 탭을 선택합니다.
56. **Lambda rotation function** 링크(`SecretsManagermysql-rotation-lambda`)를 클릭하여 AWS Lambda 콘솔로 이동합니다.

> [!NOTE]
> **Rotation** 탭 하단의 **Lambda rotation function**에 링크가 표시됩니다. 링크가 표시되지 않으면 상단 검색창에 `Lambda`를 입력하고 `SecretsManagermysql-rotation-lambda` 함수를 직접 선택합니다.

57. **Configuration** 탭 > **VPC**를 선택합니다.
58. [[Edit]] 버튼을 클릭합니다.
59. **Security groups**에서 `week12-1-rds-sg`를 제거하고 `week12-1-lambda-sg`를 선택합니다.
60. [[Save]] 버튼을 클릭합니다.

> [!IMPORTANT]
> AWS Secrets Manager가 자동 생성한 로테이션 AWS Lambda 함수는 Amazon RDS의 보안 그룹(`week12-1-rds-sg`)을 기본으로 사용합니다. 이 보안 그룹은 아웃바운드 HTTPS(443)가 허용되지 않아 AWS Secrets Manager API에 접근할 수 없습니다. `week12-1-lambda-sg`로 변경하면 Amazon RDS 접근(3306)과 AWS Secrets Manager API 접근(443) 모두 가능합니다.

61. AWS Secrets Manager 콘솔로 돌아가서 `prod/db/mysql/credentials` 시크릿을 선택합니다.
62. **Rotation** 탭을 선택합니다.
63. **Rotation status**가 `Enabled`로 표시되는지 확인합니다.

> [!NOTE]
> 시크릿 생성 직후에는 **Rotation status**가 `Disabled`로 표시될 수 있습니다. AWS CloudFormation이 로테이션 리소스를 설정하는 데 최대 2분이 소요됩니다. 페이지를 새로고침하여 `Enabled`로 변경될 때까지 기다립니다.

> [!TROUBLESHOOTING]
> **문제**: 2분 이상 기다려도 `Disabled` 상태가 유지됨
>
> **해결**:
>
> 1. [[Edit rotation]] 버튼을 클릭합니다.
> 2. **Automatic rotation** 토글을 활성화합니다.
> 3. **Rotation schedule**에서 `Schedule expression builder`를 선택합니다.
> 4. **Time unit**에서 `Hours`, **Hours**에 `23`을 입력합니다.
> 5. **Rotate immediately when the secret is stored** 체크박스를 선택합니다.
> 6. **Rotation function**에서 `Use a rotation function from your account`를 선택합니다.
> 7. **Lambda rotation function** 드롭다운에서 `SecretsManagermysql-rotation-lambda`를 선택합니다.
> 8. **Rotation strategy**에서 `Single user`를 선택합니다.
> 9. [[Save]] 버튼을 클릭합니다.

64. **Last rotated date**에 값이 표시되는지 확인합니다.

> [!NOTE]
> 보안 그룹 변경 후 이전에 실패했던 로테이션이 자동으로 재시도되어 성공할 수 있습니다. **Last rotated date**에 값이 이미 표시되면 아래 Rotate secret immediately 단계를 건너뛰어도 됩니다. 자동 재시도까지 2-3분 소요될 수 있으므로 페이지를 새로고침하며 기다립니다.

65. **Last rotated date**가 `-`인 경우 [[Rotate secret immediately]] 버튼을 클릭합니다.
66. 확인 창에서 [[Rotate]] 버튼을 클릭합니다.

> [!OUTPUT]
> "Secret scheduled for rotation" 메시지가 표시됩니다.

> [!TROUBLESHOOTING]
> **문제**: "A previous rotation isn't complete. That rotation will be reattempted" 오류 발생
>
> **원인**: 시크릿 생성 시 "Rotate immediately when the secret is stored"를 선택했기 때문에 첫 번째 로테이션이 이미 진행 중입니다.
>
> **해결**: AWS CloudShell에서 다음 명령어로 이전 로테이션을 취소한 후 다시 시도합니다:
>
> ```bash
> aws secretsmanager cancel-rotate-secret --secret-id prod/db/mysql/credentials --region ap-northeast-2
> ```

> [!NOTE]
> 로테이션 프로세스:
>
> 1. AWS Lambda 함수가 새 비밀번호를 생성합니다.
> 2. Amazon RDS에서 비밀번호를 변경합니다.
> 3. AWS Secrets Manager에 새 비밀번호를 저장합니다.
> 4. 애플리케이션은 AWS Secrets Manager에서 항상 최신 비밀번호를 조회합니다.

> [!TROUBLESHOOTING]
> **문제**: AWS CloudFormation 스택 업데이트 후 Amazon RDS 비밀번호 불일치
>
> AWS CloudFormation 스택을 업데이트하면 `DBPassword` 파라미터 값으로 Amazon RDS 비밀번호가 리셋됩니다. 그러나 AWS Secrets Manager에 저장된 비밀번호는 변경되지 않아 **비밀번호 불일치**가 발생합니다. 이 경우 로테이션 AWS Lambda 함수가 Amazon RDS에 로그인할 수 없어 로테이션도 실패합니다.
>
> **해결**:
>
> 1. Amazon RDS 콘솔에서 `week12-1-mysql-db` 인스턴스를 선택합니다.
> 2. [[Modify]] 버튼을 클릭합니다.
> 3. **Master password**를 AWS Secrets Manager에 저장된 비밀번호와 동일한 값으로 변경합니다.
> 4. **Apply immediately**를 선택하고 [[Modify DB instance]] 버튼을 클릭합니다.
> 5. 1-2분 후 AWS Lambda 함수를 다시 테스트합니다.
>
> 또는:
>
> 1. AWS Secrets Manager 콘솔에서 `prod/db/mysql/credentials` 시크릿을 선택합니다.
> 2. **Secret value** 섹션에서 [[Retrieve secret value]] 버튼을 클릭합니다.
> 3. [[Edit]] 버튼을 클릭합니다.
> 4. `password` 값을 현재 Amazon RDS 비밀번호와 동일하게 수정합니다.
> 5. [[Save]] 버튼을 클릭합니다.
> 6. **Rotation** 탭에서 [[Rotate secret immediately]] 버튼을 클릭합니다.

67. 1-2분 후 페이지를 새로고침합니다.
68. **Last rotated date**에 날짜가 표시되면 로테이션이 성공한 것입니다.
69. **Overview** 탭을 선택합니다.
70. **Secret value** 섹션에서 [[Retrieve secret value]] 버튼을 클릭합니다.
71. 비밀번호가 `LabPassword456!`에서 새로운 랜덤 값으로 변경되었는지 확인합니다.

> [!NOTE]
> 자동 로테이션이 성공적으로 완료되었습니다. Amazon RDS 비밀번호가 자동으로 변경되었습니다.

✅ **태스크 완료**: 자동 로테이션이 테스트되었습니다.

## 태스크 4: AWS Systems Manager Parameter Store에 설정 저장

이 태스크에서는 AWS Systems Manager Parameter Store에 데이터베이스 연결 문자열을 저장합니다.

72. 상단 검색창에 `Systems Manager`을 입력하고 선택합니다.
73. 왼쪽 메뉴에서 **Parameter Store**를 선택합니다.
74. [[Create parameter]] 버튼을 클릭합니다.
75. **Name**에 `/prod/app/config/db-connection-string`을 입력합니다.
76. **Description**에 `Database connection string`을 입력합니다.
77. **Tier**에서 `Standard`를 선택합니다.
78. **Type**에서 `SecureString`을 선택합니다.
79. **KMS key source**에서 `My current account`를 선택합니다.
80. **KMS Key ID**에서 `alias/secrets-encryption-key`를 선택합니다.
81. **Value**에 다음을 입력합니다 (태스크 0의 DBEndpoint로 대체):

```
mysql://admin:password@{DBEndpoint}:3306/mydb
```

예: `mysql://admin:password@week12-1-mysql-db.xxxxx.ap-northeast-2.rds.amazonaws.com:3306/mydb`

> [!NOTE]
> 이 연결 문자열은 예시입니다. 실제 환경에서는 비밀번호를 하드코딩하지 말고 AWS Secrets Manager에서 가져와야 합니다.

82. **Tags — optional** 섹션에서 [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

83. [[Create parameter]] 버튼을 클릭합니다.

✅ **태스크 완료**: 데이터베이스 연결 문자열이 AWS Systems Manager Parameter Store에 저장되었습니다.

## 태스크 5: AWS Lambda 함수 테스트

이 태스크에서는 AWS CloudFormation이 생성한 AWS Lambda 함수를 테스트하여 AWS Secrets Manager와 AWS Systems Manager Parameter Store에서 자격증명을 조회하고 Amazon RDS에 연결합니다.

84. 상단 검색창에 `Lambda`을 입력하고 선택합니다.
85. `access-secrets-demo` 함수를 선택합니다.
86. **Code** 탭을 선택합니다.
87. 코드를 확인합니다:
    - AWS Secrets Manager에서 자격증명 조회
    - AWS Systems Manager Parameter Store에서 파라미터 조회
    - Amazon RDS MySQL 연결

> [!NOTE]
> 이 AWS Lambda 함수는 AWS CloudFormation이 자동으로 생성했습니다. 코드는 다운로드한 `lambda_function.py` 파일과 동일합니다.
>
> **주요 코드 패턴**:
>
> ```python
> # 1. AWS Secrets Manager에서 자격증명 조회
> secrets_client = boto3.client('secretsmanager')
> secret_response = secrets_client.get_secret_value(SecretId=secret_name)
> db_credentials = json.loads(secret_response['SecretString'])
>
> # 2. AWS Systems Manager Parameter Store에서 파라미터 조회
> ssm_client = boto3.client('ssm')
> parameter_response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
>
> # 3. Amazon RDS MySQL 연결 (Secrets Manager에서 가져온 자격증명 사용)
> connection = mysql.connector.connect(
>     host=db_host, port=db_port,
>     user=db_credentials['username'],
>     password=db_credentials['password']
> )
> ```
>
> - `get_secret_value()`: AWS Secrets Manager에서 시크릿을 조회하고 JSON으로 파싱합니다.
> - `get_parameter(WithDecryption=True)`: SecureString 파라미터를 AWS KMS로 자동 복호화하여 조회합니다.
> - `mysql.connector.connect()`: 조회한 자격증명으로 Amazon RDS에 연결합니다.

88. **Test** 탭을 선택합니다.
89. [[Create new event]] 버튼을 클릭합니다.
90. **Event name**에 `TestEvent`를 입력합니다.

> [!NOTE]
> **Event JSON**은 기본값(`{}`)을 유지합니다.

91. [[Save]] 버튼을 클릭합니다.
92. [[Test]] 버튼을 클릭합니다.
93. 실행 결과를 확인합니다.

> [!OUTPUT]
>
> ```json
> {
>   "statusCode": 200,
>   "body": {
>     "secrets_manager": {
>       "secret_name": "prod/db/mysql/credentials",
>       "username": "admin",
>       "password_length": 32,
>       "status": "Retrieved successfully"
>     },
>     "parameter_store": {
>       "parameter_name": "/prod/app/config/db-connection-string",
>       "value": "mysql://admin:password@...",
>       "type": "SecureString",
>       "status": "Retrieved successfully"
>     },
>     "database_connection": {
>       "host": "week12-1-mysql-db.xxxxx.ap-northeast-2.rds.amazonaws.com",
>       "port": 3306,
>       "username": "admin",
>       "mysql_version": "8.4.8",
>       "current_database": null,
>       "status": "Connected successfully"
>     }
>   }
> }
> ```

> [!NOTE]
> AWS Lambda 함수가 성공적으로 실행되었습니다.
>
> - AWS Secrets Manager에서 자격증명을 조회했습니다.
> - AWS Systems Manager Parameter Store에서 파라미터를 조회했습니다.
> - Amazon RDS MySQL에 연결했습니다.

> [!NOTE]
> AWS CloudShell에서도 AWS Lambda 함수를 테스트할 수 있습니다:
>
> ```bash
> aws lambda invoke \
>   --function-name access-secrets-demo \
>   --payload '{}' \
>   --cli-binary-format raw-in-base64-out \
>   output.json \
>   --region ap-northeast-2
> ```
>
> AWS Lambda 실행 결과는 `output.json` 파일에 저장됩니다. `body` 내부의 JSON 문자열을 파싱하여 보기 좋게 출력하려면 다음 명령어를 실행합니다:
>
> ```bash
> cat output.json | jq '{statusCode: .statusCode, body: (.body | fromjson)}'
> ```

94. 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
95. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.

> [!NOTE]
> Amazon CloudWatch Logs에서 다음 2개의 로그 그룹을 확인할 수 있습니다:
>
> - `/aws/lambda/access-secrets-demo`: AWS Lambda 함수 실행 로그
> - `/aws/lambda/SecretsManagermysql-rotation-lambda`: 로테이션 AWS Lambda 함수 로그
>
> 로그 그룹을 클릭하면 **Log streams**에서 최신 실행 기록을 확인할 수 있습니다. 실행 시간, 메모리 사용량, 에러 메시지 등을 확인하여 문제를 진단할 수 있습니다.

✅ **태스크 완료**: AWS Lambda 함수가 테스트되었습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> AWS Secrets Manager 시크릿, AWS KMS 키, AWS Systems Manager Parameter Store 파라미터, 로테이션 AWS Lambda 함수는 AWS CloudFormation 스택에 포함되지 않으므로 **수동으로 먼저 삭제**해야 합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `12-1`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: 수동 생성 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS CloudShell에서 AWS Secrets Manager 시크릿을 즉시 삭제합니다:

```bash
aws secretsmanager delete-secret --secret-id prod/db/mysql/credentials --force-delete-without-recovery --region ap-northeast-2
```

> [!NOTE]
> `--force-delete-without-recovery` 옵션으로 7일 대기 기간 없이 즉시 삭제합니다.
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws secretsmanager describe-secret --secret-id prod/db/mysql/credentials --region ap-northeast-2 2>&1 || echo "삭제 완료"
> ```

8. AWS Systems Manager Parameter Store 파라미터를 삭제합니다:

```bash
aws ssm delete-parameter --name /prod/app/config/db-connection-string --region ap-northeast-2
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws ssm get-parameter --name /prod/app/config/db-connection-string --region ap-northeast-2 2>&1 || echo "삭제 완료"
> ```

9. AWS KMS 키 삭제를 예약합니다:

```bash
KEY_ID=$(aws kms list-aliases --query "Aliases[?AliasName=='alias/secrets-encryption-key'].TargetKeyId | [0]" --output text --region ap-northeast-2)
aws kms schedule-key-deletion --key-id $KEY_ID --pending-window-in-days 7 --region ap-northeast-2
```

> [!NOTE]
> AWS KMS 키는 즉시 삭제할 수 없으며, 최소 7일 대기 후 삭제됩니다. 삭제 예약 시 즉시 비용 청구가 중단됩니다.
> 삭제 예약 상태를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws kms describe-key --key-id $KEY_ID --query "KeyMetadata.KeyState" --output text --region ap-northeast-2
> ```
>
> `PendingDeletion`이 출력되면 삭제 예약 완료입니다.

10. 로테이션 AWS Lambda 함수를 삭제합니다:

```bash
aws lambda delete-function --function-name SecretsManagermysql-rotation-lambda --region ap-northeast-2
```

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws lambda get-function --function-name SecretsManagermysql-rotation-lambda --region ap-northeast-2 2>&1 || echo "삭제 완료"
> ```

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

7. 상단 검색창에 `Secrets Manager`를 입력하고 선택합니다.
8. `prod/db/mysql/credentials` 시크릿을 선택합니다.
9. **Actions** > `Delete secret`을 선택합니다.
10. **Waiting period**를 `7`일로 설정하고 [[Schedule deletion]] 버튼을 클릭합니다.
11. 상단 검색창에 `Systems Manager`를 입력하고 선택합니다.
12. 왼쪽 메뉴에서 **Parameter Store**를 선택합니다.
13. `/prod/app/config/db-connection-string` 파라미터를 선택합니다.
14. [[Delete]] 버튼을 클릭합니다.
15. 확인 창에서 [[Delete parameters]] 버튼을 클릭합니다.
16. 상단 검색창에 `KMS`를 입력하고 선택합니다.
17. 왼쪽 메뉴에서 **Customer managed keys**를 선택합니다.
18. `secrets-encryption-key`를 선택합니다.
19. **Key actions** > `Schedule key deletion`을 선택합니다.
20. **Waiting period (in days)**에 `7`을 입력합니다.
21. **Confirmation** 섹션에서 `I confirm that I want to schedule these keys for deletion` 체크박스를 선택합니다.
22. [[Schedule deletion]] 버튼을 클릭합니다.
23. 상단 검색창에 `Lambda`를 입력하고 선택합니다.
24. `SecretsManagermysql-rotation-lambda` 함수를 선택합니다.
25. **Actions** > `Delete`를 선택합니다.
26. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

### 단계 3: AWS CloudFormation 스택 삭제

27. AWS CloudFormation 콘솔로 이동합니다.
28. `SecretsManagerRDSMySQLRotationSingleUser`로 시작하는 중첩(NESTED) 스택을 선택합니다.
29. [[Delete]] 버튼을 클릭합니다.
30. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 이 중첩 스택은 AWS Secrets Manager가 로테이션을 설정할 때 자동으로 생성한 것입니다. 로테이션 AWS Lambda 함수와 AWS IAM 역할이 포함되어 있습니다. 2개가 표시될 수 있으며, 모두 삭제합니다.

31. `week12-1-secrets-lab-stack` 스택을 선택합니다.
32. [[Delete]] 버튼을 클릭합니다.
33. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 10-15분이 소요됩니다 (Amazon RDS 인스턴스 포함). AWS CloudFormation 스택을 삭제하면 Amazon RDS, Amazon VPC, AWS Lambda 함수, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

### 단계 4: Amazon CloudWatch Log Group 삭제

34. Amazon CloudWatch 콘솔로 이동합니다.
35. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
36. 검색창에 `SecretsManagermysql`을 입력합니다.
37. `/aws/lambda/SecretsManagermysql-rotation-lambda` 로그 그룹의 체크박스를 선택합니다.
38. **Actions** > `Delete log group(s)`를 선택합니다.
39. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.
> `/aws/lambda/access-secrets-demo` 로그 그룹은 AWS CloudFormation 스택에 포함되어 있어 스택 삭제 시 자동으로 삭제됩니다. 이 외에 이번 실습과 관련된 로그 그룹이 남아있다면 함께 삭제합니다.

> [!NOTE]
> AWS CLI로 삭제하려면 AWS CloudShell에서 다음 명령어를 실행합니다:
>
> ```bash
> aws logs delete-log-group --log-group-name /aws/lambda/SecretsManagermysql-rotation-lambda --region ap-northeast-2
> ```
>
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/SecretsManagermysql --query "logGroups[*].logGroupName" --output text --region ap-northeast-2
> ```
>
> 출력이 없으면 삭제 완료입니다.

### 단계 5: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

40. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
41. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
42. **Regions**에서 `ap-northeast-2`를 선택합니다.
43. **Resource types**에서 `All supported resource types`를 선택합니다.
44. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `12-1`
45. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> AWS KMS 키는 삭제 예약 상태(Pending deletion)로 7일간 표시될 수 있습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS Secrets Manager 사용 설명서](https://docs.aws.amazon.com/ko_kr/secretsmanager/latest/userguide/intro.html)
- [AWS Secrets Manager 자동 로테이션](https://docs.aws.amazon.com/ko_kr/secretsmanager/latest/userguide/rotating-secrets.html)
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [AWS KMS 개발자 가이드](https://docs.aws.amazon.com/ko_kr/kms/latest/developerguide/overview.html)

## 📚 참고: AWS Secrets Manager vs Parameter Store

### AWS Secrets Manager

**장점:**

- 자동 로테이션 기능 (Amazon RDS, Amazon Redshift, DocumentDB 등 지원)
- 버전 관리 및 롤백
- JSON 형식으로 여러 키-값 쌍 저장
- 세밀한 접근 제어

**단점:**

- 시크릿당 $0.40/월 비용
- API 호출당 $0.05/10,000건

**사용 사례:**

- 데이터베이스 자격증명 (자동 로테이션 필요)
- API 키 (민감한 정보)
- 인증서 및 SSH 키

### AWS Systems Manager Parameter Store

**장점:**

- Standard 파라미터 무료 (최대 10,000개)
- 계층적 구조 (`/prod/app/config/region`)
- SecureString으로 AWS KMS 암호화 지원
- AWS CloudFormation, AWS Lambda 등과 통합

**단점:**

- 자동 로테이션 없음
- 4KB 크기 제한 (Standard)

**사용 사례:**

- 애플리케이션 설정값
- 환경 변수
- 자주 변경되지 않는 자격증명

### 선택 기준

| 요구사항              | 권장 서비스         |
| --------------------- | ------------------- |
| 데이터베이스 자격증명 | AWS Secrets Manager |
| 자동 로테이션 필요    | AWS Secrets Manager |
| 애플리케이션 설정     | Parameter Store     |
| 비용 최소화           | Parameter Store     |
| 계층적 구조 관리      | Parameter Store     |
| 버전 관리 및 롤백     | AWS Secrets Manager |

### 자동 로테이션 원리

- **로테이션 일정**: 30일마다 자동 실행
- **AWS Lambda 함수**: AWS Secrets Manager가 자동 생성
- **로테이션 단계**:
  - `createSecret`: 새 비밀번호 생성
  - `setSecret`: Amazon RDS에 새 비밀번호 설정
  - `testSecret`: 새 비밀번호로 연결 테스트
  - `finishSecret`: 이전 버전을 AWSPREVIOUS로 표시
- **애플리케이션**: 항상 AWS Secrets Manager에서 최신 비밀번호 조회
- **무중단**: 로테이션 중에도 애플리케이션 정상 동작
