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
  - EventBridge와 AWS Lambda를 활용한 이벤트 기반 데이터 파이프라인 자동화 흐름을 이해할 수 있습니다.

prerequisites:
  - Amazon S3 기본 개념 이해.
  - SQL 쿼리 기본 지식.
  - CSV/JSON 데이터 형식 이해.
  - Week 11-2 실습 완료 (AWS Glue, Amazon Athena 기본 사용법).
---

이 실습에서는 **AWS Glue**와 **Amazon Athena**를 활용하여 **서버리스 데이터 파이프라인**을 구축합니다.

먼저 **AWS CloudFormation**을 사용하여 **Amazon S3 버킷**, **AWS IAM 역할**, **AWS Lambda 함수**, **EventBridge 규칙**, **샘플 데이터**를 자동으로 생성합니다. 그런 다음 학생이 직접 **AWS Glue Database**를 생성하고, **Crawler**를 구성하여 Amazon S3 데이터의 메타데이터를 수집합니다.

이후 **AWS Glue Visual ETL**을 사용하여 **CSV 데이터를 Parquet 형식으로 변환**하는 ETL Job을 직접 구성하고 실행합니다. 변환된 데이터를 **Amazon Athena**로 쿼리하여 분석한 후, 새로운 데이터를 업로드하여 **EventBridge**와 **AWS Lambda**가 자동으로 Crawler를 트리거하는 **이벤트 기반 파이프라인 흐름**을 확인합니다.

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
> - ✅ **자동**: Amazon S3 업로드 → EventBridge → AWS Lambda → Crawler 실행
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
> - `week11-3-data-pipeline-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, AWS IAM 역할, AWS Lambda 함수, EventBridge 규칙, 샘플 데이터 자동 생성)
> - `lambda_function.py` - AWS Lambda 함수 소스 코드 (참고용, CloudFormation이 자동 배포)
> - `sales-data.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)
> - `sales-data-2.csv` - 추가 테스트 데이터 (태스크 5에서 파이프라인 테스트용으로 업로드)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿으로 Amazon S3, AWS IAM 역할, AWS Lambda, EventBridge 규칙, 샘플 데이터 자동 생성)
> - 태스크 5: 파이프라인 테스트 (sales-data.csv 또는 sales-data-2.csv를 업로드하여 AWS Lambda 자동 트리거 확인)

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷 3개**: 데이터 버킷, 스크립트 버킷, 임시 버킷 (학번 기반 고유성)
- **AWS IAM 역할 2개**: AWS Glue 서비스 역할, AWS Lambda 실행 역할
- **AWS Lambda 함수**: 파이프라인 자동 트리거 (Amazon S3 업로드 시 Crawler 실행)
- **EventBridge 규칙**: Amazon S3 이벤트 감지
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
9. **Stack name**에 `week11-3-pipeline-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 입력합니다:
    - **StudentId**: 본인의 학번 또는 고유 식별자 (예: `20240001` 또는 `student01`)

> [!IMPORTANT]
> StudentId는 소문자, 숫자, 하이픈만 사용 가능하며 5-20자여야 합니다. 이 값은 모든 리소스 이름에 포함되어 고유성을 보장합니다.

11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 찾습니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-3`    |
| `CreatedBy` | `Student` |

