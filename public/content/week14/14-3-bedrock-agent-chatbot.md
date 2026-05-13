---
title: 'Amazon Bedrock Agents 기반 고객 지원 챗봇'
week: 14
session: 3
awsServices:
  - Amazon Bedrock
learningObjectives:
  - Amazon Bedrock Agents의 자율 에이전트 아키텍처와 ReAct 프롬프팅을 이해할 수 있습니다.
  - AWS Lambda 함수로 Action Group을 생성하고 에이전트와 연결할 수 있습니다.
  - Amazon Bedrock Knowledge Base를 에이전트에 연결하여 RAG 기능을 통합할 수 있습니다.
  - 에이전트를 테스트하고 다단계 작업을 수행할 수 있습니다.

prerequisites:
  - AWS 계정 및 관리자 권한
  - AWS Lambda 함수 기본 지식
  - JSON 데이터 구조 이해
  - 생성형 AI 기본 개념 이해
---

> [!IMPORTANT]
> **리전 설정 필수**: 이 실습은 **Week 14-2와 동일한 리전**에서 진행합니다.
>
> - **권장 리전**: Asia Pacific (Seoul) ap-northeast-2
> - Week 14-2에서 생성한 Knowledge Base를 연결하려면 같은 리전을 사용해야 합니다.
> - Amazon Bedrock Agent는 모든 모델이 지원되는 리전에서 사용합니다.

이 실습에서는 Amazon Bedrock Agent를 사용하여 QuickTable 레스토랑 예약 시스템의 지능형 챗봇을 구축합니다. 고객이 자연어로 대화하며 예약을 관리할 수 있는 AI 어시스턴트를 완성합니다. AWS Lambda 함수를 Action Group으로 연결하여 예약 조회, 생성, 취소 등의 실제 작업을 수행하고, Week 14-2에서 생성한 Knowledge Base를 통합하여 레스토랑 정보 질문에도 답변할 수 있도록 합니다. 대화형 AI의 핵심 개념과 프롬프트 엔지니어링 기법을 학습합니다.

> [!CONCEPT] Amazon Bedrock Agent 아키텍처
> Amazon Bedrock Agent는 자연어 요청을 이해하고 자율적으로 작업을 수행하는 AI 에이전트입니다.
>
> - **ReAct 프롬프팅**: Reasoning(추론) + Acting(행동)을 반복하여 복잡한 작업을 단계별로 수행합니다.
> - **Action Group**: AWS Lambda 함수와 연결하여 실제 작업(예약 조회, 생성, 취소)을 수행합니다.
> - **Knowledge Base**: RAG(Retrieval-Augmented Generation)를 통해 외부 문서 기반으로 답변합니다.
> - **에이전트 흐름**: 사용자 요청 → 의도 파악 → Action Group 호출 또는 Knowledge Base 검색 → 응답 생성.

> [!DOWNLOAD]
> [week14-3-bedrock-agent-lab.zip](/files/week14/week14-3-bedrock-agent-lab.zip)
>
> - `week14-3-bedrock-agent-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB 테이블, AWS Lambda 함수, AWS IAM 역할, 샘플 데이터 자동 생성).
> - `bedrock_agent_lambda.py` - Amazon Bedrock Agent 예약 관리 AWS Lambda 함수 (상세한 주석 및 DocString 포함, 참고용).
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿으로 Amazon DynamoDB, AWS Lambda, AWS IAM 역할, 샘플 데이터 자동 생성).
> - 태스크 1: 생성된 리소스 확인 (Amazon DynamoDB 테이블, AWS Lambda 함수 코드 확인).

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 Amazon Bedrock Agent에 필요한 기반 리소스를 자동으로 생성합니다. Amazon DynamoDB 테이블, AWS Lambda 함수, AWS IAM 역할, 샘플 예약 데이터가 자동으로 구성됩니다.

1. 다운로드한 `week14-3-bedrock-agent-lab.zip` 파일의 압축을 해제합니다.
2. `week14-3-bedrock-agent-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week14-3-bedrock-agent-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
   <img src="/images/week14/14-3-task0-step8-next.png" alt="Next 버튼 클릭" class="guide-img-md" />

9. **Stack name**에 `week14-3-bedrock-agent-stack`을 입력합니다.
10. **Parameters** 섹션에서 다음을 확인합니다:
    - **StudentId**: 본인의 학번 또는 고유 식별자를 입력합니다 (예: `20240001` 또는 `student01`)
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `14-3` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)

> [!WARNING]
> **StudentId는 반드시 본인의 학번으로 변경하세요.** 기본값(`20240001`)을 그대로 사용하면 다른 학생과 리소스 이름이 충돌할 수 있습니다.

11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task0-step11-next.png" alt="Next 버튼 클릭" class="guide-img-md" />

12. **Configure stack options** 페이지에서 아래로 스크롤합니다.
13. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources with custom names`를 선택합니다.
14. [[Submit]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task0-step14-capabilities.png" alt="Capabilities 체크 후 Submit" class="guide-img-md" />

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.  
> **Events** 탭에서 생성 과정을 확인할 수 있습니다.

15. **Outputs** 탭을 선택합니다.

    <img src="/images/week14/14-3-task0-step15.png" alt="Outputs 탭 선택" class="guide-img-md" />

16. 출력값들을 확인하고 메모장에 복사합니다:
    - `ReservationsTableName`: Amazon DynamoDB 테이블 이름
    - `ReservationHandlerFunctionName`: AWS Lambda 함수 이름 (Agent Action Group에서 사용)
    - `ReservationHandlerFunctionArn`: AWS Lambda 함수 ARN

✅ **태스크 완료**: AWS CloudFormation으로 실습 환경이 구축되었습니다.

## 태스크 1: 생성된 리소스 확인

이 태스크에서는 AWS CloudFormation이 생성한 리소스를 확인합니다. Amazon DynamoDB 테이블의 샘플 데이터와 AWS Lambda 함수 코드를 검토합니다.

### 태스크 1.1: Amazon DynamoDB 테이블 확인

17. 상단 검색창에 `DynamoDB`를 입력하고 선택합니다.
18. 왼쪽 메뉴에서 **Tables**를 선택합니다.
19. `RestaurantReservations` 테이블을 클릭합니다.
20. **Explore table items** 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task1-step20.png" alt="Explore table items" class="guide-img-md" />

21. 샘플 예약 데이터 3건이 자동으로 생성되었는지 확인합니다:
    - `RES001` - Kim Cheolsu (2026-02-15, 19:00, 4명)
    - `RES002` - Lee Younghee (2026-02-16, 18:30, 2명)
    - `RES003` - Park Minsu (2026-02-17, 20:00, 6명)

    <img src="/images/week14/14-3-task1-step21.png" alt="샘플 예약 데이터 3건 확인" class="guide-img-md" />

### 태스크 1.2: AWS Lambda 함수 확인

22. 상단 검색창에 `Lambda`를 입력하고 선택합니다.
23. `BedrockAgentReservationHandler` 함수를 클릭합니다.
24. **Code** 탭에서 함수 코드를 확인합니다.

    <img src="/images/week14/14-3-task1-step24.png" alt="Lambda 함수 코드 확인" class="guide-img-md" />

> [!NOTE]
> AWS Lambda 함수는 다음 4가지 기능을 제공합니다:
>
> - `get_reservation`: 예약 번호로 예약 정보 조회.
> - `create_reservation`: 새로운 예약 생성.
> - `list_reservations`: 예약 목록 조회 (날짜 필터 가능).
> - `cancel_reservation`: 예약 취소 (상태를 cancelled로 변경).
>
> 다운로드한 `bedrock_agent_lambda.py` 파일에 상세한 주석과 DocString이 포함되어 있으니 참고합니다.

25. **Configuration** 탭 > **Environment variables**에서 `TABLE_NAME`이 `RestaurantReservations`로 설정되어 있는지 확인합니다.

    <img src="/images/week14/14-3-task1-step25.png" alt="Environment variables 확인" class="guide-img-md" />

26. **Configuration** 탭 > **Permissions**에서 **Execution role** 섹션의 역할 이름 링크를 클릭하여 AWS IAM 콘솔로 이동합니다.

    <img src="/images/week14/14-3-task1-step26.png" alt="Permissions에서 역할 이름 클릭" class="guide-img-md" />

27. **Permissions policies** 섹션에서 `DynamoDBAccess` 인라인 정책이 포함되어 있는지 확인합니다.

    <img src="/images/week14/14-3-task1-step27.png" alt="DynamoDBAccess 인라인 정책 확인" class="guide-img-md" />

✅ **태스크 완료**: 생성된 리소스를 확인했습니다. Amazon DynamoDB 테이블에 샘플 데이터가 있고, AWS Lambda 함수가 예약 관리 기능을 제공합니다.

## 태스크 2: QuickTable Amazon Bedrock Agent 생성

이 태스크에서는 QuickTable 챗봇의 핵심인 Amazon Bedrock Agent를 생성합니다.

> [!NOTE]
> Amazon Bedrock에서는 모든 서버리스 Foundation Model에 대한 액세스가 자동으로 활성화되어 있습니다.  
> Anthropic Claude 모델은 처음 사용 시 일회성 **Use case details** 양식 제출이 필요하지만, 14-1 실습에서 이미 완료한 경우 추가 제출 없이 바로 사용할 수 있습니다.

28. Amazon Bedrock 콘솔로 이동합니다.
29. 왼쪽 메뉴에서 **Build** > **Agents**를 선택합니다.
30. [[Create Agent]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task2-step30.png" alt="Create Agent 버튼 클릭" class="guide-img-md" />

31. **Agent name**에 `QuickTableAssistant`를 입력합니다.
32. **Agent description**에 `QuickTable 레스토랑 예약을 관리하는 AI 어시스턴트`를 입력합니다.
33. [[Create]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task2-step33.png" alt="Agent 생성 - Create 클릭" class="guide-img-sm" />

> [!NOTE]
> Agent가 생성되고 Agent builder 페이지로 자동 이동합니다.

> [!TIP]
> Agent builder에 다시 접근하려면: Amazon Bedrock 콘솔 > **Build** > **Agents** > `QuickTableAssistant` 클릭 > [[Edit in Agent Builder]] 버튼을 클릭합니다.

34. **Agent resource role**을 `Create and use a new service role`로 선택합니다.
35. **Select model**을 클릭하고, **Bedrock Agents optimized** 체크박스를 **해제**한 후 **Anthropic** 카테고리에서 `Claude Sonnet 4.6`을 선택합니다.
36. **Inference**에서 `On-demand`를 선택하고 [[Apply]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task2-step36.png" alt="모델 선택 및 Apply" class="guide-img-md" />

> [!IMPORTANT]
> **Bedrock Agents optimized** 체크가 기본 활성화되어 있습니다. 체크 상태에서 표시되는 모델(Claude 3.5 Sonnet 등)은 AWS Marketplace 구독이 필요하여 권한 오류가 발생할 수 있습니다.  
> **반드시 체크를 해제**하고 Claude 4.x 모델을 선택하세요. 이 모델들은 별도 구독 없이 바로 사용 가능합니다.

> [!NOTE]
> **권장 모델 (Bedrock Agents optimized 해제 시)**:
>
> - **Claude Sonnet 4.6**: 성능과 비용의 균형 (권장).
> - **Claude Haiku 4.5**: 빠른 응답 속도, 저렴한 비용.
>
> ⚠️ 모델 목록은 지속적으로 업데이트됩니다. 위 정보는 2026년 5월 기준이며, 최신 모델은 [Claude 모델 개요](https://docs.anthropic.com/en/docs/about-claude/models/overview)를 참고합니다.

37. **Instructions for the Agent** 섹션에 다음 프롬프트를 입력합니다:

```
당신은 QuickTable 레스토랑 예약 시스템을 관리하는 친절한 AI 어시스턴트입니다.

