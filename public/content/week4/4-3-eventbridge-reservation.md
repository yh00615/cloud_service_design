---
title: 'Amazon EventBridge 기반 예약 처리 시스템'
week: 4
session: 3
awsServices:
  - Amazon EventBridge
  - AWS Lambda
  - Amazon DynamoDB
learningObjectives:
  - Amazon EventBridge의 이벤트 기반 아키텍처와 이벤트 패턴 매칭을 이해할 수 있습니다.
  - ReservationCreated 이벤트 규칙을 생성하고 AWS Lambda를 연결할 수 있습니다.
  - TableUnavailable 이벤트 규칙을 생성하고 알림을 구성할 수 있습니다.
  - 이벤트 기반 워크플로우를 테스트하고 검증할 수 있습니다.

prerequisites:
  - Week 4-2 AWS Lambda 및 Amazon API Gateway 이해
---

이 실습에서는 QuickTable 레스토랑 예약 시스템에 Amazon EventBridge 기반 이벤트 처리를 추가합니다. 예약 생성 시 자동으로 테이블 재고를 확인하고, 예약 가능 여부에 따라 고객에게 알림을 발송하는 이벤트 기반 아키텍처를 구축합니다. Week 4-2에서 구축한 예약 API와 자연스럽게 연결되어 전체 예약 시스템을 완성합니다.

> [!DOWNLOAD]
> [week4-3-eventbridge-lab.zip](/files/week4/week4-3-eventbridge-lab.zip)
>
> - `week4-3-eventbridge-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB 테이블, Amazon EventBridge Event Bus, AWS Lambda 함수 3개, AWS Lambda 역할, Amazon SNS Topic 자동 생성)
> - `reservation_processor.py` - 예약 생성 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
> - `table_availability_checker.py` - 테이블 재고 확인 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
> - `notification_sender.py` - 알림 발송 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week4-3-eventbridge-lab.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon DynamoDB 테이블**: Reservations 테이블 (예약 데이터 저장), RestaurantAvailability 테이블 (레스토랑별 시간대별 예약 가능 슬롯 저장)
- **Amazon EventBridge Event Bus**: ReservationEventBus (이벤트 라우팅)
- **AWS Lambda 함수 3개**: ReservationProcessor, TableAvailabilityChecker, NotificationSender (이벤트 처리)
- **AWS Lambda 실행 역할**: Amazon DynamoDB, Amazon EventBridge, Amazon SNS 접근 권한
- **Amazon SNS Topic**: ReservationNotifications (알림 발송)
- **Amazon CloudWatch Logs Groups**: AWS Lambda 함수 로그 저장

> [!NOTE]
> Amazon EventBridge 규칙(Rules)은 AWS CloudFormation에 포함되지 않습니다. 태스크 1-2에서 학생이 직접 이벤트 패턴을 정의하고 규칙을 생성합니다.
>
> **RestaurantAvailability 테이블 초기 데이터 및 비즈니스 로직**:
>
> AWS CloudFormation 스택은 RestaurantAvailability 테이블에 다음 초기 데이터를 자동으로 삽입합니다. timeSlot 형식은 `날짜#시간` (예: `2026-03-20#19:00`)입니다.
>
> - restaurant-001 (이탈리안 레스토랑): 2026-03-20#18:00, 2026-03-20#19:00, 2026-03-20#20:00 시간대 각 5개 테이블
> - restaurant-002 (한식당): 2026-03-20#18:00, 2026-03-20#19:00, 2026-03-20#20:00 시간대 각 8개 테이블
> - restaurant-003 (일식당): 2026-03-20#18:00, 2026-03-20#19:00, 2026-03-20#20:00 시간대 각 3개 테이블 (예약 가능 슬롯 부족 테스트용)
> - restaurant-004 (중식당): 2026-03-20#18:00, 2026-03-20#19:00, 2026-03-20#20:00 시간대 각 10개 테이블
>
> **날짜 변경 방법**: 실습 시점이 2026-03-20 이후라면 AWS CloudFormation 템플릿의 `InitializeRestaurantAvailability` 함수 코드에서 날짜를 수정할 수 있습니다. 템플릿 파일을 텍스트 에디터로 열어 `2026-03-20`을 원하는 날짜로 변경한 후 스택을 생성합니다. 태스크 3-4의 테스트 이벤트 JSON에서도 동일한 날짜를 사용해야 합니다.
>
> **partySize와 availableSlots 비교 로직**: TableAvailabilityChecker 함수는 `partySize`(예약 인원 수)와 `availableSlots`(예약 가능한 슬롯 수)를 비교합니다. 이 실습에서는 availableSlots를 "동시에 수용 가능한 예약 건수"로 단순화합니다.
>
> - partySize가 availableSlots보다 크면 예약 불가로 처리합니다 (partySize > availableSlots)
> - 예: partySize=4, availableSlots=3 → 4 > 3 → 예약 불가
> - 예: partySize=2, availableSlots=5 → 2 ≤ 5 → 예약 가능
>
> 실제 프로덕션 환경에서는 테이블 크기(2인용, 4인용, 6인용 등)를 고려하여 더 복잡한 로직을 구현해야 합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week4-3-eventbridge-lab.zip` 파일의 압축을 해제합니다.
2. `week4-3-eventbridge-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week4-3-eventbridge-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week4-3-quicktable-events-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 **EnvironmentName**이 `week4-3-quicktable-events-lab`인지 확인합니다.
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
15. [[Next]] 버튼을 클릭합니다.
16. **Review** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.
18. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
20. **Outputs** 탭을 선택합니다.
21. 출력값들을 확인합니다:
    - `ReservationsTableName`: Reservations 테이블 이름 (QuickTableReservations)
    - `RestaurantAvailabilityTableName`: RestaurantAvailability 테이블 이름 (QuickTableRestaurantAvailability)
    - `ReservationEventBusName`: Event Bus 이름 (예: week4-3-quicktable-events-lab-ReservationEventBus)
    - `LambdaExecutionRoleArn`: AWS Lambda 실행 역할 ARN
    - `ReservationNotificationTopicArn`: Amazon SNS Topic ARN

