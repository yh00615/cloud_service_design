---
title: "AWS CloudFormation 스택 생명주기 관리"
week: 6
session: 1
awsServices:
  - AWS CloudFormation
learningObjectives:
  - Infrastructure as Code의 개념과 AWS CloudFormation의 이점을 이해할 수 있습니다.
  - AWS CloudFormation 스택을 생성하고 Amazon S3 버킷을 배포할 수 있습니다.
  - 변경 세트를 사용하여 스택을 안전하게 업데이트할 수 있습니다.
  - 드리프트 감지로 수동 변경을 감지하고 스택을 삭제할 수 있습니다.
prerequisites:
  - AWS 기본 서비스 이해 (Amazon VPC, Amazon EC2, Amazon S3 등)
  - YAML 또는 JSON 기본 문법 이해
---

이 데모에서는 AWS CloudFormation 스택의 전체 생명주기를 시연합니다. 간단한 Amazon S3 버킷 스택을 생성(CREATE)하고, 변경 세트를 통해 안전하게 업데이트(UPDATE)하며, 드리프트 감지로 수동 변경을 감지한 후 스택을 삭제(DELETE)하는 전체 프로세스를 경험합니다. 각 단계에서 스택 상태 변화를 관찰하고 AWS CloudFormation이 리소스를 어떻게 관리하는지 이해합니다.

> [!DOWNLOAD]
> [week6-1-cloudformation-lab.zip](/files/week6/week6-1-cloudformation-lab.zip)
> - `s3-bucket-create.yaml` - 기본 S3 버킷 템플릿 (태스크 1에서 스택 생성)
> - `s3-bucket-update.yaml` - 태그가 추가된 S3 버킷 템플릿 (태스크 2에서 변경 세트 생성)
> 
> **관련 태스크:**
> 
> - 태스크 1: S3 스택 생성 (s3-bucket-create.yaml 사용)
> - 태스크 2: 변경 세트 생성 및 실행 (s3-bucket-update.yaml로 업데이트)
> - 태스크 3: 드리프트 감지 (수동 변경 감지)

> [!NOTE]
> 이 데모는 비용이 거의 발생하지 않습니다. Amazon S3 버킷 자체는 무료이며, 데이터를 저장하지 않으므로 스토리지 비용도 발생하지 않습니다.

## 태스크 1: 스택 생성 (CREATE) - Amazon S3 버킷 스택

이 태스크에서는 간단한 Amazon S3 버킷 템플릿을 사용하여 AWS CloudFormation 스택을 생성합니다. 스택 생성 과정에서 상태 변화(CREATE_IN_PROGRESS → CREATE_COMPLETE)를 관찰하고, 생성된 리소스를 확인합니다.

> [!CONCEPT] 스택 생성 프로세스
> AWS CloudFormation 스택 생성은 다음 단계로 진행됩니다:
> 
> - **템플릿 검증**: AWS CloudFormation이 템플릿 문법을 확인합니다.
> - **리소스 생성**: AWS API를 호출하여 Amazon S3 버킷을 생성합니다.
> - **상태 추적**: 각 리소스의 생성 상태를 모니터링합니다.
> - **출력값 생성**: Outputs 섹션에 정의된 값을 표시합니다.
> - **완료**: 모든 리소스가 성공적으로 생성되면 스택 상태가 CREATE_COMPLETE로 변경됩니다.

스택 생성 과정에서 다양한 상태 변화를 확인할 수 있습니다.

> [!NOTE]
> **상태 변화:**
> 
> - **CREATE_IN_PROGRESS** (파란색): 리소스 생성 중
> - **CREATE_COMPLETE** (초록색): 모든 리소스 생성 완료
> - **CREATE_FAILED** (빨간색): 생성 실패 (자동 롤백)
> - **ROLLBACK_IN_PROGRESS**: 실패한 리소스 삭제 중
> - **ROLLBACK_COMPLETE**: 롤백 완료

### 상세 단계

1. 다운로드한 `week6-1-cloudformation-lab.zip` 파일의 압축을 해제합니다.
2. `s3-bucket-create.yaml` 파일을 텍스트 에디터로 엽니다.
3. 템플릿 구조를 확인합니다:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Week 6-1: Simple S3 Bucket Stack - CloudFormation CREATE Lifecycle'

