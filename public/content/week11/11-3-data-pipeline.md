---
title: 'AWS Glue를 활용한 데이터 파이프라인 구축'
week: 11
session: 3
awsServices:
  - AWS Glue
  - Amazon Athena
  - Amazon S3
  - AWS Lambda
  - Amazon EventBridge
learningObjectives:
  - AWS Glue Database를 생성하고 Crawler를 구성하여 Amazon S3 데이터의 스키마를 자동으로 추론하고 Data Catalog 테이블을 생성할 수 있습니다.
  - AWS Glue Visual ETL Job을 생성하여 CSV 데이터를 Parquet 형식으로 변환하는 ETL 파이프라인을 구성할 수 있습니다.
  - Amazon Athena로 변환된 데이터를 SQL로 쿼리하고 분석할 수 있습니다.
  - Amazon EventBridge와 AWS Lambda를 활용한 이벤트 기반 데이터 파이프라인 자동화 흐름을 이해할 수 있습니다.

prerequisites:
  - Amazon S3 기본 개념 이해.
  - SQL 쿼리 기본 지식.
  - CSV/JSON 데이터 형식 이해.
  - Week 11-2 실습 완료 (AWS Glue, Amazon Athena 기본 사용법).
---

이 실습에서는 **AWS Glue**와 **Amazon Athena**를 활용하여 **서버리스 데이터 파이프라인**을 구축합니다.

먼저 **AWS CloudFormation**을 사용하여 **Amazon S3 버킷**, **AWS IAM 역할**, **AWS Lambda 함수**, **Amazon EventBridge 규칙**, **샘플 데이터**를 자동으로 생성합니다. 그런 다음 학생이 직접 **AWS Glue Database**를 생성하고, **Crawler**를 구성하여 Amazon S3 데이터의 메타데이터를 수집합니다.

이후 **AWS Glue Visual ETL**을 사용하여 **CSV 데이터를 Parquet 형식으로 변환**하는 ETL Job을 직접 구성하고 실행합니다. 변환된 데이터를 **Amazon Athena**로 쿼리하여 분석한 후, 새로운 데이터를 업로드하여 **Amazon EventBridge**와 **AWS Lambda**가 자동으로 Crawler를 트리거하는 **이벤트 기반 파이프라인 흐름**을 확인합니다.

> [!CONCEPT] ETL과 데이터 파이프라인
> **ETL(Extract, Transform, Load)**은 데이터를 추출하고 변환하여 적재하는 프로세스입니다.
>
> - **Extract**: 소스(Amazon S3, 데이터베이스 등)에서 원시 데이터를 추출합니다
> - **Transform**: 데이터 형식 변환, 정제, 집계 등을 수행합니다 (예: CSV → Parquet)
> - **Load**: 변환된 데이터를 대상 저장소에 적재합니다
>
> **Parquet 형식의 장점**:
>
> - 열 기반(Columnar) 저장으로 분석 쿼리 성능이 우수합니다
> - 압축 효율이 높아 스토리지 비용을 절감합니다
> - Amazon Athena, Amazon Redshift 등 분석 서비스와 호환됩니다

> [!NOTE]
> **이 실습의 자동화 범위**:
>
> - ✅ **자동**: Amazon S3 업로드 → Amazon EventBridge → AWS Lambda → Crawler 실행
> - ⚠️ **수동**: ETL Job 실행 (태스크 3에서 직접 실행)
>
> 완전 자동화를 위해서는 Crawler 완료 후 ETL Job을 트리거하는 추가 AWS Lambda 함수나 AWS Step Functions 워크플로우가 필요합니다.

> [!NOTE]
> 이 실습에서는 **거래 데이터(transactions.csv)**를 사용합니다. 이전 실습(Week 11-2)의 QuickTable 예약 데이터와는 다른 데이터셋입니다. 거래 데이터는 일반적인 전자상거래 트랜잭션을 나타내며, 데이터 파이프라인 구축 학습에 적합합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

> [!DOWNLOAD]
> [week11-3-data-pipeline-lab.zip](/files/week11/week11-3-data-pipeline-lab.zip)
>
> - `week11-3-data-pipeline-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, AWS IAM 역할, AWS Lambda 함수, Amazon EventBridge 규칙, 샘플 데이터 자동 생성)
> - `lambda_function.py` - AWS Lambda 함수 소스 코드 (참고용, CloudFormation이 자동 배포)
> - `sales-data.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)
> - `sales-data-2.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿으로 Amazon S3, AWS IAM 역할, AWS Lambda, Amazon EventBridge 규칙, 샘플 데이터 자동 생성)
> - 태스크 5: 파이프라인 테스트 (sales-data.csv 또는 sales-data-2.csv를 업로드하여 AWS Lambda 자동 트리거 확인)

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷 3개**: 데이터 버킷, 스크립트 버킷, 임시 버킷 (학번 기반 고유성)
- **AWS IAM 역할 2개**: AWS Glue 서비스 역할, AWS Lambda 실행 역할
- **AWS Lambda 함수**: 파이프라인 자동 트리거 (Amazon S3 업로드 시 Crawler 실행)
- **Amazon EventBridge 규칙**: Amazon S3 이벤트 감지
- **샘플 데이터**: 거래 데이터(transactions.csv) 자동 업로드

> [!NOTE]
> AWS Glue Database, Crawler, Visual ETL Job은 이 태스크에서 생성하지 않습니다. 학생이 태스크 1~3에서 직접 생성합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week11-3-data-pipeline-lab.zip` 파일의 압축을 해제합니다.
2. `week11-3-data-pipeline-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

<img src="/images/week11/11-3-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week11-3-data-pipeline-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.

<img src="/images/week11/11-3-task0-step8-next.png" alt="Next 버튼 클릭" class="guide-img-md" />

9. **Stack name**에 `week11-3-pipeline-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 확인합니다:
    - **StudentId**: 본인의 학번 또는 고유 식별자를 입력합니다 (예: `20240001` 또는 `student01`)
    - **EnvironmentName**: `week11-3-pipeline` (기본값 유지)
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `11-3` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)

> [!WARNING]
> **StudentId는 반드시 본인의 학번으로 변경하세요.** 기본값(`20240001`)을 그대로 사용하면 다른 학생과 리소스 이름이 충돌할 수 있습니다. 소문자와 숫자만 사용 가능하며 5-20자여야 합니다.

11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task0-step11-next.png" alt="Next 버튼 클릭" class="guide-img-md" />

12. **Configure stack options** 페이지에서 아래로 스크롤합니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스에 자동으로 적용됩니다. 추가 태그가 필요하면 Tags 섹션에서 넣을 수 있습니다.

13. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources with custom names`를 선택합니다.

    <img src="/images/week11/11-3-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

14. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.  
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

15. **Outputs** 탭을 선택합니다.

    <img src="/images/week11/11-3-task0-step15.png" alt="Outputs 탭 선택" class="guide-img-md" />

16. 출력값들을 확인하고 메모장에 복사합니다:
    - `DataBucketName`: 데이터 버킷 이름 (예: `week11-data-{StudentId}-ap-northeast-2`)
    - `ScriptsBucketName`: 스크립트 버킷 이름 (예: `week11-scripts-{StudentId}-ap-northeast-2`)
    - `TempBucketName`: 임시 버킷 이름 (예: `week11-temp-{StudentId}-ap-northeast-2`)
    - `GlueServiceRoleName`: AWS Glue 서비스 역할 이름

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

### Amazon S3 버킷 확인

17. 상단 검색창에 `S3`를 입력하고 선택합니다.
18. 다음 3개의 버킷이 생성되었는지 확인합니다:
    - `week11-data-{StudentId}-ap-northeast-2` (데이터 버킷)
    - `week11-scripts-{StudentId}-ap-northeast-2` (스크립트 버킷)
    - `week11-temp-{StudentId}-ap-northeast-2` (임시 버킷)

    <img src="/images/week11/11-3-task1-step18.png" alt="S3 버킷 3개 생성 확인" class="guide-img-md" />

19. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
20. 다음 폴더들이 자동으로 생성되었는지 확인합니다:
    - `raw/` - 원본 데이터 저장
    - `processed/` - 처리된 데이터 저장

    <img src="/images/week11/11-3-task1-step20.png" alt="S3 버킷 폴더 구조 확인" class="guide-img-md" />

21. `raw/` 폴더를 클릭합니다.
22. `transactions.csv` 파일이 자동으로 업로드되었는지 확인합니다.

    <img src="/images/week11/11-3-task1-step22.png" alt="transactions.csv 파일 확인" class="guide-img-md" />

23. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

    <img src="/images/week11/11-3-task1-step23.png" alt="transactions.csv 다운로드" class="guide-img-md" />

> [!NOTE]
> `transactions.csv`는 전자상거래 거래 데이터로, `transaction_id`, `customer_id`, `product_id`, `amount`, `transaction_date`, `region` 컬럼을 포함합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다. Amazon S3 버킷, AWS IAM 역할, AWS Lambda 함수, Amazon EventBridge 규칙이 자동으로 생성되었습니다.

## 태스크 1: AWS Glue Database 생성

이 태스크에서는 **AWS Glue Data Catalog**에 데이터베이스를 직접 생성합니다. 데이터베이스는 테이블의 논리적 그룹으로, Crawler가 생성하는 테이블이 저장되는 컨테이너입니다.

24. 상단 검색창에 `Glue`를 입력하고 선택합니다.
25. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
26. [[Add database]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step26.png" alt="Add database 버튼 클릭" class="guide-img-md" />

27. **Name**에 `week11_pipeline_{StudentId}`를 입력합니다. (예: `week11_pipeline_20240001`)

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다. 예: `week11_pipeline_20240001`
>
> AWS Glue Database 이름에는 하이픈(-)을 사용할 수 없습니다. 언더스코어(\_)를 사용합니다.

28. **Description - optional**에 `Week 11-3 data pipeline lab database`를 입력합니다.
29. **Location - optional**에 `s3://week11-data-{StudentId}-ap-northeast-2/`를 입력합니다. (예: `s3://week11-data-20240001-ap-northeast-2/`)
30. [[Create database]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step30.png" alt="Create database 버튼 클릭" class="guide-img-md" />

31. 데이터베이스 목록에서 `week11_pipeline_{StudentId}`가 생성되었는지 확인합니다.

    <img src="/images/week11/11-3-task2-step31.png" alt="Database 생성 확인" class="guide-img-md" />

✅ **태스크 완료**: AWS Glue Database를 직접 생성했습니다.

## 태스크 2: AWS Glue Crawler 생성 및 실행

이 태스크에서는 **AWS Glue Crawler**를 직접 생성하고 실행하여 Amazon S3의 CSV 데이터를 스캔하고 Data Catalog 테이블을 자동으로 생성합니다.

### 태스크 2.1: Crawler 생성

32. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
33. [[Create crawler]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step33.png" alt="Create crawler 버튼 클릭" class="guide-img-md" />

34. **Crawler name**에 `week11-pipeline-crawler-{StudentId}`를 입력합니다. (예: `week11-pipeline-crawler-20240001`)

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

35. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-3`    |
| `CreatedBy` | `Student` |

36. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step36.png" alt="Next 버튼 클릭" class="guide-img-md" />

37. **Is your data already mapped to Glue tables?** 에서 `Not yet`이 선택되어 있는지 확인합니다 (기본값).
38. [[Add a data source]] 버튼을 클릭합니다.
39. 모달 창에서 다음을 설정합니다:
    - **Data source**: `S3` (기본값)
    - **Network connection - optional**: 비워둡니다
    - **Location of S3 data**: `In this account` (기본값)
    - **S3 path**: [[Browse S3]] 버튼을 클릭하여 `week11-data-{StudentId}-ap-northeast-2` 버킷의 `raw/` 폴더를 선택하거나,  
      직접 `s3://week11-data-{StudentId}-ap-northeast-2/raw/`를 입력합니다. (예: `s3://week11-data-20240001-ap-northeast-2/raw/`)
    - **Subsequent crawler runs**: `Crawl all sub-folders` (기본값)

    <img src="/images/week11/11-3-task2-step39.png" alt="Add a data source 모달 설정" class="guide-img-md" />

> [!NOTE]
> **Custom classifiers** 섹션은 기본값을 유지합니다. CSV, JSON 등 일반적인 형식은 AWS Glue가 자동으로 인식합니다.

40. [[Add an S3 data source]] 버튼을 클릭합니다.
41. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step41.png" alt="Step 2 완료 후 Next" class="guide-img-md" />

42. **IAM role** 섹션의 **Existing IAM role** 드롭다운에서 `week11-3-pipeline-stack-GlueServiceRole`로 시작하는 역할을 선택합니다.

> [!NOTE]
> 정확한 역할명은 AWS CloudFormation 스택의 **Outputs** 탭에서 `GlueServiceRoleName`을 확인합니다.  
> **Lake Formation configuration**: `Use Lake Formation credentials for crawling S3 data source` 체크하지 않습니다 (기본값).  
> **Security configuration**: `None` (기본값)을 유지합니다.

43. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step43.png" alt="Step 3 Configure security settings" class="guide-img-md" />

44. **Set output and scheduling** 페이지에서 다음을 설정합니다:
    - **Target database**: 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.
    - **Table name prefix - optional**: 비워둡니다.
    - **Maximum table threshold - optional**: 비워둡니다.
    - **Crawler schedule** > **Frequency**: `On demand` (기본값)
45. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step45.png" alt="Step 4 Set output and scheduling" class="guide-img-md" />

46. **Review and create** 페이지에서 설정을 검토하고 [[Create crawler]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task2-step46.png" alt="Review and create - Crawler 생성" class="guide-img-md" />

### 태스크 2.2: Crawler 실행

47. 생성된 Crawler `week11-pipeline-crawler-{StudentId}`를 선택합니다.

    <img src="/images/week11/11-3-task2-step46-created.png" alt="Crawler 생성 완료" class="guide-img-md" />

> [!TIP]
> Crawler 생성 후 상세 페이지가 표시되지 않는 경우, 왼쪽 메뉴에서 **Crawlers**를 선택한 후 `week11-pipeline-crawler-{StudentId}`를 클릭하여 이동합니다.

48. [[Run crawler]] 버튼을 클릭합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. 페이지를 새로고침하여 상태를 확인합니다.  
> Crawler는 `raw/` 폴더의 CSV 파일을 스캔하여 자동으로 테이블을 생성합니다.  
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

49. **Crawler runs** 섹션에서 Status가 **Running** → **Completed**로 변경되는 것을 확인합니다.

    <img src="/images/week11/11-3-task2-step49.png" alt="Crawler 실행 완료 Completed 상태" class="guide-img-md" />

50. 실행이 완료되면 **Table changes** 컬럼에서 테이블 생성 결과를 확인합니다.

> [!OUTPUT]
>
> ```
> Status: Completed
> Table changes: 1 table change, 0 partition changes
> ```

### 태스크 2.3: 생성된 테이블 확인

51. 왼쪽 메뉴에서 **Data Catalog tables**를 선택합니다.

> [!TIP]
> **다른 방법**: 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택한 후 `week11_pipeline_{StudentId}` 데이터베이스를 클릭하면 **Tables** 섹션에서도 확인할 수 있습니다.

52. **Database** 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.

    <img src="/images/week11/11-3-task2-step52.png" alt="Database 드롭다운에서 선택" class="guide-img-md" />

53. 생성된 테이블 `raw`를 클릭합니다.

    <img src="/images/week11/11-3-task2-step53.png" alt="raw 테이블 클릭" class="guide-img-md" />

> [!NOTE]
> Crawler는 Amazon S3 폴더명을 기반으로 테이블 이름을 생성합니다. `raw/` 폴더를 스캔했으므로 테이블 이름이 `raw`가 됩니다.

54. **Schema** 탭에서 자동으로 추론된 컬럼들을 확인합니다:
    - `transaction_id` (bigint)
    - `customer_id` (string)
    - `product_id` (string)
    - `amount` (double)
    - `transaction_date` (string)
    - `region` (string)

    <img src="/images/week11/11-3-task2-step54.png" alt="Schema 탭 컬럼 확인" class="guide-img-md" />

> [!NOTE]
> Crawler가 CSV 파일의 헤더를 읽고 자동으로 스키마를 생성했습니다. 데이터 타입도 자동으로 추론됩니다.

✅ **태스크 완료**: AWS Glue Crawler를 직접 생성하고 실행하여 Data Catalog 테이블을 생성했습니다.

## 태스크 3: AWS Glue Visual ETL Job 생성 및 실행

이 태스크에서는 **AWS Glue Visual ETL**을 사용하여 CSV 데이터를 Parquet 형식으로 변환하는 ETL Job을 직접 구성합니다. Visual ETL은 코드 없이 드래그앤드롭으로 데이터 파이프라인을 구성할 수 있는 도구입니다.

> [!NOTE]
> **CSV vs Parquet**:
>
> - **CSV**: 행 기반 텍스트 형식. 사람이 읽기 쉽지만 쿼리 성능이 낮고 파일 크기가 큼
> - **Parquet**: 컬럼 기반 바이너리 형식. 쿼리 성능이 우수하고 압축률이 높음 (Athena 비용 절감)
>
> Week 11-2에서는 Athena CTAS로 CSV→Parquet 변환을 했습니다. 이번 태스크에서는 AWS Glue Visual ETL로 동일한 변환을 수행하여 두 방식의 차이를 비교합니다.

### 태스크 3.1: Visual ETL Job 생성

55. 왼쪽 메뉴에서 **ETL jobs**를 선택합니다.
56. **Create job** 섹션에서 **Visual ETL** 카드를 클릭합니다.

    <img src="/images/week11/11-3-task3-step56.png" alt="Visual ETL 카드 선택" class="guide-img-md" />

> [!NOTE]
> **Create job** 섹션에는 3가지 옵션이 카드 형태로 표시됩니다:
>
> - **Visual ETL**: 시각적 인터페이스로 데이터 흐름 구성 (이 실습에서 사용)
> - **Notebook**: 대화형 코드 노트북
> - **Script editor**: 스크립트 편집기
>
> 또는 왼쪽 메뉴에서 **Visual ETL**을 직접 선택해도 동일합니다.

### 태스크 3.2: Source 노드 추가

> [!TIP]
> Visual ETL 에디터가 열리면 왼쪽에 **+ Add nodes** 패널이 자동으로 표시됩니다. 패널이 닫혀있는 경우 캔버스 왼쪽 상단의 **+** 버튼을 클릭하여 열 수 있습니다.

57. 왼쪽 **+ Add nodes** 패널에서 **Sources** 탭을 선택합니다.
58. **AWS Glue Data Catalog**를 선택합니다.

    <img src="/images/week11/11-3-task3-step58.png" alt="AWS Glue Data Catalog 소스 선택" class="guide-img-md" />

59. 오른쪽 **Data source properties - Data Catalog** 패널에서 다음을 설정합니다:
    - **Database**: `week11_pipeline_{StudentId}` 선택
    - **Table**: `raw` 선택

    <img src="/images/week11/11-3-task3-step59.png" alt="Data source properties 설정" class="guide-img-md" />

> [!TIP]
> 오른쪽에 속성 패널이 보이지 않는 경우, 캔버스에 추가된 **AWS Glue Data Catalog** 노드를 클릭하면 패널이 표시됩니다.

> [!NOTE]
> Database와 Table을 선택하면 하단의 **Output schema** 탭에서 컬럼 정보를 미리 확인할 수 있습니다.

### 태스크 3.3: Transform 노드 추가

60. 캔버스의 [[+ Add nodes]] 버튼을 다시 클릭합니다.
61. **Transforms** 탭에서 **Change Schema**를 선택합니다.

    <img src="/images/week11/11-3-task3-step61.png" alt="Transforms 탭에서 Change Schema 선택" class="guide-img-md" />

62. 오른쪽 **Transform** 패널에서 다음을 확인합니다:
    - **Node parents**: `AWS Glue Data Catalog`가 자동으로 연결되어 있는지 확인합니다.
63. **Change Schema (Apply mapping)** 테이블에서 컬럼 매핑을 확인합니다:

| Source key       | Target key       | Data type | Drop |
| ---------------- | ---------------- | --------- | ---- |
| transaction_id   | transaction_id   | bigint    |      |
| customer_id      | customer_id      | string    |      |
| product_id       | product_id       | string    |      |
| amount           | amount           | double    |      |
| transaction_date | transaction_date | string    |      |
| region           | region           | string    |      |

> [!NOTE]
> 이 실습에서는 스키마를 변경하지 않고 그대로 유지합니다. Change Schema 노드는 필요시 컬럼명 변경, 데이터 타입 변환, 불필요한 컬럼 제거(Drop) 등을 수행할 수 있습니다.

### 태스크 3.4: Target 노드 추가

64. 캔버스의 [[+ Add nodes]] 버튼을 다시 클릭합니다.
65. **Targets** 탭에서 **Amazon S3**를 선택합니다.
66. 오른쪽 **Data target properties - S3** 패널에서 다음을 설정합니다:
    - **Format**: `Parquet` 선택
    - **Compression Type**: `Snappy` 유지 (기본값)
    - **S3 Target Location**: `s3://week11-data-{StudentId}-ap-northeast-2/processed/` 입력  
      (예: `s3://week11-data-20240001-ap-northeast-2/processed/`) (또는 [[Browse S3]]로 선택)

    <img src="/images/week11/11-3-task3-step66.png" alt="Data target properties - S3 설정" class="guide-img-md" />

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다. S3 경로는 반드시 슬래시(`/`)로 끝나야 합니다.

> [!NOTE]
> **Snappy 압축**: Parquet 파일의 기본 압축 알고리즘입니다. 압축/해제 속도가 빠르고 적절한 압축률을 제공하여 ETL 작업에 적합합니다.

67. 캔버스에서 3개의 노드가 연결된 것을 확인합니다:
    - **AWS Glue Data Catalog** → **Change Schema** → **Amazon S3**

### 태스크 3.5: Job 설정

68. 상단 탭에서 **Job details**를 선택합니다.
69. 다음을 설정합니다:
    - **Name**: `week11-etl-csv-to-parquet-{StudentId}` 입력 (예: `week11-etl-csv-to-parquet-20240001`)
    - **IAM Role**: 태스크 0에서 생성된 Glue 서비스 역할 선택 (Outputs의 `GlueServiceRoleName`)
    - **Glue version**: `Glue 5.0` 또는 `Glue 5.1` (콘솔 기본값 사용)
    - **Language**: `Python 3` 유지 (기본값)
    - **Worker type**: `G 1X` 유지 (기본값)
    - **Automatically scale the number of workers**: 체크 해제
    - **Requested number of workers**: `2` 입력

    <img src="/images/week11/11-3-task3-step69.png" alt="Job details 설정" class="guide-img-md" />

> [!NOTE]
> AWS Glue 5.1이 2026년 2월부터 서울 리전에서 사용 가능합니다.  
> 콘솔 기본값이 `Glue 5.0` 또는 `Glue 5.1`로 표시될 수 있으며, 어느 버전이든 이 실습에서는 동일하게 동작합니다.

> [!NOTE]
> **Automatically scale the number of workers**가 활성화되어 있으면 Worker 수를 직접 지정할 수 없습니다.  
> 이 실습에서는 비용 절감을 위해 자동 스케일링을 해제하고 Worker 수를 2로 고정합니다.

70. 아래로 스크롤하여 **Advanced properties**를 펼칩니다.
71. **Temporary path**에 `s3://week11-temp-{StudentId}-ap-northeast-2/temp/` 를 입력합니다.  
    (예: `s3://week11-temp-20240001-ap-northeast-2/temp/`) (또는 [[Browse S3]]로 선택)

    <img src="/images/week11/11-3-task3-step71.png" alt="Temporary path 설정" class="guide-img-md" />

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

72. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

    <img src="/images/week11/11-3-task3-step72.png" alt="Tags 추가" class="guide-img-md" />

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-3`    |
| `CreatedBy` | `Student` |

73. 상단의 [[Save]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task3-step73.png" alt="Job 저장 완료" class="guide-img-md" />

> [!NOTE]
> Job이 저장되면 상단에 "Successfully updated job" 메시지가 표시됩니다.

### 태스크 3.6: ETL Job 실행

74. 상단의 [[Run]] 버튼을 클릭합니다.

> [!WARNING]
> ETL Job 실행 시 비용이 발생합니다. 실습 종료 후 반드시 리소스를 삭제합니다.

> [!NOTE]
> ETL Job 실행에 3-5분이 소요됩니다.  
> AWS Glue는 Apache Spark 클러스터를 시작하고, CSV 데이터를 읽고, Parquet 형식으로 변환하여 저장합니다.  
> **Runs** 탭에서 실행 상태를 확인할 수 있습니다.

75. **Runs** 탭을 선택합니다.

    <img src="/images/week11/11-3-task3-step75-running.png" alt="ETL Job Running 상태" class="guide-img-md" />

    <img src="/images/week11/11-3-task3-step75-succeeded.png" alt="ETL Job Succeeded 상태" class="guide-img-md" />

> [!NOTE]
> **Run status**가 "**Running**"에서 "**Succeeded**"로 변경될 때까지 기다립니다. ETL Job 실행에 3-5분이 소요됩니다.

> [!TROUBLESHOOTING]
> **문제**: Run status가 "**Failed**"로 표시됩니다.
>
> **원인**: IAM 역할 권한 부족, S3 경로 오류, 또는 Database/Table 설정 오류.
>
> **해결**:
>
> 1. **Error message**를 클릭하여 상세 오류를 확인합니다.
> 2. **Visual** 탭으로 돌아가 Source의 Database/Table, Target의 S3 경로를 확인합니다.
> 3. **Job details** 탭에서 IAM Role과 Temporary path를 확인합니다.
> 4. 수정 후 [[Save]] → [[Run]]을 다시 실행합니다.

### 태스크 3.7: 변환 결과 확인

76. Amazon S3 콘솔로 이동합니다.
77. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
78. `processed/` 폴더를 클릭합니다.

    <img src="/images/week11/11-3-task3-step78.png" alt="processed 폴더의 Parquet 파일 확인" class="guide-img-md" />

79. Parquet 파일이 생성되었는지 확인합니다.

> [!NOTE]
> ETL Job이 CSV 데이터를 Parquet 형식으로 변환하여 저장했습니다.  
> Parquet 파일은 `.parquet` 또는 `.snappy.parquet` 확장자를 가집니다.  
> 원본 CSV 파일과 비교하여 파일 크기가 줄어든 것을 확인할 수 있습니다.

> [!TIP]
> AWS Glue 콘솔에서 ETL Job을 다시 열고 **Script** 탭을 선택하면 Visual ETL이 자동으로 생성한 PySpark 코드를 확인할 수 있습니다.

✅ **태스크 완료**: AWS Glue Visual ETL Job을 직접 생성하여 CSV 데이터를 Parquet 형식으로 변환했습니다.

## 태스크 4: Amazon Athena로 처리된 데이터 쿼리

이 태스크에서는 Amazon Athena를 사용하여 Parquet로 변환된 데이터를 SQL로 쿼리합니다.

### 태스크 4.1: Athena 쿼리 결과 위치 설정

80. 상단 검색창에 `Athena`를 입력하고 선택합니다.
81. Amazon Athena 시작 페이지가 표시되면 **Query your data in Athena console**을 선택하고 [[Launch query editor]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task4-step81.png" alt="Amazon Athena 시작 페이지에서 Launch query editor 클릭" class="guide-img-md" />

> [!NOTE]
> 이미 Query editor가 표시되는 경우 이 단계를 건너뜁니다. 왼쪽 메뉴에서 **Query editor tabs**를 클릭해도 동일합니다.

> [!TIP]
> 이전 실습(Week 11-2)에서 생성한 워크그룹이 삭제된 경우, "Error fetching workgroup - WorkGroup is not found" 에러가 표시될 수 있습니다. 상단 **Workgroup** 드롭다운에서 `primary`를 선택하면 해결됩니다.
>
> <img src="/images/week11/11-3-task4-step81-workgroup-error.png" alt="WorkGroup not found 에러" class="guide-img-sm" />

82. 왼쪽 메뉴에서 **Query editor tabs**를 선택합니다.
83. 상단의 **Workgroup** 드롭다운에서 `primary`가 선택되어 있는지 확인합니다.

> [!NOTE]
> 이 실습에서는 **primary 워크그룹**을 사용합니다. Week 11-2에서는 전용 워크그룹을 생성했지만, 이번 실습에서는 기본 워크그룹의 설정만 변경하여 사용합니다.

84. 상단 탭에서 **Query settings**를 선택합니다.
85. **Query result location**이 설정되어 있지 않으면 [[Manage]] 버튼을 클릭합니다.
86. **Query result location**에 `s3://week11-temp-{StudentId}-ap-northeast-2/athena-results/`를 입력합니다.  
    (예: `s3://week11-temp-20240001-ap-northeast-2/athena-results/`)

    <img src="/images/week11/11-3-task4-step86.png" alt="Query result location 설정" class="guide-img-md" />

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

87. [[Save]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task4-step87.png" alt="Query settings 저장" class="guide-img-md" />

### 태스크 4.2: 처리된 데이터 테이블 생성

88. **Editor** 탭을 선택합니다.
89. 왼쪽 패널의 **Data source**가 `AwsDataCatalog`인지 확인합니다.
90. **Database** 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.
91. 다음 쿼리를 입력합니다:

```sql
CREATE EXTERNAL TABLE processed_transactions (
    transaction_id bigint,
    customer_id string,
    product_id string,
    amount double,
    transaction_date string,
    region string
)
STORED AS PARQUET
LOCATION 's3://week11-data-{StudentId}-ap-northeast-2/processed/';
```

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다. 예: `s3://week11-data-20240001-ap-northeast-2/processed/`

> [!NOTE]
> **EXTERNAL TABLE**은 데이터를 Amazon S3에 그대로 두고 메타데이터만 AWS Glue Data Catalog에 저장합니다.  
> 테이블을 삭제해도 Amazon S3의 실제 데이터는 삭제되지 않습니다.

92. [[Run]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task4-step92.png" alt="CREATE TABLE 쿼리 실행" class="guide-img-md" />

### 태스크 4.3: 데이터 쿼리 및 분석

93. 다음 쿼리를 입력하여 처리된 데이터를 확인합니다:

```sql
SELECT * FROM processed_transactions LIMIT 10;
```

94. [[Run]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-task4-step94.png" alt="SELECT 쿼리 실행 결과" class="guide-img-md" />

95. 결과를 확인합니다.

> [!NOTE]
> CSV 원본 데이터와 동일한 내용이 Parquet 형식으로 저장되어 있음을 확인할 수 있습니다.

96. 지역별 매출을 분석하는 쿼리를 실행합니다:

```sql
SELECT
    region,
    COUNT(*) as transaction_count,
    SUM(amount) as total_sales,
    AVG(amount) as avg_transaction_value
FROM processed_transactions
GROUP BY region
ORDER BY total_sales DESC;
```

<img src="/images/week11/11-3-task4-step96.png" alt="지역별 매출 분석 쿼리 결과" class="guide-img-md" />

97. 제품별 판매 실적을 확인하는 쿼리를 실행합니다:

```sql
SELECT
    product_id,
    COUNT(*) as sales_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_price
FROM processed_transactions
GROUP BY product_id
ORDER BY total_revenue DESC;
```

<img src="/images/week11/11-3-task4-step97.png" alt="제품별 판매 실적 쿼리 결과" class="guide-img-md" />

98. 원본 테이블(`raw`)과 변환된 테이블(`processed_transactions`)의 데이터 스캔량을 비교합니다:

```sql
SELECT COUNT(*) as total_records FROM raw;
```

```sql
SELECT COUNT(*) as total_records FROM processed_transactions;
```

<img src="/images/week11/11-3-task4-step98-raw.png" alt="raw 테이블 쿼리 - Data scanned 확인" class="guide-img-md" />

<img src="/images/week11/11-3-task4-step98-parquet.png" alt="processed_transactions 테이블 쿼리 - Data scanned 확인" class="guide-img-md" />

> [!NOTE]
> 각 쿼리 실행 후 하단의 **Data scanned** 값을 비교합니다.
>
> - **raw 테이블** (CSV): `Data scanned: 0.44 KB` — CSV는 행 기반이므로 `COUNT(*)`에도 전체 파일을 스캔합니다.
> - **processed_transactions 테이블** (Parquet): `Data scanned: -` 또는 매우 적은 값 — Parquet는 파일 메타데이터에 행 수가 저장되어 있어 실제 데이터를 스캔하지 않거나 최소한으로 스캔합니다.
>
> 이 실습에서는 데이터가 소량이라 차이가 작지만,  
> 실제 운영 환경(GB~TB 규모)에서는 Parquet의 컬럼 기반 저장 방식 덕분에 필요한 컬럼만 선택적으로 읽어 데이터 스캔량이 크게 줄어듭니다.  
> Amazon Athena는 스캔한 데이터량에 따라 과금($5/TB)되므로, Parquet 변환은 비용 절감에 매우 효과적입니다.

✅ **태스크 완료**: Amazon Athena로 변환된 데이터를 쿼리하고 분석했습니다.

## 태스크 5: 이벤트 기반 파이프라인 자동화 확인

이 태스크에서는 새로운 데이터를 업로드하여 Amazon EventBridge와 AWS Lambda가 자동으로 Crawler를 트리거하는 전체 파이프라인 흐름을 확인합니다.

> [!NOTE]
> **파이프라인 자동화 흐름**:
>
> 1. 새 파일이 데이터 버킷의 `raw/` 폴더에 업로드됨
> 2. Amazon EventBridge가 Amazon S3 이벤트 감지
> 3. AWS Lambda 함수가 자동으로 실행됨
> 4. AWS Lambda 함수가 AWS Glue Crawler 시작
> 5. Crawler가 새 데이터를 스캔하고 Data Catalog 업데이트

### 태스크 5.1: 새 데이터 업로드

99. Amazon S3 콘솔로 이동합니다.
100. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
101. `raw/` 폴더를 클릭합니다.
102. [[Upload]] 버튼을 클릭합니다.
103. 다운로드한 ZIP 파일에서 `sales-data.csv` 파일을 선택합니다.
104. [[Upload]] 버튼을 클릭합니다.

     <img src="/images/week11/11-3-task5-step104.png" alt="sales-data.csv 업로드" class="guide-img-md" />

     <img src="/images/week11/11-3-task5-step104-uploaded.png" alt="sales-data.csv 업로드 완료" class="guide-img-md" />

### 태스크 5.2: AWS Lambda 자동 실행 확인

105. 상단 검색창에 `Lambda`를 입력하고 선택합니다.
106. `week11-pipeline-trigger-{StudentId}` 함수를 선택합니다.
107. **Monitor** 탭을 선택합니다.
108. [[View CloudWatch logs]] 버튼을 클릭하여 Amazon CloudWatch Logs에서 실행 로그를 확인합니다.

     <img src="/images/week11/11-3-task5-step108.png" alt="CloudWatch Logs에서 Lambda 실행 로그 확인" class="guide-img-md" />

     <img src="/images/week11/11-3-task5-step108-log.png" alt="Lambda 로그 상세 내용" class="guide-img-md" />

> [!NOTE]
> 로그에서 "Starting AWS Glue Crawler" 메시지를 확인할 수 있습니다. 이는 Amazon EventBridge가 Amazon S3 업로드 이벤트를 감지하고 AWS Lambda 함수를 자동으로 실행했음을 의미합니다.

### 태스크 5.3: Crawler 자동 실행 확인

109. AWS Glue 콘솔로 이동합니다.
110. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
111. `week11-pipeline-crawler-{StudentId}` Crawler를 선택합니다.
112. **Crawler runs** 탭에서 새로운 실행 기록이 추가되었는지 확인합니다. Status가 "**Completed**"이면 정상입니다.

     <img src="/images/week11/11-3-task5-step112.png" alt="Crawler runs에 두 번째 실행 기록 확인" class="guide-img-md" />

> [!NOTE]
> AWS Lambda 함수가 자동으로 Crawler를 시작했습니다. Crawler 실행에 약 1분이 소요됩니다. 바로 확인되지 않으면 잠시 후 페이지를 새로고침합니다. 첫 번째 실행(태스크 2)과 비교하여 **Table changes**에 변경 사항이 표시됩니다.

### 태스크 5.4: 업데이트된 데이터 확인

113. Amazon Athena 콘솔로 이동합니다.
114. **Editor** 탭을 선택합니다.
115. **Database**에서 `week11_pipeline_{StudentId}`를 선택합니다.
116. 다음 쿼리를 실행하여 새 데이터가 포함되었는지 확인합니다:

```sql
SELECT COUNT(*) as total_records FROM raw;
```

<img src="/images/week11/11-3-task5-step116.png" alt="레코드 수 증가 확인" class="guide-img-md" />

> [!NOTE]
> 레코드 수가 증가했는지 확인합니다. 초기 `transactions.csv`의 레코드 수와 비교하여 새로 업로드한 `sales-data.csv`의 레코드가 추가되었는지 확인할 수 있습니다.

> [!IMPORTANT]
> Crawler가 재실행되면 기존 `raw` 테이블의 스키마를 업데이트합니다. 그러나 `processed_transactions` 테이블은 자동으로 업데이트되지 않습니다. 새 데이터를 Parquet로 변환하려면 태스크 3의 ETL Job을 다시 실행해야 합니다.

✅ **태스크 완료**: Amazon EventBridge와 AWS Lambda를 활용한 이벤트 기반 파이프라인 자동화 흐름을 확인했습니다.

### (옵션) 두 번째 파이프라인 테스트

> [!NOTE]
> 시간이 여유 있는 경우, `sales-data-2.csv`를 추가로 업로드하여 파이프라인이 반복적으로 정상 동작하는지 확인할 수 있습니다.

117. Amazon S3 콘솔에서 데이터 버킷의 `raw/` 폴더로 이동합니다.
118. [[Upload]] 버튼을 클릭하고 `sales-data-2.csv` 파일을 업로드합니다.

     <img src="/images/week11/11-3-task5-step118.png" alt="sales-data-2.csv 업로드" class="guide-img-md" />

119. 약 1분 후 AWS Glue Crawler가 자동 실행되어 완료되는지 확인합니다.

     <img src="/images/week11/11-3-task5-step119.png" alt="Crawler 세 번째 실행 완료 확인" class="guide-img-md" />

120. Crawler 완료 후 Amazon Athena에서 다음 쿼리를 실행하여 레코드 수가 추가로 증가했는지 확인합니다.

```sql
SELECT COUNT(*) as total_records FROM raw;
```

<img src="/images/week11/11-3-task5-step120.png" alt="레코드 수 추가 증가 확인" class="guide-img-md" />

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Glue Database를 직접 생성하여 데이터 카탈로그를 구성했습니다.
- AWS Glue Crawler를 직접 생성하고 실행하여 Amazon S3 데이터의 스키마를 자동으로 추론했습니다.
- AWS Glue Visual ETL Job을 직접 생성하여 CSV 데이터를 Parquet 형식으로 변환했습니다.
- Amazon Athena로 변환된 데이터를 SQL로 쿼리하고 분석했습니다.
- Amazon EventBridge와 AWS Lambda를 활용한 이벤트 기반 파이프라인 자동화 흐름을 확인했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.  
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제가 실패하므로 먼저 버킷을 비워야 합니다.

### Tag Editor로 리소스 찾기 (참고)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`를 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `11-3`
6. [[Search resources]] 버튼을 클릭합니다.

<img src="/images/week11/11-3-cleanup-step6.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 단계 1: 수동 생성 리소스 삭제 및 Amazon S3 버킷 비우기

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell이 열리면 상단에 리전이 `ap-northeast-2 (서울)`인지 확인합니다. 다른 리전이면 상단 리전 선택기에서 변경합니다.

8. 환경 변수를 설정합니다:

```bash
# StudentId를 실제 학번으로 교체합니다 (예: 20240001)
STUDENT_ID="20240001"
echo "STUDENT_ID: ${STUDENT_ID}"
```

<img src="/images/week11/11-3-cleanup-step8.png" alt="CloudShell 환경 변수 설정" class="guide-img-sm" />

**Amazon Athena 수동 생성 테이블 삭제**

9. Amazon Athena에서 수동 생성한 테이블을 삭제합니다:

```bash
aws athena start-query-execution \
  --query-string "DROP TABLE IF EXISTS processed_transactions;" \
  --query-execution-context Database=week11_pipeline_${STUDENT_ID} \
  --work-group primary \
  --result-configuration OutputLocation=s3://week11-temp-${STUDENT_ID}-ap-northeast-2/athena-results/
```

<img src="/images/week11/11-3-cleanup-step9.png" alt="Athena 테이블 삭제 CLI 실행" class="guide-img-md" />

**AWS Glue ETL Job 삭제**

10. AWS Glue ETL Job을 삭제합니다:

```bash
aws glue delete-job --job-name week11-etl-csv-to-parquet-${STUDENT_ID}
```

<img src="/images/week11/11-3-cleanup-step10.png" alt="Glue ETL Job 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-job --job-name week11-etl-csv-to-parquet-${STUDENT_ID}
> ```
>
> `EntityNotFoundException` 오류가 나오면 삭제 완료입니다.

**AWS Glue Crawler 삭제**

11. AWS Glue Crawler를 삭제합니다:

```bash
aws glue delete-crawler --name week11-pipeline-crawler-${STUDENT_ID}
```

<img src="/images/week11/11-3-cleanup-step11.png" alt="Glue Crawler 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-crawler --name week11-pipeline-crawler-${STUDENT_ID}
> ```
>
> `EntityNotFoundException` 오류가 나오면 삭제 완료입니다.

**AWS Glue 테이블 및 Database 삭제**

12. AWS Glue 테이블과 Database를 삭제합니다:

```bash
aws glue delete-table --database-name week11_pipeline_${STUDENT_ID} --name raw
aws glue delete-table --database-name week11_pipeline_${STUDENT_ID} --name sales_data_csv 2>/dev/null
aws glue delete-table --database-name week11_pipeline_${STUDENT_ID} --name sales_data_2_csv 2>/dev/null
aws glue delete-table --database-name week11_pipeline_${STUDENT_ID} --name transactions_csv 2>/dev/null
aws glue delete-database --name week11_pipeline_${STUDENT_ID}
```

<img src="/images/week11/11-3-cleanup-step12.png" alt="Glue 테이블 및 Database 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> `sales_data_csv`, `sales_data_2_csv`, `transactions_csv` 테이블은 (옵션) 단계를 수행한 경우에만 존재합니다. 존재하지 않는 테이블은 오류가 발생하지만 `2>/dev/null`로 무시됩니다.
>
> Database 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-database --name week11_pipeline_${STUDENT_ID}
> ```
>
> `EntityNotFoundException` 오류가 나오면 삭제 완료입니다.

**Amazon S3 버킷 비우기**

13. Amazon S3 버킷을 비웁니다:

```bash
aws s3 rm s3://week11-data-${STUDENT_ID}-ap-northeast-2 --recursive
aws s3 rm s3://week11-scripts-${STUDENT_ID}-ap-northeast-2 --recursive
aws s3 rm s3://week11-temp-${STUDENT_ID}-ap-northeast-2 --recursive
```

<img src="/images/week11/11-3-cleanup-step13.png" alt="S3 버킷 비우기 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 각 명령어가 성공하면 삭제된 파일 목록이 출력됩니다. 출력이 없으면 이미 비어있는 것입니다.
>
> 버킷이 비워졌는지 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws s3 ls s3://week11-data-${STUDENT_ID}-ap-northeast-2/
> aws s3 ls s3://week11-scripts-${STUDENT_ID}-ap-northeast-2/
> aws s3 ls s3://week11-temp-${STUDENT_ID}-ap-northeast-2/
> ```
>
> 출력이 없으면 비우기 완료입니다.

14. 옵션 1 완료 후 아래 **단계 2: AWS CloudFormation 스택 삭제**로 이동합니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

**Amazon Athena 수동 생성 테이블 삭제**

15. Amazon Athena 콘솔로 이동합니다.
16. **Editor** 탭을 선택합니다.
17. **Database**에서 `week11_pipeline_{StudentId}`를 선택합니다.
18. 다음 쿼리를 실행합니다:

```sql
DROP TABLE IF EXISTS processed_transactions;
```

19. [[Run]] 버튼을 클릭합니다.

<img src="/images/week11/11-3-cleanup-step19.png" alt="DROP TABLE 쿼리 실행" class="guide-img-md" />

> [!NOTE]
> 태스크 4.2에서 Amazon Athena로 생성한 `processed_transactions` 테이블은 AWS CloudFormation이 관리하지 않으므로 수동으로 삭제해야 합니다.

**AWS Glue ETL Job 삭제**

20. AWS Glue 콘솔로 이동합니다.
21. 왼쪽 메뉴에서 **ETL jobs**를 선택합니다.
22. `week11-etl-csv-to-parquet-{StudentId}` Job을 선택합니다.
23. **Actions** > `Delete`를 선택합니다.

    <img src="/images/week11/11-3-cleanup-step23.png" alt="ETL Job Delete 선택" class="guide-img-md" />

24. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step24.png" alt="ETL Job 삭제 확인" class="guide-img-sm" />

**AWS Glue Crawler 삭제**

25. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
26. `week11-pipeline-crawler-{StudentId}` Crawler의 **State**가 "**Ready**"인지 확인합니다.

> [!IMPORTANT]
> Crawler가 실행 중인 상태에서 삭제하면 오류가 발생할 수 있습니다. "**Ready**" 상태가 될 때까지 기다립니다.

27. `week11-pipeline-crawler-{StudentId}`를 선택합니다.
28. **Actions** > `Delete`를 선택합니다.

    <img src="/images/week11/11-3-cleanup-step28.png" alt="Crawler Delete 선택" class="guide-img-md" />

29. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step29.png" alt="Crawler 삭제 확인" class="guide-img-sm" />

**AWS Glue 테이블 및 Database 삭제**

30. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
31. `week11_pipeline_{StudentId}`를 클릭합니다.
32. **Tables** 섹션에서 모든 테이블의 체크박스를 선택합니다.
33. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step33.png" alt="테이블 전체 선택 후 Delete" class="guide-img-md" />

34. 확인 창에서 `Delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step34.png" alt="테이블 삭제 확인 - Delete 입력" class="guide-img-sm" />

35. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
36. `week11_pipeline_{StudentId}`의 체크박스를 선택합니다.
37. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step37.png" alt="Database 선택 후 Delete" class="guide-img-md" />

38. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step38.png" alt="Database 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 태스크 1~3에서 직접 생성한 Database, Crawler, ETL Job은 AWS CloudFormation이 관리하지 않으므로 수동으로 삭제해야 합니다.

**Amazon S3 버킷 비우기**

> [!IMPORTANT]
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제가 실패합니다. 반드시 3개 버킷을 모두 비운 후 스택을 삭제해야 합니다.

39. Amazon S3 콘솔로 이동합니다.
40. `week11-data-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
41. [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step41.png" alt="S3 버킷 Empty 버튼 클릭" class="guide-img-md" />

42. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step42.png" alt="permanently delete 입력 후 Empty" class="guide-img-md" />

43. `week11-scripts-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
44. [[Empty]] 버튼을 클릭합니다.
45. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
46. `week11-temp-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
47. [[Empty]] 버튼을 클릭합니다.
48. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

### 단계 2: AWS CloudFormation 스택 삭제

49. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
50. `week11-3-pipeline-stack` 스택을 선택합니다.
51. [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step51.png" alt="CloudFormation Delete stack 버튼" class="guide-img-md" />

52. 확인 창에서 스택 이름 `week11-3-pipeline-stack`을 입력하고 [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step52.png" alt="스택 삭제 확인 - 스택 이름 입력" class="guide-img-sm" />

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. 삭제가 완료될 때까지 기다립니다.  
> AWS CloudFormation 스택을 삭제하면 다음 리소스가 자동으로 삭제됩니다:
>
> - Amazon S3 버킷 3개 (버킷이 비어있는 경우)
> - AWS IAM 역할 2개
> - AWS Lambda 함수
> - Amazon EventBridge 규칙

> [!TROUBLESHOOTING]
> **문제**: AWS CloudFormation 스택 삭제가 "**DELETE_FAILED**" 상태로 실패합니다.
>
> **원인**: Amazon S3 버킷에 객체가 남아 있거나, AWS Glue Crawler가 실행 중입니다.
>
> **해결**:
>
> 1. Amazon S3 콘솔에서 3개 버킷을 모두 확인하고 [[Empty]] 버튼으로 비웁니다.
> 2. AWS Glue 콘솔에서 Crawler 상태가 "**Ready**"인지 확인합니다.
> 3. AWS CloudFormation 콘솔에서 스택을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.

### 단계 3: Amazon CloudWatch Log Group 삭제

53. AWS Management Console 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
54. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
55. 다음 로그 그룹의 체크박스를 모두 선택합니다:
    - `/aws-glue/crawlers`
    - `/aws-glue/jobs/error`
    - `/aws-glue/jobs/logs-v2`
    - `/aws-glue/sessions/error`
    - `/aws-glue/sessions/output`
    - `/aws/lambda/week11-3-pipeline-SampleDataUploader-{StudentId}`
    - `/aws/lambda/week11-pipeline-trigger-{StudentId}`
56. **Actions** > `Delete log group(s)`를 선택합니다.

    <img src="/images/week11/11-3-cleanup-step56.png" alt="Actions > Delete log group(s) 선택" class="guide-img-md" />

57. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step57.png" alt="로그 그룹 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> `/aws-glue/` 로그 그룹은 AWS Glue Crawler와 ETL Job 실행 시 자동으로 생성됩니다. 다른 AWS Glue 작업에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS Glue를 사용하지 않는 경우에만 삭제합니다.

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.  
> 로그 그룹을 삭제하지 않으면 스토리지 비용이 계속 부과됩니다.

> [!TIP]
> AWS CLI로 삭제하려면 CloudShell에서 다음 명령어를 실행합니다:
>
> ```bash
> aws logs delete-log-group --log-group-name /aws-glue/crawlers
> aws logs delete-log-group --log-group-name /aws-glue/jobs/error
> aws logs delete-log-group --log-group-name /aws-glue/jobs/logs-v2
> aws logs delete-log-group --log-group-name /aws-glue/sessions/error
> aws logs delete-log-group --log-group-name /aws-glue/sessions/output
> aws logs delete-log-group --log-group-name /aws/lambda/week11-pipeline-trigger-${STUDENT_ID}
> aws logs delete-log-group --log-group-name /aws/lambda/week11-3-pipeline-SampleDataUploader-${STUDENT_ID} 2>/dev/null
> ```
>
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws-glue/ --query "logGroups[*].logGroupName" --output text
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/week11 --query "logGroups[*].logGroupName" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.
>
> <img src="/images/week11/11-3-cleanup-log-cli.png" alt="CloudWatch Log Group CLI 삭제" class="guide-img-md" />

### 최종 삭제 확인 (Tag Editor 활용)

58. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
59. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
60. **Regions**에서 `ap-northeast-2`를 선택합니다.
61. **Resource types**에서 `All supported resource types`를 선택합니다.
62. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `11-3`
63. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week11/11-3-cleanup-step63.png" alt="Tag Editor 최종 확인 - 리소스 없음" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.  
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 4: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

64. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
65. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
66. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
67. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
68. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [AWS Glue 개발자 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/dg/what-is-glue.html)
- [AWS Glue Visual ETL 사용 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/ug/author-job-glue.html)
- [Amazon Athena 사용 설명서](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/what-is.html)
- [AWS 기반 데이터 레이크 및 분석](https://aws.amazon.com/ko/big-data/datalakes-and-analytics/)
- [AWS Lambda 개발자 가이드](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/welcome.html)
- [Amazon EventBridge 사용 설명서](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/eb-what-is.html)

## 📚 참고: AWS 데이터 파이프라인 서비스 및 모범 사례

### AWS 데이터 분석 서비스

**Amazon S3 (Simple Storage Service)**

- 무제한 확장 가능한 객체 스토리지
- 데이터 레이크의 기반 스토리지
- 11개의 9(99.999999999%) 내구성
- 다양한 스토리지 클래스로 비용 최적화

**AWS Glue**

- 완전 관리형 ETL(Extract, Transform, Load) 서비스
- Visual ETL로 코드 없이 데이터 파이프라인 구성
- 자동 스키마 검색 및 카탈로그 관리 (Crawler)
- PySpark, Python Shell, Ray 작업 지원

**Amazon Athena**

- 서버리스 대화형 쿼리 서비스
- 표준 SQL로 Amazon S3 데이터 분석
- Trino 기반 고성능 쿼리 엔진
- 스캔한 데이터량에 따른 과금 ($5/TB)

**AWS Lambda**

- 서버리스 컴퓨팅 서비스
- 이벤트 기반 자동 실행
- 밀리초 단위 과금
- 자동 스케일링

**Amazon EventBridge**

- 서버리스 이벤트 버스 서비스
- AWS 서비스 간 이벤트 라우팅
- 규칙 기반 이벤트 필터링
- 다양한 대상 서비스 지원

### 데이터 파이프라인 모범 사례

**데이터 레이크 계층 구조**

- Bronze (Raw): 원본 데이터 보존
- Silver (Processed): 정제 및 표준화
- Gold (Curated): 비즈니스 로직 적용

**성능 최적화**

- 파티셔닝으로 쿼리 범위 축소
- Parquet 형식으로 압축 및 성능 향상
- 적절한 파일 크기 유지 (128MB-1GB)
- 컬럼 기반 저장 형식 활용

**비용 최적화**

- Amazon S3 Intelligent-Tiering 활용
- Amazon Athena 쿼리 최적화 (필요한 컬럼만 SELECT)
- AWS Glue Worker 수 최소화
- Parquet 변환으로 Athena 스캔 비용 절감

### AWS Glue Visual ETL 주요 노드

**Sources (데이터 소스)**

- AWS Glue Data Catalog: Data Catalog 테이블에서 데이터 읽기
- Amazon S3: S3 버킷에서 직접 CSV, JSON, Parquet 파일 읽기

**Transforms (데이터 변환)**

- Change Schema: 컬럼명 변경, 데이터 타입 변환, 컬럼 제거
- Join: 두 데이터셋을 조건 기반으로 결합
- SQL Query: SQL 쿼리로 데이터 변환
- Detect Sensitive Data: PII 등 민감 데이터 탐지

**Targets (데이터 저장)**

- Amazon S3: S3 버킷에 다양한 형식(Parquet, CSV, JSON)으로 저장
- AWS Glue Data Catalog: Data Catalog 테이블로 저장

### CSV vs Parquet 비교

| 특성        | CSV                        | Parquet                  |
| ----------- | -------------------------- | ------------------------ |
| 저장 방식   | 행 기반 (텍스트)           | 컬럼 기반 (바이너리)     |
| 압축률      | 낮음                       | 높음 (Snappy, GZIP 등)   |
| 쿼리 성능   | 전체 행 스캔 필요          | 필요한 컬럼만 읽기       |
| Athena 비용 | 높음 (전체 데이터 스캔)    | 낮음 (컬럼 선택적 스캔)  |
| 사람 가독성 | 텍스트 에디터로 확인 가능  | 전용 도구 필요           |
| 적합한 용도 | 데이터 교환, 소규모 데이터 | 분석 쿼리, 대규모 데이터 |
