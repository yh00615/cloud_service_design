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
> - `week4-3-quicktable-events-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB 테이블, Amazon EventBridge Event Bus, AWS Lambda 함수 3개, AWS Lambda 역할, Amazon SNS Topic 자동 생성)
> - `reservation_processor.py` - 예약 생성 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
> - `table_availability_checker.py` - 테이블 재고 확인 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
> - `notification_sender.py` - 알림 발송 AWS Lambda 함수 코드 (참고용 - 태스크 0에서 AWS CloudFormation이 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week4-3-quicktable-events-lab.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon DynamoDB 테이블**: Reservations 테이블 (예약 데이터 저장), RestaurantAvailability 테이블 (레스토랑별 시간대별 예약 가능 슬롯 저장)
- **AWS Lambda 함수 3개**: ReservationProcessor, TableAvailabilityChecker, NotificationSender (이벤트 처리)
- **AWS Lambda 실행 역할**: Amazon DynamoDB, Amazon EventBridge, Amazon SNS 접근 권한
- **Amazon SNS Topic**: ReservationNotifications (알림 발송)
- **Amazon CloudWatch Logs Groups**: AWS Lambda 함수 로그 저장

> [!NOTE]
> Amazon EventBridge Event Bus와 규칙(Rules)은 AWS CloudFormation에 포함되지 않습니다. 태스크 1에서 Event Bus를 생성하고, 태스크 2-3에서 학생이 직접 이벤트 패턴을 정의하고 규칙을 생성합니다.
>
> **RestaurantAvailability 테이블 초기 데이터 및 비즈니스 로직**:
>
> AWS CloudFormation 스택은 RestaurantAvailability 테이블에 다음 초기 데이터를 자동으로 삽입합니다. timeSlot 형식은 `날짜#시간` (예: `2026-03-20#19:00`)입니다.
>
> | Restaurant ID  | 이름              | 날짜       | 시간대              | 테이블 수 | 비고               |
> | -------------- | ----------------- | ---------- | ------------------- | --------- | ------------------ |
> | restaurant-001 | 이탈리안 레스토랑 | 2026-03-20 | 18:00, 19:00, 20:00 | 각 5개    |                    |
> | restaurant-002 | 한식당            | 2026-03-20 | 18:00, 19:00, 20:00 | 각 8개    |                    |
> | restaurant-003 | 일식당            | 2026-03-20 | 18:00, 19:00, 20:00 | 각 3개    | 슬롯 부족 테스트용 |
> | restaurant-004 | 중식당            | 2026-03-20 | 18:00, 19:00, 20:00 | 각 10개   |                    |
>
> **날짜 안내**: 테스트 이벤트의 날짜는 초기 데이터와 동일한 `2026-03-20`을 사용합니다. 과거 날짜여도 동작에 문제 없습니다.
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
2. `week4-3-quicktable-events-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
    <img src="/images/week4/4-3-task0-step5-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week4-3-quicktable-events-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task0-step8-next.png" alt="CloudFormation Next 버튼 클릭" class="guide-img-md" />

9. **Stack name**에 `week4-3-quicktable-events-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 확인합니다:
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `4-3` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)
    - **EnvironmentName**: `week4-3-quicktable-events-lab` (기본값 유지)
    - **EventBusName**: `QuickTableReservationEventBus` (기본값 유지 - 태스크 1에서 생성할 Event Bus 이름)

> [!NOTE]
> EventBusName 파라미터는 태스크 1에서 생성할 Event Bus의 이름입니다. 기본값을 사용하거나 원하는 이름으로 변경할 수 있습니다. 단, 태스크 1에서 Event Bus를 생성할 때 동일한 이름을 사용해야 합니다.

11. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task0-step11-next.png" alt="Parameters 설정 후 Next" class="guide-img-md" />

12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week4/4-3-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.
18. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.
    <img src="/images/week4/4-3-task0-step18-submit.png" alt="스택 생성 진행 중" class="guide-img-md" />

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다.
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다.
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다 (Events 탭에서 원인 확인 필요)
>
> 스택 생성에 3-5분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
20. **Outputs** 탭을 선택합니다.
    <img src="/images/week4/4-3-task0-step20-outputs.png" alt="Outputs 탭 확인" class="guide-img-md" />

21. 출력값들을 확인합니다:
    - `ReservationsTableName`: Reservations 테이블 이름 (QuickTableReservations)
    - `RestaurantAvailabilityTableName`: RestaurantAvailability 테이블 이름 (QuickTableRestaurantAvailability)
    - `LambdaExecutionRoleArn`: AWS Lambda 실행 역할 ARN
    - `ReservationNotificationTopicArn`: Amazon SNS Topic ARN

> [!IMPORTANT]
> **출력값 메모**: 이 실습에서는 출력값을 직접 사용하지 않습니다. 모든 리소스는 AWS Lambda 함수 환경 변수로 자동 설정되어 있습니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon EventBridge Event Bus 생성

이 태스크에서는 QuickTable 예약 시스템의 이벤트를 라우팅할 Custom Event Bus를 생성합니다.

> [!CONCEPT] Amazon EventBridge Event Bus
> Event Bus는 이벤트를 수신하고 규칙에 따라 대상으로 라우팅하는 중앙 허브입니다. AWS는 기본적으로 Default Event Bus를 제공하지만, 애플리케이션별로 Custom Event Bus를 생성하여 이벤트를 격리하고 관리할 수 있습니다.
>
> **Event Bus 유형:**
>
> - **Default Event Bus**: AWS 서비스 이벤트 수신 (예: EC2 상태 변경, S3 객체 생성)
> - **Custom Event Bus**: 사용자 정의 애플리케이션 이벤트 수신 (이 실습에서 사용)
> - **Partner Event Bus**: SaaS 파트너 이벤트 수신

### 상세 단계