주요 역할:
- 고객의 예약 요청을 받아 새로운 예약을 생성합니다.
- 예약 번호로 기존 예약을 조회합니다.
- 특정 날짜의 예약 목록을 확인합니다.
- 예약 취소 요청을 처리합니다.

대화 규칙:
- 항상 정중하고 친절하게 응답합니다.
- 예약 생성 시 고객 이름, 날짜, 시간, 인원수를 반드시 확인합니다.
- 날짜는 YYYY-MM-DD 형식으로 저장합니다.
- 시간은 HH:MM 형식(24시간)으로 저장합니다.
- 예약이 완료되면 예약 번호를 안내합니다.
- 정보가 부족하면 고객에게 추가 정보를 요청합니다.

응답 스타일:
- 간결하고 명확하게 답변합니다.
- 이모지를 적절히 사용하여 친근감을 표현합니다.
- 예약 정보는 구조화된 형식으로 제공합니다.
```

<img src="/images/week14/14-3-task2-step37.png" alt="Instructions for the Agent 입력" class="guide-img-md" />

38. 상단의 [[Save]] 버튼을 클릭합니다.

> [!IMPORTANT]
> 모델 선택과 Instructions 입력 후 반드시 [[Save]]를 클릭하여 저장합니다. 저장하지 않고 다른 화면으로 이동하면 설정이 초기화될 수 있습니다.

39. 아래로 스크롤하여 **Action groups** 섹션에서 [[Add]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task2-step39.png" alt="Action groups Add 버튼 클릭" class="guide-img-md" />

40. **Action group details**에서 다음을 입력합니다:
    - **Action group name**: `QuickTableReservationActions`
    - **Action group description**: `QuickTable 예약 관리 기능`
41. **Action group type**에서 `Define with function details`를 선택합니다.

    <img src="/images/week14/14-3-task2-step41.png" alt="Action group type 선택" class="guide-img-md" />

> [!NOTE]
> AWS 콘솔 UI는 지속적으로 업데이트됩니다.  
> "Define with function details" 옵션이 보이지 않는 경우:
>
> - "Define with API schemas" 대신 사용 가능한 옵션을 선택합니다.
> - 또는 OpenAPI 스키마 파일을 업로드하는 방식을 사용할 수 있습니다 (참고 섹션 참조).

42. **Action group invocation** 섹션에서 **Select how to define the Lambda function**을 `Select an existing Lambda function`으로 선택합니다.
43. **Select Lambda function** 드롭다운에서 `BedrockAgentReservationHandler`를 선택합니다.

    <img src="/images/week14/14-3-task2-step43.png" alt="Lambda 함수 선택" class="guide-img-md" />

> [!NOTE]
> AWS Lambda 함수를 선택하면 Amazon Bedrock Agent가 AWS Lambda를 호출할 수 있도록 리소스 기반 정책이 자동으로 추가됩니다.  
> 자동 추가가 실패하는 경우, AWS Lambda 콘솔의 Configuration > Permissions > Resource-based policy statements에서 수동으로 추가해야 합니다.  
> 참고 섹션에서 리소스 기반 정책 예시를 확인할 수 있습니다.

44. **Action group function 1** 섹션에서 다음을 입력합니다:

**함수 1: get_reservation**

- **Name**: `get_reservation`
- **Description**: `예약 번호로 예약 정보를 조회합니다`
- **Enable confirmation of action group function**: `Disabled` (기본값 유지)
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

> [!TIP]
> 파라미터 추가 후 각 셀(Name, Description, Type, Required)의 연필(✏️) 아이콘을 클릭하여 값을 편집합니다.  
> Required는 `True`로 변경하면 필수 파라미터가 됩니다.

| Parameter Name  | Type   | Required | Description              |
| --------------- | ------ | -------- | ------------------------ |
| `reservationId` | string | ✅ 필수  | `예약 번호 (예: RES001)` |

<img src="/images/week14/14-3-task2-step44.png" alt="get_reservation 함수 설정" class="guide-img-md" />

45. [[Add action group function]] 버튼을 클릭하여 두 번째 함수를 추가합니다:

**함수 2: create_reservation**

- **Function name**: `create_reservation`
- **Function description**: `새로운 예약을 생성합니다`
- **Enable confirmation of action group function**: `Disabled` (기본값 유지)
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터들을 하나씩 추가합니다:

| Parameter Name | Type    | Required | Description                      |
| -------------- | ------- | -------- | -------------------------------- |
| `customerName` | string  | ✅ 필수  | `고객 이름`                      |
| `date`         | string  | ✅ 필수  | `예약 날짜 (YYYY-MM-DD 형식)`    |
| `time`         | string  | ✅ 필수  | `예약 시간 (HH:MM 형식, 24시간)` |
| `partySize`    | integer | ✅ 필수  | `예약 인원수`                    |

<img src="/images/week14/14-3-task2-step45.png" alt="create_reservation 함수 설정" class="guide-img-md" />

46. [[Add action group function]] 버튼을 클릭하여 세 번째 함수를 추가합니다:

**함수 3: list_reservations**

- **Function name**: `list_reservations`
- **Function description**: `예약 목록을 조회합니다`
- **Enable confirmation of action group function**: `Disabled` (기본값 유지)
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

| Parameter Name | Type   | Required | Description                                                     |
| -------------- | ------ | -------- | --------------------------------------------------------------- |
| `date`         | string | ❌ 선택  | `조회할 날짜 (YYYY-MM-DD 형식, 지정하지 않으면 모든 예약 조회)` |

<img src="/images/week14/14-3-task2-step46.png" alt="list_reservations 함수 설정" class="guide-img-md" />

47. [[Add action group function]] 버튼을 클릭하여 네 번째 함수를 추가합니다:

**함수 4: cancel_reservation**

- **Function name**: `cancel_reservation`
- **Function description**: `예약을 취소합니다`
- **Enable confirmation of action group function**: `Disabled` (기본값 유지)
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

| Parameter Name  | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `reservationId` | string | ✅ 필수  | `취소할 예약 번호 (예: RES001)` |

<img src="/images/week14/14-3-task2-step47.png" alt="cancel_reservation 함수 설정" class="guide-img-md" />

48. 모든 함수 추가가 완료되면 [[Create]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task2-step48-create.png" alt="Action group Create 버튼 클릭" class="guide-img-md" />

49. Action group이 추가되었는지 확인합니다.

> [!NOTE]
> Action group 생성 후 Agent builder 페이지로 이동합니다.

50. **Knowledge bases** 섹션에서 [[Add]] 버튼을 클릭합니다 (Week 14-2 완료 시).

    <img src="/images/week14/14-3-task2-step50-kb-add.png" alt="Knowledge bases 섹션 Add 버튼" class="guide-img-md" />

> [!IMPORTANT]
> 이 단계는 Week 14-2를 완료한 경우에만 수행합니다.  
> Week 14-2에서 생성한 Knowledge Base를 연결하여 레스토랑 정보 질문에 답변할 수 있도록 합니다.  
> 14-2 실습을 완료하지 않았다면 이 단계(50-54)를 건너뛰고 55번으로 이동합니다.

51. **Select knowledge base**에서 `quicktable-restaurant-kb`를 선택합니다 (14-2에서 생성).
52. **Knowledge base instructions for Agent**에 다음을 입력합니다:

```
이 Knowledge Base는 QuickTable 레스토랑의 메뉴, 가격, 영업 시간, 위치, FAQ 정보를 포함합니다.
고객이 메뉴, 가격, 영업 시간, 위치, 주차, 특별 서비스 등에 대해 질문하면 이 Knowledge Base를 검색하여 답변합니다.
```

53. [[Add]] 버튼을 클릭합니다.
    <img src="/images/week14/14-3-task2-step53-kb-create.png" alt="Knowledge base Add 버튼 클릭" class="guide-img-md" />

54. Knowledge base가 추가되었는지 확인합니다.

    <img src="/images/week14/14-3-task2-step54-kb-added.png" alt="Knowledge base 추가 확인" class="guide-img-md" />

> [!NOTE]
> Knowledge Base를 연결하면 Agent가 예약 관리뿐만 아니라 레스토랑 정보 질문에도 답변할 수 있습니다.

55. 페이지 상단의 [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Agent 설정이 저장됩니다. 이제 Agent를 준비하고 테스트할 수 있습니다.

✅ **태스크 완료**: Amazon Bedrock Agent가 생성되고 Action Group이 설정되었습니다.

## 태스크 3: Agent 준비 및 테스트

이 태스크에서는 Agent를 준비하고 테스트 콘솔에서 대화를 시도합니다.

56. Agent 상세 페이지에서 [[Prepare]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task3-step56-prepare.png" alt="Agent Prepare 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> Agent 준비에 30초-1분이 소요됩니다. 이 과정에서 Agent의 프롬프트와 Action Group이 최적화됩니다. 준비가 완료되면 오른쪽에 **Test** 패널이 표시됩니다.

> [!IMPORTANT]
> Action Group, Knowledge Base, 또는 Instructions를 수정한 경우 반드시 [[Prepare]] 버튼을 다시 클릭해야 변경사항이 반영됩니다.  
> Prepare를 실행하지 않으면 이전 버전의 Agent가 계속 사용됩니다.

> [!TROUBLESHOOTING]
> **문제**: 테스트 시 "Access denied when calling Bedrock" 에러가 발생합니다.
>
> **원인**: Agent 서비스 역할의 모델 호출 정책에 현재 선택한 모델이 포함되지 않은 경우입니다. Agent 생성 시점과 모델 선택 시점이 다르면 발생할 수 있습니다.
>
> **해결**:
>
> 1. AWS IAM 콘솔로 이동합니다.
> 2. `AmazonBedrockExecutionRoleForAgents_` 로 시작하는 역할을 찾습니다.
> 3. `AmazonBedrockAgentBedrockFoundationModelPolicy_` 정책을 클릭합니다.
> 4. [[Edit]] 버튼을 클릭하고 Resource의 모델 ARN을 `arn:aws:bedrock:ap-northeast-2::foundation-model/*`로 변경합니다.
> 5. 또는 기존 역할을 삭제하고 Agent builder에서 `Create and use a new service role`을 다시 선택한 후 [[Save]]합니다.

57. Test 패널의 입력창에 다음 메시지를 입력합니다:

```
안녕하세요! 2월 15일 저녁 7시에 4명 예약하고 싶습니다.
```

58. [[Run]] 버튼을 클릭합니다.
59. Agent의 응답을 확인합니다.
    <img src="/images/week14/14-3-task3-step59-response.png" alt="Agent 예약 응답 확인" class="guide-img-sm" />

> [!OUTPUT]
> Agent 응답 예시:
>
> ```
> 안녕합니다! 😊 예약을 도와드리겠습니다.
>
> 예약 정보를 확인합니다:
> - 날짜: 2026-02-15
> - 시간: 19:00
> - 인원: 4명
>
> 고객님의 성함을 알려주시겠어요?
> ```

60. 다음 메시지를 입력합니다:

    <img src="/images/week14/14-3-task3-step60-input.png" alt="김철수 이름 입력" class="guide-img-sm" />

```
김철수입니다.
```

61. Agent가 예약을 생성하고 예약 번호를 제공하는지 확인합니다.

> [!NOTE]
> Agent가 한 번에 모든 정보를 추출하지 못하고 하나씩 물어볼 수 있습니다.  
> 생성형 AI의 특성상 실제 응답은 아래 예시와 다를 수 있으며, 대화가 더 길어질 수 있습니다.

> [!OUTPUT]
> Agent 응답 예시:
>
> ```
> 김철수님, 예약이 완료되었습니다! ✅
>
> 📋 예약 정보:
> - 예약 번호: RESABC12345
> - 고객명: 김철수.
> - 날짜: 2026-02-15
> - 시간: 19:00
> - 인원: 4명
> - 상태: 확정.
>
> 예약 번호를 꼭 기억합니다!
> ```

62. 예약 조회를 테스트합니다:

    <img src="/images/week14/14-3-task3-step62-query.png" alt="예약 조회 테스트" class="guide-img-sm" />

```
방금 만든 예약 정보를 확인하고 싶어요.
```

63. Agent가 예약 번호를 요청하는지 확인합니다.
64. 이전에 받은 예약 번호를 입력합니다.
65. Agent가 예약 정보를 정확히 조회하는지 확인합니다.

> [!NOTE]
> 예약 번호는 UUID 기반으로 생성되므로 실제 응답의 예약 번호는 위 예시와 다릅니다.  
> 또한 생성형 AI의 특성상 날짜 해석이 다를 수 있습니다 (예: "2월 15일" → "2026-02-15" 또는 "2026-02-15").  
> 실제 저장된 날짜는 Amazon DynamoDB 테이블에서 확인할 수 있습니다.
>
> <img src="/images/week14/14-3-task3-step65-dynamodb.png" alt="DynamoDB 테이블에서 예약 데이터 확인" class="guide-img-md" />

66. **Show trace** 토글을 활성화합니다.
67. 새로운 메시지를 입력합니다:

    <img src="/images/week14/14-3-task3-step67-trace.png" alt="Show trace 활성화 후 메시지 입력" class="guide-img-sm" />

```
2월 15일 예약 목록을 보여주세요.
```

68. Trace 패널에서 Agent의 사고 과정을 확인합니다:
    - **Pre-processing**: 사용자 입력 분석
    - **Orchestration**: 어떤 함수를 호출할지 결정
    - **Action invocation**: AWS Lambda 함수 호출
    - **Post-processing**: 응답 생성

> [!NOTE]
> Trace를 통해 Agent가 어떻게 의사결정을 하는지 이해할 수 있습니다.
>
> <img src="/images/week14/14-3-task3-step68-trace-detail.png" alt="Trace 패널에서 Agent 사고 과정 확인" class="guide-img-md" />

69. 예약 취소를 테스트합니다:

```
예약을 취소하고 싶어요.
```

70. Agent가 예약 번호를 요청하는지 확인합니다.
71. 예약 번호를 입력하고 취소가 정상적으로 처리되는지 확인합니다.

    <img src="/images/week14/14-3-task3-step71-cancel.png" alt="예약 취소 처리 확인" class="guide-img-sm" />

    <img src="/images/week14/14-3-task3-step71-dynamodb-cancelled.png" alt="DynamoDB에서 예약 상태 cancelled 확인" class="guide-img-md" />

> [!NOTE]
> `cancel_reservation` 함수는 예약이 존재하지 않아도 성공 응답을 반환합니다.  
> 이는 Amazon DynamoDB의 `update_item` 동작 특성 때문입니다.  
> 프로덕션 환경에서는 예약 존재 여부를 먼저 확인하는 로직을 추가해야 합니다.

72. Knowledge Base 연동을 테스트합니다 (14-2 완료 시):

    <img src="/images/week14/14-3-task3-step72-kb-test.png" alt="Knowledge Base 연동 테스트" class="guide-img-sm" />

```
안심 스테이크 가격이 얼마인가요?
```

73. Agent가 Knowledge Base를 검색하여 메뉴 가격을 답변하는지 확인합니다.

> [!OUTPUT]
> Agent 응답 예시:
>
> ```
> 안심 스테이크(200g)는 38,000원입니다. 😊
> 미디엄 레어로 추천되며, 감자 퓨레와 구운 야채가 포함되어 있습니다.
> ```

74. 추가 질문을 테스트합니다:

    <img src="/images/week14/14-3-task3-step74-parking.png" alt="주차 정보 질문 테스트" class="guide-img-sm" />

```
주차가 가능한가요?
```

75. Agent가 Knowledge Base에서 주차 정보를 검색하여 답변하는지 확인합니다.

✅ **태스크 완료**: Agent가 정상적으로 작동하며 예약 관리 기능을 수행합니다.

## 태스크 4: Agent 별칭 생성 및 배포

이 태스크에서는 Agent의 버전을 관리하고 프로덕션 환경에 배포하기 위한 별칭을 생성합니다.

76. Agent 상세 페이지 상단에서 **Aliases** 탭을 선택합니다.

    <img src="/images/week14/14-3-task4-step76-aliases.png" alt="Agent Aliases 탭 선택" class="guide-img-md" />

77. [[Create alias]] 버튼을 클릭합니다.
78. 다음을 입력합니다:
    - **Alias name**: `production`
    - **Description**: `Production Agent for QuickTable`
    - **Associate a version**: `Create a new version and associate it to this alias` 선택 (기본값)
79. [[Create alias]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task4-step79-create-alias.png" alt="Create alias 버튼 클릭" class="guide-img-sm" />

> [!NOTE]
> 별칭 생성이 완료될 때까지 기다립니다. 별칭을 사용하면 Agent의 여러 버전을 관리하고 안전하게 배포할 수 있습니다.

80. Agent Details 페이지의 **Aliases** 테이블에서 **Alias ID**를 확인하고 메모장에 복사합니다 (예: `45NSBQU1IN`).

    <img src="/images/week14/14-3-task4-step80-alias-id.png" alt="Aliases 테이블에서 Alias ID 확인" class="guide-img-md" />

> [!NOTE]
> 이 Alias ID는 태스크 5에서 AWS Lambda 함수로 Agent를 호출할 때 사용됩니다.  
> Agent ID는 Agent Details 페이지 상단의 **Agent overview** 섹션에서 확인할 수 있습니다.

✅ **태스크 완료**: Agent 별칭이 생성되고 배포되었습니다.

## 태스크 5: AWS Lambda 함수로 Agent 호출 테스트

이 태스크에서는 AWS Lambda 함수를 생성하여 프로그래밍 방식으로 Agent를 호출하는 방법을 학습합니다.

81. AWS Lambda 콘솔로 이동합니다.
82. [[Create function]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task5-step82-create-function.png" alt="Lambda Create function 페이지" class="guide-img-md" />

83. **Function name**에 `BedrockAgentInvoker`를 입력합니다.
84. **Runtime**에서 `Python 3.13`를 선택합니다.
85. [[Create function]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task5-step85-create.png" alt="Create function 버튼 클릭" class="guide-img-md" />

86. 함수 생성이 완료되면 "Getting started" 모달이 표시되면 [[Dismiss]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task5-step86-dismiss.png" alt="Getting started 모달 Dismiss" class="guide-img-sm" />

87. **Configuration** 탭을 선택합니다.
88. 왼쪽 메뉴에서 **General configuration**을 선택합니다.
89. [[Edit]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task5-step89-edit-timeout.png" alt="General configuration Edit 버튼" class="guide-img-md" />

90. **Timeout**을 `30` 초로 변경합니다.

> [!NOTE]
> Amazon Bedrock Agent 호출은 응답 생성에 시간이 걸립니다 (일반적으로 5-30초).  
> AWS Lambda 기본 타임아웃(3초)으로는 부족하므로 최소 30초 이상으로 설정해야 합니다.  
> Agent가 Knowledge Base를 검색하거나 여러 Action을 수행하는 경우 더 긴 시간이 필요할 수 있습니다.

91. [[Save]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-task5-step91-save-timeout.png" alt="Timeout 30초 설정 후 Save" class="guide-img-md" />

92. **Code** 탭을 선택합니다.
93. 코드 편집기의 기본 코드를 삭제하고 다음 코드를 입력합니다:

> [!NOTE]
> 이 코드는 Amazon Bedrock Agent를 프로그래밍 방식으로 호출하는 AWS Lambda 함수입니다.
>
> - 환경 변수에서 Agent ID와 Alias ID를 가져옵니다.
> - `invoke_agent` API로 Agent에 메시지를 전송합니다.
> - 스트리밍 응답을 수집하여 JSON으로 반환합니다.

```python
import json
import boto3
import os

# Amazon Bedrock Agent Runtime 클라이언트 초기화 (리전 명시)
# 환경 변수에서 리전을 가져오거나 기본값 사용
bedrock_agent_runtime = boto3.client(
    'bedrock-agent-runtime',
    region_name=os.environ.get('BEDROCK_REGION', 'ap-northeast-2')
)

def lambda_handler(event, context):
    """
    Amazon Bedrock Agent를 프로그래밍 방식으로 호출하는 AWS Lambda 함수

    Args:
        event (dict): 입력 이벤트
            - session_id (str): 세션 ID
            - input (str): 사용자 입력 텍스트
        context: AWS Lambda 실행 컨텍스트

    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공) 또는 500 (오류)
            - body (str): JSON 형식의 응답
    """
    # 환경 변수에서 Agent 정보 가져오기
    agent_id = os.environ.get('AGENT_ID')
    agent_alias_id = os.environ.get('AGENT_ALIAS_ID')

    # 이벤트에서 세션 ID와 사용자 입력 추출
    session_id = event.get('session_id', 'test-session-001')
    user_input = event.get('input', '안녕하세요')

    try:
        # Amazon Bedrock Agent 호출
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=user_input
        )

        # 응답 스트림 처리
        # EventStream 형식: {'chunk': {'bytes': b'...'}}
        completion = ""
        for event_item in response.get('completion', []):
            chunk = event_item.get('chunk')
            if chunk:
                # bytes를 문자열로 디코딩
                completion += chunk.get('bytes', b'').decode('utf-8')

        # 성공 응답 반환
        return {
            'statusCode': 200,
            'body': json.dumps({
                'session_id': session_id,
                'response': completion
            }, ensure_ascii=False)
        }

    except Exception as e:
        # 오류 응답 반환
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

94. [[Deploy]] 버튼을 클릭합니다.
    <img src="/images/week14/14-3-task5-step94-deploy.png" alt="Lambda 함수 Deploy 버튼 클릭" class="guide-img-md" />

95. **Configuration** 탭을 선택합니다.
96. 왼쪽 메뉴에서 **Permissions**를 선택합니다.
97. **Execution role** 섹션에서 역할 이름 링크를 클릭하여 AWS IAM 콘솔로 이동합니다.

    <img src="/images/week14/14-3-task5-step97-execution-role.png" alt="Execution role 링크 클릭" class="guide-img-md" />

98. [[Add permissions]] > `Attach policies`를 선택합니다.

    <img src="/images/week14/14-3-task5-step98-add-permissions.png" alt="Add permissions > Attach policies 선택" class="guide-img-md" />

99. `AmazonBedrockFullAccess`를 검색하고 체크합니다.
100. [[Add permissions]] 버튼을 클릭합니다.

      <img src="/images/week14/14-3-task5-step100-attach-policy.png" alt="AmazonBedrockFullAccess 정책 선택" class="guide-img-md" />

      <img src="/images/week14/14-3-task5-step100-policy-attached.png" alt="정책 연결 완료 확인" class="guide-img-md" />

> [!NOTE]
> 프로덕션 환경에서는 `bedrock:InvokeAgent` 권한만 포함하는 커스텀 정책을 사용해야 합니다.  
> 참고 섹션에서 최소 권한 정책 예시를 확인할 수 있습니다.

101. AWS Lambda 콘솔로 돌아와 `BedrockAgentInvoker` 함수를 선택합니다.
102. 왼쪽 메뉴에서 **Environment variables**를 선택합니다.
103. [[Edit]] 버튼을 클릭합니다.
     <img src="/images/week14/14-3-task5-step103-env-edit.png" alt="Environment variables Edit 버튼" class="guide-img-md" />

104. [[Add environment variable]] 버튼을 클릭하여 다음 환경 변수들을 추가합니다:

| 변수명           | 값               | 설명                                                                  |
| ---------------- | ---------------- | --------------------------------------------------------------------- |
| `AGENT_ID`       | (Agent ID 입력)  | Amazon Bedrock Agent ID (Agent 상세 페이지의 Agent overview에서 확인) |
| `AGENT_ALIAS_ID` | (별칭 ID 입력)   | 별칭 ID (별칭 상세 페이지에서 확인, ARN이 아닌 ID만 입력)             |
| `BEDROCK_REGION` | `ap-northeast-2` | Amazon Bedrock Agent가 배포된 리전                                    |

105. [[Save]] 버튼을 클릭합니다.
     <img src="/images/week14/14-3-task5-step105-env-save.png" alt="환경 변수 입력 후 Save" class="guide-img-md" />
     <img src="/images/week14/14-3-task5-step105-env-saved.png" alt="환경 변수 저장 완료" class="guide-img-md" />

> [!IMPORTANT]
> `AGENT_ALIAS_ID`는 별칭 ARN 전체가 아닌 ID 부분만 입력합니다.
>
> **올바른 예시**:
>
> - 별칭 ARN: `arn:aws:bedrock:ap-northeast-2:123456789012:agent-alias/ABCDEFGHIJ/TSTALIASID`
> - 입력할 값: `TSTALIASID` (ARN의 마지막 부분만).
>
> **잘못된 예시**:
>
> - ❌ 전체 ARN 입력: `arn:aws:bedrock:ap-northeast-2:123456789012:agent-alias/ABCDEFGHIJ/TSTALIASID`
> - ❌ Agent ID 입력: `ABCDEFGHIJ`
>
> 별칭 상세 페이지에서 "Alias ID" 필드의 값을 복사하여 사용합니다.

> [!TIP]
> `BEDROCK_REGION` 환경 변수를 명시적으로 설정하면 AWS Lambda 함수가 다른 리전에서 실행되더라도 올바른 리전의 Amazon Bedrock Agent를 호출할 수 있습니다.  
> `AWS_REGION`은 AWS Lambda의 예약 환경 변수이므로 사용하지 않습니다.

106. 왼쪽 메뉴에서 **Tags**를 선택합니다.
107. [[Manage tags]] 버튼을 클릭합니다.
     <img src="/images/week14/14-3-task5-step107-manage-tags.png" alt="Manage tags 버튼 클릭" class="guide-img-md" />

108. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-3`    |
| `CreatedBy` | `Student` |

109. [[Save]] 버튼을 클릭합니다.
     <img src="/images/week14/14-3-task5-step109-tags-save.png" alt="태그 저장" class="guide-img-md" />

110. **Test** 탭을 선택합니다.
111. **Event JSON** 섹션의 기본 내용을 삭제하고 다음 테스트 이벤트를 입력합니다:

```json
{
  "session_id": "test-001",
  "input": "2026-02-20 저녁 8시에 2명 예약하고 싶어요. 이름은 이영희입니다."
}
```

112. [[Test]] 버튼을 클릭하여 함수를 실행합니다.
     <img src="/images/week14/14-3-task5-step112-test.png" alt="Lambda Test 버튼 클릭" class="guide-img-md" />

113. 실행 결과를 확인합니다.
     <img src="/images/week14/14-3-task5-step113-result.png" alt="Lambda 실행 결과 확인" class="guide-img-md" />

> [!OUTPUT]
> 실행 결과 예시:
>
> ```json
> {
>   "statusCode": 200,
>   "body": {
>     "session_id": "test-001",
>     "response": "이영희님, 예약이 완료되었습니다! ✅\n\n📋 예약 정보:\n- 예약 번호: RESXYZ67890\n- 고객명: 이영희\n- 날짜: 2026-02-20\n- 시간: 20:00\n- 인원: 2명\n- 상태: 확정"
>   }
> }
> ```

✅ **태스크 완료**: AWS Lambda 함수로 Agent를 프로그래밍 방식으로 호출했습니다.

### 태스크 5.1: Amazon DynamoDB에서 예약 데이터 확인

114. 상단 검색창에 `DynamoDB`를 입력하고 선택합니다.
115. 왼쪽 메뉴에서 **Tables**를 선택합니다.
116. `RestaurantReservations` 테이블을 클릭합니다.
117. [[Explore table items]] 버튼을 클릭합니다.
118. 태스크 3과 태스크 5에서 생성한 예약 데이터가 추가되었는지 확인합니다.
     <img src="/images/week14/14-3-task5-step118-dynamodb-items.png" alt="DynamoDB 테이블에서 예약 데이터 확인" class="guide-img-md" />

> [!NOTE]
> 초기 샘플 데이터(RES001~RES003) 외에 Agent 테스트에서 생성한 예약이 추가로 표시됩니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 Amazon DynamoDB 테이블과 AWS Lambda 함수를 자동 생성했습니다.
- Amazon Bedrock Agent를 생성하고 QuickTable Action Group을 설정했습니다.
- Week 14-2에서 생성한 Knowledge Base를 Agent에 연결했습니다.
- Agent를 테스트하고 대화형 QuickTable 예약 시스템을 확인했습니다.
- Agent 별칭을 생성하여 프로덕션 환경에 배포했습니다.
- AWS Lambda 함수로 Agent를 프로그래밍 방식으로 호출했습니다.

Week 14-2에서 구축한 Knowledge Base와 14-3의 Agent를 결합하여 QuickTable 레스토랑 예약 시스템이 완성되었습니다.  
고객은 자연어로 대화하며 예약을 생성하고 관리할 수 있으며, 레스토랑 정보에 대한 질문에도 답변받을 수 있습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 단계 1: 생성된 리소스 확인 (Tag Editor)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `14-3`
6. [[Search resources]] 버튼을 클릭합니다.
   <img src="/images/week14/14-3-cleanup-step6.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!OUTPUT]
> 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 단계 2: 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
8. Amazon Bedrock Agent를 삭제합니다:

```bash
# Agent ID 확인
AGENT_ID=$(aws bedrock-agent list-agents --query "agentSummaries[?agentName=='QuickTableAssistant'].agentId" --output text)
echo "Agent ID: ${AGENT_ID}"

# Agent 삭제 (별칭과 버전도 함께 삭제됨)
aws bedrock-agent delete-agent --agent-id ${AGENT_ID} --skip-resource-in-use-check
```

<img src="/images/week14/14-3-cleanup-step8.png" alt="CloudShell에서 Agent 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws bedrock-agent list-agents --query "agentSummaries[?agentName=='QuickTableAssistant']" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

9. AWS Lambda 함수를 삭제합니다 (수동 생성분):

```bash
aws lambda delete-function --function-name BedrockAgentInvoker
```

<img src="/images/week14/14-3-cleanup-step9.png" alt="Lambda 함수 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws lambda get-function --function-name BedrockAgentInvoker
> ```
>
> `ResourceNotFoundException` 오류가 나오면 삭제 완료입니다.

10. AWS IAM 역할을 삭제합니다:

```bash
# Bedrock Agent 역할 삭제
BEDROCK_ROLES=$(aws iam list-roles --query "Roles[?starts_with(RoleName,'AmazonBedrockExecutionRoleForAgents_')].RoleName" --output text)
for ROLE in ${BEDROCK_ROLES}; do
  POLICIES=$(aws iam list-attached-role-policies --role-name ${ROLE} --query "AttachedPolicies[*].PolicyArn" --output text)
  for POLICY in ${POLICIES}; do
    aws iam detach-role-policy --role-name ${ROLE} --policy-arn ${POLICY}
  done
  INLINE=$(aws iam list-role-policies --role-name ${ROLE} --query "PolicyNames" --output text)
  for P in ${INLINE}; do
    aws iam delete-role-policy --role-name ${ROLE} --policy-name ${P}
  done
  aws iam delete-role --role-name ${ROLE}
  echo "Deleted: ${ROLE}"
done

# BedrockAgentInvoker 역할 삭제
INVOKER_ROLE=$(aws iam list-roles --query "Roles[?starts_with(RoleName,'BedrockAgentInvoker-role-')].RoleName" --output text)
if [ -n "${INVOKER_ROLE}" ]; then
  POLICIES=$(aws iam list-attached-role-policies --role-name ${INVOKER_ROLE} --query "AttachedPolicies[*].PolicyArn" --output text)
  for POLICY in ${POLICIES}; do
    aws iam detach-role-policy --role-name ${INVOKER_ROLE} --policy-arn ${POLICY}
  done
  aws iam delete-role --role-name ${INVOKER_ROLE}
  echo "Deleted: ${INVOKER_ROLE}"
fi
```

<img src="/images/week14/14-3-cleanup-step10.png" alt="IAM 역할 삭제 CLI 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws iam list-roles --query "Roles[?starts_with(RoleName,'AmazonBedrockExecutionRoleForAgents_') || starts_with(RoleName,'BedrockAgentInvoker-role-')].RoleName" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

11. 옵션 1 완료 후 아래 **단계 2: AWS CloudFormation 스택 삭제**로 이동합니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

**Amazon Bedrock Agent 삭제**

12. 상단 검색창에 `Bedrock`을 입력하고 선택합니다.
13. 왼쪽 메뉴에서 **Build** > **Agents**를 선택합니다.
14. `QuickTableAssistant` Agent를 선택합니다.
15. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step15.png" alt="Agent Delete 버튼 클릭" class="guide-img-md" />

16. 확인 창에서 `delete`를 입력합니다.
17. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step17.png" alt="Agent 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> Agent를 삭제하면 모든 별칭과 버전도 함께 삭제됩니다.

**AWS Lambda 함수 삭제 (수동 생성분)**

18. AWS Lambda 콘솔로 이동하여 왼쪽 메뉴에서 **Functions**를 선택합니다.
19. `BedrockAgentInvoker` 함수의 체크박스를 선택합니다.
20. **Actions** > `Delete`를 선택합니다.

    <img src="/images/week14/14-3-cleanup-step20.png" alt="Lambda 함수 삭제" class="guide-img-md" />

21. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step21.png" alt="Lambda 함수 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> `BedrockAgentReservationHandler` 함수는 AWS CloudFormation 스택 삭제 시 자동으로 삭제됩니다.

**AWS IAM 역할 삭제 (Amazon Bedrock Agent 역할)**

22. 상단 검색창에 `IAM`을 입력하고 선택합니다.
23. 왼쪽 메뉴에서 **Roles**를 선택합니다.
24. 검색창에 `Bedrock`을 입력합니다.
25. 다음 역할들을 선택합니다:
    - `BedrockAgentInvoker-role-` 로 시작하는 역할
    - `AmazonBedrockExecutionRoleForAgents_` 로 시작하는 역할
26. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step26.png" alt="IAM 역할 Delete 클릭" class="guide-img-md" />

27. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step27.png" alt="IAM 역할 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 역할 1개 삭제 시 확인 창에서 **역할 이름**을 입력합니다. 여러 개 동시 삭제 시 `delete`를 입력합니다.  
> `BedrockAgentReservationHandler-role-` 역할은 AWS CloudFormation 스택 삭제 시 자동으로 삭제됩니다.  
> `AmazonBedrockExecutionRoleForKnowledgeBase_` 역할은 Week 14-2 리소스 삭제 시 함께 삭제합니다.

### 단계 2: AWS CloudFormation 스택 삭제

28. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
29. `week14-3-bedrock-agent-stack` 스택을 선택합니다.
30. [[Delete stack]] 버튼을 클릭합니다.
31. 확인 창에서 스택 이름 `week14-3-bedrock-agent-stack`을 입력하고 [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step31.png" alt="CloudFormation 스택 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 스택 삭제에 1-2분이 소요됩니다.  
> AWS CloudFormation 스택을 삭제하면 다음 리소스가 자동으로 삭제됩니다:
>
> - Amazon DynamoDB 테이블 (`RestaurantReservations`)
> - AWS Lambda 함수 (`BedrockAgentReservationHandler`)
> - AWS IAM 역할 (AWS Lambda 실행 역할)

### 단계 3: Amazon CloudWatch Log Group 삭제

32. 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
33. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
34. 검색창에 `BedrockAgent`를 입력합니다.
35. 다음 로그 그룹들을 선택합니다:
    - `/aws/lambda/BedrockAgentInvoker`
    - `/aws/lambda/BedrockAgentReservationHandler`
    - `/aws/lambda/week14-3-SampleDataUploader-{StudentId}`
36. **Actions** > `Delete log group(s)`를 선택합니다.

    <img src="/images/week14/14-3-cleanup-step36.png" alt="Actions > Delete log group(s) 선택" class="guide-img-md" />

37. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step37.png" alt="로그 그룹 삭제 확인" class="guide-img-sm" />

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

> [!TIP]
> AWS CLI로 삭제하려면 CloudShell에서 다음 명령어를 실행합니다 (`${STUDENT_ID}`를 본인 학번으로 변경):
>
> ```bash
> STUDENT_ID="20240001"
> aws logs delete-log-group --log-group-name /aws/lambda/BedrockAgentInvoker
> aws logs delete-log-group --log-group-name /aws/lambda/BedrockAgentReservationHandler
> aws logs delete-log-group --log-group-name /aws/lambda/week14-3-SampleDataUploader-${STUDENT_ID} 2>/dev/null
> ```
>
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/BedrockAgent --query "logGroups[*].logGroupName" --output text
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/week14-3 --query "logGroups[*].logGroupName" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.
>
> <img src="/images/week14/14-3-cleanup-log-cli.png" alt="CloudWatch Log Group CLI 삭제" class="guide-img-md" />

### Week 14-2 리소스 삭제 (Knowledge Base 연결 시)

> [!WARNING]
> Week 14-2에서 생성한 Knowledge Base와 Amazon OpenSearch Serverless 컬렉션을 삭제하지 않았다면 **반드시 즉시 삭제**합니다.  
> Amazon OpenSearch Serverless는 사용하지 않아도 컬렉션이 존재하는 동안 지속적으로 비용이 부과됩니다. 삭제하지 않으면 매월 상당한 비용이 발생합니다.

> [!TIP]
> Week 14-2 실습 가이드의 리소스 정리 섹션에서 상세한 삭제 절차를 확인할 수 있습니다: [Week 14-2 리소스 정리](/week/14/session/2#cleanup)

38. Amazon Bedrock 콘솔로 이동합니다.
39. 왼쪽 메뉴에서 **Build** > **Knowledge bases**를 선택합니다.
40. `quicktable-restaurant-kb`를 선택합니다.
41. [[Delete]] 버튼을 클릭합니다.
42. 확인 창에서 `delete`를 입력합니다.
43. [[Delete]] 버튼을 클릭합니다.
44. 상단 검색창에 `OpenSearch`를 입력하고 선택합니다.
45. 왼쪽 메뉴에서 **Serverless** > **Collections**를 선택합니다.
46. Knowledge Base와 연결된 컬렉션을 선택합니다.

> [!NOTE]
> Quick create로 생성된 Amazon OpenSearch Serverless 컬렉션은 `bedrock-knowledge-base-` 접두사로 시작하는 이름을 가질 수 있습니다.

47. [[Delete]] 버튼을 클릭합니다.
48. 확인 창에서 `confirm`을 입력합니다.
49. [[Delete]] 버튼을 클릭합니다.
50. Amazon S3 콘솔에서 `quicktable-kb-documents-{StudentId}` 버킷을 찾습니다.
51. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
52. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
53. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
54. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

> [!NOTE]
> AWS IAM 콘솔에서 `AmazonBedrockExecutionRoleForKnowledgeBase_` 로 시작하는 역할도 삭제합니다.

### 최종 삭제 확인 (Tag Editor 활용)

55. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
56. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
57. **Regions**에서 `ap-northeast-2`를 선택합니다.
58. **Resource types**에서 `All supported resource types`를 선택합니다.
59. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `14-3`
60. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week14/14-3-cleanup-step60-search.png" alt="Tag Editor 검색 결과 확인" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.  
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon Bedrock Agents 개요](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents.html).
- [Amazon Bedrock Agents Action Groups](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents-action-groups.html).
- [Amazon Bedrock Agents Knowledge Bases](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/knowledge-base.html).
- [Claude 모델 개요](https://docs.anthropic.com/en/docs/about-claude/models/overview).
- [Amazon Bedrock 요금](https://aws.amazon.com/ko/bedrock/pricing/).
- [AWS Lambda와 Amazon Bedrock 통합](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents-lambda.html).

## 📚 참고: Amazon Bedrock Agent 핵심 개념

### Amazon Bedrock Agent 아키텍처

Amazon Bedrock Agent는 다음 구성 요소로 이루어져 있습니다:

**기반 모델 (Foundation Model)**

- QuickTable Agent의 두뇌 역할을 하는 대규모 언어 모델입니다.
- Claude Sonnet 4.6, Haiku 4.5 등 다양한 모델 선택 가능합니다.
- 사용자 입력을 이해하고 적절한 응답을 생성합니다.

**Instructions (지침)**

- Agent의 역할과 행동 방식을 정의합니다.
- 대화 스타일, 응답 형식, 제약사항 등을 명시합니다.
- 프롬프트 엔지니어링의 핵심 요소입니다.

**Action Groups (액션 그룹)**

- Agent가 수행할 수 있는 작업들의 집합입니다.
- AWS Lambda 함수와 연결되어 실제 작업을 실행합니다.
- OpenAPI 스키마 또는 함수 정의로 작업을 명시합니다.

**Knowledge Bases (지식 베이스)**

- Agent가 참조할 수 있는 문서 저장소입니다.
- RAG (Retrieval-Augmented Generation) 방식으로 동작합니다.
- Amazon S3에 저장된 문서를 벡터화하여 검색합니다.

### Action Group vs Knowledge Base

**Action Group 사용 시기:**

- 데이터베이스 조회/수정이 필요한 경우.
- 외부 API 호출이 필요한 경우.
- 실시간 데이터 처리가 필요한 경우.
- 트랜잭션 작업이 필요한 경우.

**예시**: 예약 생성, 주문 처리, 결제 실행

**Knowledge Base 사용 시기:**

- 문서 기반 질의응답이 필요한 경우.
- 정적 정보 검색이 필요한 경우.
- 컨텍스트가 많은 답변이 필요한 경우.
- 자주 변경되지 않는 정보를 다루는 경우.

**예시**: FAQ 답변, 제품 설명서 검색, 정책 안내

### Agent 프롬프트 엔지니어링

**효과적인 Instructions 작성 원칙:**

**1. 명확한 역할 정의**

```
당신은 QuickTable 레스토랑 예약 시스템을 관리하는 친절한 AI 어시스턴트입니다.
```

**2. 구체적인 작업 범위**

```
주요 역할:
- 고객의 예약 요청을 받아 새로운 예약을 생성합니다.
- 예약 번호로 기존 예약을 조회합니다.
- 특정 날짜의 예약 목록을 확인합니다.
- 예약 취소 요청을 처리합니다.
```

**3. 대화 규칙 명시**

```
대화 규칙:
- 항상 정중하고 친절하게 응답합니다
- 예약 생성 시 고객 이름, 날짜, 시간, 인원수를 반드시 확인합니다
- 정보가 부족하면 고객에게 추가 정보를 요청합니다
```

**4. 응답 형식 지정**

```
응답 스타일:
- 간결하고 명확하게 답변합니다
- 이모지를 적절히 사용하여 친근감을 표현합니다
- 예약 정보는 구조화된 형식으로 제공합니다
```

### 세션 관리 및 컨텍스트 처리

**세션 ID (Session ID)**

- 대화의 연속성을 유지하는 고유 식별자입니다.
- 같은 세션 ID로 여러 요청을 보내면 이전 대화를 기억합니다.
- 새로운 대화를 시작하려면 새로운 세션 ID를 사용합니다.

**컨텍스트 윈도우**

- Agent는 최근 대화 내역을 기억합니다.
- Claude Sonnet 4.6: 최대 200K 토큰 (약 150,000 단어).
- 긴 대화에서는 중요한 정보를 요약하여 전달합니다.

**세션 속성 (Session Attributes)**

- 세션 간 유지해야 할 정보를 저장합니다.
- 사용자 선호도, 임시 데이터 등을 저장할 수 있습니다.

### AWS Lambda 통합 패턴

**요청 형식 (Amazon Bedrock Agent → AWS Lambda)**

```json
{
  "messageVersion": "1.0",
  "agent": {
    "name": "QuickTableAssistant",
    "id": "AGENT123",
    "alias": "production",
    "version": "1"
  },
  "actionGroup": "QuickTableReservationActions",
  "function": "create_reservation",
  "parameters": [
    {
      "name": "customerName",
      "type": "string",
      "value": "김철수"
    },
    {
      "name": "date",
      "type": "string",
      "value": "2026-02-15"
    },
    {
      "name": "time",
      "type": "string",
      "value": "19:00"
    },
    {
      "name": "partySize",
      "type": "integer",
      "value": 4
    }
  ],
  "sessionId": "session-123",
  "sessionAttributes": {}
}
```

**응답 형식 (AWS Lambda → Amazon Bedrock Agent)**

```json
{
  "messageVersion": "1.0",
  "response": {
    "actionGroup": "QuickTableReservationActions",
    "function": "create_reservation",
    "functionResponse": {
      "responseBody": {
        "TEXT": {
          "body": "{\"success\": true, \"reservation_id\": \"RES123\"}"
        }
      }
    }
  }
}
```

**오류 처리 패턴**

```python
try:
    result = perform_action(params)
    return success_response(result)
except ValidationError as e:
    return error_response(f"입력값 오류: {str(e)}")
except DatabaseError as e:
    return error_response(f"데이터베이스 오류: {str(e)}")
except Exception as e:
    return error_response(f"예상치 못한 오류: {str(e)}")
```

### 비용 최적화 전략

**1. 모델 선택 최적화**

> ⚠️ 아래 모델 정보는 2026년 5월 기준이며, AWS는 지속적으로 새로운 모델을 추가합니다. 최신 모델 목록은 [Amazon Bedrock 콘솔](https://console.aws.amazon.com/bedrock/)의 Model catalog 또는 [Claude 모델 개요](https://docs.anthropic.com/en/docs/about-claude/models/overview)를 참고합니다.

- **Claude Sonnet 4.6**: 성능과 비용의 균형 (권장, Bedrock Agents optimized 해제 필요).
- **Claude Haiku 4.5**: 빠른 응답, 저렴한 비용 (Bedrock Agents optimized 해제 필요).
- **Claude Opus 4.x**: 최고 성능 (복잡한 작업, Bedrock Agents optimized 해제 필요).

**2. 프롬프트 최적화**

- 불필요한 지침 제거하여 토큰 수 감소.
- 간결하고 명확한 표현 사용.
- 예시는 필요한 경우에만 포함.

**3. 캐싱 활용**

- 자주 사용되는 응답은 Amazon DynamoDB에 캐싱.
- 동일한 질문에 대해 Agent 호출 최소화.
- TTL 설정으로 오래된 캐시 자동 삭제.

**4. 배치 처리**

- 여러 작업을 하나의 요청으로 묶어 처리.
- 불필요한 왕복 통신 최소화.

### 프로덕션 환경 권장사항

**1. 보안**

- AWS IAM 역할에 최소 권한 원칙 적용.
- AWS Lambda 함수에 Amazon VPC 엔드포인트 사용.
- 민감한 정보는 AWS Secrets Manager에 저장.
- API 키와 자격증명은 환경 변수로 관리.

**2. 모니터링**

- Amazon CloudWatch Logs로 Agent 대화 기록.
- AWS Lambda 함수 성능 메트릭 추적.
- 오류율과 응답 시간 모니터링.
- Amazon CloudWatch Alarms로 이상 징후 감지.

**3. 확장성**

- AWS Lambda 동시 실행 제한 설정.
- Amazon DynamoDB Amazon EC2 Auto Scaling 활성화.
- Agent 별칭으로 버전 관리.
- 트래픽 증가에 대비한 용량 계획.

**4. 테스트**

- 단위 테스트: AWS Lambda 함수 로직 검증.
- 통합 테스트: Agent와 AWS Lambda 연동 확인.
- 부하 테스트: 동시 사용자 처리 능력 검증.
- A/B 테스트: 프롬프트 최적화.

### 멀티턴 대화 처리

**대화 흐름 관리**

```
사용자: "예약하고 싶어요"
Agent: "네, 도와드리겠습니다. 날짜와 시간을 알려주세요."

사용자: "2월 15일 저녁 7시요"
Agent: "2월 15일 19시로 확인했습니다. 몇 분이신가요?"

사용자: "4명이요"
Agent: "4명으로 확인했습니다. 성함을 알려주세요."

사용자: "김철수입니다"
Agent: [create_reservation 함수 호출]
      "김철수님, 예약이 완료되었습니다! 예약번호는 RES123입니다."
```

**컨텍스트 유지 전략**

- 이전 대화에서 수집한 정보를 기억.
- 부족한 정보만 추가로 요청.
- 사용자가 정보를 수정하면 업데이트.
- 대화가 길어지면 중요 정보 요약.

### 오류 처리 및 재시도 전략

**1. 네트워크 오류**

```python
import time
from botocore.exceptions import ClientError

def invoke_agent_with_retry(agent_id, alias_id, session_id, input_text, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=alias_id,
                sessionId=session_id,
                inputText=input_text
            )
            return response
        except ClientError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 지수 백오프
```

**2. AWS Lambda 타임아웃**

- AWS Lambda 함수 타임아웃을 충분히 설정 (최소 30초).
- 긴 작업은 AWS Step Functions로 분리.
- 비동기 처리 패턴 고려.

**3. Agent 응답 오류**

- Agent가 잘못된 함수를 호출하는 경우.
- 파라미터가 누락되거나 잘못된 경우.
- 프롬프트를 더 명확하게 수정.
- 함수 설명을 더 상세하게 작성.

### 고급 기능

**1. 스트리밍 응답**

```python
response = bedrock_agent_runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId=alias_id,
    sessionId=session_id,
    inputText=user_input,
    enableTrace=True
)

# 스트리밍 응답 처리
for event in response.get('completion', []):
    chunk = event.get('chunk')
    if chunk:
        text = chunk.get('bytes', b'').decode('utf-8')
        print(text, end='', flush=True)
```

**2. Trace 분석**

- Agent의 사고 과정을 단계별로 확인.
- 어떤 함수를 호출했는지 추적.
- 프롬프트 최적화에 활용.
- 디버깅 및 문제 해결에 유용.

**3. 멀티 Action Group**

- 여러 AWS Lambda 함수를 Action Group으로 연결.
- 각 Action Group은 독립적인 기능 제공.
- 예: 예약 관리 + 메뉴 조회 + 리뷰 관리.

**4. Knowledge Base 통합**

- Action Group과 Knowledge Base 동시 사용.
- 문서 검색 + 실시간 작업 처리.
- RAG 기반 질의응답 + 트랜잭션 처리.

### 최소 권한 정책 예시

프로덕션 환경에서는 FullAccess 정책 대신 최소 권한 원칙을 적용한 커스텀 정책을 사용해야 합니다.

**1. AWS Lambda 함수 - Amazon DynamoDB 접근 정책**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:ap-northeast-2:*:table/RestaurantReservations"
    }
  ]
}
```

**2. AWS Lambda 함수 - Amazon Bedrock Agent 호출 정책**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeAgent"],
      "Resource": "arn:aws:bedrock:ap-northeast-2:*:agent-alias/*/*"
    }
  ]
}
```

**3. Amazon Bedrock Agent - AWS Lambda 호출 정책 (리소스 기반 정책)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:ap-northeast-2:*:function:BedrockAgentReservationHandler",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "YOUR_ACCOUNT_ID"
        },
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:bedrock:ap-northeast-2:YOUR_ACCOUNT_ID:agent/*"
        }
      }
    }
  ]
}
```

