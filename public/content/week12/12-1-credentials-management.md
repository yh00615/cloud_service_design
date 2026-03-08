---
title: 'AWS Secrets Manager와 RDS 자동 로테이션'
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
  - AWS Lambda 함수에서 Secrets Manager와 Parameter Store를 조회하고 RDS에 연결할 수 있습니다.
  - 자동 로테이션을 통해 비밀번호를 안전하게 관리할 수 있습니다.

prerequisites:
  - AWS IAM 기본 개념 이해
  - AWS Lambda 기본 사용 경험
  - 암호화 기본 개념 이해
---

이 실습에서는 AWS Secrets Manager의 핵심 기능인 **자동 로테이션**을 학습합니다. Amazon RDS MySQL 데이터베이스를 생성하고, Secrets Manager에 자격증명을 저장한 후, 자동 로테이션을 설정하여 비밀번호를 주기적으로 변경합니다. AWS Lambda 함수에서 Secrets Manager와 Parameter Store를 조회하여 실제 데이터베이스에 연결하는 과정을 실습합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제**해야 합니다.
>
> **예상 비용** (2시간 실습 기준):
>
> | 리소스              | 비용                          |
> | ------------------- | ----------------------------- |
> | Amazon RDS          | $0.017/시간 × 2시간 = $0.034  |
> | AWS Secrets Manager | $0.40/월 ÷ 30일 = $0.013      |
> | AWS KMS             | $1/월 ÷ 30일 = $0.033         |
> | **총 예상**         | **$0.08**                     |

> [!DOWNLOAD]
> [week12-1-secrets-manager-lab.zip](/files/week12/week12-1-secrets-manager-lab.zip)
>
> - `week12-1-secrets-manager-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon RDS, Amazon VPC, AWS Lambda 함수 자동 생성)
> - `lambda_function.py` - AWS Lambda 함수 코드 (참고용)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation으로 Amazon RDS + AWS Lambda 자동 생성)
> - 태스크 5: AWS Lambda 함수 테스트 (이미 생성된 함수 사용)

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 Amazon RDS MySQL 데이터베이스와 AWS Lambda 함수를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon RDS MySQL**: db.t3.micro 인스턴스
- **Amazon VPC**: 프라이빗 서브넷 2개
- **AWS Lambda 함수**: Secrets Manager 및 Parameter Store 조회, RDS 연결
- **AWS IAM 역할**: AWS Lambda 실행 역할 (Secrets Manager, Parameter Store, AWS KMS 권한 포함)
- **보안 그룹**: AWS Lambda → Amazon RDS 통신

### 상세 단계

1. 다운로드한 `week12-1-secrets-manager-lab.zip` 파일의 압축을 해제합니다.
2. `week12-1-secrets-manager-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week12-1-secrets-manager-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week12-1-secrets-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **DBUsername**: `admin`
    - **DBPassword**: `TempPassword123!`
11. [[Next]] 버튼을 클릭합니다.
12. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

