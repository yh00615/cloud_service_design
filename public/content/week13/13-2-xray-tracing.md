---
title: 'AWS X-Ray를 활용한 서버리스 애플리케이션 추적'
week: 13
session: 2
awsServices:
  - AWS X-Ray
learningObjectives:
  - 분산 추적의 개념과 AWS X-Ray의 트레이스 구조를 이해할 수 있습니다.
  - AWS Lambda 함수에 AWS X-Ray SDK를 통합하고 추적을 활성화할 수 있습니다.
  - AWS X-Ray 서비스 맵으로 애플리케이션 구조를 시각화할 수 있습니다.
  - 트레이스를 분석하여 병목 지점과 오류를 파악할 수 있습니다.

prerequisites:
  - Week 1-12 완료
  - 시스템 모니터링 기본 개념 이해
  - AWS Lambda 함수 기본 지식
---

이 실습에서는 AWS X-Ray를 사용하여 QuickTable 레스토랑 예약 시스템의 분산 추적을 구현합니다. Week 4에서 구축한 QuickTable API에 AWS X-Ray SDK를 통합하고, 서비스 맵과 트레이스를 분석하여 예약 생성 및 조회 과정의 성능과 병목 지점을 식별하는 방법을 학습합니다. Amazon API Gateway → AWS Lambda → Amazon DynamoDB로 이어지는 전체 요청 흐름을 추적하고, 각 단계의 실행 시간과 오류를 시각화합니다.