> [!NOTE]
> 위 정책들은 특정 리소스에만 접근할 수 있도록 제한하여 보안을 강화합니다.  
> `YOUR_ACCOUNT_ID`는 실제 AWS 계정 ID로 대체해야 합니다.

### OpenAPI 스키마를 사용한 Action Group 정의

함수 정의 대신 OpenAPI 3.0 스키마 파일을 업로드하여 Action Group을 정의할 수 있습니다.
이 방식은 복잡한 API를 정의하거나 기존 API 문서를 재사용할 때 유용합니다.

**OpenAPI 스키마 예시 (reservation-api.yaml)**

```yaml
openapi: 3.0.0
info:
  title: QuickTable Reservation API
  version: 1.0.0
  description: QuickTable 레스토랑 예약 관리 API

paths:
  /reservations:
    post:
      summary: 새로운 예약 생성
      description: 고객 정보와 예약 정보를 받아 새로운 예약을 생성합니다
      operationId: createReservation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - customer_name
                - date
                - time
                - party_size
              properties:
                customer_name:
                  type: string
                  description: 고객 이름
                  example: '김철수'
                date:
                  type: string
                  format: date
                  description: 예약 날짜 (YYYY-MM-DD)
                  example: '2026-02-15'
                time:
                  type: string
                  description: 예약 시간 (HH:MM)
                  example: '19:00'
                party_size:
                  type: integer
                  minimum: 1
                  maximum: 20
                  description: 인원 수
                  example: 4
      responses:
        '200':
          description: 예약 생성 성공
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  reservation_id:
                    type: string
                  message:
                    type: string

  /reservations/{reservation_id}:
    get:
      summary: 예약 조회
      description: 예약 번호로 예약 정보를 조회합니다
      operationId: getReservation
      parameters:
        - name: reservation_id
          in: path
          required: true
          schema:
            type: string
          description: 예약 번호
          example: 'RES001'
      responses:
        '200':
          description: 예약 조회 성공
          content:
            application/json:
              schema:
                type: object
                properties:
                  reservation_id:
                    type: string
                  customer_name:
                    type: string
                  date:
                    type: string
                  time:
                    type: string
                  party_size:
                    type: integer
                  status:
                    type: string
```