Parameters:
  BucketPrefix:
    Type: String
    Default: cfn-demo-bucket
    Description: S3 bucket name prefix
    AllowedPattern: ^[a-z0-9-]*$
    ConstraintDescription: Only lowercase letters, numbers, and hyphens allowed

Resources:
  DemoBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketPrefix}-${AWS::AccountId}'

Outputs:
  BucketName:
    Description: Name of the S3 bucket
    Value: !Ref DemoBucket
```

4. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
5. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
6. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
7. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
8. **Specify template**에서 `Upload a template file`을 선택합니다.
9. [[Choose file]] 버튼을 클릭한 후 `s3-bucket-create.yaml` 파일을 선택합니다.
10. [[Next]] 버튼을 클릭합니다.
11. **Stack name**에 `demo-s3-stack`을 입력합니다.
12. **Parameters** 섹션에서 **BucketPrefix** 값을 확인합니다 (기본값 `cfn-demo-bucket` 사용).
13. [[Next]] 버튼을 클릭합니다.
14. **Configure stack options** 페이지에서 **Tags** 섹션을 찾습니다.
15. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key | Value |
|-----|-------|
| `Project` | `AWS-Lab` |
| `Week` | `6-1` |
| `CreatedBy` | `CloudFormation` |

16. [[Next]] 버튼을 클릭합니다.
17. **Review and create** 페이지에서 설정을 확인합니다.
18. [[Submit]] 버튼을 클릭합니다.
19. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 1-2분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> AWS CloudFormation이 Amazon S3 버킷을 생성하는 과정을 실시간으로 관찰합니다.
> 
> **스택 태그 자동 전파**: 스택에 추가한 태그(`Project`, `Week`, `CreatedBy`)는 스택이 생성하는 모든 리소스(Amazon S3 버킷)에 자동으로 전파됩니다.

20. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
21. **Outputs** 탭을 선택합니다.
22. **BucketName** 값을 확인합니다 (예: `cfn-demo-bucket-123456789012`).
23. **Resources** 탭을 선택합니다.
24. **DemoBucket** 리소스의 **Physical ID**를 클릭합니다.
25. Amazon S3 콘솔에서 생성된 버킷을 확인합니다.

✅ **태스크 완료**: 스택 생성(CREATE) 생명주기를 시연했습니다.

## 태스크 2: 스택 업데이트 (UPDATE) - 변경 세트로 안전한 업데이트

이 태스크에서는 스택 업데이트 생명주기를 시연합니다. 태그가 추가된 템플릿으로 업데이트하면서 상태 변화(UPDATE_IN_PROGRESS → UPDATE_COMPLETE)를 관찰하고, Change set preview로 변경 사항을 미리 확인합니다.

> [!CONCEPT] 스택 업데이트 프로세스
> AWS CloudFormation 스택 업데이트는 다음 단계로 진행됩니다:
> 
> - **변경 사항 분석**: 새 템플릿과 기존 템플릿을 비교합니다
> - **Change set preview**: 어떤 리소스가 어떻게 변경되는지 미리 보여줍니다
> - **리소스 업데이트**: AWS API를 호출하여 리소스를 수정합니다
> - **상태 추적**: 각 리소스의 업데이트 상태를 모니터링합니다
> - **완료**: 모든 리소스가 성공적으로 업데이트되면 스택 상태가 UPDATE_COMPLETE로 변경됩니다
> 
> **상태 변화:**
> 
> - **UPDATE_IN_PROGRESS** (파란색): 리소스 업데이트 중
> - **UPDATE_COMPLETE** (초록색): 모든 리소스 업데이트 완료
> - **UPDATE_ROLLBACK_IN_PROGRESS**: 업데이트 실패, 이전 상태로 롤백 중
> - **UPDATE_ROLLBACK_COMPLETE**: 롤백 완료, 이전 상태로 복원됨
> 
> **Change set preview의 중요성:**
> 
> - 실제 업데이트 전에 변경 사항을 확인합니다
> - 어떤 리소스가 추가/수정/삭제되는지 표시합니다
> - Replacement 여부를 명확히 보여줍니다 (데이터 손실 위험 파악)
> - 프로덕션 환경에서 안전한 업데이트를 위해 필수적입니다

### 상세 단계

26. `s3-bucket-update.yaml` 파일을 텍스트 에디터로 엽니다.
27. 템플릿 내용을 확인합니다:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Week 6-1: S3 Bucket with Tags - CloudFormation UPDATE Lifecycle'

Parameters:
  BucketPrefix:
    Type: String
    Default: cfn-demo-bucket
    Description: S3 bucket name prefix
    AllowedPattern: ^[a-z0-9-]*$
    ConstraintDescription: Only lowercase letters, numbers, and hyphens allowed

  ProjectTag:
    Type: String
    Default: 'AWS-Lab'
    Description: Project tag value

  WeekTag:
    Type: String
    Default: '6-1'
    Description: Week tag value

  CreatedByTag:
    Type: String
    Default: 'CloudFormation'
    Description: CreatedBy tag value

Resources:
  DemoBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketPrefix}-${AWS::AccountId}'
      Tags:
        - Key: Name
          Value: !Sub '${BucketPrefix}-${AWS::AccountId}'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag

Outputs:
  BucketName:
    Description: Name of the S3 bucket
    Value: !Ref DemoBucket
```

