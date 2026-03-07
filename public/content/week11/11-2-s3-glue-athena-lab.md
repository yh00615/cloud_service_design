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

이번 실습에서는 QuickTable 레스토랑 예약 시스템의 샘플 데이터를 Amazon S3 데이터 레이크에 저장하고, AWS Glue로 메타데이터를 수집한 후, Amazon Athena로 서버리스 SQL 쿼리를 실행하여 비즈니스 인사이트를 도출합니다.

AWS CloudFormation이 자동으로 QuickTable 예약 샘플 데이터(CSV, JSON)를 Amazon S3에 업로드하고, AWS Glue Crawler로 스키마를 자동 검색한 후, Athena로 인기 레스토랑, 피크 예약 시간대, 취소율, 평균 파티 규모 등을 분석합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
> Amazon S3 버킷, AWS Glue Crawler, Amazon Athena Workgroup 등이 생성되며, 쿼리 실행 시 스캔된 데이터량에 따라 비용이 부과됩니다 ($5/TB).

> [!DOWNLOAD]
> [week11-2-datalake-lab.zip](/files/week11/week11-2-datalake-lab.zip)
>
> - `week11-2-datalake-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, AWS Glue Database, Crawler, Amazon Athena Workgroup, 샘플 데이터 자동 생성)
> - `sales.csv` - 매출 샘플 데이터 (참고용)
> - `customers.json` - 고객 샘플 데이터 (참고용)

## 태스크 0: QuickTable 데이터 레이크 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 QuickTable 예약 데이터 분석에 필요한 데이터 레이크 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷 3개**: Raw Data (예약 원본), Processed Data (집계 데이터), Query Results (Amazon Athena 결과)
- **AWS Glue Database**: QuickTable 데이터 카탈로그 메타데이터 저장소
- **AWS Glue Crawler**: 예약 데이터 스키마 자동 검색 및 테이블 생성
- **Amazon Athena Workgroup**: 쿼리 실행 환경 및 결과 저장 위치 설정
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
5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week11-2-datalake-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week11-2-quicktable-datalake-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 입력합니다:
    - **StudentId**: 학번 또는 고유 식별자 (예: `20240001` 또는 `student01`, 영문 소문자·숫자·하이픈만 사용, 5-20자)
    - **EnvironmentName**: `quicktable` (기본값 유지)

StudentId는 Amazon S3 버킷명, Glue Database명, Crawler명 등 모든 리소스 이름에 접미사로 추가되어 리소스 충돌을 방지합니다. EnvironmentName은 Amazon S3 버킷명의 접두사로 사용됩니다 (예: `quicktable-raw-{StudentId}-ap-northeast-2`). 11. [[Next]] 버튼을 클릭합니다.
11. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 찾습니다.
12. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-2`    |
| `CreatedBy` | `Student` |

13. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources with custom names`를 체크합니다.
14. [[Next]] 버튼을 클릭합니다.
15. **Review** 페이지에서 설정을 확인합니다.
16. [[Submit]] 버튼을 클릭합니다.
17. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
19. **Outputs** 탭을 선택합니다.
20. 출력값들을 확인하고 메모장에 복사합니다:
    - `RawDataBucketName`: Raw Data Amazon S3 버킷 이름 (예: quicktable-raw-20240001-ap-northeast-2)
    - `ProcessedDataBucketName`: Processed Data Amazon S3 버킷 이름 (예: quicktable-processed-20240001-ap-northeast-2)
    - `QueryResultsBucketName`: Query Results Amazon S3 버킷 이름 (예: quicktable-query-20240001-ap-northeast-2)
    - `GlueDatabaseName`: AWS Glue Database 이름 (예: quicktable_db_20240001)
    - `GlueCrawlerName`: AWS Glue Crawler 이름 (예: quicktable-crawler-20240001)
    - `AthenaWorkgroupName`: Amazon Athena Workgroup 이름 (예: quicktable-workgroup-20240001)
    - `SampleDataLocation`: QuickTable 예약 샘플 데이터 위치 (reservations.csv, restaurants.json)

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.
> 특히 StudentId를 포함한 리소스 이름을 정확히 기록합니다.

✅ **태스크 완료**: QuickTable 데이터 레이크 환경이 준비되었습니다.

## 태스크 1: QuickTable 예약 데이터 및 Amazon S3 버킷 확인

이 태스크에서는 AWS CloudFormation이 자동으로 생성한 Amazon S3 버킷과 QuickTable 예약 샘플 데이터를 확인합니다.

21. AWS Management Console에 로그인한 후 상단 검색창에 `S3`을 입력하고 선택합니다.
22. 버킷 목록에서 태스크 0에서 생성된 3개의 버킷을 확인합니다:
   - `quicktable-raw-{StudentId}-ap-northeast-2` (Raw Data 버킷 - QuickTable 예약 원본)
   - `quicktable-processed-{StudentId}-ap-northeast-2` (Processed Data 버킷 - 집계 데이터)
   - `quicktable-query-{StudentId}-ap-northeast-2` (Query Results 버킷 - Amazon Athena 결과)
23. Raw Data 버킷 (`quicktable-raw-{StudentId}-ap-northeast-2`)을 선택합니다.
24. 다음 폴더 구조가 자동으로 생성되었는지 확인합니다:
   - `reservation-data/` - QuickTable 예약 데이터 폴더
   - `restaurant-data/` - QuickTable 레스토랑 정보 폴더
25. `reservation-data/` 폴더를 클릭합니다.
26. `reservations.csv` 파일이 자동으로 업로드되었는지 확인합니다.
27. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

> [!OUTPUT]
>
> ```csv
> reservationId,userId,restaurantId,restaurantName,date,time,partySize,status,totalAmount,createdAt
> RES001,user123,REST001,강남 맛집,2024-01-15,18:30,4,confirmed,120000,2024-01-10T10:30:00.123456
> RES002,user456,REST002,서울 한식당,2024-01-16,19:00,2,cancelled,60000,2024-01-12T14:20:00.234567
> RES003,user789,REST001,강남 맛집,2024-01-17,12:00,6,confirmed,180000,2024-01-15T09:15:00.345678
> RES004,user123,REST003,부산 해물집,2024-01-20,19:30,3,confirmed,90000,2024-01-18T11:45:00.456789
> RES005,user456,REST002,서울 한식당,2024-01-22,20:00,5,confirmed,150000,2024-01-20T16:30:00.567890
> ```

28. 상위 폴더로 돌아가서 `restaurant-data/` 폴더를 클릭합니다.
29. `restaurants.json` 파일이 자동으로 업로드되었는지 확인합니다.
30. 파일을 선택하고 [[Download]] 버튼을 클릭하여 내용을 확인합니다.

> [!OUTPUT]
>
> ```json
> {"restaurantId": "REST001", "name": "강남 맛집", "cuisine": "Korean", "location": "Gangnam", "rating": 4.5}
> {"restaurantId": "REST002", "name": "서울 한식당", "cuisine": "Korean", "location": "Seoul", "rating": 4.2}
> {"restaurantId": "REST003", "name": "부산 해물집", "cuisine": "Seafood", "location": "Busan", "rating": 4.7}
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
>
> **추가 데이터 생성 방법** (선택사항):
>
> - Athena에서 데이터 생성 확인: `SELECT COUNT(*) FROM reservation_data;`
> - 5건이면 추가 데이터를 수동으로 추가하는 것을 권장합니다
> - CSV 파일에 데이터 추가 후 Amazon S3에 재업로드합니다

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

## 태스크 2: 자동 생성된 AWS Glue Crawler 실행 및 확인

이 태스크에서는 AWS CloudFormation이 자동으로 생성한 AWS Glue Database와 Crawler를 확인하고 실행합니다.

### 태스크 2.1: AWS Glue Database 확인

31. AWS Management Console에 로그인한 후 상단 검색창에 `Glue`을 입력하고 선택합니다.
32. 왼쪽 메뉴에서 **Databases**를 선택합니다.
33. 태스크 0에서 생성된 데이터베이스 `quicktable_db_{StudentId}`를 확인합니다.
34. 데이터베이스를 클릭하여 상세 정보를 확인합니다:
   - **Name**: `quicktable_db_{StudentId}`
   - **Location**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/`
   - **Description**: Data lake database for Week 11-2 lab

> [!NOTE]
> AWS Glue 데이터베이스는 테이블 메타데이터를 논리적으로 그룹화하는 컨테이너입니다.
> AWS CloudFormation이 자동으로 생성했으므로 별도로 생성할 필요가 없습니다.

### 태스크 2.2: AWS Glue Crawler 확인 및 실행

35. 왼쪽 메뉴에서 **Crawlers**를 선택합니다.
36. 태스크 0에서 생성된 Crawler `quicktable-crawler-{StudentId}`를 확인합니다.
37. Crawler를 선택하여 설정을 확인합니다:
   - **Crawler name**: `quicktable-crawler-{StudentId}`
   - **Database**: `quicktable_db_{StudentId}`
   - **Data source**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/reservation-data/`
   - **AWS IAM role**: AWS CloudFormation이 자동 생성한 역할 (예: `week11-2-quicktable-datalake-stack-GlueCrawlerRole-XXXXXX`)