13. [[Next]] 버튼을 클릭합니다.
14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create IAM resources`를 체크합니다.
15. [[Submit]] 버튼을 클릭합니다.
16. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> Amazon RDS 인스턴스 생성에 10-15분이 소요됩니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

17. 상태가 "CREATE_COMPLETE"로 변경될 때까지 기다립니다.
18. **Outputs** 탭을 선택합니다.
19. 출력값들을 메모장에 복사합니다:
    - `DBEndpoint`: Amazon RDS 엔드포인트
    - `DBPort`: Amazon RDS 포트 (3306)
    - `DBUsername`: 데이터베이스 사용자 이름 (admin)
    - `LambdaFunctionName`: AWS Lambda 함수 이름

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: AWS KMS 키 생성

이 태스크에서는 Secrets Manager와 Parameter Store에서 사용할 암호화 키를 생성합니다.

20. 상단 검색창에 `KMS`을 입력하고 선택합니다.
21. 왼쪽 메뉴에서 **Customer managed keys**를 선택합니다.
22. [[Create key]] 버튼을 클릭합니다.
23. **Key type**에서 `Symmetric`을 선택합니다.
24. **Key usage**에서 `Encrypt and decrypt`를 선택합니다.
25. [[Next]] 버튼을 클릭합니다.
26. **Alias**에 `secrets-encryption-key`를 입력합니다.
27. **Description**에 `Encryption key for Secrets Manager and Parameter Store`를 입력합니다.
28. **Tags** 섹션에서 [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

29. [[Next]] 버튼을 클릭합니다.
30. **Key administrators** 섹션에서 본인의 AWS IAM 사용자를 선택합니다.
31. [[Next]] 버튼을 클릭합니다.
32. **Key users** 섹션에서 AWS CloudFormation이 생성한 AWS Lambda 실행 역할을 선택합니다.
    - 역할 이름: `week12-1-lambda-secrets-role`
33. [[Next]] 버튼을 클릭합니다.
34. 설정을 검토하고 [[Finish]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS KMS 키가 생성되었습니다.


## 태스크 2: AWS Secrets Manager에 Amazon RDS 자격증명 저장

이 태스크에서는 AWS Secrets Manager에 Amazon RDS 데이터베이스 자격증명을 저장합니다.

35. 상단 검색창에 `Secrets Manager`을 입력하고 선택합니다.
36. [[Store a new secret]] 버튼을 클릭합니다.
37. **Secret type**에서 `Credentials for Amazon RDS database`를 선택합니다.
38. **User name**에 `admin`을 입력합니다.
39. **Password**에 `TempPassword123!`을 입력합니다.
40. **Encryption key**에서 `secrets-encryption-key`를 선택합니다.
41. **Database**에서 AWS CloudFormation이 생성한 Amazon RDS 인스턴스를 선택합니다.
	- 인스턴스 ID: `week12-1-mysql-db`
42. [[Next]] 버튼을 클릭합니다.
43. **Secret name**에 `prod/db/mysql/credentials`를 입력합니다.
44. **Description**에 `Production MySQL database credentials`를 입력합니다.
45. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

46. [[Next]] 버튼을 클릭합니다.
47. **Automatic rotation**에서 `Enable automatic rotation`을 선택합니다.

> [!IMPORTANT]
> 자동 로테이션은 AWS Secrets Manager의 핵심 기능입니다. 비밀번호를 주기적으로 자동 변경하여 보안을 강화합니다.

48. **Rotation schedule**에서 `Days`를 선택하고 `30`을 입력합니다.
49. **Rotation function**에서 `Create a new Lambda function`을 선택합니다.
50. **Lambda function name**에 `SecretsManagerRotation-mysql`을 입력합니다.
51. [[Next]] 버튼을 클릭합니다.
52. 설정을 검토합니다.
53. [[Store]] 버튼을 클릭합니다.

> [!NOTE]
> AWS Secrets Manager가 자동으로 로테이션 AWS Lambda 함수를 생성합니다. 이 함수는 Amazon RDS 비밀번호를 변경하고 Secrets Manager를 업데이트합니다.

54. 시크릿 생성이 완료될 때까지 기다립니다.

✅ **태스크 완료**: Amazon RDS 자격증명이 저장되고 자동 로테이션이 설정되었습니다.

## 태스크 3: 자동 로테이션 테스트

이 태스크에서는 자동 로테이션을 즉시 실행하여 비밀번호가 변경되는 과정을 확인합니다.

55. AWS Secrets Manager 콘솔에서 `prod/db/mysql/credentials` 시크릿을 선택합니다.
56. **Rotation configuration** 섹션으로 스크롤합니다.
57. [[Rotate secret immediately]] 버튼을 클릭합니다.
58. 확인 창에서 [[Rotate]] 버튼을 클릭합니다.

> [!NOTE]
> 로테이션 프로세스:
> 1. AWS Lambda 함수가 새 비밀번호를 생성합니다
> 2. Amazon RDS에서 비밀번호를 변경합니다
> 3. Secrets Manager에 새 비밀번호를 저장합니다
> 4. 애플리케이션은 Secrets Manager에서 항상 최신 비밀번호를 조회합니다

59. 로테이션 상태가 "Rotation in progress"로 표시됩니다.
60. 1-2분 후 페이지를 새로고침합니다.
61. 로테이션 상태가 "Rotation successful"로 변경되었는지 확인합니다.
62. **Secret value** 섹션에서 [[Retrieve secret value]] 버튼을 클릭합니다.
63. 비밀번호가 `TempPassword123!`에서 새로운 값으로 변경되었는지 확인합니다.

> [!SUCCESS]
> 자동 로테이션이 성공적으로 완료되었습니다! Amazon RDS 비밀번호가 자동으로 변경되었습니다.

✅ **태스크 완료**: 자동 로테이션이 테스트되었습니다.


## 태스크 4: Parameter Store에 설정 저장

이 태스크에서는 AWS Systems Manager Parameter Store에 데이터베이스 연결 문자열을 저장합니다.

64. 상단 검색창에 `Systems Manager`을 입력하고 선택합니다.
65. 왼쪽 메뉴에서 **Parameter Store**를 선택합니다.
66. [[Create parameter]] 버튼을 클릭합니다.
67. **Name**에 `/prod/app/config/db-connection-string`을 입력합니다.
68. **Description**에 `Database connection string`을 입력합니다.
69. **Tier**에서 `Standard`를 선택합니다.
70. **Type**에서 `SecureString`을 선택합니다.
71. **KMS key source**에서 `My current account`를 선택합니다.
72. **KMS Key ID**에서 `alias/secrets-encryption-key`를 선택합니다.
73. **Value**에 다음을 입력합니다 (태스크 0의 DBEndpoint로 대체):

```
mysql://admin:password@{DBEndpoint}:3306/mydb
```

예: `mysql://admin:password@week12-1-mysql-db.xxxxx.ap-northeast-2.rds.amazonaws.com:3306/mydb`