> [!DOWNLOAD]
> [week13-2-xray-lab.zip](/files/week13/week13-2-xray-lab.zip)
>
> - `week13-2-xray-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 QuickTable 환경 자동 생성: Reservations 테이블, CreateReservation/GetReservations AWS Lambda 함수, Amazon API Gateway, AWS X-Ray 추적 활성화)
> - `create_reservation.py` - AWS X-Ray SDK가 통합된 예약 생성 AWS Lambda 함수 코드
> - `get_reservations.py` - AWS X-Ray SDK가 통합된 예약 조회 AWS Lambda 함수 코드
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 스택 생성으로 QuickTable API 인프라 자동 배포)
> - 태스크 2: AWS X-Ray 추적 활성화 확인 (AWS Lambda 함수의 Active tracing 설정 확인)
> - 태스크 3: API 호출 및 트레이스 생성 (예약 생성/조회 API 호출하여 AWS X-Ray 트레이스 데이터 생성)

실습을 시작하기 전에 비용 정보를 확인합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
>
> **예상 비용** (ap-northeast-2 리전 기준):
>
> | 리소스             | 타입           | 비용                              |
> | ------------------ | -------------- | --------------------------------- |
> | AWS Lambda 함수    | 실행 시간 기반 | 프리 티어 범위 내 (12개월)        |
> | Amazon API Gateway | 요청 기반      | 프리 티어 범위 내 (12개월)        |
> | Amazon DynamoDB    | On-demand      | 프리 티어 범위 내 (항상 무료)     |
> | AWS X-Ray          | 트레이스 기반  | 월 100,000개까지 무료 (항상 무료) |

프리 티어 적용 기간에 유의합니다.

> [!NOTE]
> AWS Lambda와 Amazon API Gateway의 프리 티어는 계정 생성 후 12개월까지만 적용됩니다.
> Amazon DynamoDB와 AWS X-Ray는 항상 무료입니다.
> 프리 티어가 만료된 계정에서는 소액의 비용이 발생할 수 있습니다.
>
> AWS X-Ray 프리 티어는 매월 갱신되며 계정 생성 후 12개월이 아닌 **항상 무료(Always Free)**입니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 QuickTable 레스토랑 예약 시스템의 AWS X-Ray 추적 환경을 자동으로 생성합니다. Week 4에서 구축한 QuickTable API를 재생성하고, AWS X-Ray SDK를 통합한 AWS Lambda 함수를 배포합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon DynamoDB 테이블**: Reservations (사용자별 예약 데이터 저장, userId/reservationId 키)
- **AWS Lambda 함수**: CreateReservation, GetReservations (AWS X-Ray SDK 통합, 예약 생성/조회 처리)
- **AWS IAM 역할**: AWS Lambda 실행 역할 (Amazon DynamoDB 접근 + AWS X-Ray 추적 권한 포함)
- **Amazon API Gateway**: QuickTableXRayAPI (REST API, /reservations 리소스 및 POST/GET 메서드)

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week13-2-xray-lab.zip` 파일의 압축을 해제합니다.
2. `week13-2-xray-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week13-2-xray-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week13-2-xray-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 유지합니다.
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value            |
| ----------- | ---------------- |
| `Project`   | `AWS-Lab`        |
| `Week`      | `13-2`           |
| `CreatedBy` | `CloudFormation` |

> [!NOTE]
> 이 태그들은 AWS CloudFormation 스택이 생성하는 모든 리소스(Amazon DynamoDB 테이블, AWS Lambda 함수 2개, Amazon API Gateway, AWS IAM 역할)에 자동으로 전파됩니다.

14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
15. [[Next]] 버튼을 클릭합니다.
16. **Review** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.
18. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
20. **Outputs** 탭을 선택합니다.
21. 출력값들을 확인하고 메모장에 복사합니다:
	- `ApiGatewayInvokeUrl`: Amazon API Gateway Invoke URL (예: https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod)
	- `CreateReservationFunctionName`: 예약 생성 AWS Lambda 함수 이름
	- `GetReservationsFunctionName`: 예약 조회 AWS Lambda 함수 이름
	- `DynamoDBTableName`: Amazon DynamoDB 테이블 이름 (Reservations)

다음 태스크에서 이 값들을 사용합니다.

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: AWS Lambda 함수 코드 확인

이 태스크에서는 AWS CloudFormation으로 배포된 AWS Lambda 함수의 코드를 확인합니다. AWS X-Ray SDK가 통합되어 있으며, 예약 생성 및 조회 작업을 추적합니다.

22. AWS Management Console에 로그인한 후 상단 검색창에 `Lambda`을 입력하고 선택합니다.
23. 왼쪽 메뉴에서 **Functions**를 선택합니다.
24. 함수 목록에서 `CreateReservation`으로 시작하는 함수를 선택합니다.
25. **Code** 탭을 선택합니다.
26. 코드 편집기에서 AWS X-Ray SDK 통합 부분을 확인합니다.

> [!NOTE]
> AWS CloudFormation 템플릿에서 AWS X-Ray SDK가 포함된 AWS Lambda 함수 코드가 자동으로 배포되었습니다.
> 코드에는 `aws_xray_sdk` 라이브러리를 사용하여 Amazon DynamoDB 호출을 추적하는 로직이 포함되어 있습니다.
>
> **다음 코드 패턴을 확인합니다**:
>
> - `from aws_xray_sdk.core import patch_all, xray_recorder` - SDK 임포트
> - `patch_all()` - boto3 Amazon DynamoDB 호출 자동 추적
> - `@xray_recorder.capture('create_reservation')` - 커스텀 서브세그먼트 데코레이터
> - `subsegment.put_annotation()` - 검색 가능한 어노테이션 추가
> - `subsegment.put_metadata()` - 상세 메타데이터 추가
>
> **주요 코드 패턴**:
>
> ```python
> from aws_xray_sdk.core import patch_all, xray_recorder
> patch_all()  # boto3 Amazon DynamoDB 호출 자동 추적
>
> @xray_recorder.capture('create_reservation')
> def create_reservation(event):
>     subsegment = xray_recorder.current_subsegment()
>     subsegment.put_annotation('restaurantName', restaurant_name)
>     subsegment.put_metadata('reservation_data', reservation)
> ```

27. `GetReservations`로 시작하는 함수도 동일하게 확인합니다.

✅ **태스크 완료**: AWS Lambda 함수 코드를 확인했습니다.

## 태스크 2: AWS X-Ray 추적 활성화 확인

이 태스크에서는 AWS Lambda 함수의 AWS X-Ray 추적이 활성화되어 있는지 확인합니다.

28. AWS Lambda 콘솔에서 `CreateReservation` 함수를 선택합니다.
29. **Configuration** 탭을 선택합니다.
30. 왼쪽 메뉴에서 **Monitoring and operations tools**를 선택합니다.
31. **AWS X-Ray** 섹션에서 **Active tracing**이 활성화되어 있는지 확인합니다.

AWS CloudFormation 템플릿이 자동으로 설정을 완료했습니다.

> [!NOTE]
> AWS CloudFormation 템플릿에서 Active tracing이 자동으로 활성화되었습니다.
> 이 설정으로 AWS Lambda 함수의 모든 호출이 AWS X-Ray에 자동으로 추적됩니다.

32. `GetReservations` 함수도 동일하게 확인합니다.

✅ **태스크 완료**: AWS X-Ray 추적이 활성화되어 있습니다.

## 태스크 3: 예약 생성 API 호출 및 트레이스 생성

이 태스크에서는 QuickTable 예약 생성 API를 호출하여 AWS X-Ray 트레이스를 생성합니다.

33. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.
34. CloudShell이 시작될 때까지 기다립니다.
35. 환경 변수를 설정합니다:

```bash
export API_URL="YOUR_API_URL"
```

> [!IMPORTANT]
> `YOUR_API_URL` 부분을 태스크 0에서 복사한 Invoke URL로 변경합니다.
>
> **URL 형식 주의**:
>
> - Invoke URL 형식: `https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod`
> - URL 끝에 `/prod`가 이미 포함되어 있습니다
> - 요청 시 `/reservations`를 추가하여 전체 경로는 `/prod/reservations`가 됩니다
>
> **잘못된 예시**:
>
> ```bash
> export API_URL="YOUR_API_URL"  # ❌ 그대로 입력하면 안 됨
> ```
>
> **올바른 예시** (본인의 URL로 변경):
>
> ```bash
> export API_URL="https://abc123def4.execute-api.ap-northeast-2.amazonaws.com/prod"
> ```

36. 환경 변수가 올바르게 설정되었는지 확인합니다:

```bash
echo $API_URL
```

37. 다음 명령어를 실행하여 예약을 생성합니다:

```bash
curl -X POST ${API_URL}/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "강남 맛집", "date": "2024-02-20", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}'
```

> [!OUTPUT]
>
> ```json
> {
>   "userId": "anonymous",
>   "reservationId": "res-1234567890",
>   "restaurantName": "강남 맛집",
>   "date": "2024-02-20",
>   "time": "18:00",
>   "partySize": 4,
>   "phoneNumber": "010-1234-5678",
>   "status": "pending",
>   "createdAt": "2024-02-15T10:30:00.123456"
> }
> ```

요청이 성공적으로 처리되었습니다.

> [!NOTE]
> 요청 본문에 `userId` 필드가 없으므로 AWS Lambda 함수가 기본값 "anonymous"를 설정합니다.
>
> **userId 기본값 동작**:
>
> - Amazon DynamoDB 테이블의 키가 userId/reservationId이므로, 모든 예약이 "anonymous" 사용자로 생성됩니다
> - 예약 조회 시 "anonymous" 사용자의 모든 예약이 반환됩니다
> - 실제 프로덕션 환경에서는 Amazon Cognito 등을 사용하여 실제 사용자 ID를 전달해야 합니다

38. 여러 번 명령어를 실행하여 추가 트레이스를 생성합니다 (5-10회 권장).

✅ **태스크 완료**: 예약 생성 트레이스가 생성되었습니다.

## 태스크 4: 예약 조회 API 호출 및 트레이스 생성

이 태스크에서는 QuickTable 예약 조회 API를 호출하여 AWS X-Ray 트레이스를 생성합니다.

39. CloudShell에서 다음 명령어를 실행하여 예약을 조회합니다:

```bash
curl -X GET ${API_URL}/reservations
```

> [!OUTPUT]
>
> ```json
> [
>   {
>     "userId": "anonymous",
>     "reservationId": "res-1234567890",
>     "restaurantName": "강남 맛집",
>     "date": "2024-02-20",
>     "time": "18:00",
>     "partySize": 4,
>     "phoneNumber": "010-1234-5678",
>     "status": "pending",
>     "createdAt": "2024-02-15T10:30:00.123456"
>   }
> ]
> ```

40. 여러 번 명령어를 실행하여 추가 트레이스를 생성합니다.

✅ **태스크 완료**: 예약 조회 트레이스가 생성되었습니다.

## 태스크 5: 서비스 맵 확인

이 태스크에서는 AWS X-Ray 콘솔에서 QuickTable API의 서비스 맵을 확인합니다.

41. AWS Management Console에 로그인한 후 상단 검색창에 `X-Ray`을 입력하고 선택합니다.

> [!NOTE]
> AWS X-Ray를 검색하면 Amazon CloudWatch 콘솔의 AWS X-Ray 섹션으로 이동합니다.
> 또는 Amazon CloudWatch 콘솔 왼쪽 메뉴에서 **AWS X-Ray traces** > **Service map**을 선택할 수도 있습니다.

42. 왼쪽 메뉴에서 **Service map**을 선택합니다.
43. 서비스 맵에서 다음 구성 요소를 확인합니다:
	- **Client**: 요청을 보낸 클라이언트 (CloudShell/curl)
	- **Amazon API Gateway**: QuickTableXRayAPI
	- **AWS Lambda**: CreateReservation, GetReservations
	- **Amazon DynamoDB**: Reservations

> [!NOTE]
> 서비스 맵이 표시되는 데 최대 5분이 소요될 수 있습니다. 페이지를 새로고침하여 확인합니다.
>
> **서비스 맵 구성 요소**:
>
> - **Client 노드**: Amazon API Gateway가 아니라 요청을 보낸 클라이언트(CloudShell/curl)를 나타냅니다
> - **Amazon API Gateway 노드**: QuickTableXRayAPI REST API를 나타냅니다
> - 두 노드는 별도로 표시됩니다

44. AWS Lambda 함수 노드를 클릭합니다.
45. 오른쪽 패널에서 평균 응답 시간, 요청 수, 오류율을 확인합니다.

✅ **태스크 완료**: 서비스 맵을 확인했습니다.

## 태스크 6: 트레이스 분석

이 태스크에서는 AWS X-Ray 트레이스를 분석하여 예약 생성 및 조회 과정의 성능을 확인합니다.

46. 왼쪽 메뉴에서 **AWS X-Ray traces** > **Traces**를 선택합니다.
47. 트레이스 목록에서 POST /reservations 요청을 선택합니다.
48. 트레이스 타임라인에서 다음 정보를 확인합니다:
	- **전체 응답 시간**: 요청부터 응답까지 소요된 시간
	- **세그먼트**: Amazon API Gateway, AWS Lambda, Amazon DynamoDB 각각의 실행 시간
	- **서브세그먼트**: create_reservation, dynamodb_put_item 등의 커스텀 서브세그먼트

49. 세그먼트를 클릭하여 상세 정보를 확인합니다.
50. **Annotations** 탭에서 커스텀 어노테이션을 확인합니다.

> [!NOTE]
> AWS CloudFormation 템플릿으로 배포된 AWS Lambda 함수 코드에는 `subsegment.put_annotation()`으로 추가된 어노테이션이 포함되어 있습니다.
> 어노테이션에는 restaurantName, date, status 등의 정보가 포함되어 있으며, 이를 통해 특정 조건으로 트레이스를 필터링할 수 있습니다.
>
> 어노테이션이 표시되지 않는 경우:
>
> - 태스크 1에서 확인한 AWS Lambda 함수 코드에 `subsegment.put_annotation()` 호출이 있는지 재확인합니다
> - 트레이스가 충분히 생성되었는지 확인합니다 (태스크 3, 4에서 5-10회 API 호출)

51. **Metadata** 탭에서 예약 데이터를 확인합니다.

52. GET /reservations 요청도 동일하게 분석합니다.

✅ **태스크 완료**: 트레이스를 분석했습니다.

## 태스크 7: AWS X-Ray Insights 및 Analytics 활용

이 태스크에서는 AWS X-Ray Insights와 Analytics를 사용하여 자동 이상 탐지 및 트레이스 분석 기능을 확인합니다.

53. AWS X-Ray 콘솔에서 왼쪽 메뉴의 **Insights**를 선택합니다.
54. Insights 대시보드에서 다음 정보를 확인합니다:
	- **응답 시간 이상**: 평균 응답 시간이 증가한 경우
	- **오류율 이상**: 오류율이 증가한 경우
	- **스로틀링 이상**: 요청이 제한된 경우

> [!NOTE]
> AWS X-Ray Insights는 **충분한 트레이스 데이터(수백~수천 건)**가 있어야 이상 탐지가 작동합니다.
> 실습에서는 트레이스 수가 적어(수 건~수십 건) 이상이 표시되지 않을 가능성이 높습니다.
>
> **Insights 활용 시나리오**:
>
> - 프로덕션 환경에서 대량의 트레이스 데이터가 수집되는 경우
> - 응답 시간이나 오류율이 평소와 다른 패턴을 보이는 경우
> - 자동으로 이상을 탐지하고 알림을 받고 싶은 경우
> - 특정 시간대에 성능 저하가 발생했는지 확인하고 싶은 경우

55. 왼쪽 메뉴에서 **Analytics**를 선택합니다.

> [!NOTE]
> Analytics에서 어노테이션으로 그룹화하려면 AWS Lambda 코드에서 실제로 어노테이션을 추가하는 코드가 있어야 합니다.
> 태스크 1에서 확인한 AWS Lambda 함수 코드에 `subsegment.put_annotation()` 호출이 있는지 확인합니다.
> 어노테이션이 없을 경우 드롭다운에 표시되지 않습니다.

56. **Group traces by**에서 `Annotation`을 선택합니다.
57. 어노테이션 키를 선택하여 트레이스를 그룹화합니다.
58. 그래프에서 응답 시간 분포를 확인합니다.
59. **Filter traces**에서 조건을 추가하여 특정 트레이스를 필터링합니다.

> [!NOTE]
> Analytics를 사용하면 어노테이션 기반으로 트레이스를 그룹화하고 분석할 수 있습니다.
> 예: `annotation.restaurantName = "강남 맛집"` 조건으로 특정 레스토랑 예약만 필터링

✅ **태스크 완료**: AWS X-Ray Insights 및 Analytics를 활용하여 이상 탐지 및 분석 기능을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 QuickTable 예약 시스템의 AWS X-Ray 추적 환경을 구축했습니다
- AWS X-Ray SDK가 통합된 AWS Lambda 함수 코드를 확인했습니다
- 예약 생성 및 조회 API를 호출하여 트레이스를 생성했습니다
- 서비스 맵에서 Client → Amazon API Gateway → AWS Lambda → Amazon DynamoDB 흐름을 확인했습니다
- 트레이스를 분석하여 예약 생성 및 조회 과정의 성능을 확인했습니다
- AWS X-Ray Insights를 활용하여 자동 이상 탐지 기능을 확인했습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 사전 확인: Tag Editor로 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `13-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 스택 삭제: AWS CloudFormation 스택 삭제