> [!NOTE]
> AWS IAM 역할명은 AWS CloudFormation 스택명 + 리소스 논리 ID + 랜덤 접미사 형태로 자동 생성됩니다.
> 정확한 역할명은 AWS CloudFormation 스택의 **Resources** 탭에서 `GlueCrawlerRole`을 검색하여 확인할 수 있습니다.

> [!NOTE]
> **Crawler 데이터 소스 범위 분리 이유**:
>
> 이 실습에서는 의도적으로 두 개의 Crawler를 사용합니다:
>
> - **Crawler 1** (자동 생성): `reservation-data/` 폴더만 스캔 → AWS CloudFormation으로 자동 생성되는 과정 학습
> - **Crawler 2** (수동 생성): `restaurant-data/` 폴더 스캔 → Crawler를 직접 생성하는 방법 학습 (태스크 5)
>
> 실제 운영 환경에서는 하나의 Crawler로 여러 폴더를 스캔하도록 구성할 수 있습니다:
>
> - Data sources에 여러 Amazon S3 경로를 추가하거나
> - 상위 경로(`s3://bucket/`)를 지정합니다
>
> 4. [[Run]] 버튼을 클릭하여 Crawler를 실행합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. 페이지를 새로고침하여 상태를 확인합니다.
> Crawler는 `reservation-data/` 폴더의 CSV 파일을 스캔하여 자동으로 테이블을 생성합니다.
> 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다.

38. **Status**가 "Ready" → "Running" → "Stopping" → "Ready"로 변경되는 것을 확인합니다.
39. 실행이 완료되면 **Last run** 정보를 확인합니다.
40. **Tables affected** 정보를 확인합니다.

> [!OUTPUT]
>
> ```
> Crawler completed successfully
> Tables added: 1
> Tables updated: 0
> Partitions added: 0
> ```

✅ **태스크 완료**: AWS Glue Crawler를 실행하여 데이터 카탈로그를 생성했습니다.

## 태스크 3: AWS Glue 테이블 확인

이 태스크에서는 AWS Glue Crawler가 자동으로 생성한 테이블의 스키마를 확인합니다.

41. 왼쪽 메뉴에서 **Tables**를 선택합니다.
42. **Database** 드롭다운에서 `quicktable_db_{StudentId}`를 선택합니다.
43. 생성된 테이블 `reservation_data`를 클릭합니다.

> [!NOTE]
> **Crawler 실행 후 테이블명 확인 방법**:
>
> Crawler가 생성하는 테이블명은 Amazon S3 폴더명 기반이지만 예상과 다를 수 있습니다:
>
> - 하이픈(-)은 언더스코어(\_)로 변환
> - 경로 깊이에 따라 이름이 달라질 수 있음
>
> **테이블명 확인**:
>
> 1. AWS Glue 콘솔 → Tables
> 2. Database: `quicktable_db_{StudentId}` 선택
> 3. 생성된 테이블 목록 확인
>
> **Athena에서 확인**:
>
> ```sql
> SHOW TABLES IN quicktable_db_{StudentId};
> ```
>
> 4. **Schema** 탭에서 컬럼 정보를 확인합니다:

- reservationid: string
- userid: string
- restaurantid: string
- restaurantname: string
- date: string
- time: string
- partysize: bigint
- status: string
- totalamount: double
- createdat: string