> [!NOTE]
> 이 연결 문자열은 예시입니다. 실제 환경에서는 비밀번호를 하드코딩하지 말고 AWS Secrets Manager에서 가져와야 합니다.

74. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-1`    |
| `CreatedBy` | `Student` |

75. [[Create parameter]] 버튼을 클릭합니다.

✅ **태스크 완료**: 데이터베이스 연결 문자열이 Parameter Store에 저장되었습니다.

## 태스크 5: AWS Lambda 함수 테스트

이 태스크에서는 AWS CloudFormation이 생성한 AWS Lambda 함수를 테스트하여 Secrets Manager와 Parameter Store에서 자격증명을 조회하고 Amazon RDS에 연결합니다.

76. 상단 검색창에 `Lambda`을 입력하고 선택합니다.
77. `access-secrets-demo` 함수를 선택합니다.
78. **Code** 탭을 선택합니다.
79. 코드를 확인합니다:
	- Secrets Manager에서 자격증명 조회
	- Parameter Store에서 파라미터 조회
	- Amazon RDS MySQL 연결

> [!NOTE]
> 이 AWS Lambda 함수는 AWS CloudFormation이 자동으로 생성했습니다. 코드는 다운로드한 `lambda_function.py` 파일과 동일합니다.

80. **Test** 탭을 선택합니다.
81. [[Create new event]] 버튼을 클릭합니다.
82. **Event name**에 `TestEvent`를 입력합니다.
83. **Event JSON**은 기본값을 유지합니다:

```json
{}
```

84. [[Save]] 버튼을 클릭합니다.
85. [[Test]] 버튼을 클릭합니다.
86. 실행 결과를 확인합니다.

> [!OUTPUT]
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
>       "mysql_version": "8.0.35",
>       "current_database": null,
>       "status": "Connected successfully"
>     }
>   }
> }
> ```

> [!SUCCESS]
> AWS Lambda 함수가 성공적으로 실행되었습니다!
> - Secrets Manager에서 자격증명을 조회했습니다
> - Parameter Store에서 파라미터를 조회했습니다
> - Amazon RDS MySQL에 연결했습니다

87. **Logs** 섹션에서 Amazon CloudWatch Logs 링크를 클릭하여 상세 로그를 확인합니다.

✅ **태스크 완료**: AWS Lambda 함수가 테스트되었습니다.


## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `12-1`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### 1단계: AWS Secrets Manager 시크릿 즉시 삭제

> [!TIP]
> AWS CloudShell을 사용하면 7일 대기 기간 없이 즉시 삭제할 수 있습니다.

8. AWS Management Console 상단 오른쪽의 CloudShell 아이콘을 클릭합니다.
9. CloudShell이 열리면 다음 명령어를 실행합니다:

```bash
aws secretsmanager delete-secret \
  --secret-id prod/db/mysql/credentials \
  --force-delete-without-recovery \
  --region ap-northeast-2
```

> [!OUTPUT]
> ```json
> {
>   "ARN": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:prod/db/mysql/credentials-AbCdEf",
>   "Name": "prod/db/mysql/credentials",
>   "DeletionDate": 1234567890.0
> }
> ```

#### 2단계: Parameter Store 파라미터 삭제

10. AWS Systems Manager 콘솔로 이동합니다.
11. 왼쪽 메뉴에서 **Parameter Store**를 선택합니다.
12. `/prod/app/config/db-connection-string` 파라미터를 선택합니다.
13. [[Delete]] 버튼을 클릭합니다.
14. 확인 창에서 [[Delete parameters]] 버튼을 클릭합니다.

#### 3단계: AWS KMS 키 삭제 예약

15. AWS KMS 콘솔로 이동합니다.
16. `secrets-encryption-key`를 선택합니다.
17. **Key actions** > `Schedule key deletion`을 선택합니다.
18. **Waiting period**에 `7`일을 입력합니다 (최소값).
19. [[Schedule deletion]] 버튼을 클릭합니다.

> [!NOTE]
> AWS KMS 키는 삭제 예약 시 즉시 비용 청구가 중단됩니다.

#### 4단계: 로테이션 AWS Lambda 함수 삭제

20. AWS Lambda 콘솔로 이동합니다.
21. `SecretsManagerRotation-mysql` 함수를 선택합니다.
22. **Actions** > `Delete`를 선택합니다.
23. 확인 창에서 `delete`를 입력합니다.
24. [[Delete]] 버튼을 클릭합니다.

#### 5단계: AWS CloudFormation 스택 삭제

25. AWS CloudFormation 콘솔로 이동합니다.
26. `week12-1-secrets-lab-stack` 스택을 선택합니다.
27. [[Delete]] 버튼을 클릭합니다.
28. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
29. 스택 삭제가 완료될 때까지 기다립니다 (10-15분 소요).

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 Amazon RDS, Amazon VPC, AWS Lambda 함수, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

#### 6단계: Amazon CloudWatch Log Group 삭제

30. Amazon CloudWatch 콘솔로 이동합니다.
31. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
32. 다음 로그 그룹들을 선택합니다:
	- `/aws/lambda/access-secrets-demo`
	- `/aws/lambda/SecretsManagerRotation-mysql`
33. **Actions** > `Delete log group(s)`를 선택합니다.
34. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

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

| 요구사항                 | 권장 서비스         |
| ------------------------ | ------------------- |
| 데이터베이스 자격증명    | AWS Secrets Manager |
| 자동 로테이션 필요       | AWS Secrets Manager |
| 애플리케이션 설정        | Parameter Store     |
| 비용 최소화              | Parameter Store     |
| 계층적 구조 관리         | Parameter Store     |
| 버전 관리 및 롤백        | AWS Secrets Manager |

### 자동 로테이션 원리

35. **로테이션 일정**: 30일마다 자동 실행
36. **AWS Lambda 함수**: AWS Secrets Manager가 자동 생성
37. **로테이션 단계**:
	- `createSecret`: 새 비밀번호 생성
	- `setSecret`: Amazon RDS에 새 비밀번호 설정
	- `testSecret`: 새 비밀번호로 연결 테스트
   - `finishSecret`: 이전 버전을 AWSPREVIOUS로 표시
38. **애플리케이션**: 항상 Secrets Manager에서 최신 비밀번호 조회
39. **무중단**: 로테이션 중에도 애플리케이션 정상 동작
