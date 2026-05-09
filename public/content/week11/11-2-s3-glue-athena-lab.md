---
title: 'AWS Glue Crawler 설정 및 Data Catalog 확인'
week: 11
session: 2
awsServices:
  - Amazon S3
  - AWS Glue
  - Amazon Athena
learningObjectives:
  - 데이터 레이크의 개념과 AWS Glue Data Catalog의 역할을 이해할 수 있습니다.
  - AWS Glue Crawler를 생성하고 Amazon S3 데이터의 스키마를 자동 검색할 수 있습니다.
  - Amazon Athena로 AWS Glue 데이터 카탈로그를 쿼리할 수 있습니다.
  - 파티셔닝을 적용하여 쿼리 성능을 최적화할 수 있습니다.

prerequisites:
  - Amazon S3 기본 사용법 이해
  - SQL 기본 문법 이해
  - CSV, JSON 데이터 형식 이해
---

이번 실습에서는 QuickTable 레스토랑 예약 시스템의 샘플 데이터를 Amazon S3 데이터 레이크에 저장하고, AWS Glue Database와 Crawler를 직접 생성하여 메타데이터를 수집한 후, Amazon Athena Workgroup을 구성하고 서버리스 SQL 쿼리를 실행하여 비즈니스 인사이트를 도출합니다.

AWS CloudFormation이 Amazon S3 버킷과 샘플 데이터를 자동으로 준비하면, 학생이 직접 AWS Glue Data Catalog를 구성하고 Amazon Athena로 인기 레스토랑, 피크 예약 시간대, 취소율, 평균 파티 규모 등을 분석합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
> Amazon S3 버킷, AWS Glue Crawler, Amazon Athena Workgroup 등이 생성되며, 쿼리 실행 시 스캔된 데이터량에 따라 비용이 부과됩니다 ($5/TB).

> [!DOWNLOAD]
> [week11-2-datalake-lab.zip](/files/week11/week11-2-datalake-lab.zip)
>
> - `week11-2-datalake-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷 3개, AWS IAM 역할, 샘플 데이터 자동 업로드)
> - `sales.csv` - 매출 샘플 데이터 (참고용)
> - `customers.json` - 고객 샘플 데이터 (참고용)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿으로 Amazon S3 버킷, AWS IAM 역할, 샘플 데이터 자동 생성)

## 태스크 0: Amazon S3 데이터 레이크 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 **Amazon S3 버킷**과 **샘플 데이터**, **AWS IAM 역할**을 자동으로 생성합니다. AWS Glue Database, Crawler, Amazon Athena Workgroup은 이후 태스크에서 직접 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷 3개**: Raw Data (예약 원본), Processed Data (집계 데이터), Query Results (Amazon Athena 결과)
- **AWS IAM 역할**: AWS Glue Crawler가 Amazon S3 및 AWS Glue 카탈로그에 접근하기 위한 권한
- **샘플 데이터**: AWS Lambda 함수를 통해 QuickTable 예약 데이터 자동 업로드 (reservations.csv, restaurants.json)

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week11-2-datalake-lab.zip` 파일의 압축을 해제합니다.
2. `week11-2-datalake-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

    <img src="/images/week11/11-2-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week11-2-datalake-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task0-step8-upload.png" alt="CloudFormation 템플릿 업로드" class="guide-img-md" />

9. **Stack name**에 `week11-2-quicktable-datalake-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 입력합니다:
    - **StudentId**: 학번 또는 고유 식별자 (예: `20240001` 또는 `student01`, 영문 소문자·숫자·하이픈만 사용, 5-20자)
    - **EnvironmentName**: `quicktable` (기본값 유지)

> [!NOTE]
> StudentId는 Amazon S3 버킷명 등 모든 리소스 이름에 접미사로 추가되어 리소스 충돌을 방지합니다.
> EnvironmentName은 Amazon S3 버킷명의 접두사로 사용됩니다 (예: `quicktable-raw-{StudentId}-ap-northeast-2`).

11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task0-step11-options.png" alt="CloudFormation Configure stack options" class="guide-img-md" />

12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week11/11-2-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. **Outputs** 탭을 선택합니다.
19. 출력값들을 확인하고 메모장에 복사합니다:
    - `RawDataBucketName`: Raw Data Amazon S3 버킷 이름 (예: quicktable-raw-20240001-ap-northeast-2)
    - `ProcessedDataBucketName`: Processed Data Amazon S3 버킷 이름 (예: quicktable-processed-20240001-ap-northeast-2)
    - `QueryResultsBucketName`: Query Results Amazon S3 버킷 이름 (예: quicktable-query-20240001-ap-northeast-2)
    - `GlueCrawlerRoleArn`: AWS Glue Crawler용 AWS IAM 역할 ARN
    - `SampleDataLocation`: QuickTable 예약 샘플 데이터 위치 (reservations.csv, restaurants.json)

    <img src="/images/week11/11-2-task0-step19-outputs.png" alt="CloudFormation Outputs 탭" class="guide-img-md" />

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.
> 특히 `GlueCrawlerRoleArn`은 태스크 2에서 Crawler 생성 시 필요합니다.

✅ **태스크 완료**: Amazon S3 데이터 레이크 환경이 준비되었습니다.

## 태스크 1: QuickTable 예약 데이터 및 Amazon S3 버킷 확인

이 태스크에서는 AWS CloudFormation이 자동으로 생성한 **Amazon S3 버킷**과 QuickTable 예약 샘플 데이터를 확인합니다.

20. AWS Management Console에 로그인한 후 상단 검색창에 `S3`을 입력하고 선택합니다.
21. 버킷 목록에서 태스크 0에서 생성된 3개의 버킷을 확인합니다:
    - `quicktable-raw-{StudentId}-ap-northeast-2` (Raw Data 버킷 - QuickTable 예약 원본)
    - `quicktable-processed-{StudentId}-ap-northeast-2` (Processed Data 버킷 - 집계 데이터)
    - `quicktable-query-{StudentId}-ap-northeast-2` (Query Results 버킷 - Amazon Athena 결과)

    <img src="/images/week11/11-2-task1-step21-buckets.png" alt="S3 버킷 목록" class="guide-img-md" />

22. Raw Data 버킷 (`quicktable-raw-{StudentId}-ap-northeast-2`)을 선택합니다.
23. 다음 폴더 구조가 자동으로 생성되었는지 확인합니다:
    - `reservation-data/` - QuickTable 예약 데이터 폴더
    - `restaurant-data/` - QuickTable 레스토랑 정보 폴더

    <img src="/images/week11/11-2-task1-step23-folders.png" alt="S3 폴더 구조" class="guide-img-md" />

24. `reservation-data/` 폴더를 클릭합니다.
25. `reservations.csv` 파일이 자동으로 업로드되었는지 확인합니다.

    <img src="/images/week11/11-2-task1-step25-csv.png" alt="reservations.csv 파일 확인" class="guide-img-md" />

26. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

    <img src="/images/week11/11-2-task1-step26-json.png" alt="파일 다운로드" class="guide-img-md" />

> [!OUTPUT]
>
> ```csv
> reservationId,userId,restaurantId,restaurantName,date,time,partySize,status,totalAmount,createdAt
> RES001,user123,REST001,Gangnam Restaurant,2024-01-15,18:30,4,confirmed,120000,2024-01-10T10:30:00.123456
> RES002,user456,REST002,Seoul Korean,2024-01-16,19:00,2,cancelled,60000,2024-01-12T14:20:00.234567
> RES003,user789,REST001,Gangnam Restaurant,2024-01-17,12:00,6,confirmed,180000,2024-01-15T09:15:00.345678
> RES004,user123,REST003,Busan Seafood,2024-01-20,19:30,3,confirmed,90000,2024-01-18T11:45:00.456789
> RES005,user456,REST002,Seoul Korean,2024-01-22,20:00,5,confirmed,150000,2024-01-20T16:30:00.567890
> ```

27. 상위 폴더로 돌아가서 `restaurant-data/` 폴더를 클릭합니다.
28. `restaurants.json` 파일이 자동으로 업로드되었는지 확인합니다.

    <img src="/images/week11/11-2-task1-step28-restaurant-folder.png" alt="restaurant-data 폴더" class="guide-img-md" />

29. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

    <img src="/images/week11/11-2-task1-step29-restaurant-json.png" alt="restaurants.json 파일" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {"restaurantId": "REST001", "name": "Gangnam Restaurant", "cuisine": "Korean", "location": "Gangnam", "rating": 4.5}
> {"restaurantId": "REST002", "name": "Seoul Korean", "cuisine": "Korean", "location": "Seoul", "rating": 4.2}
> {"restaurantId": "REST003", "name": "Busan Seafood", "cuisine": "Seafood", "location": "Busan", "rating": 4.7}
> ```

> [!NOTE]
> **JSON Lines 형식 주의사항**:
>
> 이 실습의 `restaurants.json`은 JSON Lines 형식입니다:
>
> - 각 줄이 독립적인 JSON 객체
> - 배열(`[]`) 없이 줄바꿈으로 구분
> - AWS Glue Crawler가 자동으로 인식
>
> **표준 JSON 배열 형식과의 차이**:
>
> ```json
> // JSON Lines (이 실습에서 사용)
> {"restaurantId": "REST001", ...}
> {"restaurantId": "REST002", ...}
>
> // 표준 JSON 배열 (Crawler가 잘못 인식할 수 있음)
> [
>   {"restaurantId": "REST001", ...},
>   {"restaurantId": "REST002", ...}
> ]
> ```
>
> Crawler가 스키마를 잘못 추론한 경우 Edit schema에서 수동으로 컬럼 타입을 수정할 수 있습니다.

> [!TIP]
> **샘플 데이터 확장 권장**:
>
> 최소 50-100건의 데이터가 있어야 의미있는 분석 결과를 확인할 수 있습니다.
>
> 현재 5건으로도 실습은 가능하지만, 집계 결과가 원본 데이터와 거의 동일하게 보일 수 있습니다.

> [!CONCEPT] 데이터 레이크 구조 (Data Lake Structure)
> **폴더 구조 설계**
>
> - `reservation-data/`: QuickTable 예약 원본 데이터 (CSV)
> - `restaurant-data/`: QuickTable 레스토랑 정보 (JSON)
> - `processed/`: 처리된 데이터 (Parquet)
> - `athena-results/`: 쿼리 결과 저장
>
> **파티셔닝 전략**
>
> - 날짜별: `year=2024/month=01/day=15/`
> - 리전별: `region=Seoul/`
> - 조합: `year=2024/month=01/region=Seoul/`
>
> **파일 형식**
>
> - CSV: 간단, 사람이 읽기 쉬움
> - JSON: 중첩 구조 지원
> - Parquet: 컬럼형, 압축 효율적 (권장)
> - ORC: 컬럼형, Hive 최적화
>
> **Amazon S3 스토리지 클래스**
>
> - Standard: 자주 접근하는 데이터
> - Intelligent-Tiering: 자동 최적화
> - Glacier: 아카이브 (저렴)

✅ **태스크 완료**: Amazon S3 버킷 및 샘플 데이터를 확인했습니다.

## 태스크 2: AWS Glue Database 및 Crawler 생성

이 태스크에서는 **AWS Glue Database**를 직접 생성하고, 예약 데이터를 스캔할 **Crawler**를 생성하여 실행합니다.

### 태스크 2.1: AWS Glue Database 생성

30. AWS Management Console에 로그인한 후 상단 검색창에 `Glue`를 입력하고 선택합니다.
31. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
32. [[Add database]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step32-add-database.png" alt="Add database 버튼" class="guide-img-md" />

33. **Database type**에서 `Glue Database`를 선택합니다 (기본값).
34. **Name**에 `quicktable_db_{StudentId}`를 입력합니다.

> [!NOTE]
> `{StudentId}`를 실제 학번으로 교체합니다 (예: `quicktable_db_20240001`).
> Database 이름에는 영문 소문자, 숫자, 언더스코어만 사용할 수 있습니다.

35. **Description - optional**에 `QuickTable data lake database for Week 11-2 lab`을 입력합니다.
36. **Location - optional**에 `s3://quicktable-raw-{StudentId}-ap-northeast-2/`를 입력합니다 (예: `s3://quicktable-raw-20240001-ap-northeast-2/`).

> [!NOTE]
> Location은 선택사항입니다. 이 실습에서는 Crawler 생성 시 S3 경로를 직접 지정하므로 비워두어도 동작에 영향이 없습니다. 입력하면 데이터베이스의 기본 데이터 위치가 명시적으로 기록됩니다.