44. **Table properties**에서 다음을 확인합니다:
   - **Location**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/reservation-data/`
   - **Input format**: org.apache.hadoop.mapred.TextInputFormat
   - **Output format**: org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat
   - **SerDe**: org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe
45. 필요시 스키마를 수정합니다:
   - {{Edit schema}} 버튼을 클릭합니다.
   - 데이터 타입을 변경합니다 (필요한 경우).
   - [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> AWS Glue 테이블은 Amazon S3 데이터의 메타데이터만 관리합니다. SerDe(Serializer/Deserializer)는 데이터 형식(CSV, JSON, Parquet)을 읽고 쓰는 방법을 정의합니다.
> Crawler가 CSV 파일을 자동으로 인식하여 적절한 SerDe를 설정했습니다.

✅ **태스크 완료**: AWS Glue 테이블 스키마를 확인했습니다.

## 태스크 4: Amazon Athena 쿼리 실행

이 태스크에서는 Athena를 사용하여 Amazon S3 데이터를 표준 SQL로 쿼리합니다.

### 태스크 4.1: Amazon Athena Workgroup 확인 및 기본 쿼리

46. AWS Management Console에 로그인한 후 상단 검색창에 `Athena`을 입력하고 선택합니다.

> [!WARNING]
> **Workgroup 변경 전 주의사항**:
>
> Workgroup을 변경하면 현재 쿼리 에디터의 내용이 초기화될 수 있습니다.
>
> **권장 순서**:
>
> 1. Athena 콘솔 접속 즉시 Workgroup 먼저 선택
> 2. 그 다음 Database 선택
> 3. 마지막으로 쿼리 작성 및 실행
>
> **이미 쿼리를 작성한 경우**:
>
> - 쿼리를 로컬에 복사한 후 Workgroup 변경
> - Database 재선택 후 쿼리 붙여넣기

47. 상단의 **Workgroup** 드롭다운에서 `quicktable-workgroup-{StudentId}`를 선택합니다.

> [!IMPORTANT]
> AWS CloudFormation이 자동으로 생성한 Workgroup을 반드시 선택해야 합니다.
> 기본 Workgroup(primary)을 사용하면 쿼리 결과 위치 미설정 오류가 발생할 수 있습니다.

> [!NOTE]
> AWS CloudFormation이 자동으로 Amazon Athena Workgroup을 생성하고 쿼리 결과 위치를 설정했습니다.
> 쿼리 결과는 `s3://quicktable-query-{StudentId}-ap-northeast-2/athena-results/`에 저장됩니다.
> Workgroup 선택 후 페이지가 새로고침되면서 해당 Workgroup의 설정이 적용됩니다.

48. **Editor** 탭을 선택합니다.
49. **Database**에서 `quicktable_db_{StudentId}`를 선택합니다.
50. 왼쪽 패널에서 테이블 목록을 확인합니다 (예: `reservation_data`).
51. 첫 번째 쿼리를 실행합니다:

```sql
-- 전체 데이터 조회
SELECT * FROM reservation_data
LIMIT 10;
```

52. [[Run]] 버튼을 클릭합니다.
53. 결과를 확인합니다.

> [!NOTE]
> Athena는 표준 SQL을 지원하며 스캔한 데이터량에 따라 과금됩니다 ($5/TB). 쿼리 실행 정보에서 Run time과 Data scanned를 확인할 수 있습니다.

### 태스크 4.2: 집계 및 분석 쿼리

54. 레스토랑별 예약 수 및 평균 금액을 조회합니다:

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

55. [[Run]] 버튼을 클릭하고 결과를 확인합니다.
56. 예약 상태별 분석을 조회합니다:

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

57. 시간대별 예약 패턴을 조회합니다:

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

✅ **태스크 완료**: Athena로 데이터를 쿼리하고 분석했습니다.

## 태스크 5: 추가 데이터 소스 Crawler 생성 및 실행

이 태스크에서는 JSON 형식의 레스토랑 정보 데이터를 위한 새로운 Crawler를 생성하고 실행합니다.

### 태스크 5.1: 레스토랑 데이터용 Crawler 생성

58. AWS Glue 콘솔로 이동합니다.
59. 왼쪽 메뉴에서 **Crawlers**를 선택합니다.
60. [[Create crawler]] 버튼을 클릭합니다.
61. **Crawler name**에 `quicktable-restaurants-crawler-{StudentId}`를 입력합니다.

> [!NOTE]
> **Description** 필드는 선택사항입니다. 비워두어도 됩니다.

62. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `11-2`    |
| `CreatedBy` | `Student` |

63. [[Next]] 버튼을 클릭합니다.
64. **Data source configuration**에서 다음을 입력합니다:
   - **Data source**: `Amazon S3`를 선택합니다.
   - **Amazon S3 path**: `s3://quicktable-raw-{StudentId}-ap-northeast-2/restaurant-data/`를 입력합니다.