8. AWS CloudFormation 콘솔로 이동합니다.
9. `week13-2-xray-lab-stack` 스택을 선택합니다.
10. [[Delete]] 버튼을 클릭합니다.
11. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
12. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 Amazon DynamoDB 테이블, AWS Lambda 함수, Amazon API Gateway, AWS IAM 역할이 모두 자동으로 삭제됩니다.
> AWS X-Ray 트레이스 데이터는 자동으로 삭제되지 않지만, 30일 후 자동으로 만료됩니다.

### Amazon CloudWatch Log Group 삭제

13. AWS Management Console에 로그인한 후 상단 검색창에 `CloudWatch`을 입력하고 선택합니다.
14. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
15. 다음 로그 그룹을 검색하여 삭제합니다:
	- `/aws/lambda/CreateReservation-*`
	- `/aws/lambda/GetReservations-*`
	- `/aws/apigateway/QuickTableXRayAPI`

> [!NOTE]
> AWS CloudFormation으로 생성된 AWS Lambda 함수 이름에는 스택 ID가 포함되어 있습니다.
> 예: `/aws/lambda/CreateReservation-week13-2-xray-lab-stack-ABC123`
>
> Amazon API Gateway 로그 그룹(`/aws/apigateway/QuickTableXRayAPI`)은 AWS CloudFormation 템플릿에서 Amazon CloudWatch 로깅을 명시적으로 활성화한 경우에만 생성됩니다.
> 해당 로그 그룹이 존재하지 않을 수 있으며, 존재하는 로그 그룹만 삭제하면 됩니다.

