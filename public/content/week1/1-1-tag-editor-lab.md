---
title: 'AWS Resource Groups & Tag Editor를 활용한 리소스 관리'
week: 1
session: 1
awsServices:
  - AWS Resource Groups & Tag Editor
learningObjectives:
  - AWS 리소스 태그의 개념과 중요성을 이해할 수 있습니다.
  - Tag Editor를 사용하여 리소스를 검색하고 관리할 수 있습니다.
  - Resource Groups를 생성하여 관련 리소스를 그룹화할 수 있습니다.
  - 태그 기반 리소스 정리 방법을 학습할 수 있습니다.
prerequisites:
  - AWS Management Console 기본 사용법
  - AWS 계정 및 로그인 정보
  - AWS IAM 권한: AWS CloudFormation, Amazon S3, AWS Lambda, Amazon DynamoDB, AWS IAM 리소스 생성 권한
  - 기본 리전: ap-northeast-2 (서울)
---

> [!DOWNLOAD]
> [week1-1-tag-editor-lab.zip](/files/week1/week1-1-tag-editor-lab.zip)
>
> - `week1-1-tag-editor-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 QuickTable 리소스 자동 생성: Amazon S3 버킷 2개, AWS Lambda 함수 1개, Amazon DynamoDB 테이블 1개, AWS IAM 역할 1개)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (`week1-1-tag-editor-lab.yaml` 파일을 사용하여 AWS CloudFormation 스택 생성)

이 데모에서는 **AWS Resource Groups & Tag Editor**를 사용하여 태그 기반으로 리소스를 검색하고 관리하는 방법을 학습합니다.  
태그는 AWS 리소스 관리의 핵심 도구입니다.

> [!CONCEPT] AWS 리소스 태그 (Resource Tags)
> AWS 리소스 태그는 리소스를 분류하고 추적하는 데 사용되는 키-값 쌍입니다.
>
> **주요 활용 사례**:
>
> - 프로젝트별, 환경별, 비용 센터별로 리소스 구분
> - AWS Cost Explorer에서 태그별 비용 분석
> - Tag Editor로 특정 태그를 가진 리소스 빠르게 검색
> - Resource Groups로 관련 리소스 논리적 그룹화

> [!CONCEPT] AWS Resource Groups & Tag Editor
> **AWS Resource Groups & Tag Editor**는 여러 AWS 서비스의 리소스를 한 곳에서 검색하고 태그를 관리할 수 있는 통합 도구입니다.
>
> **Tag Editor 기능**:
>
> - 여러 리전의 리소스를 한 번에 검색
> - 여러 AWS 서비스의 리소스를 통합 검색
> - 태그 키와 값으로 필터링
> - 여러 리소스에 동시에 태그 추가/수정/삭제
>
> **Resource Groups 기능**:
>
> - 태그 기반 동적 그룹 생성
> - Amazon CloudWatch 대시보드와 통합하여 그룹 단위 모니터링
> - AWS Systems Manager와 통합하여 그룹 단위 자동화

AWS CloudFormation을 사용하여 QuickTable 레스토랑 예약 시스템의 기본 AWS 리소스(Amazon S3 버킷, AWS Lambda 함수, Amazon DynamoDB 테이블)를 자동으로 생성하고, 이 리소스들에 태그를 추가합니다. AWS CloudFormation은 인프라를 코드로 관리할 수 있게 해주는 서비스로, 템플릿 파일 하나로 여러 리소스를 일관되게 생성하고 관리할 수 있습니다.

**AWS Resource Groups & Tag Editor**로 태그 기반 검색을 수행하고, Resource Groups를 생성하여 관련 리소스를 그룹화합니다. 이 데모를 통해 앞으로 진행할 모든 실습에서 리소스를 효율적으로 관리하고 정리하는 방법을 익힐 수 있습니다.

> [!NOTE]
> 이 데모는 AWS 리소스를 생성하지만, AWS 프리티어 범위 내에서 사용 가능하며 비용이 거의 발생하지 않습니다.  
> Amazon S3 버킷, AWS Lambda 함수, Amazon DynamoDB 테이블은 사용하지 않으면 비용이 발생하지 않습니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 QuickTable 레스토랑 예약 시스템의 기본 AWS 리소스를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷 2개**: 예약 데이터 저장용 버킷 (quicktable-reservations-{고유접미사}), 로그 저장용 버킷 (quicktable-logs-{고유접미사})
- **AWS Lambda 함수 1개**: 예약 조회 함수 (QuickTableGetReservation)
- **Amazon DynamoDB 테이블 1개**: 예약 데이터 테이블 (QuickTableReservations)
- **AWS IAM 역할 1개**: AWS Lambda 함수 실행 역할 (QuickTableLambdaExecutionRole)

모든 리소스에는 `Week=1-1` 태그가 자동으로 추가되어 나중에 Tag Editor로 쉽게 찾을 수 있습니다.

> [!NOTE]
> Amazon S3 버킷 이름은 전 세계적으로 고유해야 하므로, AWS CloudFormation이 자동으로 고유 접미사를 추가합니다. 예: `quicktable-reservations-a1b2c3d4e5f6`. 태스크 0의 **Outputs** 탭에서 정확한 버킷 이름을 확인할 수 있습니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week1-1-tag-editor-lab.zip` 파일의 압축을 해제합니다.
2. `week1-1-tag-editor-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

   <img src="/images/week1/1-1-task0-step4-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

> [!TIP]
> **다른 방법**:
>
> AWS Management Console 상단 검색창에서 `CloudFormation`을 검색한 후 검색 결과에서 바로 **Create stack**을 선택하는 방법도 있습니다.
>
> <img src="/images/week1/1-1-task0-step4-search-create-stack.png" alt="검색창에서 CloudFormation Create stack 바로 선택" class="guide-img-md" />

5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 **week1-1-tag-editor-lab.yaml** 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.

   <img src="/images/week1/1-1-task0-step8-next-button.png" alt="CloudFormation 템플릿 업로드 후 Next 버튼 클릭" class="guide-img-md" />

9. **Stack name**에 `week1-1-tag-editor-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다.
11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week1/1-1-task0-step11-next-button.png" alt="CloudFormation 스택 이름 입력 후 Next 버튼 클릭" class="guide-img-md" />