**OpenAPI 스키마 사용 방법**

- Agent builder에서 Action Group 생성 시 **Action group type**에서 `Define with API schemas`를 선택합니다.
- **Action group schema**에서 `Upload API schema`를 선택합니다.
- [[Choose file]] 버튼을 클릭하여 OpenAPI YAML 파일을 업로드합니다.
- **Action group invocation**에서 AWS Lambda 함수를 선택합니다.

**OpenAPI 스키마의 장점**

- **표준화**: OpenAPI 3.0 표준 준수로 다른 도구와 호환.
- **재사용**: 기존 API 문서를 그대로 사용 가능.
- **검증**: 스키마 기반 자동 검증으로 오류 방지.
- **문서화**: API 문서가 자동으로 생성됨.
- **버전 관리**: Git으로 스키마 버전 관리 가능.

### 문제 해결 가이드

**문제 1: Agent가 함수를 호출하지 않음**

**증상**: Agent가 대화만 하고 AWS Lambda 함수를 호출하지 않습니다.

**원인**:

- 함수 설명이 불명확하여 Agent가 언제 호출해야 할지 모름.
- 프롬프트에 함수 사용 지침이 부족함.
- 사용자 입력이 함수 호출 조건을 만족하지 않음.

**해결**:

- 함수 설명을 더 명확하고 구체적으로 작성합니다.
- 프롬프트에 "예약 요청 시 create_reservation 함수를 호출합니다" 같은 명시적 지침을 추가합니다.
- 사용자에게 더 구체적인 정보를 요청하도록 프롬프트를 수정합니다.
- Agent 테스트 시 Trace를 활성화하여 Agent의 사고 과정을 확인합니다.