16. 각 로그 그룹을 선택한 후 **Actions** > `Delete log group(s)`를 선택합니다.
17. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.
> 로그 그룹을 삭제하지 않으면 스토리지 비용(GB당 월 $0.50)이 계속 부과됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/aws-xray.html)
- [AWS X-Ray SDK for Python](https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/)
- [AWS Lambda와 AWS X-Ray 통합](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/services-xray.html)
- [AWS X-Ray 서비스 맵](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-console-servicemap.html)
- [AWS X-Ray Insights](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-insights.html)

## 📚 참고: QuickTable 예약 시스템의 AWS X-Ray 추적

### 분산 추적 아키텍처

QuickTable 레스토랑 예약 시스템에서 AWS X-Ray는 다음과 같은 분산 추적을 제공합니다:

**요청 흐름**:

18. 클라이언트가 Amazon API Gateway에 예약 생성 요청을 전송합니다.
19. Amazon API Gateway가 CreateReservation AWS Lambda 함수를 호출합니다.
20. AWS Lambda 함수가 Amazon DynamoDB Reservations 테이블에 예약 데이터를 저장합니다.
21. 응답이 역순으로 클라이언트에게 전달됩니다.

**추적 정보**:

- 전체 요청 시간: Amazon API Gateway 수신부터 클라이언트 응답까지
- AWS Lambda 실행 시간: 함수 초기화 + 비즈니스 로직 실행
- Amazon DynamoDB 작업 시간: PutItem/Query 작업 소요 시간