14. [[Next]] 버튼을 클릭합니다.
15. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources with custom names`를 선택합니다.
16. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

17. **Outputs** 탭을 선택합니다.
18. 출력값들을 확인하고 메모장에 복사합니다:
    - `DataBucketName`: 데이터 버킷 이름 (예: `week11-data-{StudentId}-ap-northeast-2`)
    - `ScriptsBucketName`: 스크립트 버킷 이름 (예: `week11-scripts-{StudentId}-ap-northeast-2`)
    - `TempBucketName`: 임시 버킷 이름 (예: `week11-temp-{StudentId}-ap-northeast-2`)
    - `GlueServiceRoleName`: AWS Glue 서비스 역할 이름

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

### Amazon S3 버킷 확인

19. 상단 검색창에 `S3`를 입력하고 선택합니다.
20. 다음 3개의 버킷이 생성되었는지 확인합니다:
    - `week11-data-{StudentId}-ap-northeast-2` (데이터 버킷)
    - `week11-scripts-{StudentId}-ap-northeast-2` (스크립트 버킷)
    - `week11-temp-{StudentId}-ap-northeast-2` (임시 버킷)
21. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
22. 다음 폴더들이 자동으로 생성되었는지 확인합니다:
    - `raw/` - 원본 데이터 저장
    - `processed/` - 처리된 데이터 저장
23. `raw/` 폴더를 클릭합니다.
24. `transactions.csv` 파일이 자동으로 업로드되었는지 확인합니다.
25. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

> [!NOTE]
> `transactions.csv`는 전자상거래 거래 데이터로, `transaction_id`, `customer_id`, `product_id`, `amount`, `transaction_date`, `region` 컬럼을 포함합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다. Amazon S3 버킷, AWS IAM 역할, AWS Lambda 함수, EventBridge 규칙이 자동으로 생성되었습니다.

## 태스크 1: AWS Glue Database 생성

이 태스크에서는 **AWS Glue Data Catalog**에 데이터베이스를 직접 생성합니다. 데이터베이스는 테이블의 논리적 그룹으로, Crawler가 생성하는 테이블이 저장되는 컨테이너입니다.

26. 상단 검색창에 `Glue`를 입력하고 선택합니다.
27. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
28. [[Add database]] 버튼을 클릭합니다.
29. **Name**에 `week11_pipeline_{StudentId}`를 입력합니다.

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다. 예: `week11_pipeline_20240001`
>
> AWS Glue Database 이름에는 하이픈(-)을 사용할 수 없습니다. 언더스코어(\_)를 사용합니다.

30. **Location - optional**에 `s3://week11-data-{StudentId}-ap-northeast-2/`를 입력합니다.
31. **Description - optional**에 `Week 11-3 data pipeline lab database`를 입력합니다.
32. [[Create database]] 버튼을 클릭합니다.
33. 데이터베이스 목록에서 `week11_pipeline_{StudentId}`가 생성되었는지 확인합니다.

✅ **태스크 완료**: AWS Glue Database를 직접 생성했습니다.

## 태스크 2: AWS Glue Crawler 생성 및 실행

이 태스크에서는 **AWS Glue Crawler**를 직접 생성하고 실행하여 Amazon S3의 CSV 데이터를 스캔하고 Data Catalog 테이블을 자동으로 생성합니다.

### 태스크 2.1: Crawler 생성

34. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
35. [[Create crawler]] 버튼을 클릭합니다.
36. **Crawler name**에 `week11-pipeline-crawler-{StudentId}`를 입력합니다.

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

37. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-3`    |
| `CreatedBy` | `Student` |

38. [[Next]] 버튼을 클릭합니다.
39. **Data source configuration**에서 다음을 설정합니다:
    - **Is your data already mapped to Glue tables?**: `Not yet` 선택
    - **Data sources**: [[Add a data source]] 버튼을 클릭합니다.
40. **Add a data source** 대화상자에서 다음을 설정합니다:
    - **Data source**: `S3` 선택
    - **S3 path**: `s3://week11-data-{StudentId}-ap-northeast-2/raw/` 입력 (또는 Browse S3로 선택)
41. [[Add an Amazon S3 data source]] 버튼을 클릭합니다.
42. [[Next]] 버튼을 클릭합니다.
43. **Security configuration**에서 **Existing IAM role**을 선택합니다.
44. 태스크 0에서 AWS CloudFormation이 생성한 역할을 선택합니다.

> [!NOTE]
> Outputs 탭에서 확인한 `GlueServiceRoleName` 값을 사용합니다. 역할 이름은 `week11-3-pipeline-stack-GlueServiceRole-XXXXXXXXXXXX` 형태입니다.

45. [[Next]] 버튼을 클릭합니다.
46. **Set output and scheduling**에서 다음을 설정합니다:
    - **Target database**: `week11_pipeline_{StudentId}` 선택
    - **Crawler schedule**: `On demand` 유지
47. [[Next]] 버튼을 클릭합니다.
48. 설정을 검토하고 [[Create crawler]] 버튼을 클릭합니다.

### 태스크 2.2: Crawler 실행

49. 생성된 Crawler `week11-pipeline-crawler-{StudentId}`를 선택합니다.
50. [[Run]] 버튼을 클릭합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. **State**가 "Running"에서 "Ready"로 변경될 때까지 기다립니다.
> 페이지를 새로고침하여 최신 상태를 확인할 수 있습니다.