**문제 2: AWS Lambda 함수 응답 파싱 오류**

**증상**: Agent가 AWS Lambda 함수 응답을 이해하지 못하고 오류를 반환합니다.

**원인**:

- AWS Lambda 함수가 잘못된 형식으로 응답을 반환함.
- JSON 직렬화 오류.
- 응답 구조가 Amazon Bedrock Agent 요구사항과 맞지 않음.

**해결**:

- AWS Lambda 함수 응답이 올바른 형식인지 확인합니다:

```python
return {
    'messageVersion': '1.0',
    'response': {
        'actionGroup': action_group,
        'function': function_name,
        'functionResponse': {
            'responseBody': {
                'TEXT': {
                    'body': json.dumps(result)  # JSON 문자열로 변환
                }
            }
        }
    }
}
```

- Amazon CloudWatch Logs에서 AWS Lambda 함수 로그를 확인합니다.
- 응답 데이터가 JSON 직렬화 가능한지 확인합니다 (datetime 객체는 문자열로 변환).

**문제 3: "Access Denied" 오류**

**증상**: Agent가 AWS Lambda 함수를 호출할 때 권한 오류가 발생합니다.

**원인**:

- Amazon Bedrock Agent에 AWS Lambda 함수 호출 권한이 없음.
- AWS Lambda 함수에 리소스 기반 정책이 설정되지 않음.