### AWS X-Ray 구성 요소

**세그먼트 (Segment)**:

- **Amazon API Gateway 세그먼트**: API 요청 수신 및 AWS Lambda 호출
- **AWS Lambda 세그먼트**: CreateReservation 또는 GetReservations 함수 실행
- **Amazon DynamoDB 세그먼트**: Reservations 테이블 읽기/쓰기 작업

**서브세그먼트 (Subsegment)**:

- **create_reservation**: 예약 생성 비즈니스 로직
- **get_reservations**: 예약 조회 비즈니스 로직
- **dynamodb_put_item**: Amazon DynamoDB PutItem 작업
- **dynamodb_query**: Amazon DynamoDB Query 작업
- **validate_input**: 입력 데이터 검증

**어노테이션 (Annotation)**:

- `restaurantName`: 레스토랑 이름 (검색 가능)
- `date`: 예약 날짜 (검색 가능)
- `status`: 예약 상태 (검색 가능)
- `operation`: 작업 유형 (create, get)

**메타데이터 (Metadata)**:

- `reservation_data`: 전체 예약 데이터
- `user_id`: 사용자 ID
- `request_body`: 요청 본문

### 서비스 맵 분석

QuickTable 서비스 맵은 다음 구성 요소를 보여줍니다:

```
Client → Amazon API Gateway → AWS Lambda (CreateReservation) → Amazon DynamoDB (Reservations)
                            → AWS Lambda (GetReservations) → Amazon DynamoDB (Reservations)
```