> [!IMPORTANT]
> **출력값 메모**: 이후 태스크에서 사용되는 출력값은 `ReservationEventBusName` 하나뿐입니다. 태스크 1-2에서 Amazon EventBridge 규칙 생성 시 Event Bus를 선택할 때 참고합니다. 나머지 출력값(LambdaExecutionRoleArn, ReservationNotificationTopicArn 등)은 참고용이며 실습에서 직접 사용하지 않습니다.
>
> **날짜 변경 방법 (중요)**: 실습 시점이 2026-03-20 이후라면 다음 두 가지를 모두 수정해야 합니다:
>
> 1. **AWS CloudFormation 템플릿**: `week4-3-eventbridge-lab.yaml` 파일을 텍스트 에디터로 열어 `InitializeAvailabilityFunction` 함수 코드에서 `2026-03-20`을 원하는 날짜로 변경한 후 스택을 생성합니다.
> 2. **테스트 이벤트 JSON**: 태스크 3-4의 테스트 이벤트 JSON에서 `"date": "2026-03-20"`을 동일한 날짜로 변경합니다.
>
> 두 날짜가 일치하지 않으면 RestaurantAvailability 테이블에 해당 날짜의 데이터가 없어 실습이 정상 동작하지 않습니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: ReservationCreated 이벤트 규칙 생성

이 태스크에서는 Amazon EventBridge에서 ReservationCreated 이벤트를 수신하여 TableAvailabilityChecker AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 태스크 설명

Amazon EventBridge 규칙은 이벤트 패턴을 정의하여 특정 이벤트만 필터링하고 대상 서비스로 전달합니다. 이 태스크에서는 `source=reservation.service`, `detail-type=ReservationCreated` 조건을 만족하는 이벤트만 TableAvailabilityChecker AWS Lambda 함수로 라우팅하는 규칙을 생성합니다.

### 상세 단계

> [!IMPORTANT]
> **태스크 1과 태스크 2의 차이점**: 이 두 태스크는 Amazon EventBridge 규칙 생성 과정이 거의 동일하지만, 다음 3가지만 다릅니다:
>
> 1. **규칙 이름 (Name)**: ReservationCreatedRule vs TableUnavailableRule
> 2. **이벤트 패턴 JSON**: source와 detail-type 값이 다름
> 3. **대상 AWS Lambda 함수**: TableAvailabilityChecker vs NotificationSender
>
> 나머지 단계는 모두 동일하므로 이 3가지 차이점에 집중하여 진행합니다.

22. AWS Management Console에 로그인한 후 상단 검색창에 `EventBridge`을 입력하고 선택합니다.
23. 왼쪽 메뉴에서 **Rules**를 선택합니다.
24. **Event bus** 드롭다운에서 태스크 0에서 생성한 Event Bus를 선택합니다.

> [!NOTE]
> Event Bus 이름은 `week4-3-quicktable-events-lab-ReservationEventBus` 형식입니다.

25. [[Create rule]] 버튼을 클릭합니다.
26. **Define rule detail** 페이지에서 다음을 입력합니다:
	- **Name**: `ReservationCreatedRule`
	- **Description**: `Route ReservationCreated events to TableAvailabilityChecker`
	- **Event bus**: 태스크 0에서 생성한 Event Bus 선택 (이미 선택되어 있음)
27. **Rule type**에서 `Rule with an event pattern`을 선택합니다.
28. [[Next]] 버튼을 클릭합니다.
29. **Build event pattern** 페이지에서 **Event source**는 `Other`를 선택합니다.
30. **Creation method**에서 `Custom pattern (JSON editor)` 또는 `Edit pattern`을 선택합니다.

> [!NOTE]
> Amazon EventBridge 콘솔에서 이벤트 패턴을 입력하는 방법은 두 가지입니다:
>
> - **Pattern builder (GUI)**: 드롭다운으로 source, detail-type 등을 선택
> - **Custom pattern (JSON)**: JSON을 직접 입력
>
> 이 실습에서는 JSON 직접 입력 방식을 사용하므로 "Custom pattern" 또는 "Edit pattern" 옵션을 먼저 선택해야 합니다.

31. **Event pattern** 섹션에서 다음 JSON을 입력합니다:

```json
{
  "source": ["reservation.service"],
  "detail-type": ["ReservationCreated"]
}
```

> [!CONCEPT] 이벤트 패턴 (Event Pattern)
> 이벤트 패턴은 Amazon EventBridge가 이벤트를 필터링하는 규칙입니다. JSON 형식으로 정의하며, `source`, `detail-type`, `detail` 필드를 기준으로 매칭합니다.
>
> - **source**: 이벤트를 발행한 서비스 또는 애플리케이션 (예: `reservation.service`)
> - **detail-type**: 이벤트 타입 (예: `ReservationCreated`, `TableUnavailable`)
> - **detail**: 이벤트 상세 데이터 (선택적 필터링)
>
> 배열 내 하나라도 일치하면 조건이 충족됩니다 (OR 연산). 모든 필드가 일치해야 이벤트가 대상으로 전달됩니다 (AND 연산).

32. [[Next]] 버튼을 클릭합니다.
33. **Select target(s)** 페이지에서 **Target types**는 `AWS service`를 선택합니다.
34. **Select a target**에서 `AWS Lambda function`을 선택합니다.
35. **Function** 드롭다운에서 `TableAvailabilityChecker`를 선택합니다.

> [!NOTE]
> TableAvailabilityChecker AWS Lambda 함수는 태스크 0에서 AWS CloudFormation이 자동으로 생성했습니다. 함수 이름은 `week4-3-quicktable-events-lab-TableAvailabilityChecker` 형식입니다.

36. [[Next]] 버튼을 클릭합니다.
37. **Configure tags** 페이지에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