> [!NOTE]
> 이 템플릿은 태스크 1에서 콘솔로 수동 추가한 태그들을 템플릿 코드에 반영한 버전입니다.
> 수동으로 관리하던 태그를 Infrastructure as Code 방식으로 전환하여 버전 관리와 재사용이 가능하도록 개선합니다.
> 
> 버킷 이름은 동일하므로 기존 버킷이 수정됩니다.

28. AWS CloudFormation 콘솔로 이동합니다.
29. `demo-s3-stack`을 선택합니다.
30. [[Update stack]] 드롭다운을 클릭합니다.
31. **Create a change set**을 선택합니다.

> [!NOTE]
> **변경 세트(Change Set) 방식:**
> - 변경 세트를 먼저 생성하여 어떤 리소스가 어떻게 변경되는지 검토합니다
> - 검토 후 문제가 없으면 변경 세트를 실행하여 실제 업데이트를 수행합니다
> - 프로덕션 환경에서 안전한 업데이트를 위해 권장되는 방식입니다

32. **Change set type**에서 `Standard change set`을 선택합니다.
33. **Prerequisite - Prepare template**에서 `Replace existing template`을 선택합니다.
34. **Specify template**에서 `Upload a template file`을 선택합니다.
35. [[Choose file]] 버튼을 클릭한 후 `s3-bucket-update.yaml` 파일을 선택합니다.
36. [[Next]] 버튼을 클릭합니다.
37. **Changeset name**에 `update-tags-changeset`을 입력합니다 (또는 자동 생성된 이름 사용).
38. **Parameters** 섹션에서 기본값을 확인합니다:
    - **BucketPrefix**: `cfn-demo-bucket`
    - **ProjectTag**: `AWS-Lab`
    - **WeekTag**: `6-1`
    - **CreatedByTag**: `CloudFormation`
39. [[Next]] 버튼을 클릭합니다.
40. **Configure change set options** 페이지에서 기본값을 유지하고 [[Next]] 버튼을 클릭합니다.
41. **Review change set** 페이지에서 설정을 확인합니다.
42. [[Create change set]] 버튼을 클릭합니다.

> [!NOTE]
> 변경 세트 생성에 10-20초가 소요됩니다. 상태가 "CREATE_COMPLETE"로 변경될 때까지 기다립니다.

43. 변경 세트가 생성되면 **Overview** 탭에서 다음 정보를 확인합니다:
    - **Change set status**: CREATE_COMPLETE (초록색)
    - **Execution status**: AVAILABLE
44. **Resource changes** 탭을 클릭합니다.
45. 변경될 리소스 목록을 확인합니다:
    - **Logical ID**: `DemoBucket`
    - **Action**: `Modify`
    - **Replacement**: `False`

> [!NOTE]
> Resource changes 탭에서는 변경될 리소스의 기본 정보만 표시됩니다.
> 구체적으로 어떤 속성이 어떻게 변경되는지 보려면 JSON changes 탭을 확인해야 합니다.

46. **JSON changes** 탭을 클릭합니다.
47. JSON 형식으로 표시된 상세 변경 내용을 확인합니다:
    - **action**: `Modify`
    - **logicalResourceId**: `DemoBucket`
    - **physicalResourceId**: 실제 버킷 이름 (예: cfn-demo-bucket-123456789012)
    - **resourceType**: `AWS::S3::Bucket`
    - **replacement**: `False`
    - **scope**: `["Tags"]` (태그만 변경됨)
    - **details**: 변경 전후 태그 값 비교
      - **beforeContext**: 기존 태그 (없음)
      - **afterContext**: 새로운 태그 (Name, Project, Week, CreatedBy)