**해결**:

- AWS Lambda 함수 콘솔로 이동합니다.
- **Configuration** 탭을 선택합니다.
- 왼쪽 메뉴에서 **Permissions**를 선택합니다.
- **Resource-based policy statements** 섹션에서 Amazon Bedrock Agent 권한을 확인합니다.
- 권한이 없으면 다음 명령어로 추가합니다:

```bash
aws lambda add-permission \
  --function-name BedrockAgentReservationHandler \
  --statement-id AllowBedrockInvoke \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn arn:aws:bedrock:ap-northeast-2:YOUR_ACCOUNT_ID:agent/YOUR_AGENT_ID
```

**문제 4: Knowledge Base 검색 결과가 부정확함**

**증상**: Agent가 Knowledge Base에서 관련 없는 문서를 검색합니다.

**원인**:

- 문서 청킹이 적절하지 않음.
- 임베딩 모델이 한국어를 잘 지원하지 않음.
- 검색 쿼리가 모호함.

**해결**:

- Knowledge Base 설정에서 청크 크기를 조정합니다 (300 → 500 토큰).
- 임베딩 모델을 Cohere Embed Multilingual v3로 변경합니다.
- 문서에 메타데이터를 추가하여 필터링을 활성화합니다.
- 사용자 질문을 더 구체적으로 유도하도록 프롬프트를 수정합니다.