**성능 지표**:

- **평균 응답 시간**: 전체 요청 처리 시간
- **요청 수**: 시간당 예약 생성/조회 요청 수
- **오류율**: 실패한 요청 비율
- **스로틀링**: Amazon DynamoDB 용량 초과로 제한된 요청

**병목 지점 식별**:

- AWS Lambda 콜드 스타트: 첫 요청 시 초기화 시간 증가
- Amazon DynamoDB 쓰기 지연: 대량 예약 생성 시 지연 발생

### AWS X-Ray SDK 사용 패턴

**자동 추적**:

```python
from aws_xray_sdk.core import patch_all
patch_all()  # boto3 Amazon DynamoDB 호출 자동 추적
```

**커스텀 서브세그먼트**:

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('create_reservation')
def create_reservation(event):
    # 예약 생성 로직
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation('restaurantName', restaurant_name)
    subsegment.put_annotation('date', date)
    subsegment.put_metadata('reservation_data', reservation)
```

**어노테이션 및 메타데이터**:

```python
segment = xray_recorder.current_segment()
segment.put_annotation('operation', 'create')  # 검색 가능
segment.put_metadata('request', event)  # 상세 정보
```

### 실전 활용 사례

**1. 성능 최적화**:

- 트레이스 분석으로 Amazon DynamoDB Query 시간이 긴 것을 발견
- GSI 추가로 쿼리 성능 개선 (500ms → 50ms)

**2. 오류 추적**:

- 특정 레스토랑 예약 시 오류율 증가 발견
- 메타데이터 분석으로 입력 데이터 검증 오류 확인
- 검증 로직 개선으로 오류율 감소

**3. 용량 계획**:

- 서비스 맵에서 피크 시간대 요청 수 확인
- Amazon DynamoDB Amazon EC2 Auto Scaling 설정으로 용량 자동 조정

**4. 사용자 경험 개선**:

- 평균 응답 시간 분석으로 느린 API 식별
- AWS Lambda 메모리 증가로 실행 시간 단축

### 모범 사례

**어노테이션 활용**:

- 검색 가능한 정보는 어노테이션으로 저장합니다
- 레스토랑 이름, 날짜, 상태 등을 어노테이션으로 추가합니다
- 필터링 및 그룹화에 활용합니다

**서브세그먼트 세분화**:

- 병목 지점을 정확히 식별하기 위해 서브세그먼트를 세분화합니다
- 입력 검증, 비즈니스 로직, Amazon DynamoDB 작업을 별도 서브세그먼트로 추적합니다

**오류 처리**:

- 오류 발생 시 세그먼트에 오류 정보를 기록합니다
- 오류 원인과 스택 트레이스를 메타데이터로 저장합니다

**샘플링 규칙**:

- 프로덕션 환경에서는 샘플링 규칙을 사용하여 비용을 절감합니다
- 중요한 요청은 100% 추적하고, 일반 요청은 샘플링합니다
- 예: 예약 생성은 100%, 예약 조회는 10% 샘플링
- **기본 샘플링**: 초당 1개 요청 + 추가 요청의 5% (Reservoir + Fixed rate)
- **커스텀 규칙**: AWS X-Ray 콘솔에서 URL 패턴, HTTP 메서드, 서비스별로 샘플링 비율 설정 가능