> [!CONCEPT] 변경 세트 정보 해석
> - **Action**: `Modify` - 기존 리소스를 수정합니다. (추가/삭제 아님)
> - **Replacement**: `False` - 리소스가 교체되지 않습니다. (데이터 유지)
> - **Scope**: `["Tags"]` - 태그 속성만 변경됩니다.
> - **Details**: beforeContext와 afterContext로 변경 전후를 비교할 수 있습니다.
> 
> 이 변경은 안전합니다. 기존 버킷에 태그만 추가되고 데이터는 그대로 유지됩니다.
>> 
> **변경 세트 탭 설명:**
> - **Overview**: 변경 세트 상태 및 실행 가능 여부 확인.
> - **Resource changes**: 변경될 리소스 목록 (Logical ID, Action, Replacement만 표시).
> - **JSON changes**: 변경 사항의 상세 내용 (physicalResourceId, scope, beforeContext, afterContext 등 모든 정보).
> - **Template**: 새로운 템플릿 전체 내용.
> - **Input**: 입력한 파라미터 값.

> [!IMPORTANT]
> Replacement가 True인 경우 반드시 데이터 백업을 먼저 수행해야 합니다.
> 특히 데이터베이스, 스토리지 리소스는 신중하게 검토합니다.

48. 변경 내용을 확인한 후 우측 상단의 [[Execute changeset]] 버튼을 클릭합니다.
49. 확인 대화상자가 나타나면 롤백 정책을 확인합니다:
    - **Behaviour on provisioning failure**: `Roll back all stack resources` (기본값, 선택됨)
    - **Delete newly created resources during a rollback**: `Use deletion policy` (기본값, 선택됨)

> [!CONCEPT] 변경 세트 실행 시 롤백 정책
> 
> **Behaviour on provisioning failure** (프로비저닝 실패 시 동작):
> - **Roll back all stack resources**: 실패 시 스택을 마지막으로 알려진 안정 상태로 롤백합니다 (권장).
> - **Preserve successfully provisioned resources**: 성공한 리소스는 유지하고 실패한 리소스만 롤백합니다.
> 
> **Delete newly created resources during a rollback** (롤백 중 새로 생성된 리소스 삭제):
> - **Use deletion policy**: 리소스의 DeletionPolicy 속성에 따라 유지 또는 삭제합니다 (권장).
> - **Delete all newly created resources**: 롤백 시 생성된 모든 리소스를 삭제합니다.
> 
> 이 실습에서는 기본 설정을 사용하며, 실패 시 안전하게 이전 상태로 롤백됩니다.

50. 기본 설정을 유지하고 [[Execute changeset]] 버튼을 클릭합니다.
51. 스택 페이지로 돌아가며 상태가 "UPDATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 업데이트에 1-2분이 소요됩니다. **Events** 탭에서 업데이트 과정을 확인할 수 있습니다.

52. 상태가 "UPDATE_COMPLETE"로 변경될 때까지 기다립니다.
53. **Resources** 탭을 선택합니다.
54. **DemoBucket** 리소스의 **Physical ID**를 클릭합니다.
55. Amazon S3 콘솔에서 **Properties** 탭을 선택합니다.
56. 하단의 **Tags** 섹션으로 스크롤합니다.
57. 템플릿에 정의된 4개의 태그가 있는지 확인합니다:
    - `Name: cfn-demo-bucket-123456789012`
    - `Project: AWS-Lab`
    - `Week: 6-1`
    - `CreatedBy: CloudFormation`

> [!NOTE]
> 태스크 1에서는 콘솔에서 수동으로 스택 태그 3개(Project, Week, CreatedBy)를 추가했습니다.
> 태스크 2에서는 이 태그들을 YAML 파일 코드에 작성하여 Infrastructure as Code 방식으로 전환했습니다.
> 
> 이제 태그가 YAML 파일에 코드로 작성되어 있으므로 버전 관리가 가능하고, 동일한 파일로 여러 환경에 재사용할 수 있습니다.