51. **Tables added** 값이 1인지 확인합니다.

### 태스크 2.3: 생성된 테이블 확인

52. 왼쪽 메뉴에서 **Data Catalog** > **Tables**를 선택합니다.
53. **Database** 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.
54. 생성된 테이블 `raw`를 클릭합니다.

> [!NOTE]
> Crawler는 Amazon S3 폴더명을 기반으로 테이블 이름을 생성합니다. `raw/` 폴더를 스캔했으므로 테이블 이름이 `raw`가 됩니다.

55. **Schema** 탭에서 자동으로 추론된 컬럼들을 확인합니다:
    - `transaction_id` (bigint)
    - `customer_id` (string)
    - `product_id` (string)
    - `amount` (double)
    - `transaction_date` (string)
    - `region` (string)

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

56. 왼쪽 메뉴에서 **ETL jobs**를 선택합니다.
57. **Create job** 섹션에서 **Visual ETL** 카드를 클릭합니다.

> [!NOTE]
> **Create job** 섹션에는 3가지 옵션이 카드 형태로 표시됩니다:
>
> - **Visual ETL**: 시각적 인터페이스로 데이터 흐름 구성 (이 실습에서 사용)
> - **Notebook**: 대화형 코드 노트북
> - **Script editor**: 스크립트 편집기
>
> 또는 왼쪽 메뉴에서 **Visual ETL**을 직접 선택해도 동일합니다.

### 태스크 3.2: Source 노드 추가

58. 캔버스의 [[+ Add nodes]] 버튼을 클릭합니다.
59. **Sources** 탭에서 **AWS Glue Data Catalog**를 선택합니다.
60. 오른쪽 **Data source properties - Data Catalog** 패널에서 다음을 설정합니다:
    - **Database**: `week11_pipeline_{StudentId}` 선택
    - **Table**: `raw` 선택

> [!NOTE]
> Database와 Table을 선택하면 하단의 **Output schema** 탭에서 컬럼 정보를 미리 확인할 수 있습니다.

### 태스크 3.3: Transform 노드 추가

61. 캔버스의 [[+ Add nodes]] 버튼을 다시 클릭합니다.
62. **Transforms** 탭에서 **Change Schema**를 선택합니다.
63. 오른쪽 **Transform** 패널에서 다음을 확인합니다:
    - **Node parents**: `AWS Glue Data Catalog`가 자동으로 연결되어 있는지 확인합니다.
64. **Change Schema (Apply mapping)** 테이블에서 컬럼 매핑을 확인합니다:

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

65. 캔버스의 [[+ Add nodes]] 버튼을 다시 클릭합니다.
66. **Targets** 탭에서 **Amazon S3**를 선택합니다.
67. 오른쪽 **Data target properties - S3** 패널에서 다음을 설정합니다:
    - **Format**: `Parquet` 선택
    - **Compression Type**: `Snappy` 유지 (기본값)
    - **S3 Target Location**: `s3://week11-data-{StudentId}-ap-northeast-2/processed/` 입력

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다. S3 경로는 반드시 슬래시(`/`)로 끝나야 합니다.

> [!NOTE]
> **Snappy 압축**: Parquet 파일의 기본 압축 알고리즘입니다. 압축/해제 속도가 빠르고 적절한 압축률을 제공하여 ETL 작업에 적합합니다.

68. 캔버스에서 3개의 노드가 연결된 것을 확인합니다:
    - **AWS Glue Data Catalog** → **Change Schema** → **Amazon S3**

### 태스크 3.5: Job 설정

69. 상단 탭에서 **Job details**를 선택합니다.
70. 다음을 설정합니다:
    - **Name**: `week11-etl-csv-to-parquet-{StudentId}` 입력
    - **IAM Role**: 태스크 0에서 생성된 Glue 서비스 역할 선택 (Outputs의 `GlueServiceRoleName`)
    - **Glue version**: `Glue 5.0` 또는 `Glue 5.1` (콘솔 기본값 사용)