**문제 5: 응답 속도가 느림**

**증상**: Agent 응답에 10초 이상 소요됩니다.

**원인**:

- AWS Lambda 함수 콜드 스타트.
- Amazon DynamoDB 쿼리 최적화 부족.
- Knowledge Base 검색 시간.
- 프롬프트가 너무 길어 토큰 처리 시간 증가.

**해결**:

- AWS Lambda 함수에 Provisioned Concurrency를 설정하여 콜드 스타트 방지합니다.
- Amazon DynamoDB 테이블에 적절한 인덱스를 생성합니다.
- Knowledge Base 검색 결과 수를 줄입니다 (기본 5개 → 3개).
- 프롬프트를 간결하게 수정하여 토큰 수를 줄입니다.
- 더 빠른 모델(Claude Haiku 4.5)을 사용합니다.

### 추가 모범 사례

**1. 프롬프트 버전 관리**

- 프롬프트를 Git으로 버전 관리합니다.
- 변경 사항을 추적하고 롤백할 수 있도록 합니다.
- A/B 테스트를 통해 최적의 프롬프트를 찾습니다.

**2. 로깅 및 모니터링**

- 모든 Agent 대화를 Amazon CloudWatch Logs에 기록합니다.
- 사용자 만족도를 추적하기 위한 피드백 메커니즘을 구현합니다.
- 자주 발생하는 오류를 분석하여 프롬프트를 개선합니다.