37. [[Create database]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step37-create-database.png" alt="Create database" class="guide-img-md" />

38. 데이터베이스 목록에서 `quicktable_db_{StudentId}`가 생성되었는지 확인합니다.

    <img src="/images/week11/11-2-task2-step38-database-created.png" alt="Database 생성 확인 1" class="guide-img-md" />

    <img src="/images/week11/11-2-task2-step38-database-detail.png" alt="Database 생성 확인 2" class="guide-img-md" />

> [!NOTE]
> AWS Glue Database는 테이블 메타데이터를 논리적으로 그룹화하는 컨테이너입니다.
> 실제 데이터를 저장하지 않으며, Amazon S3에 저장된 데이터의 스키마 정보만 관리합니다.
> Amazon Athena, Amazon EMR, Amazon Redshift Spectrum 등 여러 서비스에서 이 카탈로그를 공유할 수 있습니다.
>
> **Amazon RDS / Amazon DynamoDB와의 차이:**
>
> | 구분        | AWS Glue Database               | Amazon RDS / Amazon DynamoDB |
> | ----------- | ------------------------------- | ---------------------------- |
> | 역할        | 메타데이터(스키마) 저장         | 실제 데이터 저장 및 처리     |
> | 데이터 위치 | Amazon S3 (외부)                | 서비스 내부 스토리지         |
> | 쿼리 엔진   | Amazon Athena 등 별도 엔진 사용 | 자체 쿼리 엔진 내장          |
> | 용도        | 분석용 데이터 레이크 카탈로그   | 트랜잭션 처리 (OLTP)         |

### 태스크 2.2: AWS Glue Crawler 생성

39. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
40. [[Create crawler]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step40-create-crawler.png" alt="Create crawler Step 1" class="guide-img-md" />

> [!NOTE]
> Crawler 생성은 5단계로 진행됩니다:
>
> - **Step 1**: Set crawler properties (이름, 설명, 태그)
> - **Step 2**: Choose data sources and classifiers (데이터 소스 설정)
> - **Step 3**: Configure security settings (IAM 역할 선택)
> - **Step 4**: Set output and scheduling (출력 데이터베이스, 스케줄)
> - **Step 5**: Review and create (검토 및 생성)

41. **Name**에 `quicktable-crawler-{StudentId}`를 입력합니다 (예: `quicktable-crawler-20240001`).

> [!NOTE]
> **Description** 필드는 선택사항입니다. 비워두어도 됩니다.

42. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-2`    |
| `CreatedBy` | `Student` |

43. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step43-next.png" alt="Step 1 완료 후 Next" class="guide-img-md" />

44. **Is your data already mapped to Glue tables?** 에서 `Not yet`이 선택되어 있는지 확인합니다 (기본값).
45. [[Add a data source]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step45-add-datasource.png" alt="Add a data source" class="guide-img-md" />

46. 모달 창에서 다음을 설정합니다:
    - **Data source**: `S3` (기본값)
    - **Network connection - optional**: 비워둡니다
    - **Location of S3 data**: `In this account` (기본값)
    - **S3 path**: [[Browse S3]] 버튼을 클릭하여 `quicktable-raw-{StudentId}-ap-northeast-2` 버킷의 `reservation-data/` 폴더를 선택하거나,  
      직접 `s3://quicktable-raw-{StudentId}-ap-northeast-2/reservation-data/`를 입력합니다.  
      (예: `s3://quicktable-raw-20240001-ap-northeast-2/reservation-data/`)
    - **Subsequent crawler runs**: `Crawl all sub-folders` (기본값)

    <img src="/images/week11/11-2-task2-step46-modal1.png" alt="Add data source 모달 설정 1" class="guide-img-sm" />

    <img src="/images/week11/11-2-task2-step46-modal2.png" alt="Add data source 모달 설정 2" class="guide-img-sm" />

> [!NOTE]
> **Custom classifiers** 섹션은 기본값을 유지합니다. CSV, JSON 등 일반적인 형식은 AWS Glue가 자동으로 인식합니다.

47. [[Add an S3 data source]] 버튼을 클릭합니다.
48. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step48-next.png" alt="Step 2 완료 후 Next" class="guide-img-md" />

49. **IAM role** 섹션의 **Existing IAM role** 드롭다운에서 `week11-2-quicktable-datalake-stack-GlueCrawlerRole`로 시작하는 역할을 선택합니다.

> [!NOTE]
> 정확한 역할명은 AWS CloudFormation 스택의 **Outputs** 탭에서 `GlueCrawlerRoleArn`을 확인합니다.  
> **Lake Formation configuration**: `Use Lake Formation credentials for crawling S3 data source` 체크하지 않습니다 (기본값).  
> **Security configuration**: `None` (기본값)을 유지합니다.

50. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step50-security.png" alt="Step 3 Configure security settings" class="guide-img-md" />

51. **Set output and scheduling** 페이지에서 다음을 설정합니다:
    - **Target database**: 드롭다운에서 `quicktable_db_{StudentId}`를 선택합니다.
    - **Table name prefix - optional**: 비워둡니다.
    - **Maximum table threshold - optional**: 비워둡니다.
    - **Crawler schedule** > **Frequency**: `On demand` (기본값)
52. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task2-step52-output.png" alt="Step 4 Set output and scheduling" class="guide-img-md" />

53. **Review and create** 페이지에서 설정을 검토하고 [[Create crawler]] 버튼을 클릭합니다.

### 태스크 2.3: Crawler 실행

54. Crawler 생성이 완료되면 상세 페이지가 표시됩니다. State가 **READY**인지 확인합니다.

    <img src="/images/week11/11-2-task2-step54-crawler-created.png" alt="Crawler 생성 완료 상세 페이지" class="guide-img-md" />

> [!TIP]
> 상세 페이지가 표시되지 않는 경우, 왼쪽 메뉴에서 **Crawlers**를 선택한 후 `quicktable-crawler-{StudentId}`를 클릭하여 이동합니다.
>
> <img src="/images/week11/11-2-task2-step54-crawler-list.png" alt="Crawlers 목록에서 선택" class="guide-img-sm" />

55. [[Run crawler]] 버튼을 클릭합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. 페이지를 새로고침하여 상태를 확인합니다.  
> Crawler는 `reservation-data/` 폴더의 CSV 파일을 스캔하여 자동으로 테이블을 생성합니다.  
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

56. **Crawler runs** 섹션에서 Status가 **Running** → **Completed**로 변경되는 것을 확인합니다.

    <img src="/images/week11/11-2-task2-step56-crawler-running.png" alt="Crawler 실행 중 Running 상태" class="guide-img-md" />

    <img src="/images/week11/11-2-task2-step56-crawler-completed.png" alt="Crawler 실행 완료 Completed 상태" class="guide-img-md" />

57. 실행이 완료되면 **Table changes** 컬럼에서 테이블 생성 결과를 확인합니다.

> [!OUTPUT]
>
> ```
> Status: Completed
> Table changes: 1 table change, 0 partition changes
> ```

> [!NOTE]
> **Crawler 데이터 소스 범위 분리 이유**:
>
> 이 실습에서는 의도적으로 두 개의 Crawler를 사용합니다:
>
> - **Crawler 1** (이 태스크): `reservation-data/` 폴더만 스캔
> - **Crawler 2** (태스크 5): `restaurant-data/` 폴더 스캔
>
> 실제 운영 환경에서는 하나의 Crawler로 여러 폴더를 스캔하도록 구성할 수 있습니다:
>
> - Data sources에 여러 Amazon S3 경로를 추가하거나
> - 상위 경로(`s3://bucket/`)를 지정합니다

✅ **태스크 완료**: AWS Glue Database와 Crawler를 생성하고 실행하여 데이터 카탈로그를 생성했습니다.

## 태스크 3: AWS Glue 테이블 확인

이 태스크에서는 AWS Glue Crawler가 자동으로 생성한 **테이블의 스키마**를 확인합니다.

58. AWS Glue 콘솔 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
59. 데이터베이스 목록에서 `quicktable_db_{StudentId}`를 클릭합니다.

    <img src="/images/week11/11-2-task3-step59-databases.png" alt="Databases 목록에서 quicktable_db 선택" class="guide-img-md" />

60. 데이터베이스 상세 페이지에서 **Tables** 섹션을 확인합니다.

    <img src="/images/week11/11-2-task3-step60-db-detail.png" alt="Database 상세 페이지 - Tables 섹션에서 reservation_data 테이블 확인" class="guide-img-md" />

61. Crawler가 생성한 `reservation_data` 테이블을 클릭합니다.

> [!TIP]
> **다른 방법**: 왼쪽 메뉴에서 **Data Catalog** > **Tables**를 선택하면 테이블 목록에서 `reservation_data`를 직접 클릭하여 테이블 상세 페이지로 이동할 수 있습니다.

> [!NOTE]
> **Crawler 실행 후 테이블명 확인 방법**:
>
> Crawler가 생성하는 테이블명은 Amazon S3 폴더명 기반이지만 예상과 다를 수 있습니다:
>
> - 하이픈(-)은 언더스코어(\_)로 변환
> - 경로 깊이에 따라 이름이 달라질 수 있음
>
> **Athena에서 확인**:
>
> ```sql
> SHOW TABLES IN quicktable_db_{StudentId};
> ```

62. **Schema** 탭에서 컬럼 정보를 확인합니다:

    <img src="/images/week11/11-2-task3-step62-schema.png" alt="reservation_data 테이블 Schema 탭 - 10개 컬럼 정보" class="guide-img-md" />

| #   | Column name    | Data type | Partition key | Comment |
| --- | -------------- | --------- | ------------- | ------- |
| 1   | reservationid  | string    | -             | -       |
| 2   | userid         | string    | -             | -       |
| 3   | restaurantid   | string    | -             | -       |
| 4   | restaurantname | string    | -             | -       |
| 5   | date           | string    | -             | -       |
| 6   | time           | string    | -             | -       |
| 7   | partysize      | bigint    | -             | -       |
| 8   | status         | string    | -             | -       |
| 9   | totalamount    | bigint    | -             | -       |
| 10  | createdat      | string    | -             | -       |

63. **Table overview** 탭에서 다음을 확인합니다:
    - **Table details** 섹션:
      - **Classification**: `CSV`
      - **Location**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/reservation-data/`
    - **▶ Advanced properties**를 클릭하여 펼칩니다:
      - **Input format**: org.apache.hadoop.mapred.TextInputFormat
      - **Output format**: org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat
      - **Serde serialization lib**: org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe

    <img src="/images/week11/11-2-task3-step63-advanced-properties.png" alt="Table overview - Advanced properties 펼친 상태" class="guide-img-md" />

64. **Schema** 탭에서 [[Edit schema]] 버튼을 클릭합니다.
65. `totalamount` 행의 체크박스를 선택합니다.
66. 상단의 [[Edit]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task3-step66-edit-schema.png" alt="Edit schema - totalamount 행 선택 후 Edit 버튼 클릭" class="guide-img-md" />

67. **Edit schema entry** 모달 창에서 **Data type** 드롭다운을 `double`로 변경합니다.
68. [[Save]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task3-step68-edit-entry.png" alt="Edit schema entry 모달 - Data type을 double로 변경" class="guide-img-sm" />

69. `totalamount`의 Data type이 `double`로 변경된 것을 확인합니다.
70. [[Save as new table version]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task3-step70-save-version.png" alt="Edit schema - totalamount double 변경 확인 후 Save as new table version" class="guide-img-md" />

    <img src="/images/week11/11-2-task3-step70-saved.png" alt="스키마 저장 완료" class="guide-img-md" />

> [!NOTE]
> Crawler는 샘플 데이터의 값(120000, 60000 등)이 정수이므로 `bigint`로 추론합니다.
> 실제 금액 데이터는 소수점이 포함될 수 있으므로 `double`로 변경하는 것이 적절합니다.
> 스키마 수정이 불필요하다면 이 단계를 건너뛰어도 됩니다.

> [!NOTE]
> AWS Glue 테이블은 Amazon S3 데이터의 메타데이터만 관리합니다. SerDe(Serializer/Deserializer)는 데이터 형식(CSV, JSON, Parquet)을 읽고 쓰는 방법을 정의합니다.
> Crawler가 CSV 파일을 자동으로 인식하여 적절한 SerDe를 설정했습니다.

✅ **태스크 완료**: AWS Glue 테이블 스키마를 확인했습니다.

## 태스크 4: Amazon Athena Workgroup 생성 및 쿼리 실행

이 태스크에서는 **Amazon Athena Workgroup**을 직접 생성하고, Amazon S3 데이터를 표준 SQL로 쿼리합니다.

### 태스크 4.1: Amazon Athena Workgroup 생성

71. AWS Management Console에 로그인한 후 상단 검색창에 `Athena`를 입력하고 선택합니다.
72. 왼쪽 메뉴에서 **Administration** > **Workgroups**를 선택합니다.
73. [[Create workgroup]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task4-step73-workgroups.png" alt="Athena Workgroups 페이지 - Create workgroup 버튼" class="guide-img-md" />

74. **Workgroup details** 섹션에서 다음을 입력합니다:
    - **Workgroup name**: `quicktable-workgroup-{StudentId}` (예: `quicktable-workgroup-20240001`)
    - **Description - Optional**: `QuickTable data lake workgroup for Week 11-2 lab`

    <img src="/images/week11/11-2-task4-step74-workgroup-details.png" alt="Workgroup details - 이름과 설명 입력" class="guide-img-md" />

75. **Analytics engine** 섹션에서 **Choose the type of engine**이 `Athena SQL`로 선택되어 있는지 확인합니다.
76. **Upgrade query engine**은 `Automatic`을 유지합니다.

    <img src="/images/week11/11-2-task4-step76-engine.png" alt="Analytics engine - Athena SQL 선택, Upgrade query engine Automatic" class="guide-img-md" />

77. **Authentication** 섹션에서 `AWS Identity and Access Management (IAM)`이 선택되어 있는지 확인합니다.

    <img src="/images/week11/11-2-task4-step77-authentication.png" alt="Authentication - IAM 선택" class="guide-img-md" />

78. **Query result configuration** 섹션에서 다음을 설정합니다:
    - **Management of query results**: `Customer-managed`를 선택합니다.
    - **Location of query result**: [[Browse S3]] 버튼을 클릭하여 `quicktable-query-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
    - 경로 끝에 `athena-results/`를 추가합니다 (예: `s3://quicktable-query-20240001-ap-northeast-2/athena-results/`).

    <img src="/images/week11/11-2-task4-step78-query-result1.png" alt="Query result configuration - Customer-managed 선택" class="guide-img-md" />

    <img src="/images/week11/11-2-task4-step78-query-result2.png" alt="Query result configuration - S3 경로 입력" class="guide-img-md" />

> [!NOTE]
> 최종 경로는 `s3://quicktable-query-{StudentId}-ap-northeast-2/athena-results/`입니다.
> 이 경로에 Athena 쿼리 결과 파일이 자동으로 저장됩니다.
>
> 기본값인 `Athena-managed`를 선택하면 Athena가 쿼리 결과를 자동 관리하고 24시간 후 삭제합니다.
> 이 실습에서는 결과를 직접 확인하기 위해 `Customer-managed`를 선택합니다.

79. **Additional configurations** 섹션에서 **Use defaults** 토글을 끕니다.
80. **Tags - Optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-2`    |
| `CreatedBy` | `Student` |

<img src="/images/week11/11-2-task4-step80-tags.png" alt="Tags - Optional 섹션에서 태그 추가" class="guide-img-md" />

81. [[Create workgroup]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon Athena Workgroup은 쿼리 실행 환경을 격리하고 쿼리 결과 저장 위치를 지정하는 단위입니다.
> 기본 Workgroup(primary)을 사용하면 쿼리 결과 위치 미설정 오류가 발생할 수 있으므로, 반드시 전용 Workgroup을 생성합니다.

### 태스크 4.2: 기본 쿼리 실행

82. Workgroup 생성이 완료되면 상세 페이지에서 다음을 확인합니다:
    - **Workgroup state**: `Turned on`
    - **Authentication**: `AWS Identity and Access Management (IAM)`
    - **Location of query result**: `s3://quicktable-query-{StudentId}-ap-northeast-2/athena-results/`

    <img src="/images/week11/11-2-task4-step82-workgroup-detail.png" alt="Workgroup 생성 완료 - 상세 페이지" class="guide-img-md" />

83. 왼쪽 메뉴에서 **Query editor tabs**를 선택합니다.
84. 상단의 **Workgroup** 드롭다운에서 `quicktable-workgroup-{StudentId}`를 선택합니다.

    <img src="/images/week11/11-2-task4-step84-workgroup-select.png" alt="Query editor - Workgroup 드롭다운에서 선택" class="guide-img-md" />

> [!WARNING]
> **Workgroup 변경 전 주의사항**:
>
> Workgroup을 변경하면 현재 쿼리 에디터의 내용이 초기화될 수 있습니다.
>
> **권장 순서**:
>
> 1. Workgroup 먼저 선택
> 2. Database 선택
> 3. 쿼리 작성 및 실행

85. 왼쪽 **Data** 패널에서 다음을 설정합니다:
    - **Data source**: `AwsDataCatalog` (기본값)
    - **Catalogue**: `None` (기본값 유지)
    - **Database**: `quicktable_db_{StudentId}`를 선택합니다.

    <img src="/images/week11/11-2-task4-step85-data-panel.png" alt="Data 패널 - Data source, Catalogue, Database 설정" class="guide-img-md" />

86. **Tables and views** 목록에서 `reservation_data` 테이블이 표시되는지 확인합니다.
87. 쿼리 에디터에 다음을 입력합니다:

```sql
-- 전체 데이터 조회
SELECT * FROM reservation_data
LIMIT 10;
```

88. [[Run]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task4-step88-run-query.png" alt="쿼리 실행 결과" class="guide-img-md" />

89. **Query results** 탭에서 결과를 확인합니다.

> [!NOTE]
> Athena는 표준 SQL을 지원하며 스캔한 데이터량에 따라 과금됩니다 ($5/TB). 쿼리 실행 정보에서 Run time과 Data scanned를 확인할 수 있습니다.

### 태스크 4.3: 집계 및 분석 쿼리

90. 레스토랑별 예약 수 및 평균 금액을 조회합니다:

```sql
-- 레스토랑별 예약 수 및 평균 금액
SELECT
    restaurantname,
    COUNT(*) as reservation_count,
    AVG(totalamount) as avg_amount,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count
FROM reservation_data
GROUP BY restaurantname
ORDER BY reservation_count DESC;
```

91. [[Run]] 또는 [[Run again]] 버튼을 클릭하고 결과를 확인합니다.

    <img src="/images/week11/11-2-task4-step91-query-result.png" alt="레스토랑별 예약 수 및 평균 금액 쿼리 결과" class="guide-img-md" />

92. 예약 상태별 분석을 조회합니다:

```sql
-- 예약 상태별 분석
SELECT
    status,
    COUNT(*) as count,
    AVG(partysize) as avg_party_size,
    AVG(totalamount) as avg_amount
FROM reservation_data
GROUP BY status;
```

<img src="/images/week11/11-2-task4-step92-status-query.png" alt="예약 상태별 분석 쿼리 결과" class="guide-img-md" />

93. 시간대별 예약 패턴을 조회합니다:

```sql
-- 시간대별 예약 패턴
SELECT
    "time",
    COUNT(*) as reservation_count,
    AVG(partysize) as avg_party_size
FROM reservation_data
GROUP BY "time"
ORDER BY reservation_count DESC;
```

<img src="/images/week11/11-2-task4-step93-time-query.png" alt="시간대별 예약 패턴 쿼리 결과" class="guide-img-md" />

> [!NOTE]
> **Athena 예약어 처리**:
>
> `time`과 `date`는 Athena(Presto 기반)의 예약어입니다. 큰따옴표로 감싸야 쿼리 오류를 방지할 수 있습니다.
>
> **주요 예약어 목록** (컬럼명으로 사용 시 큰따옴표 필요):
>
> - `date`, `time`, `year`, `month`, `day`
> - `timestamp`, `interval`
> - `current_date`, `current_time`
> - `table`, `column`, `schema`

> [!OUTPUT]
>
> ```
> Run time: 2.1 seconds
> Data scanned: 1.5 KB
> Rows returned: 5
>
> time         | reservation_count | avg_party_size
> -------------|-------------------|----------------
> 19:00        | 1                 | 2.0
> 18:30        | 1                 | 4.0
> 12:00        | 1                 | 6.0
> 19:30        | 1                 | 3.0
> 20:00        | 1                 | 5.0
> ```

✅ **태스크 완료**: Amazon Athena Workgroup을 생성하고 데이터를 쿼리했습니다.

## 태스크 5: 추가 데이터 소스 Crawler 생성 및 실행

이 태스크에서는 JSON 형식의 레스토랑 정보 데이터를 위한 **두 번째 Crawler**를 생성하고 실행합니다.

### 태스크 5.1: 레스토랑 데이터용 Crawler 생성

94. AWS Glue 콘솔로 이동합니다.
95. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
96. [[Create crawler]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task5-step96-create-crawler.png" alt="Create crawler 버튼" class="guide-img-md" />

97. **Name**에 `quicktable-restaurants-crawler-{StudentId}`를 입력합니다 (예: `quicktable-restaurants-crawler-20240001`).

> [!NOTE]
> **Description** 필드는 선택사항입니다. 비워두어도 됩니다.

98. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-2`    |
| `CreatedBy` | `Student` |

99. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-task5-step99-next.png" alt="Step 1 완료 후 Next" class="guide-img-md" />

100. **Is your data already mapped to Glue tables?** 에서 `Not yet`이 선택되어 있는지 확인합니다 (기본값).
101. [[Add a data source]] 버튼을 클릭합니다.
102. 모달 창에서 다음을 설정합니다:
     - **Data source**: `S3` (기본값)
     - **Network connection - optional**: 비워둡니다
     - **Location of S3 data**: `In this account` (기본값)
     - **S3 path**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/restaurant-data/`를 입력합니다 (예: `s3://quicktable-raw-20240001-ap-northeast-2/restaurant-data/`).
     - **Subsequent crawler runs**: `Crawl all sub-folders` (기본값)

103. [[Add an S3 data source]] 버튼을 클릭합니다.

     <img src="/images/week11/11-2-task5-step103-add-source.png" alt="Add an S3 data source 완료" class="guide-img-sm" />

104. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week11/11-2-task5-step104-next.png" alt="Step 2 완료 후 Next" class="guide-img-md" />

105. **IAM role** 섹션의 **Existing IAM role** 드롭다운에서 `week11-2-quicktable-datalake-stack-GlueCrawlerRole`로 시작하는 역할을 선택합니다.

> [!NOTE]
> 정확한 역할명은 AWS CloudFormation 스택의 **Outputs** 탭에서 `GlueCrawlerRoleArn`을 확인합니다.

106. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week11/11-2-task5-step106-security.png" alt="Step 3 Configure security settings - IAM role 선택" class="guide-img-md" />

107. **Set output and scheduling** 페이지에서 다음을 설정합니다:
     - **Target database**: 드롭다운에서 `quicktable_db_{StudentId}`를 선택합니다.
     - **Table name prefix - optional**: 비워둡니다.
     - **Crawler schedule** > **Frequency**: `On demand` (기본값)

108. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week11/11-2-task5-step108-output.png" alt="Step 4 Set output and scheduling" class="guide-img-md" />

109. **Review and create** 페이지에서 설정을 검토하고 [[Create crawler]] 버튼을 클릭합니다.

     <img src="/images/week11/11-2-task5-step109-review.png" alt="Review and create - Crawler 생성" class="guide-img-md" />

### 태스크 5.2: Crawler 실행 및 테이블 확인

110. Crawler 생성이 완료되면 상세 페이지가 표시됩니다. State가 **READY**인지 확인합니다.

     <img src="/images/week11/11-2-task5-step110-crawler-created.png" alt="Crawler 생성 완료 상세 페이지" class="guide-img-md" />

111. [[Run crawler]] 버튼을 클릭합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. JSON Lines 형식의 파일을 스캔하여 자동으로 테이블을 생성합니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

112. **Crawler runs** 섹션에서 Status가 **Running** → **Completed**로 변경되는 것을 확인합니다.
113. 실행이 완료되면 **Table changes** 컬럼에서 테이블 생성 결과를 확인합니다.

     <img src="/images/week11/11-2-task5-step113-tables.png" alt="Crawler 실행 완료 - Table changes 확인" class="guide-img-md" />

114. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
115. `quicktable_db_{StudentId}`를 클릭합니다.
116. **Tables** 섹션에서 새로 생성된 `restaurant_data` 테이블을 클릭합니다.

     <img src="/images/week11/11-2-task5-step116-restaurant-table.png" alt="restaurant_data 테이블 상세 페이지" class="guide-img-md" />

117. **Schema** 탭에서 컬럼 정보를 확인합니다:

     <img src="/images/week11/11-2-task5-step117-schema.png" alt="restaurant_data 테이블 Schema - 5개 컬럼" class="guide-img-md" />

| #   | Column name  | Data type | Partition key | Comment |
| --- | ------------ | --------- | ------------- | ------- |
| 1   | restaurantid | string    | -             | -       |
| 2   | name         | string    | -             | -       |
| 3   | cuisine      | string    | -             | -       |
| 4   | location     | string    | -             | -       |
| 5   | rating       | double    | -             | -       |

> [!NOTE]
> AWS Glue Crawler는 JSON 파일의 camelCase 키(restaurantId)를 소문자(restaurantid)로 변환합니다.
> 이는 Hive 메타스토어 호환성을 위한 AWS Glue의 기본 동작입니다.
> Athena 쿼리 시 소문자 컬럼명을 사용해야 합니다.

### 태스크 5.3: 레스토랑 데이터 쿼리

118. AWS Management Console 상단 검색창에 `Athena`를 입력하고 선택합니다.
119. 왼쪽 메뉴에서 **Query editor tabs**를 선택합니다.
120. **Workgroup** 드롭다운에서 `quicktable-workgroup-{StudentId}`가 선택되어 있는지 확인합니다.
121. 왼쪽 **Data** 패널의 **Tables and views** 목록에서 `restaurant_data` 테이블이 추가된 것을 확인합니다.
122. 다음 쿼리를 실행합니다:

```sql
-- 레스토랑 데이터 조회
SELECT * FROM restaurant_data
ORDER BY rating DESC;
```

<img src="/images/week11/11-2-task5-step122-restaurant-query.png" alt="레스토랑 데이터 조회 쿼리 결과" class="guide-img-md" />

123. 지역별 레스토랑 수를 조회합니다:

```sql
-- 지역별 레스토랑 수
SELECT
    location,
    COUNT(*) as restaurant_count,
    AVG(rating) as avg_rating
FROM restaurant_data
GROUP BY location
ORDER BY restaurant_count DESC;
```

<img src="/images/week11/11-2-task5-step123-location-query.png" alt="지역별 레스토랑 수 쿼리 결과" class="guide-img-md" />

124. 요리 종류별 평균 평점을 조회합니다:

```sql
-- 요리 종류별 평균 평점
SELECT
    cuisine,
    COUNT(*) as restaurant_count,
    AVG(rating) as avg_rating,
    MAX(rating) as max_rating
FROM restaurant_data
GROUP BY cuisine
ORDER BY avg_rating DESC;
```

<img src="/images/week11/11-2-task5-step124-cuisine-query.png" alt="요리 종류별 평균 평점 쿼리 결과" class="guide-img-md" />

> [!NOTE]
> 테이블명이 `restaurant_data`인 이유는 Amazon S3 폴더명(`restaurant-data/`)을 기반으로 Crawler가 자동 생성했기 때문입니다.
> 하이픈(-)은 언더스코어(\_)로 변환되며, 컬럼명도 모두 소문자로 변환됩니다.

✅ **태스크 완료**: JSON 형식 레스토랑 데이터를 위한 Crawler를 생성하고 쿼리를 실행했습니다.

## 태스크 6: CTAS를 사용하여 쿼리 결과를 새 테이블로 저장

이 태스크에서는 **CTAS 쿼리**를 사용하여 쿼리 결과를 새로운 테이블로 저장하고 CSV를 Parquet 형식으로 변환합니다.

### 태스크 6.1: CTAS로 Parquet 테이블 생성

125. Athena에서 다음 CTAS 쿼리를 실행합니다.

> [!WARNING]
> 아래 쿼리에서 `{StudentId}` 부분을 **모두** 실제 학번으로 교체한 후 실행합니다 (총 3곳).
> 예: `{StudentId}` → `20240001`

```sql
-- 예약 분석 결과를 Parquet로 저장
-- 주의: {StudentId}를 실제 학번으로 교체합니다 (예: 20240001)
CREATE TABLE reservation_analysis_{StudentId}
WITH (
    format = 'PARQUET',
    external_location = 's3://quicktable-processed-{StudentId}-ap-northeast-2/reservation-analysis-{StudentId}/',
    partitioned_by = ARRAY['status']
) AS
SELECT
    restaurantname,
    COUNT(*) as reservation_count,
    AVG(partysize) as avg_party_size,
    AVG(totalamount) as avg_amount,
    status
FROM reservation_data
GROUP BY restaurantname, status;
```

> [!IMPORTANT]
> CTAS 쿼리에서 `{StudentId}` 부분을 실제 학번으로 교체합니다.
> 테이블명과 Amazon S3 경로 모두에 StudentId를 포함해야 합니다.
> 예: `CREATE TABLE reservation_analysis_20240001` 및 `s3://quicktable-processed-20240001-ap-northeast-2/reservation-analysis-20240001/`
>
> **StudentId 접미사가 필요한 이유**: 같은 AWS Glue Database를 공유하는 환경에서 여러 학생이 동일한 테이블명을 사용하면 충돌이 발생합니다.

> [!WARNING]
> **CTAS 재실행 시 주의사항**: 동일한 `external_location`으로 CTAS를 재실행하면 "Location already exists" 오류가 발생합니다.
>
> **재실행이 필요한 경우**:
>
> 1. 기존 테이블 메타데이터를 삭제합니다: `DROP TABLE reservation_analysis_{StudentId};`
> 2. Amazon S3 콘솔에서 `s3://quicktable-processed-{StudentId}-ap-northeast-2/reservation-analysis-{StudentId}/` 폴더의 모든 파일을 삭제합니다.
> 3. CTAS 쿼리를 다시 실행합니다.
>
> **Amazon S3 파티션 폴더 구조**:
>
> ```
> s3://quicktable-processed-{StudentId}-ap-northeast-2/reservation-analysis-{StudentId}/
> ├── status=confirmed/
> │   └── 20240218_123456_00001_abcde.parquet
> └── status=cancelled/
>     └── 20240218_123456_00001_abcde.parquet
> ```
>
> **왜 테이블 메타데이터와 Amazon S3 파일을 모두 삭제해야 하는가?**:
>
> - `DROP TABLE`은 AWS Glue Data Catalog의 메타데이터만 삭제합니다
> - Amazon S3에 저장된 실제 Parquet 파일은 그대로 남아있습니다
> - CTAS 재실행 시 Amazon S3 경로가 이미 존재하면 오류가 발생합니다
> - 따라서 메타데이터 삭제 + Amazon S3 파일 삭제를 모두 수행해야 합니다

126. 쿼리가 완료되면 왼쪽 **Tables and views** 목록에서 `reservation_analysis_{StudentId}` 테이블이 추가된 것을 확인합니다.

     <img src="/images/week11/11-2-task6-step125-ctas.png" alt="CTAS 쿼리 실행 완료 - reservation_analysis 테이블 생성" class="guide-img-md" />

127. 새로 생성된 테이블을 쿼리합니다:

```sql
-- 주의: {StudentId}를 실제 학번으로 교체합니다 (예: 20240001)
SELECT *
FROM reservation_analysis_{StudentId}
WHERE status = 'confirmed'
ORDER BY reservation_count DESC;
```

<img src="/images/week11/11-2-task6-step127-select.png" alt="reservation_analysis 테이블 쿼리 결과" class="guide-img-md" />

> [!NOTE]
> **Parquet 형식의 장점**:
>
> - CSV 대비 70-90% 압축률 제공
> - 쿼리 속도 2-10배 향상
> - 컬럼형 저장으로 필요한 컬럼만 스캔
>
> **CTAS 파티셔닝 규칙**:
>
> - `partitioned_by`는 데이터를 물리적으로 분리하여 저장하는 컬럼을 지정합니다
> - 파티셔닝 컬럼은 SELECT 목록 마지막에 위치해야 합니다
> - 파티셔닝 컬럼은 집계 없이 그대로 포함되어야 합니다
> - 파티션 디렉터리로 데이터가 저장됩니다 (예: `status=confirmed/`, `status=cancelled/`)
>
> **이 쿼리에서 `date` 컬럼을 제거한 이유**:
>
> - `date`는 Athena 예약어이므로 큰따옴표(`"date"`)로 감싸야 합니다
> - 파티셔닝 컬럼(`status`)은 SELECT 목록 마지막에 위치해야 하는데, `date`가 중간에 있으면 규칙 위반
> - 집계 쿼리에서 `date`를 GROUP BY에 포함하면 날짜별로 분리되어 집계 의미가 감소
> - 레스토랑별 전체 예약 통계를 보려면 `date` 없이 집계하는 것이 더 유용합니다

### 태스크 6.2: 생성된 테이블 쿼리 및 성능 확인

128. Amazon S3 콘솔로 이동합니다.

     <img src="/images/week11/11-2-task6-step128-s3-console.png" alt="S3 콘솔 - Processed Data 버킷" class="guide-img-md" />

129. Processed Data 버킷 (`quicktable-processed-{StudentId}-ap-northeast-2`)을 선택합니다.

     <img src="/images/week11/11-2-task6-step129-processed-bucket.png" alt="Processed Data 버킷 내부" class="guide-img-md" />

130. `reservation-analysis-{StudentId}/` 폴더로 이동합니다.

     <img src="/images/week11/11-2-task6-step130-folder.png" alt="reservation-analysis 폴더" class="guide-img-md" />

131. 파티션 구조를 확인합니다:
     - `status=confirmed/` 폴더
     - `status=cancelled/` 폴더

132. 각 폴더 내의 Parquet 파일을 확인합니다.

     <img src="/images/week11/11-2-task6-step132-partition.png" alt="파티션 폴더 구조" class="guide-img-md" />

     <img src="/images/week11/11-2-task6-step132-parquet.png" alt="Parquet 파일 확인" class="guide-img-md" />

> [!NOTE]
> **Parquet 형식이란?**
>
> Parquet은 Apache에서 개발한 컬럼형(columnar) 저장 형식입니다.
>
> - **컬럼형 저장**: 행(row) 단위가 아닌 컬럼(column) 단위로 데이터를 저장하여, 필요한 컬럼만 읽을 수 있습니다.
> - **압축 효율**: CSV 대비 70-90% 압축률을 제공합니다.
> - **쿼리 성능**: 필요한 컬럼만 스캔하므로 쿼리 속도가 2-10배 향상됩니다.
> - **비용 절감**: Athena는 스캔된 데이터량 기준으로 과금되므로, Parquet 사용 시 비용이 크게 절감됩니다.
>
> 원본 CSV 파일과 Parquet 파일의 크기를 비교해보면 차이를 확인할 수 있습니다. 데이터 레이크에서는 Parquet 형식 사용을 권장합니다.

✅ **태스크 완료**: CTAS로 최적화된 테이블을 생성했습니다.

> [!TIP]
> **추가 학습: Amazon CloudWatch Log Group 확인**
>
> 이 실습에서 AWS CloudFormation이 생성한 AWS Lambda 함수(`SampleDataUploader`)는 실행 시 Amazon CloudWatch에 로그를 기록합니다.
>
> - CloudWatch 콘솔 > **Logs** > **Log Management**에서 `/aws/lambda/week11-2-SampleDataUploader-{StudentId}` 로그 그룹을 확인할 수 있습니다.
> - 로그 스트림을 클릭하면 Lambda 함수가 Amazon S3에 샘플 데이터를 업로드한 과정(START, END, REPORT)을 확인할 수 있습니다.
> - **REPORT** 줄에서 Duration(실행 시간), Memory Used(메모리 사용량) 등 Lambda 실행 메트릭을 확인해봅니다.
>
> 이 로그 그룹은 리소스 정리 시 수동으로 삭제해야 합니다 (AWS CloudFormation이 자동 삭제하지 않음).

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation을 통해 Amazon S3 데이터 레이크 인프라를 구축했습니다.
- QuickTable 예약 샘플 데이터 및 레스토랑 정보를 Amazon S3 버킷에서 확인했습니다.
- AWS Glue Database를 직접 생성하고 데이터 카탈로그를 구성했습니다.
- AWS Glue Crawler를 직접 생성하고 예약 데이터의 메타데이터를 자동 수집했습니다.
- AWS Glue 데이터 카탈로그 테이블 스키마를 확인했습니다.
- Amazon Athena Workgroup을 직접 생성하고 쿼리 환경을 구성했습니다.
- Athena를 사용하여 QuickTable 예약 분석 쿼리를 실행했습니다.
- JSON 형식 레스토랑 데이터를 위한 추가 Crawler를 생성하고 실행했습니다.
- CTAS를 사용하여 CSV를 Parquet 형식으로 변환하고 파티셔닝을 적용했습니다.

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
   - **Tag value**: `11-2`
6. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 1: Amazon S3 버킷 비우기 및 수동 생성 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
8. 환경 변수를 설정합니다:

```bash
# StudentId를 실제 학번으로 교체합니다 (예: 20240001)
STUDENT_ID="20240001"
echo "STUDENT_ID: ${STUDENT_ID}"
```

<img src="/images/week11/11-2-cleanup-step8-env-var.png" alt="CloudShell 환경 변수 설정" class="guide-img-md" />

**Amazon S3 버킷 비우기**

9. Amazon S3 버킷을 비웁니다:

```bash
aws s3 rm s3://quicktable-raw-${STUDENT_ID}-ap-northeast-2 --recursive
aws s3 rm s3://quicktable-processed-${STUDENT_ID}-ap-northeast-2 --recursive
aws s3 rm s3://quicktable-query-${STUDENT_ID}-ap-northeast-2 --recursive
```

<img src="/images/week11/11-2-cleanup-step9-s3-rm.png" alt="S3 버킷 비우기 CLI 실행 결과" class="guide-img-md" />

> [!NOTE]
> 버킷이 비워졌는지 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws s3 ls s3://quicktable-raw-${STUDENT_ID}-ap-northeast-2/
> aws s3 ls s3://quicktable-processed-${STUDENT_ID}-ap-northeast-2/
> aws s3 ls s3://quicktable-query-${STUDENT_ID}-ap-northeast-2/
> ```
>
> 출력이 없으면 비우기 완료입니다.

**Amazon Athena Workgroup 삭제**

10. Amazon Athena Workgroup을 삭제합니다:

```bash
aws athena delete-work-group \
  --work-group quicktable-workgroup-${STUDENT_ID} \
  --recursive-delete-option
```

<img src="/images/week11/11-2-cleanup-step10-athena-delete.png" alt="Athena Workgroup 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제가 성공하면 출력이 없습니다. 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws athena get-work-group --work-group quicktable-workgroup-${STUDENT_ID}
> ```
>
> `InvalidRequestException` 오류가 나오면 삭제 완료입니다.

**AWS Glue Crawler 삭제**

11. AWS Glue Crawler를 삭제합니다:

```bash
aws glue delete-crawler --name quicktable-crawler-${STUDENT_ID}
aws glue delete-crawler --name quicktable-restaurants-crawler-${STUDENT_ID}
```

<img src="/images/week11/11-2-cleanup-step11-crawler-delete.png" alt="Glue Crawler 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-crawler --name quicktable-crawler-${STUDENT_ID}
> ```
>
> `EntityNotFoundException` 오류가 나오면 삭제 완료입니다.

12. AWS Glue 테이블을 삭제합니다:

```bash
aws glue delete-table --database-name quicktable_db_${STUDENT_ID} --name reservation_data
aws glue delete-table --database-name quicktable_db_${STUDENT_ID} --name restaurant_data
aws glue delete-table --database-name quicktable_db_${STUDENT_ID} --name reservation_analysis_${STUDENT_ID}
```

<img src="/images/week11/11-2-cleanup-step12-table-delete.png" alt="Glue 테이블 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-tables --database-name quicktable_db_${STUDENT_ID} --query "TableList[*].Name" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

13. AWS Glue Database를 삭제합니다:

```bash
aws glue delete-database --name quicktable_db_${STUDENT_ID}
```

<img src="/images/week11/11-2-cleanup-step13-database-delete.png" alt="Glue Database 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> Database가 삭제되었는지 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws glue get-database --name quicktable_db_${STUDENT_ID}
> ```
>
> `EntityNotFoundException` 오류가 나오면 삭제 완료입니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

**Amazon S3 버킷 비우기**

14. Amazon S3 콘솔로 이동합니다.
15. `quicktable-raw-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
16. [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step16-empty.png" alt="S3 버킷 Empty" class="guide-img-md" />

17. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step17-permanently-delete.png" alt="permanently delete 입력 후 Empty" class="guide-img-md" />

18. `quicktable-processed-{StudentId}-ap-northeast-2` 버킷에 대해 15-17단계를 반복합니다.
19. `quicktable-query-{StudentId}-ap-northeast-2` 버킷에 대해 15-17단계를 반복합니다.

**Amazon Athena Workgroup 삭제**

20. Amazon Athena 콘솔로 이동합니다.
21. 왼쪽 메뉴에서 **Administration** > **Workgroups**를 선택합니다.
22. `quicktable-workgroup-{StudentId}`의 라디오 버튼을 선택합니다.
23. **Actions** 드롭다운에서 `Delete`를 선택합니다.

    <img src="/images/week11/11-2-cleanup-step23-actions-delete.png" alt="Workgroup Actions 드롭다운에서 Delete 선택" class="guide-img-md" />

24. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step24-confirm-delete.png" alt="Workgroup 삭제 확인 - confirm 입력" class="guide-img-sm" />

**AWS Glue Crawler 삭제**

25. AWS Glue 콘솔로 이동합니다.
26. 왼쪽 메뉴에서 **Data Catalog** > **Crawlers**를 선택합니다.
27. `quicktable-crawler-{StudentId}`와 `quicktable-restaurants-crawler-{StudentId}`의 체크박스를 모두 선택합니다.
28. **Action** 드롭다운에서 `Delete crawlers`를 선택합니다.

    <img src="/images/week11/11-2-cleanup-step28-delete-crawlers.png" alt="Crawlers 선택 후 Action > Delete crawlers" class="guide-img-md" />

29. 확인 창에서 `Delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step29-confirm-delete.png" alt="Delete crawlers 확인 - Delete 입력" class="guide-img-sm" />

> [!NOTE]
> Crawler를 한 개씩 삭제하는 경우에는 입력 없이 [[Delete]] 버튼만 클릭하면 됩니다.
>
> <img src="/images/week11/11-2-cleanup-step29-single-delete1.png" alt="단일 Crawler 삭제 확인 1" class="guide-img-sm" />
>
> <img src="/images/week11/11-2-cleanup-step29-single-delete2.png" alt="단일 Crawler 삭제 확인 2" class="guide-img-sm" />

**AWS Glue 테이블 및 Database 삭제**

30. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
31. `quicktable_db_{StudentId}`를 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step31-db-detail.png" alt="Database 상세 페이지 - Tables 섹션" class="guide-img-md" />

32. **Tables** 섹션에서 모든 테이블의 체크박스를 선택합니다.

    <img src="/images/week11/11-2-cleanup-step32-select-tables.png" alt="테이블 3개 체크박스 선택" class="guide-img-md" />

33. [[Delete]] 버튼을 클릭합니다.
34. 확인 창에서 `Delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step34-delete-tables.png" alt="Delete tables 확인 - Delete 입력" class="guide-img-sm" />

35. 왼쪽 메뉴에서 **Data Catalog** > **Databases**를 선택합니다.
36. `quicktable_db_{StudentId}`의 체크박스를 선택합니다.
37. [[Delete]] 버튼을 클릭합니다.
38. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step38-delete-database.png" alt="Delete Database 확인" class="guide-img-sm" />

> [!NOTE]
> 태스크 2~5에서 직접 생성한 Database, Crawler, Athena Workgroup은 AWS CloudFormation이 관리하지 않으므로 수동으로 삭제해야 합니다.
> Crawler가 생성한 테이블과 CTAS로 생성한 테이블도 수동 삭제 대상입니다.

### 단계 2: AWS CloudFormation 스택 삭제

39. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
40. `week11-2-quicktable-datalake-stack` 스택을 선택합니다.
41. [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step41-delete-stack.png" alt="CloudFormation Delete stack 버튼" class="guide-img-md" />

42. 확인 창에서 스택 이름 `week11-2-quicktable-datalake-stack`을 입력하고 [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step42-confirm-stack.png" alt="스택 삭제 확인 - 스택 이름 입력" class="guide-img-sm" />

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. 삭제가 완료될 때까지 기다립니다.
> AWS CloudFormation 스택을 삭제하면 AWS IAM 역할과 Amazon S3 버킷이 함께 삭제됩니다.

### 단계 3: Amazon CloudWatch Log Group 삭제

43. AWS Management Console 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
44. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
45. 다음 로그 그룹의 체크박스를 모두 선택합니다:
    - `/aws/lambda/week11-2-SampleDataUploader-{StudentId}`
    - `/aws-glue/crawlers`
46. **Actions** 드롭다운에서 `Delete log group(s)`를 선택합니다.

    <img src="/images/week11/11-2-cleanup-step46-actions-delete-log.png" alt="Actions > Delete log group(s) 선택" class="guide-img-md" />

47. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step47-confirm-delete-log.png" alt="Delete log group(s) 확인" class="guide-img-sm" />

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.
> 로그 그룹을 삭제하지 않으면 스토리지 비용(GB당 월 $0.50)이 계속 부과됩니다.

> [!TIP]
> AWS CLI로 삭제하려면 CloudShell에서 다음 명령어를 실행합니다:
>
> ```bash
> aws logs delete-log-group \
>   --log-group-name /aws/lambda/week11-2-SampleDataUploader-${STUDENT_ID} \
>   --region ap-northeast-2
> aws logs delete-log-group \
>   --log-group-name /aws-glue/crawlers \
>   --region ap-northeast-2
> ```
>
> <img src="/images/week11/11-2-cleanup-step47-cli-log-delete.png" alt="CLI 로그 그룹 삭제" class="guide-img-md" />
>
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/week11-2-SampleDataUploader --query "logGroups[*].logGroupName" --output text --region ap-northeast-2
> aws logs describe-log-groups --log-group-name-prefix /aws-glue/crawlers --query "logGroups[*].logGroupName" --output text --region ap-northeast-2
> ```
>
> 출력이 없으면 삭제 완료입니다.

### 단계 4: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

48. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
49. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
50. **Regions**에서 `ap-northeast-2`를 선택합니다.
51. **Resource types**에서 `All supported resource types`를 선택합니다.
52. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `11-2`
53. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week11/11-2-cleanup-step53-tageditor-confirm.png" alt="Tag Editor 검색 결과 - 리소스 없음 확인" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

> [!TROUBLESHOOTING]
> **문제**: AWS CloudFormation 스택 삭제가 실패합니다.
>
> **원인**: Amazon S3 버킷에 객체가 남아있습니다.
>
> **해결**:
>
> 1. 스택 삭제 실패 메시지에서 어떤 버킷이 문제인지 확인합니다.
> 2. 해당 버킷으로 이동하여 Empty 버튼을 클릭합니다.
> 3. AWS CloudFormation 콘솔로 돌아가서 스택 삭제를 다시 시도합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

54. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
55. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
56. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
57. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
58. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [AWS Glue 개발자 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/dg/what-is-glue.html)
- [Amazon Athena 사용 설명서](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/what-is.html)
- [AWS 기반 데이터 레이크 및 분석](https://aws.amazon.com/ko/big-data/datalakes-and-analytics/)
- [Amazon Athena 성능 튜닝](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/performance-tuning.html)

## 📚 참고: 데이터 레이크 핵심 개념 및 최적화

### 데이터 레이크 아키텍처 (Data Lake Architecture)

**계층 구조**

- **Raw (Bronze)**: 원본 데이터, 변경 불가
- **Processed (Silver)**: 정제된 데이터, 스키마 적용
- **Curated (Gold)**: 비즈니스 로직 적용, 집계

**데이터 레이크 vs 데이터 웨어하우스**

- 데이터 레이크: 모든 형식, 스키마 온 리드
- 데이터 웨어하우스: 구조화된 데이터, 스키마 온 라이트

### AWS Glue (AWS Glue)

**AWS Glue 크롤러**

- 메타데이터 자동 수집
- 스키마 추론
- 파티션 인식
- 테이블 생성/업데이트

**AWS Glue 데이터 카탈로그**

- 중앙 메타데이터 저장소
- Amazon Athena, Amazon EMR, Amazon Redshift Spectrum 공유
- Hive 메타스토어 호환

**AWS Glue ETL**

- 서버리스 ETL 작업
- PySpark, Scala 지원
- 자동 스케일링

### Amazon Athena (Amazon Athena)

**쿼리 엔진**

- Presto 기반
- 표준 SQL 지원
- 서버리스

**과금 모델**

- 스캔된 데이터량 기준
- $5 per TB (서울 리전 기준)
- 첫 1TB/월 무료 (AWS 프리 티어)
- 압축 및 파티셔닝으로 절감

**제한사항**

- 쿼리 타임아웃: DML 쿼리는 최대 30분 (서비스 한도)
- 결과 크기: 제한 없음 (Amazon S3 저장)
- 동시 쿼리 한도:
  - DML 쿼리 (SELECT, CTAS): 25개 (기본값)
  - DDL 쿼리 (CREATE, ALTER, DROP 등): 20개 (기본값)
  - 서비스 한도 조정 요청으로 증가 가능

> [!NOTE]
> **CTAS (CREATE TABLE AS SELECT) 분류**:
>
> - CTAS는 DML 쿼리로 분류됩니다 (AWS 공식 문서 기준)
> - 따라서 DML 쿼리 한도(25개)에 포함됩니다
> - DDL 쿼리는 CREATE TABLE, ALTER TABLE, DROP TABLE 등 메타데이터만 변경하는 작업입니다

### 최적화 전략 (Optimization Strategy)

**파일 형식**

- Parquet: 컬럼형, 압축 효율적 (권장), 70-90% 압축률, 쿼리 속도 2-10배 향상
- ORC: Hive 최적화
- Avro: 스키마 진화 지원
- 파일 크기: 128MB ~ 1GB 권장

**파티셔닝**

- 날짜별 파티션 (가장 일반적)
- 계층적 파티션 (year/month/day)
- 자주 필터링하는 컬럼 선택 (날짜, 리전 등)
- 적절한 파티션 수 유지 (수천 개 이하)

**압축**

- Snappy: 빠른 압축/해제
- Gzip: 높은 압축률
- Zstandard: 균형잡힌 성능

**비용 절감**

- 필요한 컬럼만 SELECT하여 스캔량 감소
- WHERE 절로 파티션 프루닝 활용
- Amazon S3 수명 주기 정책으로 오래된 데이터 Glacier 이동