> [!NOTE]
> AWS Glue 5.1이 2026년 2월부터 서울 리전에서 사용 가능합니다. 콘솔 기본값이 `Glue 5.0` 또는 `Glue 5.1`로 표시될 수 있으며, 어느 버전이든 이 실습에서는 동일하게 동작합니다.

    - **Language**: `Python 3` 유지 (기본값)
    - **Worker type**: `G 1X` 유지 (기본값)
    - **Automatically scale the number of workers**: 체크 해제
    - **Requested number of workers**: `2` 입력

> [!NOTE]
> **Automatically scale the number of workers**가 활성화되어 있으면 Worker 수를 직접 지정할 수 없습니다.
> 이 실습에서는 비용 절감을 위해 자동 스케일링을 해제하고 Worker 수를 2로 고정합니다.

71. 아래로 스크롤하여 **Advanced properties**를 펼칩니다.
72. **Temporary path**에 `s3://week11-temp-{StudentId}-ap-northeast-2/temp/` 를 입력합니다.

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

73. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-3`    |
| `CreatedBy` | `Student` |

74. 상단의 [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Job이 저장되면 상단의 "Job has not been saved" 메시지가 사라집니다.

### 태스크 3.6: ETL Job 실행

75. 상단의 [[Run]] 버튼을 클릭합니다.

> [!NOTE]
> ETL Job 실행에 3-5분이 소요됩니다. AWS Glue는 Apache Spark 클러스터를 시작하고, CSV 데이터를 읽고, Parquet 형식으로 변환하여 저장합니다.
> **Runs** 탭에서 실행 상태를 확인할 수 있습니다.

76. **Runs** 탭을 선택합니다.

> [!NOTE]
> **Run status**가 "Running"에서 "Succeeded"로 변경될 때까지 기다립니다. ETL Job 실행에 3-5분이 소요됩니다.

> [!TROUBLESHOOTING]
> **문제**: Run status가 "Failed"로 표시됩니다
>
> **원인**: IAM 역할 권한 부족, S3 경로 오류, 또는 Database/Table 설정 오류
>
> **해결**:
>
> 1. **Error message**를 클릭하여 상세 오류를 확인합니다
> 2. **Visual** 탭으로 돌아가 Source의 Database/Table, Target의 S3 경로를 확인합니다
> 3. **Job details** 탭에서 IAM Role과 Temporary path를 확인합니다
> 4. 수정 후 [[Save]] → [[Run]]을 다시 실행합니다

### 태스크 3.7: 변환 결과 확인

77. Amazon S3 콘솔로 이동합니다.
78. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
79. `processed/` 폴더를 클릭합니다.
80. Parquet 파일이 생성되었는지 확인합니다.

> [!NOTE]
> ETL Job이 CSV 데이터를 Parquet 형식으로 변환하여 저장했습니다. Parquet 파일은 `.parquet` 또는 `.snappy.parquet` 확장자를 가집니다. 원본 CSV 파일과 비교하여 파일 크기가 줄어든 것을 확인할 수 있습니다.

81. **Script** 탭을 선택하면 Visual ETL이 자동으로 생성한 PySpark 코드를 확인할 수 있습니다.

> [!NOTE]
> Visual ETL은 시각적으로 구성한 파이프라인을 자동으로 PySpark 코드로 변환합니다. Script 탭에서 생성된 코드를 확인하고 학습할 수 있습니다.

✅ **태스크 완료**: AWS Glue Visual ETL Job을 직접 생성하여 CSV 데이터를 Parquet 형식으로 변환했습니다.

## 태스크 4: Amazon Athena로 처리된 데이터 쿼리

이 태스크에서는 Amazon Athena를 사용하여 Parquet로 변환된 데이터를 SQL로 쿼리합니다.

### 태스크 4.1: Athena 쿼리 결과 위치 설정

82. 상단 검색창에 `Athena`를 입력하고 선택합니다.
83. Amazon Athena 시작 페이지가 표시되면 **Query your data in Athena console** 섹션을 찾아 해당 영역을 클릭합니다.

> [!NOTE]
> 이미 Query editor가 표시되는 경우 89단계를 건너뜁니다.

84. 왼쪽 메뉴에서 **Query editor**를 선택합니다.
85. 상단의 **Workgroup** 드롭다운에서 `primary`가 선택되어 있는지 확인합니다.

> [!NOTE]
> 이 실습에서는 **primary 워크그룹**을 사용합니다. Week 11-2에서는 전용 워크그룹을 생성했지만, 이번 실습에서는 기본 워크그룹의 설정만 변경하여 사용합니다.

86. 상단 탭에서 **Query settings**를 선택합니다.
87. **Query result location**이 설정되어 있지 않으면 [[Manage]] 버튼을 클릭합니다.
88. **Query result location**에 `s3://week11-temp-{StudentId}-ap-northeast-2/athena-results/`를 입력합니다.