**3. 점진적 배포**

- Agent 별칭을 사용하여 카나리 배포를 수행합니다.
- 일부 사용자에게만 새 버전을 제공하고 모니터링합니다.
- 문제가 없으면 전체 사용자에게 배포합니다.

**4. 사용자 경험 최적화**

- 응답 시간을 최소화합니다 (목표: 3초 이내).
- 긴 응답은 스트리밍으로 제공하여 체감 속도를 개선합니다.
- 오류 발생 시 친절한 안내 메시지를 제공합니다.
- 사용자가 쉽게 이해할 수 있는 언어를 사용합니다.

**5. 데이터 프라이버시**

- 민감한 정보는 로그에 기록하지 않습니다.
- 개인정보는 암호화하여 저장합니다.
- 데이터 보관 기간을 설정하고 자동 삭제합니다.
- GDPR, CCPA 등 규정을 준수합니다.

**6. 테스트 자동화**

- 회귀 테스트를 자동화하여 변경 사항이 기존 기능에 영향을 주지 않는지 확인합니다.
- 다양한 시나리오를 테스트 케이스로 작성합니다.
- CI/CD 파이프라인에 테스트를 통합합니다.

**7. 비용 모니터링**

- AWS Cost Explorer로 Amazon Bedrock 사용 비용을 추적합니다.
- 예산 알림을 설정하여 예상치 못한 비용 증가를 감지합니다.
- 사용량이 많은 시간대를 분석하여 최적화합니다.