✅ **태스크 완료**: 변경 세트를 사용한 스택 업데이트(UPDATE) 생명주기를 시연했습니다.

## 태스크 3: 드리프트 감지 - 수동 변경 감지

이 태스크에서는 드리프트 감지 기능을 사용하여 AWS CloudFormation 외부에서 수동으로 변경된 리소스를 찾아냅니다. Amazon S3 콘솔에서 수동으로 태그를 추가한 후 드리프트를 감지합니다.

> [!CONCEPT] 드리프트 (Drift) 감지
> 
> 드리프트는 AWS CloudFormation 템플릿과 실제 리소스 상태의 불일치를 의미합니다.
> AWS 콘솔, CLI, API를 통한 수동 변경으로 발생하며, 인프라 일관성을 해칩니다.
> 
> **드리프트 발생 원인:**
>
> - 개발자가 AWS 콘솔에서 직접 태그를 추가합니다.
> - 운영팀이 보안 그룹 규칙을 수동으로 수정합니다.
> - 자동화 스크립트가 리소스 속성을 변경합니다.
> - 다른 AWS CloudFormation 스택이 동일한 리소스를 수정합니다.
>
> 
> **드리프트 감지 프로세스:**
>
> - **템플릿 비교**: AWS CloudFormation이 템플릿과 실제 리소스를 비교합니다.
> - **차이점 식별**: 각 리소스의 속성을 하나씩 확인하여 차이점을 찾습니다.
> - **상태 업데이트**: 드리프트가 발견되면 스택 상태를 DRIFTED로 변경합니다.
> - **상세 정보 제공**: Expected vs Actual 값을 비교하여 정확한 차이점을 표시합니다.
>

### 상세 단계

#### 1단계: 수동으로 태그 추가 (드리프트 발생)

58. Amazon S3 콘솔로 이동합니다.
59. `cfn-demo-bucket-`로 시작하는 버킷을 선택합니다.
60. **Properties** 탭을 선택합니다.
61. 하단의 **Tags** 섹션으로 스크롤합니다.
62. [[Add new tag]] 버튼을 클릭합니다.
63. 다음 태그를 추가합니다:
	- **Key**: `ManualTag`
	- **Value**: `AddedManually`
64. [[Save changes]] 버튼을 클릭합니다.

> [!NOTE]
> 이 태그는 AWS CloudFormation 템플릿에 정의되지 않았으므로 드리프트가 발생합니다.
> AWS CloudFormation은 이 변경을 인식하지 못하고 있습니다.

#### 2단계: 드리프트 감지 실행

65. AWS CloudFormation 콘솔로 이동합니다.
66. `demo-s3-stack`을 선택합니다.
67. **Stack actions** 드롭다운을 클릭합니다.
68. `Detect drift`를 선택합니다.

> [!NOTE]
> 드리프트 감지가 즉시 시작되며 1-2분이 소요됩니다. AWS CloudFormation이 템플릿과 실제 리소스를 비교합니다.
> 화면 상단에 "Drift detection has been initiated" 메시지가 표시됩니다.

69. 페이지를 새로고침합니다.
70. **Stack info** 탭에서 **Drift status**를 확인합니다.
71. 상태가 "DRIFTED"로 표시되는지 확인합니다.

#### 3단계: 드리프트 상세 정보 확인

72. **Stack actions** 드롭다운을 클릭합니다.
73. `View drift results`를 선택합니다.
74. **Resource drift status** 탭에서 드리프트가 발생한 리소스를 확인합니다.
75. **DemoBucket** 리소스의 **Drift status**가 "DRIFTED"인지 확인합니다.
76. **DemoBucket** 리소스를 선택합니다.
77. [[View drift details]] 버튼을 클릭합니다.
78. 드리프트 차이점을 확인합니다:
	- **Property**: `Tags.1`
	- **Change**: `ADD` (태그 추가됨)
	- **Expected value**: `-` (템플릿에 정의되지 않음)
	- **Current value**: `{"Key":"ManualTag","Value":"AddedManually"}`

> [!NOTE]
> **Details** 섹션에서는 Expected와 Actual의 전체 태그 배열을 JSON 형식으로 비교할 수 있습니다.
> Expected에는 템플릿에 정의된 4개 태그(Name, Project, Week, CreatedBy)가 표시되고, Actual에는 5개 태그(템플릿 4개 + ManualTag 1개)가 표시됩니다.