> [!IMPORTANT]
> `{StudentId}`를 본인의 학번 또는 고유 식별자로 변경합니다.

89. [[Save]] 버튼을 클릭합니다.

### 태스크 4.2: 처리된 데이터 테이블 생성

90. **Editor** 탭을 선택합니다.
91. 왼쪽 패널의 **Data source**가 `AwsDataCatalog`인지 확인합니다.
92. **Database** 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.
93. 다음 쿼리를 입력합니다:

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
> **EXTERNAL TABLE**은 데이터를 Amazon S3에 그대로 두고 메타데이터만 AWS Glue Data Catalog에 저장합니다. 테이블을 삭제해도 Amazon S3의 실제 데이터는 삭제되지 않습니다.

94. [[Run]] 버튼을 클릭합니다.

### 태스크 4.3: 데이터 쿼리 및 분석

95. 다음 쿼리를 입력하여 처리된 데이터를 확인합니다:

```sql
SELECT * FROM processed_transactions LIMIT 10;
```

96. [[Run]] 버튼을 클릭합니다.
97. 결과를 확인합니다.

> [!NOTE]
> CSV 원본 데이터와 동일한 내용이 Parquet 형식으로 저장되어 있음을 확인할 수 있습니다.

98. 지역별 매출을 분석하는 쿼리를 실행합니다:

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

99. 제품별 판매 실적을 확인하는 쿼리를 실행합니다:

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

100. 원본 테이블(`raw`)과 변환된 테이블(`processed_transactions`)의 데이터 스캔량을 비교합니다:

```sql
SELECT COUNT(*) as total_records FROM raw;
```

```sql
SELECT COUNT(*) as total_records FROM processed_transactions;
```

> [!NOTE]
> 각 쿼리 실행 후 하단의 **Data scanned** 값을 비교합니다. Parquet 형식은 컬럼 기반 저장이므로 필요한 컬럼만 읽어 데이터 스캔량이 줄어듭니다. Athena는 스캔한 데이터량에 따라 과금($5/TB)되므로 Parquet 변환은 비용 절감에 효과적입니다.

✅ **태스크 완료**: Amazon Athena로 변환된 데이터를 쿼리하고 분석했습니다.

## 태스크 5: 이벤트 기반 파이프라인 자동화 확인

이 태스크에서는 새로운 데이터를 업로드하여 EventBridge와 AWS Lambda가 자동으로 Crawler를 트리거하는 전체 파이프라인 흐름을 확인합니다.

> [!NOTE]
> **파이프라인 자동화 흐름**:
>
> 1. 새 파일이 데이터 버킷의 `raw/` 폴더에 업로드됨
> 2. EventBridge가 Amazon S3 이벤트 감지
> 3. AWS Lambda 함수가 자동으로 실행됨
> 4. AWS Lambda 함수가 AWS Glue Crawler 시작
> 5. Crawler가 새 데이터를 스캔하고 Data Catalog 업데이트

### 태스크 5.1: 새 데이터 업로드

101. Amazon S3 콘솔로 이동합니다.
102. 데이터 버킷(`week11-data-{StudentId}-ap-northeast-2`)을 선택합니다.
103. `raw/` 폴더를 클릭합니다.
104. [[Upload]] 버튼을 클릭합니다.
105. 다운로드한 ZIP 파일에서 `sales-data.csv` 파일을 선택합니다.
106. [[Upload]] 버튼을 클릭합니다.

### 태스크 5.2: AWS Lambda 자동 실행 확인

107. 상단 검색창에 `Lambda`를 입력하고 선택합니다.
108. `week11-pipeline-trigger-{StudentId}` 함수를 선택합니다.
109. **Monitor** 탭을 선택합니다.
110. **Logs**를 클릭하여 Amazon CloudWatch Logs에서 실행 로그를 확인합니다.