22. AWS Management Console 상단 검색창에 `EventBridge`를 입력하고 선택합니다.
23. 왼쪽 메뉴에서 **Event buses**를 선택합니다.
24. **Custom event bus** 섹션에서 [[Create event bus]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task1-step24-create-eventbus.png" alt="Create event bus 버튼 클릭" class="guide-img-md" />

25. **Event bus details** 섹션에서 다음을 입력합니다:
    - **Name**: `QuickTableReservationEventBus`

> [!IMPORTANT]
> Event Bus 이름은 태스크 0에서 AWS CloudFormation 스택 생성 시 입력한 **EventBusName** 파라미터 값과 정확히 일치해야 합니다. 기본값을 사용했다면 `QuickTableReservationEventBus`를 입력합니다.

26. **Description** (선택 사항)에 `QuickTable reservation system event bus`를 입력합니다.
27. **Encryption** 섹션은 기본값(`Use AWS owned key`)을 유지합니다.

> [!NOTE]
> AWS owned key는 AWS가 관리하는 암호화 키로, 추가 비용 없이 Event Bus 데이터를 암호화합니다. 더 강력한 보안이 필요한 경우 Customer managed key를 사용할 수 있습니다.

28. **Logs** 섹션은 비활성화 상태로 유지합니다.
    <img src="/images/week4/4-3-task1-step28-eventbus-created.png" alt="Event Bus 설정 화면" class="guide-img-md" />

29. **Archives** 섹션은 비활성화 상태로 유지합니다.
30. **Schema discovery** 섹션은 비활성화 상태로 유지합니다.

> [!NOTE]
> Schema discovery를 활성화하면 Event Bus를 통과하는 이벤트의 스키마를 자동으로 추론하여 Schema Registry에 저장합니다. 이 실습에서는 사용하지 않지만, 프로덕션 환경에서는 이벤트 구조를 문서화하는 데 유용합니다.

31. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

32. [[Create]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task1-step32-create.png" alt="Create 버튼 클릭" class="guide-img-md" />

33. Event Bus 생성이 완료되면 `QuickTableReservationEventBus` 상세 페이지로 이동합니다.
    <img src="/images/week4/4-3-task1-step33-created.png" alt="Event Bus 생성 완료" class="guide-img-md" />

✅ **태스크 완료**: Event Bus가 생성되었습니다.

## 태스크 2: ReservationCreated 이벤트 규칙 생성

이 태스크에서는 Amazon EventBridge에서 ReservationCreated 이벤트를 수신하여 TableAvailabilityChecker AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 태스크 설명

Amazon EventBridge 규칙은 이벤트 패턴을 정의하여 특정 이벤트만 필터링하고 대상 서비스로 전달합니다. 이 태스크에서는 `source=reservation.service`, `detail-type=ReservationCreated` 조건을 만족하는 이벤트만 TableAvailabilityChecker AWS Lambda 함수로 라우팅하는 규칙을 생성합니다.

### 상세 단계

> [!IMPORTANT]
> **태스크 2와 태스크 3의 차이점**: 이 두 태스크는 Amazon EventBridge 규칙 생성 과정이 거의 동일하지만, 다음 3가지만 다릅니다:
>
> 1. **규칙 이름 (Name)**: ReservationCreatedRule vs TableUnavailableRule
> 2. **이벤트 패턴 JSON**: source와 detail-type 값이 다름
> 3. **대상 AWS Lambda 함수**: TableAvailabilityChecker vs NotificationSender
>
> 나머지 단계는 모두 동일하므로 이 3가지 차이점에 집중하여 진행합니다.

34. 왼쪽 메뉴에서 **Rules**를 선택합니다.
35. **Event bus** 드롭다운에서 태스크 1에서 생성한 Event Bus(`QuickTableReservationEventBus`)를 선택합니다.
36. [[Create rule]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step36-create-rule.png" alt="Create rule 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> Enhanced builder (드래그 앤 드롭 방식)가 기본으로 표시됩니다. 이 실습에서는 **Advanced builder** (Step-by-step 방식)를 사용합니다.

37. **Builder mode**에서 `Advanced builder`를 선택합니다.
38. **Define rule detail** 페이지에서 다음을 입력합니다:
    - **Name**: `ReservationCreatedRule`
    - **Description**: `Route ReservationCreated events to TableAvailabilityChecker`
    - **Event bus**: 태스크 1에서 생성한 Event Bus 선택 (이미 선택되어 있음)

> [!NOTE]
> Custom Event Bus를 선택하면 Schedule rule은 지원되지 않으므로 Rule type 선택 없이 자동으로 이벤트 패턴 방식이 적용됩니다.

39. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step39-define-rule.png" alt="Define rule detail Next" class="guide-img-md" />

40. **Build event pattern** 페이지에서 **Event source**는 `Other`를 선택합니다.
41. **Creation method**에서 `Custom pattern (JSON editor)` 또는 `Edit pattern`을 선택합니다.

> [!NOTE]
> Amazon EventBridge 콘솔에서 이벤트 패턴을 입력하는 방법은 두 가지입니다:
>
> - **Pattern builder (GUI)**: 드롭다운으로 source, detail-type 등을 선택
> - **Custom pattern (JSON)**: JSON을 직접 입력
>
> 이 실습에서는 JSON 직접 입력 방식을 사용하므로 "Custom pattern" 또는 "Edit pattern" 옵션을 먼저 선택해야 합니다.
>
> **Amazon EventBridge 콘솔 UI 업데이트 (2025년 11월~):** Amazon EventBridge에 새로운 visual rule builder가 도입되었습니다. 새 콘솔에서는 드래그 앤 드롭 방식으로 이벤트를 선택하고 Event pattern 패널에서 JSON을 직접 편집할 수 있습니다. 기존 wizard 방식도 계속 사용 가능하며, 이 실습의 핵심인 이벤트 패턴 JSON 입력과 대상 Lambda 함수 연결 흐름은 동일합니다.

42. **Event pattern** 섹션에서 다음 JSON을 입력합니다:

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

43. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step43-event-pattern.png" alt="Event pattern 설정 후 Next" class="guide-img-md" />

44. **Select target(s)** 페이지에서 **Target types**는 `AWS service`를 선택합니다.
45. **Select a target**에서 `Lambda function`을 선택합니다.
46. **Function** 드롭다운에서 `TableAvailabilityChecker`를 선택합니다 (예: `week4-3-quicktable-events-lab-TableAvailabilityChecker`).

> [!NOTE]
> TableAvailabilityChecker AWS Lambda 함수는 태스크 0에서 AWS CloudFormation이 자동으로 생성했습니다. 함수 이름은 `week4-3-quicktable-events-lab-TableAvailabilityChecker` 형식입니다.

47. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step47-target.png" alt="Select target 설정 후 Next" class="guide-img-md" />

48. **Configure tags** 페이지에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

49. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step49-tags.png" alt="Configure tags Next" class="guide-img-md" />

50. **Review and create** 페이지에서 설정을 확인합니다.
    <img src="/images/week4/4-3-task2-step50-review.png" alt="Review and create 확인" class="guide-img-md" />

51. [[Create rule]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task2-step51-created.png" alt="Rule 생성 완료" class="guide-img-md" />

> [!NOTE]
> Amazon EventBridge 규칙이 AWS Lambda 함수를 트리거할 수 있도록 권한이 자동으로 추가됩니다.

규칙 생성 후 필요에 따라 수정하거나 삭제할 수 있습니다.

> [!TIP]
> **Amazon EventBridge 규칙 수정 및 삭제**: 생성한 규칙을 수정하거나 삭제하려면 Amazon EventBridge 콘솔의 Rules 페이지에서 규칙을 선택한 후 [[Edit]] 또는 [[Delete]] 버튼을 클릭합니다. 규칙 삭제 시 확인 창에 `delete`를 입력해야 합니다 (규칙 이름이 아님).

✅ **태스크 완료**: ReservationCreated 이벤트 규칙이 생성되었습니다.

## 태스크 3: TableUnavailable 이벤트 규칙 생성

이 태스크에서는 Amazon EventBridge에서 TableUnavailable 이벤트를 수신하여 NotificationSender AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 태스크 설명

TableAvailabilityChecker AWS Lambda 함수가 예약 가능한 슬롯이 부족하다고 판단하면 TableUnavailable 이벤트를 발행합니다. 이 이벤트를 수신하여 NotificationSender AWS Lambda 함수를 트리거하는 규칙을 생성합니다.

### 상세 단계

> [!IMPORTANT]
> **태스크 2와의 차이점**: 이 태스크는 태스크 2와 거의 동일하지만, 다음 3가지만 다릅니다:
>
> 1. **규칙 이름**: `TableUnavailableRule` (태스크 2는 ReservationCreatedRule)
> 2. **이벤트 패턴**: `source=availability.service`, `detail-type=TableUnavailable` (태스크 2는 reservation.service, ReservationCreated)
> 3. **대상 함수**: `NotificationSender` (태스크 2는 TableAvailabilityChecker)
>
> 이 3가지 차이점에 집중하여 진행합니다.

52. 왼쪽 메뉴에서 **Rules**를 선택합니다.
53. **Event bus** 드롭다운에서 태스크 1에서 생성한 Event Bus(`QuickTableReservationEventBus`)를 선택합니다.
54. [[Create rule]] 버튼을 클릭합니다.
55. **Builder mode**에서 `Advanced builder`를 선택합니다.
56. **Define rule detail** 페이지에서 다음을 입력합니다:
    - **Name**: `TableUnavailableRule`
    - **Description**: `Route TableUnavailable events to NotificationSender`
    - **Event bus**: 태스크 1에서 생성한 Event Bus 선택 (이미 선택되어 있음)
57. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task3-step57-rule2-created.png" alt="Rule 2 Define rule detail Next" class="guide-img-md" />

58. **Build event pattern** 페이지에서 **Event source**는 `Other`를 선택합니다.
59. **Creation method**에서 `Custom pattern (JSON editor)` 또는 `Edit pattern`을 선택합니다.
60. **Event pattern** 섹션에서 다음 JSON을 입력합니다:

```json
{
  "source": ["availability.service"],
  "detail-type": ["TableUnavailable"]
}
```

61. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task3-step61-event-pattern.png" alt="Event pattern 설정 후 Next" class="guide-img-md" />

62. **Select target(s)** 페이지에서 **Target types**는 `AWS service`를 선택합니다.
63. **Select a target**에서 `Lambda function`을 선택합니다.
64. **Function** 드롭다운에서 `NotificationSender`를 선택합니다 (예: `week4-3-quicktable-events-lab-NotificationSender`).
65. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task3-step65-target.png" alt="Select target 설정 후 Next" class="guide-img-md" />

66. **Configure tags** 페이지에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `4-3`     |
| `CreatedBy` | `Student` |

67. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task3-step67-created.png" alt="Tags 설정 후 Next" class="guide-img-md" />

68. **Review and create** 페이지에서 설정을 확인합니다.
    <img src="/images/week4/4-3-task3-step68-review.png" alt="Review and create 확인" class="guide-img-md" />

69. [[Create rule]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task3-step69-created.png" alt="Rule 생성 완료" class="guide-img-md" />

✅ **태스크 완료**: TableUnavailable 이벤트 규칙이 생성되었습니다.

## 태스크 4: 예약 생성 테스트 (이벤트 기반 워크플로우 확인)

이 태스크에서는 ReservationProcessor AWS Lambda 함수를 수동으로 실행하여 전체 이벤트 기반 워크플로우를 테스트합니다.

### 태스크 설명

ReservationProcessor 함수를 테스트 이벤트로 실행하면 ReservationCreated 이벤트가 발행되고, 태스크 2에서 생성한 Amazon EventBridge 규칙이 이 이벤트를 감지하여 TableAvailabilityChecker 함수를 자동으로 트리거합니다.

**이벤트 흐름**:

- ReservationProcessor → Amazon DynamoDB에 예약 저장.
- ReservationProcessor → Amazon EventBridge에 ReservationCreated 이벤트 발행.
- Amazon EventBridge → ReservationCreatedRule 규칙 매칭.
- Amazon EventBridge → TableAvailabilityChecker 함수 트리거.
- TableAvailabilityChecker → 가용성 확인.
- (불가 시) TableAvailabilityChecker → Amazon EventBridge에 TableUnavailable 이벤트 발행
- (불가 시) Amazon EventBridge → TableUnavailableRule 규칙 매칭
- (불가 시) Amazon EventBridge → NotificationSender 함수 트리거

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

70. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
71. `ReservationProcessor` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-ReservationProcessor`).

> [!NOTE]
> ReservationProcessor AWS Lambda 함수는 태스크 0에서 AWS CloudFormation이 자동으로 생성했습니다. 함수 이름은 `week4-3-quicktable-events-lab-ReservationProcessor` 형식입니다.
>
> <img src="/images/week4/4-3-task4-step71-lambda.png" alt="ReservationProcessor 함수 선택" class="guide-img-md" />

72. **Test** 탭을 선택합니다.
73. **Test event action**에서 `Create new event`를 선택합니다.
74. **Event name**에 `TestResAvailableEvent`를 입력합니다.
75. **Event JSON**에 다음 내용을 입력합니다:

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

> [!NOTE]
> restaurant-001은 19:00 시간대에 5개의 예약 가능 슬롯이 있으므로, partySize=2인 예약은 성공합니다. 테스트 이벤트의 날짜는 초기 데이터와 동일한 `2026-03-20`을 사용합니다.

76. [[Save]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-task4-step76-test.png" alt="Test 이벤트 저장" class="guide-img-md" />

77. [[Test]] 버튼을 클릭합니다.
78. 함수 실행이 완료됩니다.
79. 테스트 실행 후 "Executing function: succeeded" 메시지를 확인하고 **Details**를 확장하여 실행 결과를 확인합니다.
    <img src="/images/week4/4-3-task4-step79-result.png" alt="Executing function succeeded" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "statusCode": 200,
>   "body": "{\"message\": \"Reservation created successfully\", \"reservationId\": \"res-001\"}"
> }
> ```

80. **Monitor** 탭을 선택합니다.
    <img src="/images/week4/4-3-task4-step80-details.png" alt="Monitor 탭 선택" class="guide-img-md" />

81. **View Amazon CloudWatch Logs** 링크를 클릭합니다.
    <img src="/images/week4/4-3-task4-step81-cloudwatch.png" alt="View CloudWatch Logs 클릭" class="guide-img-md" />

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

82. 최신 로그 스트림을 선택합니다.
83. 로그에서 "ReservationCreated event published" 메시지를 확인합니다.
    <img src="/images/week4/4-3-task4-step83-log-stream.png" alt="CloudWatch 로그 확인" class="guide-img-md" />

> [!NOTE]
> 이 메시지는 ReservationProcessor 함수가 Amazon EventBridge에 이벤트를 성공적으로 발행했음을 의미합니다.

84. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
85. 검색창에 `TableAvailabilityChecker`를 입력하여 함수를 찾습니다.
86. `TableAvailabilityChecker` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-TableAvailabilityChecker`).

> [!NOTE]
> 함수 이름이 `week4-3-quicktable-events-lab-TableAvailabilityChecker`로 길기 때문에 검색창을 사용하면 쉽게 찾을 수 있습니다.
>
> **Amazon EventBridge 전달 지연**: ReservationProcessor 실행 후 Amazon EventBridge가 TableAvailabilityChecker를 트리거하기까지 수 초~1분이 소요될 수 있습니다. 로그가 보이지 않으면 1-2분 대기 후 새로고침합니다.

87. **Monitor** 탭을 선택합니다.
    <img src="/images/week4/4-3-task4-step87-test2.png" alt="TableAvailabilityChecker Monitor 탭" class="guide-img-md" />

88. **View Amazon CloudWatch Logs** 링크를 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

Amazon CloudWatch Logs 콘솔에서 로그 스트림 목록이 표시됩니다.

> [!TIP]
> **로그 스트림 식별 방법**: Amazon CloudWatch Logs 콘솔에서 로그 스트림 목록이 표시되면 **Last event time** 컬럼을 기준으로 정렬하여 가장 최근 스트림을 선택합니다. 기본적으로 최신 순으로 정렬되어 있으므로 목록 맨 위의 스트림을 선택하면 됩니다.

89. 최신 로그 스트림을 선택합니다.
90. 로그에서 "Table available: party size (2) within available slots (5)" 메시지를 확인합니다.
    <img src="/images/week4/4-3-task4-step90-log-unavailable.png" alt="TableAvailabilityChecker 로그 확인" class="guide-img-md" />

> [!NOTE]
> TableAvailabilityChecker 함수가 자동으로 실행되었다면 태스크 2에서 생성한 Amazon EventBridge 규칙이 정상적으로 동작하는 것입니다. 예약 가능한 경우 TableUnavailable 이벤트가 발행되지 않으므로 NotificationSender 함수는 실행되지 않습니다.

만약 로그가 표시되지 않는다면 다음 문제 해결 방법을 시도합니다.

> [!TROUBLESHOOTING]
> **문제**: TableAvailabilityChecker 함수의 Amazon CloudWatch Logs가 생성되지 않습니다.
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

### Amazon EventBridge 규칙 동작 확인

91. Amazon EventBridge 콘솔로 이동합니다.
92. 왼쪽 메뉴에서 **Rules**를 선택합니다.
93. **Event bus** 드롭다운에서 `QuickTableReservationEventBus`를 선택합니다.
94. `ReservationCreatedRule` 규칙을 선택합니다.
    <img src="/images/week4/4-3-task5-step94-send-event.png" alt="ReservationCreatedRule 선택" class="guide-img-md" />

95. **Monitoring** 탭을 선택합니다.
    <img src="/images/week4/4-3-task5-step95-event-sent.png" alt="Monitoring 탭 확인" class="guide-img-md" />
96. **Invocations** 메트릭에서 규칙이 트리거된 횟수를 확인합니다.

> [!NOTE]
> Invocations 메트릭이 1 이상이면 Amazon EventBridge 규칙이 정상적으로 동작한 것입니다. Amazon CloudWatch 메트릭은 1-2분의 지연이 있을 수 있으므로 메트릭이 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

### 느슨한 결합 확인

97. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
98. `ReservationProcessor` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-ReservationProcessor`).
99. **Code** 탭을 선택합니다.
    <img src="/images/week4/4-3-task5-step99-lambda-result.png" alt="Lambda Code 탭 확인" class="guide-img-md" />

100.  함수 코드에서 다른 AWS Lambda 함수를 직접 호출하는 코드가 없음을 확인합니다.

> [!TIP]
> ReservationProcessor 함수는 Amazon EventBridge에 이벤트만 발행하고, 다른 Lambda 함수를 직접 호출하지 않습니다:
>
> ```python
> # Amazon EventBridge에 ReservationCreated 이벤트 발행
> response = eventbridge.put_events(
>     Entries=[{
>         'Source': 'reservation.service',
>         'DetailType': 'ReservationCreated',
>         'Detail': json.dumps(event_detail),
>         'EventBusName': EVENT_BUS_NAME
>     }]
> )
> ```
>
> TableAvailabilityChecker나 NotificationSender를 직접 호출하는 코드가 없습니다. Amazon EventBridge 규칙이 이벤트를 라우팅하는 방식으로 느슨하게 결합되어 있습니다.

> [!CONCEPT] 느슨한 결합 (Loose Coupling)
> 이 실습에서 구현한 아키텍처는 느슨한 결합의 좋은 예시입니다:
>
> **확인 사항**:
>
> - ReservationProcessor 함수는 TableAvailabilityChecker 함수를 직접 호출하지 않습니다.
> - TableAvailabilityChecker 함수는 NotificationSender 함수를 직접 호출하지 않습니다.
> - 각 함수는 Amazon EventBridge에 이벤트를 발행하기만 하고, Amazon EventBridge가 규칙에 따라 적절한 대상 함수를 트리거합니다.
>
> **장점**:
>
> - 한 함수가 실패해도 다른 함수는 정상 동작합니다.
> - 새로운 함수를 추가할 때 기존 함수 코드를 수정할 필요가 없습니다.
> - 각 함수를 독립적으로 테스트하고 배포할 수 있습니다.
> - 함수 간 의존성이 없어 유지보수가 쉽습니다.
>
> 이것이 실습 목표 3 "AWS Lambda 함수 간 느슨한 결합을 구현할 수 있습니다"의 핵심입니다.

101. Amazon DynamoDB 콘솔로 이동합니다.
102. 왼쪽 메뉴에서 **Tables**를 선택합니다.
103. `QuickTableReservations` 테이블을 선택합니다.
     <img src="/images/week4/4-3-task5-step103-dynamodb.png" alt="DynamoDB 테이블 선택" class="guide-img-md" />

104. [[Explore table items]] 버튼을 클릭합니다.
     <img src="/images/week4/4-3-task5-step104-items.png" alt="Explore table items" class="guide-img-md" />
105. `reservationId`가 `res-001`인 항목을 확인합니다.
     <img src="/images/week4/4-3-task5-step105-reservation.png" alt="예약 데이터 확인" class="guide-img-md" />

> [!NOTE]
> Amazon DynamoDB 테이블에 예약 데이터가 저장되어 있으면 ReservationProcessor 함수가 정상적으로 동작한 것입니다.

✅ **태스크 완료**: 예약 가능 시나리오가 정상적으로 동작합니다.

## 태스크 5: 예약 불가 시나리오 테스트

이 태스크에서는 예약 가능한 슬롯이 부족한 경우를 테스트하여 TableUnavailable 이벤트와 NotificationSender 함수가 정상적으로 동작하는지 확인합니다.

### 태스크 설명

restaurant-003은 19:00 시간대에 3개의 예약 가능 슬롯만 있습니다. partySize=4인 예약을 요청하면 TableAvailabilityChecker 함수가 TableUnavailable 이벤트를 발행하고, 태스크 3에서 생성한 Amazon EventBridge 규칙이 이 이벤트를 감지하여 NotificationSender 함수를 트리거합니다.

> [!IMPORTANT]
> **비동기 처리 이해하기:**
>
> 이 실습의 아키텍처는 비동기 이벤트 기반으로 설계되었습니다. ReservationProcessor 함수는 다음 순서로 동작합니다:
>
> 1. 예약 데이터를 Amazon DynamoDB에 먼저 저장합니다.
> 2. ReservationCreated 이벤트를 Amazon EventBridge에 발행합니다.
> 3. 즉시 성공 응답(200)을 반환합니다.
>
> 이후 TableAvailabilityChecker 함수가 **비동기적으로** 가용성을 확인하고, 예약이 불가능한 경우 TableUnavailable 이벤트를 발행하여 NotificationSender 함수가 고객에게 알림을 발송합니다.
>
> 따라서 **예약이 불가능한 경우에도 ReservationProcessor 함수는 200 성공 응답을 반환합니다.** 이는 이벤트 기반 아키텍처의 특성으로, 각 함수가 독립적으로 동작하며 느슨하게 결합되어 있습니다.

> [!NOTE]
> 이 실습에서는 예약 불가 시 알림 발송까지만 구현합니다. 프로덕션 환경에서는 예약 취소/롤백 로직(예: DynamoDB 항목 삭제 또는 상태 변경)을 추가로 구현해야 합니다.

### 상세 단계

106. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
107. `ReservationProcessor` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-ReservationProcessor`).
108. **Test** 탭을 선택합니다.
109. **Test event action**에서 `Create new event`를 선택합니다.
110. **Event name**에 `TestResUnavailEvent`를 입력합니다.
111. **Event JSON**에 다음 내용을 입력합니다:

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

> [!NOTE]
> restaurant-003은 19:00 시간대에 3개의 예약 가능 슬롯만 있으므로, partySize=4인 예약은 실패합니다. 테스트 이벤트의 날짜는 초기 데이터와 동일한 `2026-03-20`을 사용합니다.

112. [[Save]] 버튼을 클릭합니다.
113. [[Test]] 버튼을 클릭합니다.
     <img src="/images/week4/4-3-task6-step113-test-unavailable.png" alt="Test 실행" class="guide-img-md" />

114. 함수 실행이 완료됩니다.
115. 테스트 실행 후 "Executing function: succeeded" 메시지를 확인하고 **Details**를 확장하여 실행 결과를 확인합니다.

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

116. **Monitor** 탭을 선택합니다.
117. **View Amazon CloudWatch Logs** 링크를 클릭합니다.
118. 최신 로그 스트림을 선택합니다.
     <img src="/images/week4/4-3-task6-step118-log-unavailable.png" alt="CloudWatch 로그 확인" class="guide-img-md" />

119. 로그에서 `Reservation saved to DynamoDB: res-002`와 `ReservationCreated event published: res-002` 메시지를 확인합니다.

> [!NOTE]
> ReservationProcessor 함수가 정상적으로 실행되었습니다. 이제 Amazon DynamoDB에 예약 데이터가 저장되었는지 확인합니다.

120. Amazon DynamoDB 콘솔로 이동합니다.
121. 왼쪽 메뉴에서 **Tables**를 선택합니다.
122. `QuickTableReservations` 테이블을 선택합니다.
123. [[Explore table items]] 버튼을 클릭합니다.
     <img src="/images/week4/4-3-task6-step123-dynamodb-items.png" alt="DynamoDB 예약 데이터 확인" class="guide-img-md" />

124. `reservationId`가 `res-002`인 항목을 확인합니다.

> [!NOTE]
> Amazon DynamoDB 테이블에 예약 데이터가 저장되어 있으면 ReservationProcessor 함수가 정상적으로 동작한 것입니다. 예약 불가 시나리오에서도 예약 데이터는 먼저 저장되고, 이후 TableAvailabilityChecker가 비동기적으로 가용성을 확인합니다.

125. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
126. `TableAvailabilityChecker` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-TableAvailabilityChecker`).
127. **Monitor** 탭을 선택합니다.
128. **View Amazon CloudWatch Logs** 링크를 클릭합니다.
129. 최신 로그 스트림을 선택합니다.
     <img src="/images/week4/4-3-task6-step129-notification.png" alt="TableUnavailable 로그 확인" class="guide-img-md" />

130. 로그에서 "Table unavailable: party size (4) exceeds available slots (3)" 메시지를 확인합니다.
131. 로그에서 "TableUnavailable event published" 메시지를 확인합니다.

> [!NOTE]
> TableAvailabilityChecker 함수가 예약 불가를 판단하고 TableUnavailable 이벤트를 발행했습니다.

132. AWS Lambda 콘솔의 **Functions** 탭으로 이동합니다.
133. `NotificationSender` 함수를 선택합니다 (예: `week4-3-quicktable-events-lab-NotificationSender`).
     <img src="/images/week4/4-3-task6-step133-notification-sender.png" alt="NotificationSender 함수 선택" class="guide-img-md" />

134. **Monitor** 탭을 선택합니다.
135. **View Amazon CloudWatch Logs** 링크를 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Logs는 1-2분의 지연이 있을 수 있습니다. 로그가 표시되지 않으면 1-2분 대기 후 페이지를 새로고침합니다.

136. 최신 로그 스트림을 선택합니다.
     <img src="/images/week4/4-3-task6-step136-notification-log.png" alt="NotificationSender 로그 확인" class="guide-img-md" />

137. 로그에서 "Sending notification for reservation: res-002" 메시지를 확인합니다.
138. 로그에서 "Notification sent" 메시지를 확인합니다.

> [!NOTE]
> NotificationSender 함수가 자동으로 실행되었다면 태스크 3에서 생성한 Amazon EventBridge 규칙이 정상적으로 동작하는 것입니다.
>
> 이 실습에서는 Amazon SNS 이메일 구독을 설정하지 않으므로 실제 이메일은 수신되지 않습니다. 알림 발송 여부는 NotificationSender 함수의 Amazon CloudWatch 로그로 확인합니다.

### Amazon EventBridge 규칙 동작 확인

139. Amazon EventBridge 콘솔로 이동합니다.
140. 왼쪽 메뉴에서 **Rules**를 선택합니다.
141. **Event bus** 드롭다운에서 `QuickTableReservationEventBus`를 선택합니다.
142. `ReservationCreatedRule` 규칙을 선택합니다.
143. **Monitoring** 탭을 선택합니다.
     <img src="/images/week4/4-3-task7-step143-invocations.png" alt="ReservationCreatedRule Invocations 확인" class="guide-img-md" />

144. **Invocations** 그래프에서 규칙이 실행된 횟수를 확인합니다.

> [!NOTE]
> 태스크 4와 태스크 5에서 각각 1번씩 ReservationCreated 이벤트를 발행했으므로, Invocations 그래프에 2개의 데이터 포인트가 표시되어야 합니다. 그래프 데이터는 1-2분의 지연이 있을 수 있으므로, 표시되지 않으면 페이지를 새로고침합니다.

145. Amazon EventBridge 콘솔로 이동합니다.
146. 왼쪽 메뉴에서 **Rules**를 선택합니다.
147. **Event bus** 드롭다운에서 `QuickTableReservationEventBus`를 선택합니다.
148. `TableUnavailableRule` 규칙을 선택합니다.
149. **Monitoring** 탭을 선택합니다.
     <img src="/images/week4/4-3-task7-step149-invocations2.png" alt="TableUnavailableRule Invocations 확인" class="guide-img-md" />

150. **Invocations** 그래프에서 규칙이 실행된 횟수를 확인합니다.

> [!NOTE]
> 태스크 5에서만 TableUnavailable 이벤트가 발행되었으므로, Invocations 그래프에 1개의 데이터 포인트가 표시되어야 합니다.

Monitoring 탭에서는 규칙의 실행 통계를 확인할 수 있습니다.

> [!TIP]
> **Amazon EventBridge Monitoring 탭 활용**: Monitoring 탭에서는 규칙이 매칭한 이벤트 수, 대상 함수 호출 성공/실패 횟수, 평균 지연 시간 등을 확인할 수 있습니다. 이벤트 기반 아키텍처를 운영할 때 규칙이 정상적으로 동작하는지 모니터링하는 데 유용합니다.

✅ **태스크 완료**: 예약 불가 시나리오가 정상적으로 동작합니다.

다음을 성공적으로 수행했습니다:

- Amazon EventBridge 규칙을 생성하여 이벤트 기반 아키텍처를 구축했습니다.
- ReservationCreated 이벤트 규칙을 생성하고 이벤트 패턴을 정의했습니다.
- TableUnavailable 이벤트 규칙을 생성하고 타겟을 연결했습니다.
- 이벤트 기반 워크플로우를 테스트하여 느슨한 결합을 확인했습니다.
- AWS Lambda 함수 간 직접 호출 없이 이벤트를 통한 통신을 구현했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

---

### 단계 1: 생성된 리소스 확인 (Tag Editor)

실습에서 생성한 모든 리소스를 확인합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `All regions`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `4-3`
6. [[Search resources]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 **찾는 용도**로만 사용됩니다.
> 실제 삭제는 2단계에서 수행합니다.
> Amazon EventBridge 규칙과 Event Bus는 Tag Editor에서 검색되지 않을 수 있으므로, 아래 단계에서 직접 삭제합니다.

---

### 단계 2: Amazon EventBridge 리소스 삭제

수동으로 생성한 Amazon EventBridge 규칙과 Event Bus를 먼저 삭제합니다. 이 리소스들은 AWS CloudFormation 스택에 포함되지 않으므로 별도로 삭제해야 합니다.

다음 두 가지 방법 중 하나를 선택하여 리소스를 삭제할 수 있습니다.

### 옵션 1: AWS 콘솔에서 수동 삭제 (권장)

> [!TIP]
> AWS 관리 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 권장합니다.
>
> AWS CLI 명령어에 익숙한 경우 아래 [옵션 2](#option-2)를 사용하면 더 빠르게 삭제할 수 있습니다.

**Amazon EventBridge 규칙 삭제**

8. Amazon EventBridge 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Rules**를 선택합니다.
10. **Event bus** 드롭다운에서 `QuickTableReservationEventBus`를 선택합니다.
11. `ReservationCreatedRule` 규칙을 선택합니다.
12. [[Delete]] 버튼을 클릭합니다.
13. 확인 창에 `delete`를 입력한 후 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-cleanup-step13-delete-rule.png" alt="규칙 삭제 확인" class="guide-img-md" />

> [!NOTE]
> Amazon EventBridge 규칙 삭제 시 확인 창에 `delete`를 입력해야 합니다. 규칙 이름을 입력하는 것이 아닙니다.

14. 동일한 방법으로 `TableUnavailableRule` 규칙을 선택합니다.
15. [[Delete]] 버튼을 클릭합니다.
16. 확인 창에 `delete`를 입력한 후 [[Delete]] 버튼을 클릭합니다.

**Amazon EventBridge Event Bus 삭제**

> [!NOTE]
> Event Bus는 학생이 태스크 1에서 직접 생성한 리소스이므로 AWS CloudFormation 스택 삭제로는 삭제되지 않습니다. 규칙을 모두 삭제한 후 Event Bus를 삭제해야 합니다.

17. 왼쪽 메뉴에서 **Event buses**를 선택합니다.
18. **Custom event bus** 섹션에서 `QuickTableReservationEventBus`를 선택합니다.
19. [[Delete]] 버튼을 클릭합니다.
20. 확인 창에 Event Bus 이름 `QuickTableReservationEventBus`를 입력한 후 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-cleanup-step20-delete-eventbus.png" alt="Event Bus 삭제 확인" class="guide-img-md" />

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 위 [옵션 1](#option-1)을 참고합니다.

21. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
22. Amazon EventBridge 규칙의 타겟을 제거하고 규칙을 삭제합니다:

```bash
EVENT_BUS_NAME="QuickTableReservationEventBus"

RULES=$(aws events list-rules \
  --region ap-northeast-2 \
  --event-bus-name $EVENT_BUS_NAME \
  --query 'Rules[].Name' \
  --output text)

for RULE in $RULES; do
  TARGETS=$(aws events list-targets-by-rule \
    --region ap-northeast-2 \
    --event-bus-name $EVENT_BUS_NAME \
    --rule $RULE \
    --query 'Targets[].Id' \
    --output text)

  aws events remove-targets \
    --region ap-northeast-2 \
    --event-bus-name $EVENT_BUS_NAME \
    --rule $RULE \
    --ids $TARGETS

  aws events delete-rule \
    --region ap-northeast-2 \
    --event-bus-name $EVENT_BUS_NAME \
    --name $RULE
done
```

<img src="/images/week4/4-3-cleanup-step22-cli-rules.png" alt="CLI 규칙 삭제 실행" class="guide-img-md" />

> [!TIP] CLI로 규칙 삭제 확인
>
> ```bash
> aws events list-rules --region ap-northeast-2 --event-bus-name QuickTableReservationEventBus --query 'Rules[].Name' --output text
> ```
>
> 결과가 비어있으면 규칙 삭제 완료입니다.

23. Event Bus를 삭제합니다:

```bash
aws events delete-event-bus \
  --region ap-northeast-2 \
  --name QuickTableReservationEventBus
```

<img src="/images/week4/4-3-cleanup-step23-cli-eventbus.png" alt="CLI Event Bus 삭제 실행" class="guide-img-lg" />

> [!TIP] CLI로 삭제 확인
>
> ```bash
> aws events list-rules --region ap-northeast-2 --event-bus-name QuickTableReservationEventBus 2>&1 | grep -q "ResourceNotFoundException" && echo "삭제 완료" || echo "삭제 진행 중"
> ```

---

### 단계 3: AWS CloudFormation 스택 삭제

24. AWS CloudFormation 콘솔로 이동합니다.
25. `week4-3-quicktable-events-lab-stack` 스택을 선택합니다.
26. [[Delete stack]] 버튼을 클릭합니다.
27. 확인 창에서 스택 이름 `week4-3-quicktable-events-lab-stack`을 입력합니다.
28. [[Delete stack]] 버튼을 클릭하여 삭제를 확인합니다.
    <img src="/images/week4/4-3-cleanup-step28-delete-stack.png" alt="Delete stack 확인" class="guide-img-md" />

29. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 AWS Lambda 함수 3개, Amazon DynamoDB 테이블 2개, AWS Lambda 역할, Amazon SNS Topic 등이 자동으로 삭제됩니다. Amazon CloudWatch Log Groups는 스택에 포함되어 있어 함께 삭제되지만, 실습 중 추가 생성된 Log Groups가 남아있을 수 있으므로 4단계에서 확인합니다.

---

### 단계 4: Amazon CloudWatch Log Groups 삭제

이 실습에서는 AWS CloudFormation 템플릿에 Amazon CloudWatch Log Groups가 포함되어 있어 스택 삭제 시 자동으로 삭제됩니다. 하지만 스택 삭제 전에 AWS Lambda 함수가 실행되면서 추가 Log Groups가 생성될 수 있으므로, 다음 단계로 확인하고 남아있는 Log Groups를 삭제합니다.

### 옵션 1: AWS 콘솔에서 수동 삭제

30. Amazon CloudWatch 콘솔로 이동합니다.
31. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
32. 다음 Log Group들을 찾아 삭제합니다:
    - `/aws/lambda/week4-3-quicktable-events-lab-ReservationProcessor`
    - `/aws/lambda/week4-3-quicktable-events-lab-TableAvailabilityChecker`
    - `/aws/lambda/week4-3-quicktable-events-lab-NotificationSender`
    - `/aws/lambda/week4-3-quicktable-events-lab-InitializeAvailability`
33. 각 Log Group을 선택한 후 **Actions** > `Delete log group(s)`를 선택합니다.
    <img src="/images/week4/4-3-cleanup-step33-delete-loggroup.png" alt="Delete log group 선택" class="guide-img-md" />

34. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-cleanup-step34-delete-confirm.png" alt="Log Group 삭제 확인" class="guide-img-sm" />

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

35. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
36. Amazon CloudWatch Log Groups를 삭제합니다:

```bash
LOG_GROUPS=$(aws logs describe-log-groups \
  --region ap-northeast-2 \
  --log-group-name-prefix "/aws/lambda/week4-3-quicktable-events-lab-" \
  --query 'logGroups[].logGroupName' \
  --output text)

for LOG_GROUP in $LOG_GROUPS; do
  aws logs delete-log-group \
    --region ap-northeast-2 \
    --log-group-name $LOG_GROUP
done
```

<img src="/images/week4/4-3-cleanup-step36-cli-loggroups.png" alt="CLI Log Groups 삭제 실행" class="guide-img-lg" />

> [!TIP] CLI로 삭제 확인
>
> ```bash
> aws logs describe-log-groups --region ap-northeast-2 --log-group-name-prefix "/aws/lambda/week4-3-quicktable-events-lab-" --query 'logGroups[].logGroupName' --output text
> ```
>
> 결과가 비어있으면 삭제 완료입니다.

---

### 단계 5: 삭제 확인

모든 리소스가 삭제되었는지 확인합니다.

37. Tag Editor로 이동합니다.
38. **Regions**에서 `All regions`를 선택합니다.
39. **Resource types**에서 `All supported resource types`를 선택합니다.
40. **Tags** 섹션에서 다음 태그를 입력합니다:
    - **Tag key**: `Week`
    - **Optional tag value**: `4-3`
41. [[Search resources]] 버튼을 클릭합니다.
    <img src="/images/week4/4-3-cleanup-step41-tageditor-final.png" alt="Tag Editor 최종 확인" class="guide-img-md" />

42. 검색 결과가 비어있는지 확인합니다.

> [!NOTE]
> 리소스가 삭제되면 태그도 함께 제거되므로 Tag Editor에서 검색 결과가 비어있으면 정상적으로 삭제된 것입니다.
> 스택 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.
> Amazon EventBridge 규칙과 Event Bus는 Tag Editor에서 검색되지 않을 수 있으므로, Amazon EventBridge 콘솔에서 직접 삭제 여부를 확인합니다.

> [!SUCCESS]
> 검색 결과가 비어있으면 모든 리소스가 정상적으로 삭제되었습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 6: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

43. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
44. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
45. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
46. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
47. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [Amazon EventBridge 개발자 가이드](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/what-is-amazon-eventbridge.html)
- [이벤트 기반 아키텍처 패턴](https://aws.amazon.com/ko/event-driven-architecture/)
- [Amazon EventBridge 이벤트 패턴](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/eb-event-patterns.html)
- [Amazon EventBridge 대상으로 AWS Lambda 사용](https://docs.aws.amazon.com/ko_kr/eventbridge/latest/userguide/eb-targets.html)

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

- 모든 조건이 일치해야 이벤트가 전달됩니다.
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