> [!NOTE]
> 이 데모에서는 드리프트를 수정하지 않고 그대로 둡니다.
> 드리프트 감지의 목적은 변경을 자동으로 수정하는 것이 아니라 관리자에게 알리는 것입니다.
> 
> **드리프트 수정 방법:**
> 
> - **방법 1**: 템플릿에 `ManualTag`를 추가하여 실제 상태를 반영합니다 (권장).
> - **방법 2**: Amazon S3 콘솔에서 `ManualTag`를 삭제하여 템플릿과 일치시킵니다.

✅ **태스크 완료**: 드리프트 감지로 수동 변경을 감지했습니다.

## 리소스 정리

> [!WARNING]
> 이 데모는 비용이 거의 발생하지 않지만, 실습 종료 후 모든 리소스를 삭제하는 것이 좋습니다.

### 1단계: Amazon S3 버킷 비우기 (필요시)

> [!NOTE]
> 이 데모에서는 버킷에 파일을 업로드하지 않았으므로 이 단계는 건너뛸 수 있습니다.
> 
> Amazon S3 버킷에 파일이 있으면 AWS CloudFormation 스택 삭제가 실패합니다.
> 버킷에 파일을 업로드한 경우에만 다음 단계를 수행합니다.

70. Amazon S3 콘솔로 이동합니다.
71. `cfn-demo-bucket-`로 시작하는 버킷을 선택합니다.
72. [[Empty]] 버튼을 클릭합니다.
73. 확인 창에서 `permanently delete`를 입력합니다.
74. [[Empty]] 버튼을 클릭합니다.

### 2단계: AWS CloudFormation 스택 삭제

79. AWS CloudFormation 콘솔로 이동합니다.
80. `demo-s3-stack`을 선택합니다.
81. [[Delete stack]] 버튼을 클릭합니다.
82. 확인 창에서 스택 이름 `demo-s3-stack`을 입력합니다.
83. [[Delete stack]] 버튼을 클릭합니다.
84. 스택 상태가 "DELETE_IN_PROGRESS"로 변경됩니다.
85. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택 삭제에 1-2분이 소요됩니다. **Events** 탭에서 삭제 과정을 확인할 수 있습니다.
> AWS CloudFormation이 Amazon S3 버킷을 삭제하는 과정을 실시간으로 관찰합니다.

86. 페이지를 새로고침합니다.
87. 스택이 목록에서 사라졌는지 확인합니다.

> [!NOTE]
> DELETE_COMPLETE 상태가 되면 스택이 자동으로 목록에서 제거됩니다.
> 이는 스택과 모든 리소스가 성공적으로 삭제되었음을 의미합니다.

### 3단계: 리소스 삭제 확인

88. Amazon S3 콘솔로 이동합니다.
89. `cfn-demo-bucket-`로 시작하는 버킷이 목록에서 사라졌는지 확인합니다.

> [!TIP]
> AWS CloudFormation 스택을 삭제하면 스택이 생성한 모든 리소스(Amazon S3 버킷)가 자동으로 삭제됩니다.
> 수동으로 각 리소스를 삭제할 필요가 없습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 마무리

이 데모에서 다음을 성공적으로 시연했습니다:

- **스택 생성 (CREATE)**: 간단한 Amazon S3 버킷 스택을 생성하고 상태 변화를 관찰했습니다
- **스택 업데이트 (UPDATE)**: Change set preview로 변경 사항을 미리 확인하고 안전하게 업데이트했습니다
- **드리프트 감지**: 수동으로 변경된 리소스를 감지하고 템플릿과의 차이점을 확인했습니다
- **스택 삭제 (DELETE)**: 스택과 모든 리소스를 자동으로 삭제하고 생명주기를 완료했습니다

다음 세션에서는 실제로 AWS CloudFormation 템플릿을 작성하여 Amazon VPC 환경을 구축하는 실습을 진행합니다.

## 추가 학습 리소스