> [!NOTE]
> 로그에서 "Starting AWS Glue Crawler" 메시지를 확인할 수 있습니다. 이는 EventBridge가 Amazon S3 업로드 이벤트를 감지하고 AWS Lambda 함수를 자동으로 실행했음을 의미합니다.

### 태스크 5.3: Crawler 자동 실행 확인

111. AWS Glue 콘솔로 이동합니다.
112. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
113. `week11-pipeline-crawler-{StudentId}` Crawler를 선택합니다.
114. **State**가 "Running"인지 확인합니다.

> [!NOTE]
> AWS Lambda 함수가 자동으로 Crawler를 시작했습니다. Crawler는 새로 업로드된 데이터를 스캔하여 Data Catalog를 업데이트합니다. **State**가 "Ready"로 변경될 때까지 기다립니다.

### 태스크 5.4: 업데이트된 데이터 확인

115. Amazon Athena 콘솔로 이동합니다.
116. **Editor** 탭을 선택합니다.
117. **Database**에서 `week11_pipeline_{StudentId}`를 선택합니다.
118. 다음 쿼리를 실행하여 새 데이터가 포함되었는지 확인합니다:

```sql
SELECT COUNT(*) as total_records FROM raw;
```

> [!NOTE]
> 레코드 수가 증가했는지 확인합니다. 초기 `transactions.csv`의 레코드 수와 비교하여 새로 업로드한 `sales-data.csv`의 레코드가 추가되었는지 확인할 수 있습니다.

> [!IMPORTANT]
> Crawler가 재실행되면 기존 `raw` 테이블의 스키마를 업데이트합니다. 그러나 `processed_transactions` 테이블은 자동으로 업데이트되지 않습니다. 새 데이터를 Parquet로 변환하려면 태스크 3의 ETL Job을 다시 실행해야 합니다.

✅ **태스크 완료**: EventBridge와 AWS Lambda를 활용한 이벤트 기반 파이프라인 자동화 흐름을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Glue Database를 직접 생성하여 데이터 카탈로그를 구성했습니다
- AWS Glue Crawler를 직접 생성하고 실행하여 Amazon S3 데이터의 스키마를 자동으로 추론했습니다
- AWS Glue Visual ETL Job을 직접 생성하여 CSV 데이터를 Parquet 형식으로 변환했습니다
- Amazon Athena로 변환된 데이터를 SQL로 쿼리하고 분석했습니다
- EventBridge와 AWS Lambda를 활용한 이벤트 기반 파이프라인 자동화 흐름을 확인했습니다

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 반드시 수행하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`를 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `11-3`
6. [[Search resources]] 버튼을 클릭합니다.

> [!OUTPUT]
> 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제 후 스택 삭제

#### 1단계: Athena 수동 생성 테이블 삭제

7. Amazon Athena 콘솔로 이동합니다.
8. **Editor** 탭을 선택합니다.
9. **Database**에서 `week11_pipeline_{StudentId}`를 선택합니다.
10. 다음 쿼리를 실행합니다:

```sql
DROP TABLE IF EXISTS processed_transactions;
```

11. [[Run]] 버튼을 클릭합니다.

> [!NOTE]
> 태스크 4.2에서 Athena로 생성한 `processed_transactions` 테이블은 AWS CloudFormation이 관리하지 않으므로 수동으로 삭제해야 합니다.

#### 2단계: AWS Glue ETL Job 삭제

12. AWS Glue 콘솔로 이동합니다.
13. 왼쪽 메뉴에서 **ETL jobs**를 선택합니다.
14. `week11-etl-csv-to-parquet-{StudentId}` Job을 선택합니다.
15. **Actions** > `Delete`를 선택합니다.
16. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

#### 3단계: AWS Glue Crawler 삭제

17. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
18. `week11-pipeline-crawler-{StudentId}` Crawler의 **State**가 "Ready"인지 확인합니다.

> [!IMPORTANT]
> Crawler가 실행 중인 상태에서 삭제하면 오류가 발생할 수 있습니다. "Ready" 상태가 될 때까지 기다립니다.

19. `week11-pipeline-crawler-{StudentId}`를 선택합니다.
20. **Actions** > `Delete`를 선택합니다.
21. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

#### 4단계: AWS Glue 테이블 및 Database 삭제

22. 왼쪽 메뉴에서 **Data Catalog** > **Tables**를 선택합니다.
23. **Database** 드롭다운에서 `week11_pipeline_{StudentId}`를 선택합니다.
24. `raw` 테이블을 선택합니다.
25. **Actions** > `Delete table`을 선택합니다.
26. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
27. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
28. `week11_pipeline_{StudentId}`를 선택합니다.
29. [[Delete]] 버튼을 클릭합니다.
30. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

#### 5단계: Amazon S3 버킷 비우기

> [!IMPORTANT]
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제가 실패합니다. 반드시 3개 버킷을 모두 비운 후 스택을 삭제해야 합니다.

31. Amazon S3 콘솔로 이동합니다.
32. `week11-data-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
33. [[Empty]] 버튼을 클릭합니다.
34. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
35. `week11-scripts-{StudentId}-ap-northeast-2` 버킷에 대해 33-35단계를 반복합니다.
36. `week11-temp-{StudentId}-ap-northeast-2` 버킷에 대해 33-35단계를 반복합니다.