12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 찾습니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `CreatedBy` | `Student` |

> [!NOTE]
> **AWS CloudFormation 템플릿 태그**: AWS CloudFormation 템플릿은 모든 리소스에 필수 태그 3개(`Project`, `Week`, `CreatedBy`)와 추가 태그(`Component`)를 자동으로 추가했습니다. 이 태스크에서는 이미 추가된 태그를 확인하고, 실습 목적으로 추가 태그를 수동으로 추가하는 방법을 학습합니다.

> [!NOTE]
> **스택 레벨 태그 전파**: 태스크 0에서 AWS CloudFormation 스택에 추가한 `Project`와 `CreatedBy` 태그는 태그 전파를 지원하는 일부 리소스에 자동으로 전파될 수 있습니다. 이 실습에서는 템플릿 레벨 태그와 스택 레벨 태그의 차이를 이해하고, 수동 태그 추가 방법을 학습하는 것이 목적입니다.

14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation may create AWS IAM resources`를 체크합니다.
15. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week1/1-1-task0-step15-next-button.png" alt="CloudFormation Capabilities 체크 후 Next 버튼 클릭" class="guide-img-md" />

16. **Review** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

    <img src="/images/week1/1-1-task0-step17-submit-button.png" alt="CloudFormation Review 페이지에서 Submit 버튼 클릭" class="guide-img-md" />

18. 스택 생성이 시작됩니다. 상태가 "**CREATE_IN_PROGRESS**"로 표시됩니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
    <img src="/images/week1/1-1-task0-step19-stack-complete.png" alt="CloudFormation 스택 생성 완료 상태" class="guide-img-md" />
20. **Outputs** 탭을 선택합니다.
21. 출력값들을 확인하고 메모장에 복사합니다:
    <img src="/images/week1/1-1-task0-step21-outputs.png" alt="CloudFormation 스택 Outputs 탭의 출력값" class="guide-img-md" />
    - `GetReservationFunctionName`: QuickTable 예약 조회 AWS Lambda 함수 이름
    - `LogsBucketName`: QuickTable 로그 버킷 이름 (예: quicktable-logs-a1b2c3d4e5f6)
    - `ReservationsBucketName`: QuickTable 예약 데이터 버킷 이름 (예: quicktable-reservations-a1b2c3d4e5f6)
    - `ReservationsTableName`: QuickTable 예약 Amazon DynamoDB 테이블 이름

> [!IMPORTANT]
> 이 출력값들은 태스크 1에서 사용됩니다. 반드시 메모장에 저장합니다.
> 특히 버킷 이름은 고유 접미사가 포함되어 있으므로 정확한 이름을 복사해야 합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon S3 버킷에 태그 추가

이 태스크에서는 AWS CloudFormation으로 생성된 Amazon S3 버킷의 태그를 확인하고, 추가 태그를 수동으로 추가하는 방법을 학습합니다. 태그는 키-값 쌍으로 구성되며, 리소스를 분류하고 관리하는 데 사용됩니다.

> [!NOTE]
> **AWS CloudFormation 템플릿 태그**: AWS CloudFormation 템플릿은 모든 리소스에 `Week=1-1` 태그를 자동으로 추가했습니다.  
> 이 태스크에서는 이미 추가된 태그를 확인하고, 실습 목적으로 추가 태그(`Environment`, `Owner`)를 수동으로 추가하는 방법을 학습합니다.

### 첫 번째 버킷: Amazon S3 콘솔에서 태그 추가

22. AWS Management Console에 로그인한 후 상단 검색창에 `S3`을 입력하고 선택합니다.
23. 왼쪽 메뉴에서 **General purpose buckets**를 선택합니다.
24. 태스크 0의 Outputs에서 복사한 `ReservationsBucketName` 값을 사용하여 버킷을 찾습니다.
   <img src="/images/week1/1-1-task1-step3-bucket-search.png" alt="S3 콘솔에서 버킷 검색" class="guide-img-md" />

> [!TIP]
> 버킷이 많은 경우 검색창에 복사한 버킷 이름을 붙여넣어 필터링합니다.

25. 해당 버킷을 선택합니다.
26. **Properties** 탭을 선택합니다.
27. 아래로 스크롤하여 **Tags** 섹션을 찾습니다.
28. 기존 태그를 확인합니다.
   <img src="/images/week1/1-1-task1-step7-tags-section.png" alt="S3 버킷의 Tags 섹션" class="guide-img-md" />

> [!NOTE]
> AWS CloudFormation 템플릿이 추가한 `Week=1-1` 태그가 이미 존재합니다. 여기에 추가 태그를 수동으로 추가합니다.

29. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key           | Value         |
| ------------- | ------------- |
| `Environment` | `Development` |
| `Owner`       | `TeamA`       |

30. [[Save changes]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-task1-step9-add-tag.png" alt="S3 버킷에 태그 추가" class="guide-img-md" />
   <img src="/images/week1/1-1-task1-step9-add-tag-2.png" alt="S3 버킷 태그 저장" class="guide-img-md" />

✅ **태스크 완료**: 첫 번째 Amazon S3 버킷에 태그가 추가되었습니다.

## 태스크 2: Tag Editor로 두 번째 버킷에 태그 일괄 추가

이 태스크에서는 **AWS Resource Groups & Tag Editor**를 사용하여 두 번째 Amazon S3 버킷에 태그를 일괄 추가합니다. Tag Editor는 여러 리소스에 동시에 태그를 추가할 수 있는 강력한 도구로, 대규모 리소스 관리 시 매우 유용합니다.

### Tag Editor로 리소스 검색

31. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
32. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
33. **Regions**에서 `All regions`를 선택합니다.
34. **Resource types**에서 `AWS::Amazon S3::Bucket`을 선택합니다.
35. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `1-1`
36. [[Search resources]] 버튼을 클릭합니다.
37. 검색 결과에서 2개의 버킷이 표시됩니다.
38. **Tags** 열에서 `quicktable-reservations-{접미사}` 버킷의 태그 개수를 클릭합니다.
   <img src="/images/week1/1-1-task2-step8-tags-popup.png" alt="Tag Editor 검색 결과에서 태그 개수 클릭" class="guide-img-sm" />

> [!NOTE]
> **Tags** 열에 표시된 숫자(예: 6)를 클릭하면 해당 리소스의 상세 태그 목록을 확인할 수 있습니다.

39. 태그 목록을 확인합니다.
   <img src="/images/week1/1-1-task2-step9-tags-detail.png" alt="첫 번째 버킷의 태그 상세 목록" class="guide-img-sm" />

> [!OUTPUT]
>
> ```
> Custom tags:
> - Component: Storage
> - CreatedBy: Student
> - Environment: Development
> - Owner: TeamA
> - Project: AWS-Lab
> - Week: 1-1
> ```

40. 팝업 창을 닫습니다.
41. **Tags** 열에서 `quicktable-logs-{접미사}` 버킷의 태그 개수를 클릭합니다.
42. 태그 목록을 확인합니다.
    <img src="/images/week1/1-1-task2-step12-logs-bucket-tags-detail.png" alt="두 번째 버킷의 태그 상세 목록" class="guide-img-sm" />

> [!OUTPUT]
>
> ```
> Custom tags:
> - Component: Logging
> - CreatedBy: Student
> - Project: AWS-Lab
> - Week: 1-1
>
> 두 번째 버킷(logs)에는 Environment와 Owner 태그가 없습니다.
> ```

43. 팝업 창을 닫습니다.

### Tag Editor로 태그 일괄 추가

44. 검색 결과에서 `quicktable-logs-{접미사}` 버킷을 체크합니다.

> [!TIP]
> 태스크 0의 Outputs에서 복사한 `LogsBucketName` 값과 일치하는 버킷을 선택합니다.

> [!NOTE]
> Tag Editor에서는 여러 리소스를 동시에 선택하여 태그를 일괄 추가할 수 있습니다.  
> 예를 들어, 2개의 버킷을 모두 선택한 후 동일한 태그를 한 번에 추가할 수 있습니다.  
> 이 실습에서는 로그 버킷 1개만 선택하지만, 실무에서는 수십 개의 리소스를 동시에 선택하여 효율적으로 태그를 관리할 수 있습니다.

45. [[Manage tags of selected resources]] 버튼을 클릭합니다.
    <img src="/images/week1/1-1-task2-step15-manage-tags.png" alt="Manage tags of selected resources 버튼" class="guide-img-sm" />

> [!NOTE]
> Tag Editor UI는 주기적으로 업데이트됩니다. "Edit tags of selected resources" 또는 유사한 버튼이 표시될 수 있습니다.

46. **Edit tags of all selected resources** 섹션에서 [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key          | Value         |
| ------------ | ------------- |
| `CostCenter` | `CC-1001`     |
| `Department` | `Engineering` |

47. [[Review and apply tag changes]] 버튼을 클릭합니다.
    <img src="/images/week1/1-1-task2-step17-review-changes.png" alt="Review and apply tag changes 버튼" class="guide-img-md" />

> [!NOTE]
> Tag Editor UI는 주기적으로 업데이트됩니다. "Review and apply changes" 또는 유사한 버튼이 표시될 수 있습니다.

48. 확인 창에서 추가될 태그를 확인합니다.

> [!OUTPUT]
>
> ```
> Apply tag changes to the selected resource
>
> The following tags will be applied to the selected resource:
> - CostCenter: CC-1001
> - Department: Engineering
> ```

49. [[Apply changes to all selected]] 버튼을 클릭합니다.
    <img src="/images/week1/1-1-task2-step19-apply-changes.png" alt="Apply changes to all selected 버튼" class="guide-img-sm" />

> [!NOTE]
> 버튼명은 "Apply" 또는 "Save"로 표시될 수 있습니다.

50. 태그 추가가 완료될 때까지 기다립니다.
    <img src="/images/week1/1-1-task2-step20-tag-complete.png" alt="태그 추가 완료 화면" class="guide-img-sm" />

> [!SUCCESS]
> Tag Editor를 사용하여 두 번째 Amazon S3 버킷에 태그를 일괄 추가했습니다.

✅ **태스크 완료**: Tag Editor로 두 번째 버킷에 태그가 추가되었습니다.

## 태스크 3: Tag Editor로 모든 리소스 검색

이 태스크에서는 **Tag Editor**를 사용하여 이 실습에서 생성한 모든 리소스를 검색합니다. Tag Editor는 여러 AWS 서비스의 리소스를 한 곳에서 검색할 수 있는 통합 도구로, 특정 태그를 가진 모든 리소스를 빠르게 찾을 수 있습니다.

51. Tag Editor 페이지에서 검색 조건을 초기화합니다.
52. **Regions**에서 `All regions`를 선택합니다.
53. **Resource types**에서 `All supported resource types`를 선택합니다.
54. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `1-1`
55. [[Search resources]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-task3-step5-search-results.png" alt="Tag Editor 검색 결과 - Week=1-1 태그를 가진 모든 리소스" class="guide-img-sm" />

> [!IMPORTANT]
> **All regions 선택 이유**: AWS IAM 역할은 글로벌 리소스이지만, Tag Editor에서 항상 검색되지는 않습니다.  
> All regions를 선택하면 리전별 리소스(Amazon S3, AWS Lambda, Amazon DynamoDB)를 확실하게 검색할 수 있습니다.

> [!OUTPUT]
>
> ```
> 다음 리소스가 표시됩니다:
> - Amazon S3 버킷 2개 (quicktable-reservations-xxx, quicktable-logs-xxx)
> - AWS Lambda 함수 1개 (QuickTableGetReservation)
> - Amazon DynamoDB 테이블 1개 (QuickTableReservations)
>
> 총 4개의 리소스가 Week=1-1 태그를 가지고 있습니다.
> ```

> [!NOTE]
> **IAM Role이 검색되지 않는 이유**: AWS IAM은 글로벌 서비스이며, Tag Editor의 IAM 리소스 인덱싱이 제한적입니다.  
> IAM Role에 태그가 있어도 Tag Editor 검색 결과에 나타나지 않을 수 있습니다. IAM Role의 태그는 IAM 콘솔에서 직접 확인할 수 있습니다.

> [!IMPORTANT]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

56. 검색 결과에서 리소스 타입, 리소스 이름, 태그 정보를 확인합니다.
57. 각 리소스를 선택하여 태그 상세 정보를 확인합니다.

> [!TIP]
> 두 Amazon S3 버킷 모두 이제 Week=1-1, Project=AWS-Lab, CreatedBy=Student 태그를 가지고 있습니다.  
> AWS CloudFormation 시스템 태그(aws:cloudformation:stack-name 등)가 추가로 표시될 수 있습니다.

✅ **태스크 완료**: Tag Editor로 모든 리소스를 검색했습니다.

## 태스크 4: Resource Groups 생성

이 태스크에서는 Resource Groups를 생성하여 관련 리소스를 그룹화합니다. Resource Groups는 태그 기반으로 리소스를 논리적으로 그룹화하여 한 곳에서 관리할 수 있게 해줍니다. 프로젝트별, 환경별, 팀별로 리소스를 그룹화하면 모니터링, 자동화, 비용 추적이 용이해집니다.

58. 왼쪽 메뉴에서 **AWS Resource Groups**를 선택합니다.
59. [[Create resource group]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-task4-step2-create-group.png" alt="왼쪽 메뉴에서 Create Resource Group 선택" class="guide-img-sm" />
60. **Group type**에서 `Tag based`를 선택합니다.
61. **Grouping criteria** 섹션에서 다음을 입력합니다:
    - **Resource types**: `All supported resource types` (기본값)
    - **Tag key**: `Week`
    - **Tag value**: `1-1`
62. 아래로 스크롤하여 [[Preview group resources]] 버튼을 클릭합니다.

> [!NOTE]
> 💡 Resource Groups 콘솔 UI는 주기적으로 업데이트됩니다. "Preview group resources" 또는 "View group resources" 버튼이 표시될 수 있습니다.
>
> 💡 Week=1-1 태그를 가진 모든 리소스가 미리보기에 표시됩니다: Amazon S3 버킷 2개, AWS Lambda 함수 1개, Amazon DynamoDB 테이블 1개.

63. **Group details** 섹션에서 다음을 입력합니다:
    - **Group name**: `week1-1-lab-resources`
    - **Group description**: `Week 1-1 Tag Editor Lab Resources`
64. [[Create group]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-task4-step7-create-group-button.png" alt="Create group 버튼" class="guide-img-sm" />

> [!TIP]
> Resource Groups 생성 시 **Group tags (Optional)** 기능을 사용하면 Resource Group 자체에 태그를 추가할 수 있습니다.  
> 이를 통해 여러 Resource Groups를 태그 기반으로 분류하고 관리할 수 있습니다.  
> 예를 들어, 프로젝트별, 환경별로 Resource Groups를 그룹화하여 일괄 관리할 수 있습니다.

✅ **태스크 완료**: Resource Groups가 생성되었습니다.

## 태스크 5: Resource Groups에서 리소스 확인

이 태스크에서는 생성한 Resource Groups에서 그룹화된 리소스를 확인합니다. Resource Groups를 통해 관련 리소스를 한눈에 파악하고 관리할 수 있습니다.

65. 왼쪽 메뉴에서 **Saved resource groups**를 선택합니다.
66. `week1-1-lab-resources` 그룹을 선택합니다.
   <img src="/images/week1/1-1-task5-step2-select-group.png" alt="week1-1-lab-resources 그룹 선택" class="guide-img-sm" />
67. **Resources** 탭에서 그룹에 포함된 리소스 목록을 확인합니다.
68. 각 리소스의 타입, 이름, 리전, 태그 정보를 확인합니다.
   <img src="/images/week1/1-1-task5-step4-resource-details.png" alt="Resource Groups에 포함된 리소스 목록" class="guide-img-sm" />

✅ **태스크 완료**: Resource Groups에서 리소스를 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 QuickTable 예약 시스템의 기본 AWS 리소스를 자동 생성했습니다.
- Amazon S3 콘솔에서 첫 번째 버킷에 태그를 직접 추가했습니다.
- Tag Editor로 두 번째 버킷에 태그를 일괄 추가했습니다.
- Tag Editor로 태그 기반 리소스 검색을 수행했습니다.
- Resource Groups를 생성하여 관련 리소스를 그룹화했습니다.

> [!TIP]
> 이후 모든 실습에서 동일한 리소스 정리 패턴을 사용합니다.  
> 🗑️ Tag Editor로 Week 태그 검색 → 리소스 확인 → AWS CloudFormation 스택 삭제 → Resource Groups 삭제  
> 이 패턴을 숙지하면 리소스 삭제 누락을 방지할 수 있습니다.

---

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

## 1단계: 생성된 리소스 확인 (Tag Editor)

실습에서 생성한 모든 리소스를 확인합니다.

69. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
70. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
71. **Regions**에서 `All regions`를 선택합니다.
72. **Resource types**에서 `All supported resource types`를 선택합니다.
73. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `1-1`
74. [[Search resources]] 버튼을 클릭합니다.
75. 이 실습에서 생성한 모든 QuickTable 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 **찾는 용도**로만 사용됩니다.
> 실제 삭제는 2단계에서 수행합니다.

## 2단계: 리소스 삭제

### AWS CloudFormation 스택 삭제

이 실습에서는 추가로 리소스를 만들지 않았기 때문에 AWS CloudFormation 스택을 삭제하면 태스크 0에서 생성한 모든 리소스가 자동으로 삭제됩니다.

76. AWS CloudFormation 콘솔로 이동합니다.
77. 왼쪽 메뉴에서 **Stacks**를 선택합니다.
78. `week1-1-tag-editor-lab-stack` 스택을 선택합니다.
79. [[Delete stack]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-cleanup-step4-delete-stack.png" alt="CloudFormation 스택 Delete 버튼" class="guide-img-sm" />
80. 확인 창이 나타나면 입력 필드에 삭제할 스택 이름을 입력합니다.

> [!NOTE]
> 입력 필드 위에 "Type "{스택이름}" to confirm deletion of the stack" 메시지가 표시됩니다. 이 메시지에 표시된 스택 이름을 정확히 입력해야 합니다. 이번 실습에서는 `week1-1-tag-editor-lab-stack`을 입력합니다.

81. [[Delete stack]] 버튼을 클릭합니다.
   <img src="/images/week1/1-1-cleanup-step6-delete-stack-button.png" alt="스택 삭제 확인 후 Delete stack 버튼 클릭" class="guide-img-sm" />
82. 스택 삭제가 완료될 때까지 기다립니다.
   <img src="/images/week1/1-1-cleanup-step7-stack-deleting.png" alt="CloudFormation 스택 삭제 진행 중" class="guide-img-md" />

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다.  
> AWS CloudFormation 스택을 삭제하면 QuickTable Amazon S3 버킷, AWS Lambda 함수, Amazon DynamoDB 테이블, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

> [!NOTE]
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제가 실패할 수 있습니다.  
> 이 실습에서는 버킷에 파일을 업로드하지 않았으므로 정상적으로 삭제됩니다. 만약 스택 삭제 실패 시 Amazon S3 콘솔에서 해당 버킷을 먼저 비운 후 스택 삭제를 재시도합니다.

### Resource Groups 삭제

Resource Groups는 리소스를 그룹화하는 논리적 컨테이너이므로 AWS CloudFormation 스택 삭제 후 별도로 삭제해야 합니다.

83. AWS Management Console 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
84. 왼쪽 메뉴에서 **Saved resource groups**를 선택합니다.
85. `week1-1-lab-resources` 그룹 이름을 클릭하거나 그룹을 선택한 후 [[View details]] 버튼을 클릭합니다.
86. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week1/1-1-cleanup-step11-rg-delete.png" alt="Resource Group Delete 버튼" class="guide-img-md" />
87. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week1/1-1-cleanup-step12-rg-delete-confirm.png" alt="Resource Group 삭제 확인 대화상자" class="guide-img-sm" />

> [!IMPORTANT]
> Resource Groups는 AWS CloudFormation 스택 삭제로 함께 제거되지 않으므로 반드시 별도로 삭제해야 합니다.

## 3단계: 삭제 확인

모든 리소스가 삭제되었는지 확인합니다.

88. Tag Editor로 이동합니다.
89. **Regions**에서 `All regions`를 선택합니다.
90. **Resource types**에서 `All supported resource types`를 선택합니다.
91. **Tags** 섹션에서 다음 태그를 입력합니다:
    - **Tag key**: `Week`
    - **Optional tag value**: `1-1`
92. [[Search resources]] 버튼을 클릭합니다.
93. 검색 결과가 비어있는지 확인합니다.
   <img src="/images/week1/1-1-cleanup-step3-6-search-empty.png" alt="Tag Editor 검색 결과가 비어있는 화면" class="guide-img-md" />

> [!NOTE]
> 리소스가 삭제되면 태그도 함께 제거되므로 Tag Editor에서 검색 결과가 비어있으면 정상적으로 삭제된 것입니다.  
> AWS IAM 역할은 Tag Editor에서 검색되지 않으므로, AWS CloudFormation 스택으로 생성하지 않은 AWS IAM 역할이 있다면 AWS IAM 콘솔에서 직접 삭제하는 것을 권장합니다.

> [!SUCCESS]
> 검색 결과가 비어있으면 모든 리소스가 정상적으로 삭제되었습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Tag Editor 모범 사례 및 전략](https://docs.aws.amazon.com/ko_kr/tag-editor/latest/userguide/best-practices-and-strats.html)
- [Tag Editor 사용 가이드](https://docs.aws.amazon.com/ko_kr/tag-editor/latest/userguide/tag-editor.html)
- [Resource Groups 개요](https://docs.aws.amazon.com/ko_kr/ARG/latest/userguide/resource-groups.html)

## 📚 참고: AWS 리소스 태그 전략

### 태그의 중요성

AWS 태그는 리소스를 효과적으로 관리하기 위한 핵심 도구입니다. 태그를 통해 다음을 수행할 수 있습니다:

**리소스 분류 및 검색**

- 프로젝트별, 환경별, 팀별로 리소스 그룹화
- Tag Editor로 특정 태그를 가진 리소스 빠르게 검색
- Resource Groups로 관련 리소스 논리적 그룹화

**비용 추적 및 최적화**

- AWS Cost Explorer에서 태그별 비용 분석
- 프로젝트별, 부서별 비용 할당
- 예산 알림 설정 시 태그 기반 필터링

**자동화 및 운영**

- AWS Systems Manager에서 태그 기반 자동화
- AWS Lambda 함수에서 태그 기반 리소스 관리
- Amazon CloudWatch 알람에서 태그 기반 모니터링

### 표준 태그 전략

이 강의에서 사용하는 표준 태그 3개:

| Tag Key     | Tag Value       | 설명                             |
| ----------- | --------------- | -------------------------------- |
| `Project`   | `AWS-Lab`       | 프로젝트 식별자 (고정값)         |
| `Week`      | `{주차}-{세션}` | 주차 및 세션 번호 (예: 1-1, 5-3) |
| `CreatedBy` | `Student`       | 생성자 구분 (고정값)             |

**태그 명명 규칙**:

- Tag Key는 PascalCase 사용 (Project, Week, CreatedBy)
- Tag Value는 간결하고 명확하게 작성
- 일관성 유지가 가장 중요

### Tag Editor 활용

**검색 기능**

- 여러 리전의 리소스를 한 번에 검색
- 여러 AWS 서비스의 리소스를 통합 검색
- 태그 키와 값으로 필터링

**일괄 태그 관리**

- 여러 리소스에 동시에 태그 추가/수정/삭제
- 태그 표준화 및 정리 작업 효율화
- 태그 규칙 준수 확인

**제한사항**

| 제한사항               | 설명                                                                                                              |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 검색 및 태그 관리 전용 | Tag Editor는 리소스를 찾고 태그를 관리하는 용도로만 사용됩니다.                                                   |
| 리소스 삭제 불가       | 실제 리소스 삭제는 각 서비스 콘솔에서 수행해야 합니다.                                                            |
| 일부 리소스 미지원     | 모든 AWS 리소스 타입을 지원하지는 않습니다.                                                                       |
| 리전 선택 필요         | 특정 리전 또는 All regions를 선택하여 검색합니다. 글로벌 리소스(AWS IAM 등)는 All regions 선택 시에만 표시됩니다. |

### Resource Groups 활용

**그룹 타입**

- **Tag based**: 태그 기반 동적 그룹 (태그가 일치하는 리소스 자동 포함)
- **AWS CloudFormation stack based**: AWS CloudFormation 스택 기반 그룹

**통합 기능**

- Amazon CloudWatch 대시보드: 그룹 단위 모니터링
- AWS Systems Manager: 그룹 단위 자동화 및 패치 관리
- AWS Config: 그룹 단위 규정 준수 확인

**모범 사례**

- 프로젝트별, 환경별, 애플리케이션별로 그룹 생성
- 명확한 그룹 이름과 설명 사용
- 정기적으로 그룹 멤버십 검토

### 태그 기반 리소스 정리

**실습 종료 시 리소스 정리 프로세스**:

94. Tag Editor로 Week 태그 검색 (예: Week=1-1)
95. 해당 주차에서 생성한 모든 리소스 확인
96. AWS CloudFormation 스택 삭제 (자동 생성 리소스)
97. Resource Groups 삭제 (별도 삭제 필요)
98. Tag Editor로 삭제 확인

**장점**:

- 실습에서 생성한 리소스를 빠르게 찾을 수 있음
- 삭제 누락 방지
- 불필요한 비용 발생 방지