- [AWS CloudFormation 사용 설명서](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/Welcome.html)
- [AWS CloudFormation 템플릿 레퍼런스](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/template-reference.html)
- [AWS CloudFormation 모범 사례](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [변경 세트 사용](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html)
- [드리프트 감지](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html)

## 📚 참고: AWS CloudFormation 핵심 개념

### Infrastructure as Code (IaC)

**IaC란?**
- 인프라를 코드로 정의하고 관리하는 방식입니다.
- 수동 작업 대신 템플릿 파일로 리소스를 생성합니다.
- 버전 관리, 재사용, 자동화가 가능합니다.

**전통적 방식 vs IaC**

| 구분 | 전통적 방식 | Infrastructure as Code |
|------|------------|----------------------|
| **리소스 생성** | AWS 콘솔에서 수동 클릭 | 템플릿 파일로 자동 생성 |
| **일관성** | 사람마다 다르게 설정 가능 | 항상 동일한 결과 보장 |
| **재사용** | 매번 처음부터 다시 생성 | 템플릿 재사용으로 빠른 배포 |
| **버전 관리** | 변경 이력 추적 어려움 | Git 등으로 변경 이력 관리 |
| **문서화** | 별도 문서 작성 필요 | 템플릿 자체가 문서 역할 |
| **오류 가능성** | 수동 작업으로 실수 발생 | 자동화로 실수 최소화 |

**IaC의 장점**
- **속도**: 몇 분 만에 전체 인프라 구축
- **일관성**: 개발/스테이징/프로덕션 환경 동일하게 구성
- **재사용**: 템플릿을 여러 프로젝트에서 재사용
- **버전 관리**: Git으로 인프라 변경 이력 추적
- **협업**: 팀원 간 인프라 코드 공유 및 리뷰
- **자동화**: CI/CD 파이프라인에 통합 가능

### AWS CloudFormation 템플릿 구조

**주요 섹션**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: '템플릿 설명'

Parameters:
  # 사용자 입력값 정의
  BucketPrefix:
    Type: String
    Default: my-bucket
    Description: Amazon S3 버킷 이름 접두사

Resources:
  # 생성할 AWS 리소스 정의
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${BucketPrefix}-${AWS::AccountId}'

Outputs:
  # 스택 생성 후 출력할 값
  BucketName:
    Description: 생성된 버킷 이름
    Value: !Ref MyBucket
```

**섹션별 설명**

| 섹션 | 필수 여부 | 설명 |
|------|----------|------|
| `AWSTemplateFormatVersion` | 선택 | 템플릿 버전 (현재 `2010-09-09`만 지원) |
| `Description` | 선택 | 템플릿 설명 (최대 1024자) |
| `Parameters` | 선택 | 사용자 입력값 정의 (재사용성 향상) |
| `Resources` | **필수** | 생성할 AWS 리소스 정의 |
| `Outputs` | 선택 | 스택 생성 후 출력할 값 (다른 스택에서 참조 가능) |

### AWS CloudFormation 내장 함수

**주요 내장 함수**

| 함수 | 설명 | 예시 |
|------|------|------|
| `!Ref` | 리소스 또는 파라미터 참조 | `!Ref MyBucket` → 버킷 이름 |
| `!Sub` | 문자열 치환 | `!Sub '${BucketPrefix}-${AWS::AccountId}'` |
| `!GetAtt` | 리소스 속성 가져오기 | `!GetAtt MyBucket.Arn` → 버킷 ARN |
| `!Join` | 문자열 결합 | `!Join ['-', [my, bucket, name]]` |
| `!Select` | 리스트에서 값 선택 | `!Select [0, !GetAZs '']` → 첫 번째 AZ |

**예시: !Ref 함수**

```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-demo-bucket

Outputs:
  BucketName:
    Value: !Ref MyBucket  # my-demo-bucket 반환
```

**예시: !Sub 함수**

```yaml
Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'app-${Environment}-${AWS::AccountId}'
      # 결과: app-dev-123456789012
```

**예시: !GetAtt 함수**

```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket

Outputs:
  BucketArn:
    Value: !GetAtt MyBucket.Arn
    # 결과: arn:aws:s3:::my-bucket-name
```

### IaC 도구 비교

**AWS CloudFormation**
- AWS 네이티브 서비스
- JSON/YAML 템플릿 사용
- AWS 리소스만 지원
- 무료 (생성된 리소스만 과금)
- 선언적 방식

**AWS CDK (Cloud Development Kit)**
- 프로그래밍 언어로 인프라 정의 (TypeScript, Python, Java 등)
- AWS CloudFormation으로 변환되어 배포
- 재사용 가능한 컴포넌트 (Constructs)
- 타입 안전성 및 IDE 지원
- 복잡한 로직 구현 가능

**AWS SAM (Serverless Application Model)**
- 서버리스 애플리케이션 전용
- AWS CloudFormation의 확장
- 간소화된 문법
- 로컬 테스트 지원
- AWS Lambda, Amazon API Gateway 등에 최적화

**Terraform**
- 멀티 클라우드 지원 (AWS, Azure, GCP 등)
- HCL 언어 사용
- 상태 파일 관리 필요
- 풍부한 프로바이더 생태계
- 선언적 방식

### 스택 정책 (Stack Policy)

**목적**:
- 중요한 리소스를 실수로 삭제하거나 교체하는 것을 방지합니다.
- 프로덕션 데이터베이스, 스토리지 등을 보호합니다.

**예시**:
```json
{
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": ["Update:Replace", "Update:Delete"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ResourceType": ["AWS::RDS::DBInstance"]
        }
      }
    },
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "Update:*",
      "Resource": "*"
    }
  ]
}
```

**주의사항**:
- 스택 정책은 한 번 설정하면 제거할 수 없습니다.
- 새로운 정책으로 덮어쓰거나 업데이트 시 임시로 재정의할 수 있습니다.
- 스택 삭제는 정책과 무관하게 가능합니다.

### DeletionPolicy 속성

**목적**:
- 스택 삭제 시 특정 리소스의 동작을 제어합니다.

**옵션**:
- `Delete` (기본값): 스택과 함께 리소스 삭제
- `Retain`: 리소스를 보존하고 스택에서만 제거
- `Snapshot`: 삭제 전 스냅샷 생성 (Amazon RDS, EBS 등)

**예시**:
```yaml
Resources:
  MyDatabase:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      # ...

  MyBucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    Properties:
      # ...