#### 6단계: AWS CloudFormation 스택 삭제

37. AWS CloudFormation 콘솔로 이동합니다.
38. `week11-3-pipeline-stack` 스택을 선택합니다.
39. [[Delete]] 버튼을 클릭합니다.
40. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. 삭제가 완료될 때까지 기다립니다.
> AWS CloudFormation 스택을 삭제하면 다음 리소스가 자동으로 삭제됩니다:
>
> - Amazon S3 버킷 3개 (버킷이 비어있는 경우)
> - AWS IAM 역할 2개
> - AWS Lambda 함수
> - EventBridge 규칙

> [!TROUBLESHOOTING]
> **문제**: AWS CloudFormation 스택 삭제가 "DELETE_FAILED" 상태로 실패합니다
>
> **원인**: Amazon S3 버킷에 객체가 남아 있거나, AWS Glue Crawler가 실행 중입니다.
>
> **해결**:
>
> 1. Amazon S3 콘솔에서 3개 버킷을 모두 확인하고 Empty 버튼으로 비웁니다
> 2. AWS Glue 콘솔에서 Crawler 상태가 "Ready"인지 확인합니다
> 3. AWS CloudFormation 콘솔에서 스택을 다시 선택하고 Delete 버튼을 클릭합니다

#### 7단계: Amazon S3 버킷 삭제 확인

41. Amazon S3 콘솔로 이동합니다.
42. `week11-data-{StudentId}-ap-northeast-2` 버킷이 남아있는 경우 선택합니다.
43. [[Delete]] 버튼을 클릭합니다.
44. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.
45. `week11-scripts-{StudentId}-ap-northeast-2` 버킷에 대해 44-46단계를 반복합니다.
46. `week11-temp-{StudentId}-ap-northeast-2` 버킷에 대해 44-46단계를 반복합니다.

#### 8단계: Amazon CloudWatch Log Group 삭제

47. AWS Management Console 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
48. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
49. 검색창에 `week11-pipeline-trigger`를 입력합니다.
50. `/aws/lambda/week11-pipeline-trigger-{StudentId}` 로그 그룹을 선택합니다.
51. **Actions** > `Delete log group(s)`를 선택합니다.
52. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
53. 검색창에 `week11-3-data-pipeline-lab-SampleDataUploader`를 입력합니다.
54. 해당 로그 그룹이 존재하면 선택하고 동일하게 삭제합니다.

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.
> 로그 그룹을 삭제하지 않으면 스토리지 비용(GB당 월 $0.50)이 계속 부과됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS Glue 개발자 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/dg/what-is-glue.html)
- [AWS Glue Visual ETL 사용 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/ug/author-job-glue.html)
- [Amazon Athena 사용 설명서](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/what-is.html)
- [데이터 레이크 아키텍처](https://aws.amazon.com/ko/big-data/datalakes-and-analytics/)
- [AWS Lambda 개발자 가이드](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/welcome.html)
- [EventBridge 사용 설명서](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/eb-what-is.html)

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
- PySpark 및 Python Shell 작업 지원

**Amazon Athena**

- 서버리스 대화형 쿼리 서비스
- 표준 SQL로 Amazon S3 데이터 분석
- Presto 기반 고성능 쿼리 엔진
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