38. [[Next]] 버튼을 클릭합니다.
39. **Review and create** 페이지에서 설정을 확인합니다.
40. [[Create rule]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon EventBridge 규칙이 AWS Lambda 함수를 트리거할 수 있도록 권한이 자동으로 추가됩니다.

규칙 생성 후 필요에 따라 수정하거나 삭제할 수 있습니다.

> [!TIP]
> **Amazon EventBridge 규칙 수정 및 삭제**: 생성한 규칙을 수정하거나 삭제하려면 Amazon EventBridge 콘솔의 Rules 페이지에서 규칙을 선택한 후 [[Edit]] 또는 [[Delete]] 버튼을 클릭합니다. 규칙 삭제 시 확인 창에 `delete`를 입력해야 합니다 (규칙 이름이 아님).

✅ **태스크 완료**: ReservationCreated 이벤트 규칙이 생성되었습니다.

## 태스크 2: TableUnavailable 이벤트 규칙 생성

이 태스크에서는 Amazon EventBridge에서 TableUnavailable 이벤트를 수신하여 NotificationSender AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 태스크 설명

TableAvailabilityChecker AWS Lambda 함수가 예약 가능한 슬롯이 부족하다고 판단하면 TableUnavailable 이벤트를 발행합니다. 이 이벤트를 수신하여 NotificationSender AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 상세 단계

> [!IMPORTANT]
> **태스크 1과의 차이점**: 이 태스크는 태스크 1과 거의 동일하지만, 다음 3가지만 다릅니다:
>
> 1. **규칙 이름**: `TableUnavailableRule` (태스크 1은 ReservationCreatedRule)
> 2. **이벤트 패턴**: `source=availability.service`, `detail-type=TableUnavailable` (태스크 1은 reservation.service, ReservationCreated)
> 3. **대상 함수**: `NotificationSender` (태스크 1은 TableAvailabilityChecker)
>
> 이 3가지 차이점에 집중하여 진행합니다.

41. Amazon EventBridge 콘솔로 이동합니다.
42. 왼쪽 메뉴에서 **Rules**를 선택합니다.
43. **Event bus** 드롭다운에서 태스크 0에서 생성한 Event Bus를 선택합니다.
44. [[Create rule]] 버튼을 클릭합니다.
45. **Define rule detail** 페이지에서 다음을 입력합니다:
	- **Name**: `TableUnavailableRule`
	- **Description**: `Route TableUnavailable events to NotificationSender`
	- **Event bus**: 태스크 0에서 생성한 Event Bus 선택 (이미 선택되어 있음)
46. **Rule type**에서 `Rule with an event pattern`을 선택합니다.
47. [[Next]] 버튼을 클릭합니다.
48. **Build event pattern** 페이지에서 **Event source**는 `Other`를 선택합니다.
49. **Creation method**에서 `Custom pattern (JSON editor)` 또는 `Edit pattern`을 선택합니다.
50. **Event pattern** 섹션에서 다음 JSON을 입력합니다:

```json
{
  "source": ["availability.service"],
  "detail-type": ["TableUnavailable"]
}
```

51. [[Next]] 버튼을 클릭합니다.
52. **Select target(s)** 페이지에서 **Target types**는 `AWS service`를 선택합니다.
53. **Select a target**에서 `AWS Lambda function`을 선택합니다.
54. **Function** 드롭다운에서 `NotificationSender`를 선택합니다.
55. [[Next]] 버튼을 클릭합니다.
56. **Configure tags** 페이지에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

57. [[Next]] 버튼을 클릭합니다.
58. **Review and create** 페이지에서 설정을 확인합니다.
59. [[Create rule]] 버튼을 클릭합니다.

✅ **태스크 완료**: TableUnavailable 이벤트 규칙이 생성되었습니다.

## 태스크 3: 예약 생성 테스트 (이벤트 기반 워크플로우 확인)

이 태스크에서는 ReservationProcessor AWS Lambda 함수를 수동으로 실행하여 전체 이벤트 기반 워크플로우를 테스트합니다.

### 태스크 설명

ReservationProcessor 함수를 테스트 이벤트로 실행하면 ReservationCreated 이벤트가 발행되고, 태스크 1에서 생성한 Amazon EventBridge 규칙이 이 이벤트를 감지하여 TableAvailabilityChecker 함수를 자동으로 트리거합니다.

**이벤트 흐름**:

60. ReservationProcessor → Amazon DynamoDB에 예약 저장.
61. ReservationProcessor → Amazon EventBridge에 ReservationCreated 이벤트 발행.
62. Amazon EventBridge → ReservationCreatedRule 규칙 매칭.
63. Amazon EventBridge → TableAvailabilityChecker 함수 트리거.
64. TableAvailabilityChecker → 가용성 확인.
65. (불가 시) TableAvailabilityChecker → Amazon EventBridge에 TableUnavailable 이벤트 발행
66. (불가 시) Amazon EventBridge → TableUnavailableRule 규칙 매칭
67. (불가 시) Amazon EventBridge → NotificationSender 함수 트리거

> [!NOTE]
> 이 실습에서는 AWS Lambda 함수를 직접 테스트하여 이벤트 기반 워크플로우를 확인합니다. 실제 프로덕션 환경에서는 Amazon API Gateway를 통해 ReservationProcessor 함수를 호출하며, 사용자 요청이 자동으로 이벤트 기반 워크플로우를 트리거합니다.

### AWS Lambda 함수 코드 확인

ReservationProcessor AWS Lambda 함수는 태스크 0에서 AWS CloudFormation이 자동으로 생성했습니다. 다음은 함수의 핵심 코드입니다 (참고용):

```python
# 예약 데이터를 Amazon DynamoDB에 저장
dynamodb.put_item(
    TableName=table_name,
    Item={
        'reservationId': {'S': reservation_id},
        'userId': {'S': user_id},
        'restaurantId': {'S': restaurant_id},
        # ... 기타 필드
    }
)

# Amazon EventBridge에 ReservationCreated 이벤트 발행
eventbridge.put_events(
    Entries=[
        {
            'Source': 'reservation.service',
            'DetailType': 'ReservationCreated',
            'Detail': json.dumps(event_detail),
            'EventBusName': event_bus_name
        }
    ]
)
```

> [!NOTE]
> 전체 AWS Lambda 함수 코드는 다운로드한 ZIP 파일의 `reservation_processor.py` 파일에서 확인할 수 있습니다.
>
> **date/time → timeSlot 변환 로직**: ReservationProcessor 함수는 `date`와 `time` 필드를 받아 `날짜#시간` 형식의 `timeSlot`으로 변환합니다. 예를 들어, `date="2026-03-20"`, `time="19:00"`은 `timeSlot="2026-03-20#19:00"`으로 변환되어 Amazon DynamoDB RestaurantAvailability 테이블을 조회하는 데 사용됩니다.

### 상세 단계

68. AWS Lambda 콘솔로 이동합니다.
69. `ReservationProcessor` 함수를 선택합니다.

> [!NOTE]
> ReservationProcessor AWS Lambda 함수는 태스크 0에서 AWS CloudFormation이 자동으로 생성했습니다. 함수 이름은 `week4-3-quicktable-events-lab-ReservationProcessor` 형식입니다.

70. **Test** 탭을 선택합니다.
71. **Test event action**에서 `Create new event`를 선택합니다.
72. **Event name**에 `TestReservationAvailableEvent`를 입력합니다.
73. **Event JSON**에 다음 내용을 입력합니다:

```json
{
  "reservationId": "res-001",
  "userId": "user-123",
  "restaurantId": "restaurant-001",
  "date": "2026-03-20",
  "time": "19:00",
  "partySize": 2,
  "phoneNumber": "010-1234-5678"
}
```

> [!IMPORTANT]
> **날짜 변경 필수**: 실습 시점이 2026-03-20 이후라면 `date` 필드를 실습 시점 기준 미래 날짜로 변경합니다. 단, AWS CloudFormation 템플릿의 초기 데이터 날짜도 동일하게 수정해야 합니다 (태스크 0 출력값 확인 섹션의 IMPORTANT Alert 참조).
>
> restaurant-001은 19:00 시간대에 5개의 예약 가능 슬롯이 있으므로, partySize=2인 예약은 성공합니다.

74. [[Save]] 버튼을 클릭합니다.
75. [[Test]] 버튼을 클릭합니다.
76. 함수 실행이 완료됩니다.
77. **Execution result** 섹션에서 실행 결과를 확인합니다.

> [!OUTPUT]
>
> ```json
> {
>   "statusCode": 200,
>   "body": "{\"message\": \"Reservation created successfully\", \"reservationId\": \"res-001\"}"
> }
> ```

78. **Monitor** 탭을 선택합니다.
79. **View Amazon CloudWatch Logs** 링크를 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

80. 최신 로그 스트림을 선택합니다.
81. 로그에서 "ReservationCreated event published" 메시지를 확인합니다.

> [!NOTE]
> 이 메시지는 ReservationProcessor 함수가 Amazon EventBridge에 이벤트를 성공적으로 발행했음을 의미합니다.

82. AWS Lambda 콘솔로 이동합니다.
83. 검색창에 `TableAvailabilityChecker`를 입력하여 함수를 찾습니다.
84. `TableAvailabilityChecker` 함수를 선택합니다.

> [!NOTE]
> 함수 이름이 `week4-3-quicktable-events-lab-TableAvailabilityChecker`로 길기 때문에 검색창을 사용하면 쉽게 찾을 수 있습니다.
>
> **Amazon EventBridge 전달 지연**: ReservationProcessor 실행 후 Amazon EventBridge가 TableAvailabilityChecker를 트리거하기까지 수 초~1분이 소요될 수 있습니다. 로그가 보이지 않으면 1-2분 대기 후 새로고침합니다.

85. **Monitor** 탭을 선택합니다.
86. **View Amazon CloudWatch Logs** 링크를 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

Amazon CloudWatch Logs 콘솔에서 로그 스트림 목록이 표시됩니다.

> [!TIP]
> **로그 스트림 식별 방법**: Amazon CloudWatch Logs 콘솔에서 로그 스트림 목록이 표시되면 **Last event time** 컬럼을 기준으로 정렬하여 가장 최근 스트림을 선택합니다. 기본적으로 최신 순으로 정렬되어 있으므로 목록 맨 위의 스트림을 선택하면 됩니다.

87. 최신 로그 스트림을 선택합니다.
88. 로그에서 "Table available: party size (2) within available slots (5)" 메시지를 확인합니다.

> [!NOTE]
> TableAvailabilityChecker 함수가 자동으로 실행되었다면 태스크 1에서 생성한 Amazon EventBridge 규칙이 정상적으로 동작하는 것입니다. 예약 가능한 경우 TableUnavailable 이벤트가 발행되지 않으므로 NotificationSender 함수는 실행되지 않습니다.

만약 로그가 표시되지 않는다면 다음 문제 해결 방법을 시도합니다.

> [!TROUBLESHOOTING]
> **문제**: TableAvailabilityChecker 함수의 Amazon CloudWatch Logs가 생성되지 않습니다
>
> **증상**: Monitor 탭에서 "View Amazon CloudWatch Logs" 링크를 클릭해도 로그 스트림이 표시되지 않습니다.
>
> **원인**: Amazon EventBridge 규칙이 올바르게 설정되지 않았거나, AWS Lambda 함수 권한이 부족합니다.
>
> **해결**:
>
> 1. Amazon EventBridge 콘솔에서 ReservationCreatedRule 규칙의 Targets 섹션에 TableAvailabilityChecker 함수가 연결되어 있는지 확인합니다.
> 2. AWS Lambda 콘솔에서 TableAvailabilityChecker 함수의 Configuration > Permissions > Resource-based policy statements에서 Amazon EventBridge 호출 권한을 확인합니다.
> 3. ReservationProcessor 함수로 돌아가 테스트 이벤트를 다시 실행한 후 1-2분 대기합니다.
> 4. ReservationProcessor 함수로 돌아가 테스트 이벤트를 다시 실행한 후 1-2분 대기합니다.

### Amazon EventBridge 규칙 동작 확인

89. Amazon EventBridge 콘솔로 이동합니다.
90. 왼쪽 메뉴에서 **Rules**를 선택합니다.
91. **Event bus** 드롭다운에서 `week4-3-quicktable-events-lab-ReservationEventBus`를 선택합니다.
92. `ReservationCreatedRule` 규칙을 선택합니다.
93. **Monitoring** 탭을 선택합니다.
94. **Invocations** 메트릭에서 규칙이 트리거된 횟수를 확인합니다.

> [!NOTE]
> Invocations 메트릭이 1 이상이면 Amazon EventBridge 규칙이 정상적으로 동작한 것입니다. Amazon CloudWatch 메트릭은 1-2분의 지연이 있을 수 있으므로 메트릭이 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

### 느슨한 결합 확인

95. AWS Lambda 콘솔로 이동합니다.
96. `ReservationProcessor` 함수를 선택합니다.
97. **Code** 탭을 선택합니다.
98. 함수 코드에서 다른 AWS Lambda 함수를 직접 호출하는 코드가 없음을 확인합니다.

> [!CONCEPT] 느슨한 결합 (Loose Coupling)
> 이 실습에서 구현한 아키텍처는 느슨한 결합의 좋은 예시입니다:
>
> **확인 사항**:
>
> - ReservationProcessor 함수는 TableAvailabilityChecker 함수를 직접 호출하지 않습니다
> - TableAvailabilityChecker 함수는 NotificationSender 함수를 직접 호출하지 않습니다
> - 각 함수는 Amazon EventBridge에 이벤트를 발행하기만 하고, Amazon EventBridge가 규칙에 따라 적절한 대상 함수를 트리거합니다
>
> **장점**:
>
> - 한 함수가 실패해도 다른 함수는 정상 동작합니다
> - 새로운 함수를 추가할 때 기존 함수 코드를 수정할 필요가 없습니다
> - 각 함수를 독립적으로 테스트하고 배포할 수 있습니다
> - 함수 간 의존성이 없어 유지보수가 쉽습니다
>
> 이것이 실습 목표 3 "AWS Lambda 함수 간 느슨한 결합을 구현할 수 있습니다"의 핵심입니다.

99. Amazon DynamoDB 콘솔로 이동합니다.
100. 왼쪽 메뉴에서 **Tables**를 선택합니다.
101. `QuickTableReservations` 테이블을 선택합니다.
102. [[Explore table items]] 버튼을 클릭합니다.
103. `reservationId`가 `res-001`인 항목을 확인합니다.

> [!NOTE]
> Amazon DynamoDB 테이블에 예약 데이터가 저장되어 있으면 ReservationProcessor 함수가 정상적으로 동작한 것입니다.

✅ **태스크 완료**: 예약 가능 시나리오가 정상적으로 동작합니다.

## 태스크 4: 예약 불가 시나리오 테스트

이 태스크에서는 예약 가능한 슬롯이 부족한 경우를 테스트하여 TableUnavailable 이벤트와 NotificationSender 함수가 정상적으로 동작하는지 확인합니다.

### 태스크 설명

restaurant-003은 19:00 시간대에 3개의 예약 가능 슬롯만 있습니다. partySize=4인 예약을 요청하면 TableAvailabilityChecker 함수가 TableUnavailable 이벤트를 발행하고, 태스크 2에서 생성한 Amazon EventBridge 규칙이 이 이벤트를 감지하여 NotificationSender 함수를 트리거합니다.

> [!IMPORTANT]
> **비동기 처리 이해하기:**
>
> 이 실습의 아키텍처는 비동기 이벤트 기반으로 설계되었습니다. ReservationProcessor 함수는 다음 순서로 동작합니다:
>
> 1. 예약 데이터를 Amazon DynamoDB에 먼저 저장합니다
> 2. ReservationCreated 이벤트를 Amazon EventBridge에 발행합니다
> 3. 즉시 성공 응답(200)을 반환합니다
>
> 이후 TableAvailabilityChecker 함수가 **비동기적으로** 가용성을 확인하고, 예약이 불가능한 경우 TableUnavailable 이벤트를 발행하여 NotificationSender 함수가 고객에게 알림을 발송합니다.
>
> 따라서 **예약이 불가능한 경우에도 ReservationProcessor 함수는 200 성공 응답을 반환합니다.** 이는 이벤트 기반 아키텍처의 특성으로, 각 함수가 독립적으로 동작하며 느슨하게 결합되어 있습니다.

### 상세 단계

104. AWS Lambda 콘솔로 이동합니다.
105. `ReservationProcessor` 함수를 선택합니다.
106. **Test** 탭을 선택합니다.
107. **Test event action**에서 `Create new event`를 선택합니다.
108. **Event name**에 `TestReservationUnavailableEvent`를 입력합니다.
109. **Event JSON**에 다음 내용을 입력합니다:

```json
{
  "reservationId": "res-002",
  "userId": "user-456",
  "restaurantId": "restaurant-003",
  "date": "2026-03-20",
  "time": "19:00",
  "partySize": 4,
  "phoneNumber": "010-9876-5432"
}
```

> [!IMPORTANT]
> **날짜 변경 필수**: 실습 시점이 2026-03-20 이후라면 `date` 필드를 실습 시점 기준 미래 날짜로 변경합니다. 단, AWS CloudFormation 템플릿의 초기 데이터 날짜도 동일하게 수정해야 합니다 (태스크 0 출력값 확인 섹션의 IMPORTANT Alert 참조).
>
> restaurant-003은 19:00 시간대에 3개의 예약 가능 슬롯만 있으므로, partySize=4인 예약은 실패합니다.

110. [[Save]] 버튼을 클릭합니다.
111. [[Test]] 버튼을 클릭합니다.
112. 함수 실행이 완료됩니다.
113. **Execution result** 섹션에서 실행 결과를 확인합니다.

> [!OUTPUT]
>
> ```json
> {
>   "statusCode": 200,
>   "body": "{\"message\": \"Reservation created successfully\", \"reservationId\": \"res-002\"}"
> }
> ```

> [!NOTE]
> 예약 불가 시나리오에서도 ReservationProcessor 함수는 200 성공 응답을 반환합니다. 이는 비동기 이벤트 기반 아키텍처의 특성으로, 예약 데이터는 먼저 저장되고 이후 TableAvailabilityChecker가 비동기적으로 가용성을 확인합니다.

114. **Monitor** 탭을 선택합니다.
115. **View Amazon CloudWatch Logs** 링크를 클릭합니다.
116. 최신 로그 스트림을 선택합니다.
117. 로그에서 "Reservation created successfully" 메시지를 확인합니다.

> [!NOTE]
> ReservationProcessor 함수가 정상적으로 실행되었습니다. 이제 Amazon DynamoDB에 예약 데이터가 저장되었는지 확인합니다.

118. Amazon DynamoDB 콘솔로 이동합니다.
119. 왼쪽 메뉴에서 **Tables**를 선택합니다.
120. `QuickTableReservations` 테이블을 선택합니다.
121. [[Explore table items]] 버튼을 클릭합니다.
122. `reservationId`가 `res-002`인 항목을 확인합니다.

> [!NOTE]
> Amazon DynamoDB 테이블에 예약 데이터가 저장되어 있으면 ReservationProcessor 함수가 정상적으로 동작한 것입니다. 예약 불가 시나리오에서도 예약 데이터는 먼저 저장되고, 이후 TableAvailabilityChecker가 비동기적으로 가용성을 확인합니다.

123. AWS Lambda 콘솔로 이동합니다.
124. `TableAvailabilityChecker` 함수를 선택합니다.
125. **Monitor** 탭을 선택합니다.
126. **View Amazon CloudWatch Logs** 링크를 클릭합니다.
127. 최신 로그 스트림을 선택합니다.
128. 로그에서 "Table unavailable: party size (4) exceeds available slots (3)" 메시지를 확인합니다.
129. 로그에서 "TableUnavailable event published" 메시지를 확인합니다.

> [!NOTE]
> TableAvailabilityChecker 함수가 예약 불가를 판단하고 TableUnavailable 이벤트를 발행했습니다.

130. AWS Lambda 콘솔로 이동합니다.
131. `NotificationSender` 함수를 선택합니다.
132. **Monitor** 탭을 선택합니다.
133. **View Amazon CloudWatch Logs** 링크를 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

134. 최신 로그 스트림을 선택합니다.
135. 로그에서 "Sending notification for reservation: res-002" 메시지를 확인합니다.
136. 로그에서 "Notification sent" 메시지를 확인합니다.

> [!NOTE]
> NotificationSender 함수가 자동으로 실행되었다면 태스크 2에서 생성한 Amazon EventBridge 규칙이 정상적으로 동작하는 것입니다.
>
> 이 실습에서는 Amazon SNS 이메일 구독을 설정하지 않으므로 실제 이메일은 수신되지 않습니다. 알림 발송 여부는 NotificationSender 함수의 Amazon CloudWatch 로그로 확인합니다.

### Amazon EventBridge 규칙 동작 확인

137. Amazon EventBridge 콘솔로 이동합니다.
138. 왼쪽 메뉴에서 **Rules**를 선택합니다.
139. **Event bus** 드롭다운에서 `week4-3-quicktable-events-lab-ReservationEventBus`를 선택합니다.
140. `ReservationCreatedRule` 규칙을 선택합니다.
141. **Monitoring** 탭을 선택합니다.
142. **Invocations** 그래프에서 규칙이 실행된 횟수를 확인합니다.

> [!NOTE]
> 태스크 3과 태스크 4에서 각각 1번씩 ReservationCreated 이벤트를 발행했으므로, Invocations 그래프에 2개의 데이터 포인트가 표시되어야 합니다. 그래프 데이터는 1-2분의 지연이 있을 수 있으므로, 표시되지 않으면 페이지를 새로고침합니다.

143. Amazon EventBridge 콘솔로 이동합니다.
144. 왼쪽 메뉴에서 **Rules**를 선택합니다.
145. **Event bus** 드롭다운에서 `week4-3-quicktable-events-lab-ReservationEventBus`를 선택합니다.
146. `TableUnavailableRule` 규칙을 선택합니다.
147. **Monitoring** 탭을 선택합니다.
148. **Invocations** 그래프에서 규칙이 실행된 횟수를 확인합니다.

> [!NOTE]
> 태스크 4에서만 TableUnavailable 이벤트가 발행되었으므로, Invocations 그래프에 1개의 데이터 포인트가 표시되어야 합니다.

Monitoring 탭에서는 규칙의 실행 통계를 확인할 수 있습니다.

> [!TIP]
> **Amazon EventBridge Monitoring 탭 활용**: Monitoring 탭에서는 규칙이 매칭한 이벤트 수, 대상 함수 호출 성공/실패 횟수, 평균 지연 시간 등을 확인할 수 있습니다. 이벤트 기반 아키텍처를 운영할 때 규칙이 정상적으로 동작하는지 모니터링하는 데 유용합니다.

✅ **태스크 완료**: 예약 불가 시나리오가 정상적으로 동작합니다.

다음을 성공적으로 수행했습니다:

- Amazon EventBridge 규칙을 생성하여 이벤트 기반 아키텍처를 구축했습니다
- ReservationCreated 이벤트 규칙을 생성하고 이벤트 패턴을 정의했습니다
- TableUnavailable 이벤트 규칙을 생성하고 타겟을 연결했습니다
- 이벤트 기반 워크플로우를 테스트하여 느슨한 결합을 확인했습니다
- AWS Lambda 함수 간 직접 호출 없이 이벤트를 통한 통신을 구현했습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

---

## 1단계: 리소스 삭제

다음 두 가지 방법 중 하나를 선택하여 리소스를 삭제할 수 있습니다.

### 옵션 1: AWS 콘솔에서 수동 삭제 (권장)

> [!TIP]
> AWS 관리 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 권장합니다.
>
> AWS CLI 명령어에 익숙한 경우 아래 [옵션 2](#option-2)를 사용하면 더 빠르게 삭제할 수 있습니다.

**Amazon EventBridge 규칙 삭제**

1. Amazon EventBridge 콘솔로 이동합니다.
2. 왼쪽 메뉴에서 **Rules**를 선택합니다.
3. **Event bus** 드롭다운에서 `week4-3-quicktable-events-lab-ReservationEventBus`를 선택합니다.
4. `ReservationCreatedRule` 규칙을 선택합니다.
5. [[Delete]] 버튼을 클릭합니다.
6. 확인 창에 `delete`를 입력한 후 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon EventBridge 규칙 삭제 시 확인 창에 `delete`를 입력해야 합니다. 규칙 이름을 입력하는 것이 아닙니다.

7. 동일한 방법으로 `TableUnavailableRule` 규칙을 선택합니다.
8. [[Delete]] 버튼을 클릭합니다.
9. 확인 창에 `delete`를 입력한 후 [[Delete]] 버튼을 클릭합니다.

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 위 [옵션 1](#option-1)을 참고합니다.

10. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
11. CloudShell이 열리면 다음 명령어를 실행합니다:

```bash
# Amazon EventBridge 규칙 삭제
EVENT_BUS_NAME="week4-3-quicktable-events-lab-ReservationEventBus"

RULES=$(aws events list-rules \
  --region ap-northeast-2 \
  --event-bus-name $EVENT_BUS_NAME \
  --query 'Rules[].Name' \
  --output text)

if [ -n "$RULES" ]; then
  for RULE in $RULES; do
    echo "삭제 중: Amazon EventBridge Rule $RULE"

    # 타겟 제거
    TARGETS=$(aws events list-targets-by-rule \
      --region ap-northeast-2 \
      --event-bus-name $EVENT_BUS_NAME \
      --rule $RULE \
      --query 'Targets[].Id' \
      --output text)

    if [ -n "$TARGETS" ]; then
      aws events remove-targets \
        --region ap-northeast-2 \
        --event-bus-name $EVENT_BUS_NAME \
        --rule $RULE \
        --ids $TARGETS
    fi

    # 규칙 삭제
    aws events delete-rule \
      --region ap-northeast-2 \
      --event-bus-name $EVENT_BUS_NAME \
      --name $RULE
  done
  echo "Amazon EventBridge Rules 삭제 완료"
else
  echo "삭제할 Amazon EventBridge Rules가 없습니다"
fi
```

> [!NOTE]
> 스크립트는 Amazon EventBridge 규칙의 타겟을 먼저 제거한 후 규칙을 삭제합니다. 삭제는 즉시 완료됩니다.

---

## 2단계: AWS CloudFormation 스택 삭제

12. AWS CloudFormation 콘솔로 이동합니다.
13. `week4-3-quicktable-events-lab-stack` 스택을 선택합니다.
14. [[Delete]] 버튼을 클릭합니다.
15. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
16. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 AWS Lambda 함수 3개, Amazon DynamoDB 테이블, Amazon EventBridge Event Bus, AWS Lambda 역할, Amazon SNS Topic 등 모든 리소스가 자동으로 삭제됩니다.

---

## 2단계: AWS CloudFormation 스택 삭제

17. AWS CloudFormation 콘솔로 이동합니다.
18. `week4-3-quicktable-events-lab-stack` 스택을 선택합니다.
19. [[Delete]] 버튼을 클릭합니다.
20. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
21. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 AWS Lambda 함수 3개, Amazon DynamoDB 테이블, Amazon EventBridge Event Bus, AWS Lambda 역할, Amazon SNS Topic 등 모든 리소스가 자동으로 삭제됩니다.

---

## 3단계: Amazon CloudWatch Log Groups 삭제

Amazon CloudWatch Log Groups는 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

### 옵션 1: AWS 콘솔에서 수동 삭제

22. Amazon CloudWatch 콘솔로 이동합니다.
23. 왼쪽 메뉴에서 **Log groups**를 선택합니다.
24. 다음 Log Group들을 찾아 삭제합니다:
	- `/aws/lambda/week4-3-quicktable-events-lab-ReservationProcessor`
	- `/aws/lambda/week4-3-quicktable-events-lab-TableAvailabilityChecker`
	- `/aws/lambda/week4-3-quicktable-events-lab-NotificationSender`
25. 각 Log Group을 선택한 후 **Actions** > `Delete log group(s)`를 선택합니다.
26. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

27. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
28. CloudShell이 열리면 다음 명령어를 실행합니다:

```bash
# Amazon CloudWatch Log Groups 삭제
LOG_GROUPS=$(aws logs describe-log-groups \
  --region ap-northeast-2 \
  --log-group-name-prefix "/aws/lambda/week4-3-quicktable-events-lab-" \
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
> AWS Lambda 함수가 3개이므로 Log Group도 3개 생성됩니다. 스크립트는 모든 Log Group을 자동으로 찾아 삭제합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon EventBridge 개발자 가이드](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/what-is-amazon-eventbridge.html)
- [이벤트 기반 아키텍처 패턴](https://aws.amazon.com/ko/event-driven-architecture/)
- [Amazon EventBridge 이벤트 패턴](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/eb-event-patterns.html)
- [AWS Lambda와 Amazon EventBridge 통합](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/with-eventbridge.html)

---

## 📚 참고: Amazon EventBridge 핵심 개념

### Amazon EventBridge 이벤트 버스 (Event Bus)

Amazon EventBridge Event Bus는 이벤트를 수신하고 라우팅하는 중앙 허브입니다. 여러 소스에서 발생한 이벤트를 수집하여 규칙에 따라 적절한 대상으로 전달합니다.

**주요 특징:**

- 이벤트 수신 및 저장
- 규칙 기반 이벤트 필터링
- 대상 서비스로 이벤트 전달
- 이벤트 재시도 및 Dead Letter Queue 지원

**이벤트 버스 유형:**

- **Default Event Bus**: AWS 서비스 이벤트 수신
- **Custom Event Bus**: 사용자 정의 애플리케이션 이벤트 수신
- **Partner Event Bus**: SaaS 파트너 이벤트 수신

### 이벤트 패턴 매칭

Amazon EventBridge는 이벤트 패턴을 사용하여 특정 이벤트만 필터링하고 대상으로 전달합니다. 이벤트 패턴은 JSON 형식으로 정의되며, 이벤트의 source, detail-type, detail 필드를 기준으로 매칭합니다.

**기본 패턴 예시:**

```json
{
  "source": ["reservation.service"],
  "detail-type": ["ReservationCreated"]
}
```

**조건부 패턴 예시:**

```json
{
  "source": ["reservation.service"],
  "detail-type": ["ReservationCreated"],
  "detail": {
    "partySize": [{ "numeric": [">=", 6] }]
  }
}
```

**패턴 매칭 규칙:**

- 모든 조건이 일치해야 이벤트가 전달됩니다
- 배열 내 하나라도 일치하면 조건 충족 (OR 연산)
- 숫자 비교 연산자 지원: `>`, `>=`, `<`, `<=`, `=`
- 문자열 패턴 매칭: `prefix`, `suffix`, `exists`

### 느슨한 결합 아키텍처 (Loose Coupling)

Amazon EventBridge를 사용하면 서비스 간 직접 의존성을 제거하고 느슨한 결합을 구현할 수 있습니다. 각 AWS Lambda 함수는 다른 함수를 직접 호출하지 않고 이벤트를 발행하기만 하면 됩니다.

**강한 결합 (기존 방식):**

```
ReservationLambda → TableCheckLambda → NotificationLambda
```

- ReservationLambda가 TableCheckLambda를 직접 호출
- TableCheckLambda가 NotificationLambda를 직접 호출
- 한 서비스 장애 시 전체 워크플로우 중단
- 새로운 서비스 추가 시 기존 코드 수정 필요

**느슨한 결합 (Amazon EventBridge 방식):**

```
ReservationLambda → Amazon EventBridge(ReservationCreated) → TableCheckLambda
                                                               ↓
                                                Amazon EventBridge(TableUnavailable)
                                                               ↓
                                                     NotificationLambda
```

- ReservationLambda는 이벤트만 발행
- Amazon EventBridge가 이벤트를 적절한 대상으로 라우팅
- TableCheckLambda가 TableUnavailable 이벤트를 발행하면 NotificationLambda가 트리거됨
- 한 서비스 장애 시 다른 서비스는 정상 동작
- 새로운 서비스 추가 시 Amazon EventBridge 규칙만 추가

**장점:**

- 서비스 독립성 향상
- 확장성 증가
- 유지보수 용이
- 테스트 간소화

### AWS Lambda와 Amazon EventBridge 통합

AWS Lambda 함수는 Amazon EventBridge와 두 가지 방식으로 통합됩니다.

**1. 이벤트 발행 (Event Publishing):**

AWS Lambda 함수에서 Amazon EventBridge에 이벤트를 발행합니다.

```python
import boto3
import json

eventbridge = boto3.client('events')

def lambda_handler(event, context):
    # 예약 처리 로직
    reservation_id = event['reservationId']

    # Amazon EventBridge에 이벤트 발행
    response = eventbridge.put_events(
        Entries=[
            {
                'Source': 'reservation.service',
                'DetailType': 'ReservationCreated',
                'Detail': json.dumps({
                    'reservationId': reservation_id,
                    'status': 'PENDING'
                }),
                'EventBusName': 'ReservationEventBus'
            }
        ]
    )

    return {'statusCode': 200, 'body': 'Reservation created'}
```

**2. 이벤트 수신 (Event Consumption):**

Amazon EventBridge 규칙이 AWS Lambda 함수를 트리거합니다.

```python
def lambda_handler(event, context):
    # Amazon EventBridge에서 전달된 이벤트
    reservation_id = event['detail']['reservationId']
    status = event['detail']['status']

    # 테이블 재고 확인 로직
    print(f"Checking table availability for reservation: {reservation_id}")

    return {'statusCode': 200, 'body': 'Table availability checked'}
```

**권한 설정:**

AWS Lambda 함수가 Amazon EventBridge에 이벤트를 발행하려면 다음 권한이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "events:PutEvents",
      "Resource": "arn:aws:events:*:*:event-bus/ReservationEventBus"
    }
  ]
}
```

Amazon EventBridge 규칙이 AWS Lambda 함수를 트리거하려면 다음 권한이 자동으로 추가됩니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:TableAvailabilityChecker"
    }
  ]
}
```

### 이벤트 기반 아키텍처 모범 사례

**1. 명확한 이벤트 이름 사용:**

- `ReservationCreated`, `TableUnavailable`, `NotificationSent`
- 과거형 사용 (이미 발생한 사실)
- 도메인 용어 사용

**2. 일관된 이벤트 구조:**

```json
{
  "source": "서비스명",
  "detail-type": "이벤트타입",
  "detail": {
    "이벤트 데이터"
  }
}
```

**3. 최소 페이로드 원칙:**

- 필요한 정보만 포함
- 민감한 정보 제외
- 참조 ID 사용 (전체 데이터 대신)

**4. 멱등성 보장:**

- 동일한 이벤트가 여러 번 처리되어도 결과가 동일
- Amazon DynamoDB Conditional Write 사용
- 이벤트 ID로 중복 처리 방지

**5. 에러 처리:**

- 재시도 정책 설정 (최대 3회, 지수 백오프)
- Dead Letter Queue 구성
- Amazon CloudWatch Logs로 실패 이벤트 추적

**6. 모니터링:**

- Amazon CloudWatch 메트릭으로 이벤트 수 추적
- AWS X-Ray로 이벤트 흐름 시각화
- 알람 설정 (실패율, 지연 시간)