```

### 교차 스택 참조 (Cross-Stack Reference)

**목적**:
- 여러 스택 간에 값을 공유합니다.
- 스택을 논리적으로 분리하면서도 연결합니다.

**Export (내보내기)**:
```yaml
Outputs:
  VPCId:
    Description: Amazon VPC ID
    Value: !Ref Amazon VPC
    Export:
      Name: MyVPC-ID
```

**Import (가져오기)**:
```yaml
Resources:
  MySubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !ImportValue MyVPC-ID
```

**장점**:
- 네트워크 스택과 애플리케이션 스택을 분리할 수 있습니다.
- 공통 리소스를 여러 스택에서 재사용할 수 있습니다.
- 스택 간 의존성을 명확히 관리할 수 있습니다.

### 중첩 스택 (Nested Stacks)

**목적**:
- 복잡한 템플릿을 여러 개의 작은 템플릿으로 분리합니다.
- 재사용 가능한 템플릿 컴포넌트를 만듭니다.

**예시**:
```yaml
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/bucket/network-template.yaml
      Parameters:
        VPCCidr: 10.0.0.0/16
```

**장점**:
- 템플릿 크기 제한 (51,200 bytes)을 우회할 수 있습니다.
- 모듈화된 인프라 구성이 가능합니다.
- 팀 간 협업이 용이합니다.

### AWS CloudFormation 모범 사례

**템플릿 작성**:
- 파라미터를 활용하여 재사용 가능한 템플릿을 작성합니다.
- 출력값을 명확히 정의하여 다른 스택에서 참조할 수 있게 합니다.
- 태그를 일관되게 사용하여 리소스를 관리합니다.
- 설명을 추가하여 템플릿의 목적을 명확히 합니다.

**스택 관리**:
- 변경 세트를 사용하여 업데이트 전 변경 사항을 확인합니다.
- 스택 정책으로 중요 리소스를 보호합니다.
- 정기적으로 드리프트 감지를 실행합니다.
- 템플릿을 Git 등의 버전 관리 시스템에 저장합니다.

**보안**:
- AWS IAM 역할을 사용하여 최소 권한 원칙을 적용합니다.
- AWS Secrets Manager나 Parameter Store를 사용하여 민감한 정보를 관리합니다.
- 퍼블릭 액세스가 필요 없는 리소스는 프라이빗으로 유지합니다.

**비용 최적화**:
- 개발 환경은 필요할 때만 생성하고 사용 후 삭제합니다.
- 리소스 태그를 사용하여 비용을 추적합니다.
- 불필요한 리소스는 즉시 삭제합니다.