65. [[Add an Amazon S3 data source]] 버튼을 클릭합니다.
66. [[Next]] 버튼을 클릭합니다.
67. **AWS IAM role**에서 `Choose an existing AWS IAM role`을 선택합니다.
68. 기존 역할을 선택합니다 (예: `week11-2-quicktable-datalake-stack-GlueCrawlerRole-XXXXXXXXXXXX`).

> [!NOTE]
> AWS IAM 역할명은 AWS CloudFormation 스택명 + 리소스 논리 ID + 랜덤 접미사 형태로 자동 생성됩니다.
> 정확한 역할명은 AWS CloudFormation 스택의 **Resources** 탭에서 `GlueCrawlerRole`을 검색하여 확인할 수 있습니다.

69. [[Next]] 버튼을 클릭합니다.
70. **Target database**에서 `quicktable_db_{StudentId}`를 선택합니다.
71. [[Next]] 버튼을 클릭합니다.
72. **Crawler schedule**에서 `On demand`를 선택합니다.
73. 설정을 검토하고 [[Create crawler]] 버튼을 클릭합니다.

### 태스크 5.2: Crawler 실행 및 테이블 확인

74. 생성된 Crawler `quicktable-restaurants-crawler-{StudentId}`를 선택합니다.
75. [[Run]] 버튼을 클릭합니다.

> [!NOTE]
> Crawler 실행에 1-2분이 소요됩니다. JSON Lines 형식의 파일을 스캔하여 자동으로 테이블을 생성합니다.

76. 실행이 완료되면 왼쪽 메뉴에서 **Tables**를 선택합니다.
77. **Database** 드롭다운에서 `quicktable_db_{StudentId}`를 선택합니다.
78. 새로 생성된 테이블 (예: `restaurant_data`)을 클릭합니다.

> [!NOTE]
> **Crawler 실행 후 테이블명 확인 방법**:
>
> Crawler가 생성하는 테이블명은 Amazon S3 폴더명 기반이지만 예상과 다를 수 있습니다:
>
> - 하이픈(-)은 언더스코어(\_)로 변환
> - 경로 깊이에 따라 이름이 달라질 수 있음
>
> **테이블명 확인**:
>
> 1. AWS Glue 콘솔 → Tables
> 2. Database: `quicktable_db_{StudentId}` 선택
> 3. 생성된 테이블 목록 확인
>
> **Athena에서 확인**:
>
> ```sql
> SHOW TABLES IN quicktable_db_{StudentId};
> ```

79. **Schema** 탭에서 컬럼 정보를 확인합니다:
   - restaurantid: string
   - name: string
   - cuisine: string
   - location: string
   - rating: double

> [!NOTE]
> AWS Glue Crawler는 JSON 파일의 camelCase 키(restaurantId)를 소문자(restaurantid)로 변환합니다.
> 이는 Hive 메타스토어 호환성을 위한 AWS Glue의 기본 동작입니다.
> Athena 쿼리 시 소문자 컬럼명을 사용해야 합니다.

### 태스크 5.3: 레스토랑 데이터 쿼리

80. Amazon Athena 콘솔로 이동합니다.
81. 다음 쿼리를 실행합니다:

```sql
-- 레스토랑 데이터 조회
SELECT * FROM restaurant_data
ORDER BY rating DESC;
```

82. 지역별 레스토랑 수를 조회합니다:

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

83. 요리 종류별 평균 평점을 조회합니다:

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

> [!NOTE]
> 테이블명이 `restaurant_data`인 이유는 Amazon S3 폴더명(`restaurant-data/`)을 기반으로 Crawler가 자동 생성했기 때문입니다.
> 하이픈(-)은 언더스코어(\_)로 변환되며, 컬럼명도 모두 소문자로 변환됩니다.

✅ **태스크 완료**: JSON 형식 레스토랑 데이터를 위한 Crawler를 생성하고 쿼리를 실행했습니다.

## 태스크 6: CTAS를 사용하여 쿼리 결과를 새 테이블로 저장

이 태스크에서는 CTAS 쿼리를 사용하여 쿼리 결과를 새로운 테이블로 저장하고 CSV를 Parquet 형식으로 변환합니다.

### 태스크 6.1: CTAS로 Parquet 테이블 생성

84. Athena에서 CTAS 쿼리를 실행합니다:

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
> **StudentId 접미사가 필요한 이유**: 같은 AWS Glue Database를 공유하는 환경에서 여러 학생이 동일한 테이블명(`reservation_analysis`)을 사용하면 충돌이 발생합니다. StudentId 접미사를 추가하면 각 학생의 테이블이 고유하게 유지됩니다.

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

85. [[Run]] 버튼을 클릭합니다.

> [!NOTE]
> 쿼리가 완료될 때까지 기다립니다. CTAS는 쿼리 결과를 새 테이블로 저장하면서 동시에 데이터 형식을 변환합니다.
> 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다.

86. 새로 생성된 테이블을 쿼리합니다:

```sql
-- 주의: {StudentId}를 실제 학번으로 교체합니다 (예: 20240001)
SELECT *
FROM reservation_analysis_{StudentId}
WHERE status = 'confirmed'
ORDER BY reservation_count DESC;
```

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

87. Amazon S3 콘솔로 이동합니다.
88. Processed Data 버킷 (`quicktable-processed-{StudentId}-ap-northeast-2`)을 선택합니다.
89. `reservation-analysis-{StudentId}/` 폴더로 이동합니다.
90. 파티션 구조를 확인합니다:
   - `status=confirmed/` 폴더
   - `status=cancelled/` 폴더
91. 각 폴더 내의 Parquet 파일을 확인합니다.
92. 원본 CSV 파일과 Parquet 파일의 크기를 비교합니다.

> [!TIP]
> Parquet 파일은 컬럼형 저장 방식으로 스토리지 비용과 쿼리 비용을 모두 절감합니다. 데이터 레이크에서는 Parquet 형식 사용을 권장합니다.

✅ **태스크 완료**: CTAS로 최적화된 테이블을 생성했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation을 통한 QuickTable 데이터 레이크 인프라 자동 구축
- QuickTable 예약 샘플 데이터 및 레스토랑 정보 Amazon S3 버킷 확인
- AWS Glue Crawler 실행 및 예약 데이터 메타데이터 자동 수집
- AWS Glue 데이터 카탈로그 테이블 스키마 확인
- Athena를 사용한 QuickTable 예약 분석 쿼리 실행 (인기 레스토랑, 예약 패턴, 취소율)
- JSON 형식 레스토랑 데이터를 위한 추가 Crawler 생성 및 실행
- CTAS를 사용하여 CSV를 Parquet 형식으로 변환 및 파티셔닝 적용

AWS CloudFormation이 자동으로 QuickTable 예약 샘플 데이터를 Amazon S3에 업로드하고, Glue와 Athena를 사용하여 비즈니스 인사이트를 도출하는 방법을 학습했습니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제가 실패하므로 먼저 버킷을 비워야 합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `11-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### 1단계: Amazon S3 버킷 비우기 (필수)

AWS CloudFormation 스택 삭제 전에 반드시 수행해야 합니다:

8. Amazon S3 콘솔로 이동합니다.
9. `quicktable-raw-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
10. [[Empty]] 버튼을 클릭합니다.
11. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
12. `quicktable-processed-{StudentId}-ap-northeast-2` 버킷에 대해 2-4단계를 반복합니다.
13. `quicktable-query-{StudentId}-ap-northeast-2` 버킷에 대해 2-4단계를 반복합니다.

> [!NOTE]
> 태스크 6에서 CTAS로 Processed Data 버킷에 Parquet 파일을 생성했고, Athena 쿼리 결과가 Query Results 버킷에 저장되었습니다.
> 3개 버킷 모두 비워야 AWS CloudFormation 스택 삭제가 성공합니다.
>
> **버킷 비우기와 삭제의 관계**:
>
> - 1단계에서 버킷을 비우면 AWS CloudFormation 스택 삭제 시 버킷도 함께 삭제됩니다
> - 하지만 AWS CloudFormation 템플릿에서 `DeletionPolicy: Retain`을 설정한 경우, 버킷이 남아있을 수 있습니다
> - 이 경우 4단계에서 수동으로 버킷을 삭제해야 합니다

#### 2단계: 수동 생성 리소스 삭제

태스크 5에서 수동으로 생성한 리소스를 삭제합니다:

14. AWS Glue 콘솔로 이동합니다.
15. 왼쪽 메뉴에서 **Crawlers**를 선택합니다.
16. `quicktable-restaurants-crawler-{StudentId}`를 선택합니다.
17. **Actions** > `Delete`를 선택합니다.
18. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
19. 왼쪽 메뉴에서 **Tables**를 선택합니다.
20. **Database** 드롭다운에서 `quicktable_db_{StudentId}`를 선택합니다.
21. `restaurant_data` 테이블을 선택합니다.
22. **Actions** > `Delete table`을 선택합니다.
23. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
24. `reservation_analysis_{StudentId}` 테이블을 선택합니다.
25. **Actions** > `Delete table`을 선택합니다.
26. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 태스크 5에서 Crawler가 생성한 `restaurant_data` 테이블과 태스크 6에서 Athena CTAS로 생성한 `reservation_analysis_{StudentId}` 테이블은 AWS Glue Data Catalog의 메타데이터입니다.
> AWS CloudFormation은 배포 시점에 생성한 리소스만 관리하므로, 실습 중 동적으로 생성된 이 테이블들은 수동으로 삭제해야 합니다.

#### 3단계: AWS CloudFormation 스택 삭제

27. AWS CloudFormation 콘솔로 이동합니다.
28. `week11-2-quicktable-datalake-stack` 스택을 선택합니다.
29. [[Delete]] 버튼을 클릭합니다.
30. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
31. 스택 삭제가 완료될 때까지 기다립니다 (3-5분 소요).

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 태스크 0에서 생성한 대부분의 리소스(AWS Glue Database, AWS Glue Crawler, Amazon Athena Workgroup, AWS IAM 역할)가 자동으로 삭제됩니다.
> Amazon S3 버킷 3개는 스택 삭제 시 함께 삭제되지 않고 남아있습니다. 버킷에 객체가 있으면 삭제가 실패하므로 1단계에서 반드시 버킷을 비워야 합니다.

#### 4단계: Amazon S3 버킷 삭제

AWS CloudFormation 스택 삭제 후 Amazon S3 버킷이 남아있습니다. 완전히 삭제하려면:

32. Amazon S3 콘솔로 이동합니다.
33. `quicktable-raw-{StudentId}-ap-northeast-2` 버킷을 선택합니다.
34. [[Delete]] 버튼을 클릭합니다.
35. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.
36. `quicktable-processed-{StudentId}-ap-northeast-2` 버킷에 대해 2-4단계를 반복합니다.
37. `quicktable-query-{StudentId}-ap-northeast-2` 버킷에 대해 2-4단계를 반복합니다.

> [!NOTE]
> Amazon S3 버킷은 이미 1단계에서 비웠으므로 바로 삭제할 수 있습니다.
> 버킷을 유지하면 향후 실습에서 재사용할 수 있지만, 스토리지 비용이 발생할 수 있습니다.

> [!TROUBLESHOOTING]
> **문제**: AWS CloudFormation 스택 삭제가 실패합니다
>
> **원인**: Amazon S3 버킷에 객체가 남아있습니다
>
> **해결**:
>
> 1. 스택 삭제 실패 메시지에서 어떤 버킷이 문제인지 확인합니다
> 2. 해당 버킷으로 이동하여 Empty 버튼을 클릭합니다
> 3. AWS CloudFormation 콘솔로 돌아가서 스택 삭제를 다시 시도합니다

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 리소스

- [AWS Glue 개발자 가이드](https://docs.aws.amazon.com/ko_kr/glue/latest/dg/what-is-glue.html)
- [Amazon Athena 사용 설명서](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/what-is.html)
- [데이터 레이크 모범 사례](https://aws.amazon.com/ko/big-data/datalakes-and-analytics/)
- [Amazon Athena 성능 튜닝](https://docs.aws.amazon.com/ko_kr/athena/latest/ug/performance-tuning.html)

## 📚 참고: 데이터 레이크 핵심 개념 및 최적화

### 데이터 레이크 아키텍처

**계층 구조**

- **Raw (Bronze)**: 원본 데이터, 변경 불가
- **Processed (Silver)**: 정제된 데이터, 스키마 적용
- **Curated (Gold)**: 비즈니스 로직 적용, 집계

**데이터 레이크 vs 데이터 웨어하우스**

- 데이터 레이크: 모든 형식, 스키마 온 리드
- 데이터 웨어하우스: 구조화된 데이터, 스키마 온 라이트

### AWS Glue

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

### Amazon Athena

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

### 최적화 전략

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
