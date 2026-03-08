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
> - **권장 리전**: US East (N. Virginia) 또는 US West (Oregon)
> - Week 14-2에서 생성한 Knowledge Base를 연결하려면 같은 리전을 사용해야 합니다
> - Amazon Bedrock Agent는 모든 모델이 지원되는 리전에서 사용합니다

이 실습에서는 Amazon Bedrock Agent를 사용하여 QuickTable 레스토랑 예약 시스템의 지능형 챗봇을 구축합니다. 고객이 자연어로 대화하며 예약을 관리할 수 있는 AI 어시스턴트를 완성합니다. AWS Lambda 함수를 Action Group으로 연결하여 예약 조회, 생성, 취소 등의 실제 작업을 수행하고, Week 14-2에서 생성한 Knowledge Base를 통합하여 레스토랑 정보 질문에도 답변할 수 있도록 합니다. 대화형 AI의 핵심 개념과 프롬프트 엔지니어링 기법을 학습합니다.

> [!DOWNLOAD]
> [week14-3-bedrock-agent-lab.zip](/files/week14/week14-3-bedrock-agent-lab.zip)
>
> - `bedrock_agent_lambda.py` - Amazon Bedrock Agent 예약 관리 AWS Lambda 함수 (태스크 2에서 AWS Lambda 함수 코드로 사용, 상세한 주석 및 DocString 포함)
>
> **관련 태스크:**
>
> - 태스크 2: AWS Lambda 함수를 생성하여 예약 관리 기능 구현 (bedrock_agent_lambda.py를 참고하여 Amazon Bedrock Agent Action Group 핸들러 및 예약 관리 로직 구현)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
>
> **예상 비용** (US East 리전 기준):
>
> | 리소스                       | 타입            | 비용           |
> | ---------------------------- | --------------- | -------------- |
> | Amazon Bedrock Agent         | 요청당          | $0.00025-0.002 |
> | 모델 추론 (Claude 3 Sonnet)  | 1,000 입력 토큰 | $0.003         |
> | 모델 추론 (Claude 3 Sonnet)  | 1,000 출력 토큰 | $0.015         |
> | OpenSearch Serverless (14-2) | 시간당 (2 OCU)  | $0.48          |
> | **총 예상 (14-2 포함)**      | **시간당**      | **약 $0.48**   |
>
> **⚠️ 중요**: Week 14-2에서 생성한 OpenSearch Serverless 컬렉션이 남아있다면 시간당 $0.48 비용이 계속 발생합니다.
> 14-2 실습 후 리소스를 정리하지 않았다면 반드시 확인하고 삭제합니다.

## 태스크 1: Amazon DynamoDB 테이블을 생성하여 QuickTable 예약 데이터 저장

이 태스크에서는 QuickTable 챗봇이 관리할 예약 데이터를 저장할 Amazon DynamoDB 테이블을 생성합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `DynamoDB`을 입력하고 선택합니다.
2. [[Create table]] 버튼을 클릭합니다.
3. **Table name**에 `RestaurantReservations`를 입력합니다.
4. **Partition key**에 `reservationId`를 입력합니다.
5. **Data type**은 `String`을 선택합니다.
6. **Table settings**에서 `Customize settings`를 선택합니다.
7. **Read/write capacity settings**에서 `On-demand`를 선택합니다.
8. **Encryption at rest**는 `Owned by Amazon DynamoDB`를 선택합니다.
9. 아래로 스크롤하여 **Tags - optional** 섹션을 확인합니다.
10. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-3`    |
| `CreatedBy` | `Student` |

11. [[Create table]] 버튼을 클릭합니다.
12. 테이블 생성이 완료될 때까지 기다립니다.

> [!NOTE]
> 테이블 생성에 10-20초가 소요됩니다. 상태가 "Active"로 변경될 때까지 기다립니다.

13. 생성된 테이블을 클릭합니다.
14. **Actions** > `Create item`을 선택합니다.
15. **Attributes** 섹션에서 다음 값을 입력합니다:
	- **reservationId**: `RES001`
16. [[Add new attribute]] 버튼을 클릭합니다.
17. `String`을 선택합니다.
18. **Attribute name**에 `customerName`을 입력합니다.
19. **Value**에 `김철수`를 입력합니다.
20. 같은 방식으로 다음 속성들을 추가합니다:
	- `date` (String): `2026-02-15`
	- `time` (String): `19:00`
	- `partySize` (Number): `4`
	- `status` (String): `confirmed`
21. [[Create item]] 버튼을 클릭합니다.
22. 같은 방식으로 다음 샘플 예약 데이터를 추가합니다:

**예약 2:**

- `reservationId` (String): `RES002`
- `customerName` (String): `이영희`
- `date` (String): `2026-02-16`
- `time` (String): `18:30`
- `partySize` (Number): `2`
- `status` (String): `confirmed`

**예약 3:**

- `reservationId` (String): `RES003`
- `customerName` (String): `박민수`
- `date` (String): `2026-02-17`
- `time` (String): `20:00`
- `partySize` (Number): `6`
- `status` (String): `confirmed`

✅ **태스크 완료**: Amazon DynamoDB 테이블이 생성되고 샘플 데이터가 추가되었습니다.

## 태스크 2: AWS Lambda 함수를 생성하여 QuickTable 예약 관리 기능 구현

이 태스크에서는 QuickTable 챗봇이 예약을 조회하고 생성할 수 있도록 AWS Lambda 함수를 생성합니다.

23. AWS Management Console에 로그인한 후 상단 검색창에 `Lambda`을 입력하고 선택합니다.
24. [[Create function]] 버튼을 클릭합니다.
25. **Author from scratch**를 선택합니다.
26. **Function name**에 `BedrockAgentReservationHandler`를 입력합니다.
27. **Runtime**에서 `Python 3.12`를 선택합니다.
28. **Architecture**는 `x86_64`를 선택합니다.
29. [[Create function]] 버튼을 클릭합니다.
30. 함수 생성이 완료될 때까지 기다립니다.
31. **Code** 탭에서 기본 코드를 모두 삭제합니다.
32. 다음 코드를 복사하여 붙여넣습니다:

> [!TIP]
> 다운로드한 `bedrock_agent_lambda.py` 파일의 코드를 참고할 수 있습니다. 파일에는 상세한 주석과 DocString이 포함되어 있어 코드 이해에 도움이 됩니다.

```python
"""
QuickTable Amazon Bedrock Agent 예약 관리 AWS Lambda 함수

이 AWS Lambda 함수는 Amazon Bedrock Agent의 Action Group으로 동작하며,
QuickTable 레스토랑 예약 시스템의 예약 관리 기능을 제공합니다.

주요 기능:
- 예약 조회 (get_reservation)
- 예약 생성 (create_reservation)
- 예약 목록 조회 (list_reservations)
- 예약 취소 (cancel_reservation)

환경 변수:
- TABLE_NAME: Amazon DynamoDB 테이블 이름 (기본값: RestaurantReservations)
"""

import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Amazon DynamoDB 리소스 초기화
# 환경 변수에서 테이블 이름을 가져오거나 기본값 사용
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'RestaurantReservations'))

def lambda_handler(event, context):
    """
    AWS Lambda 함수의 메인 핸들러

    Amazon Bedrock Agent로부터 요청을 받아 적절한 함수로 라우팅하고,
    결과를 Amazon Bedrock Agent 응답 형식으로 반환합니다.

    Args:
        event (dict): Amazon Bedrock Agent로부터 전달된 이벤트 객체
            - agent (dict): Agent 정보 (name, id, alias, version)
            - actionGroup (str): Action Group 이름
            - function (str): 호출할 함수 이름
            - parameters (list): 함수 파라미터 목록
            - sessionId (str): 세션 ID
            - sessionAttributes (dict): 세션 속성
        context (object): AWS Lambda 실행 컨텍스트

    Returns:
        dict: Amazon Bedrock Agent 응답 형식의 딕셔너리
            - messageVersion (str): 메시지 버전 (1.0)
            - response (dict): 응답 객체
                - actionGroup (str): Action Group 이름
                - function (str): 실행된 함수 이름
                - functionResponse (dict): 함수 실행 결과

    Security Note:
        이벤트 로그에 사용자 입력이 포함될 수 있습니다.
        프로덕션 환경에서는 개인정보(PII)가 Amazon CloudWatch Logs에 기록되지 않도록 주의해야 합니다.

    Example:
        >>> event = {
        ...     'actionGroup': 'ReservationActions',
        ...     'function': 'get_reservation',
        ...     'parameters': [{'name': 'reservationId', 'value': 'RES001'}]
        ... }
        >>> lambda_handler(event, {})
        {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': 'ReservationActions',
                'function': 'get_reservation',
                'functionResponse': {...}
            }
        }
    """
    # 디버깅을 위한 이벤트 로깅
    # 주의: 사용자 입력이 포함될 수 있으므로 프로덕션에서는 민감 정보 마스킹 필요
    print(f"Received event: {json.dumps(event)}")

    # Amazon Bedrock Agent에서 전달된 정보 추출
    agent = event.get('agent', {})  # Agent 정보 (선택사항)
    action_group = event.get('actionGroup', '')  # Action Group 이름
    function = event.get('function', '')  # 호출할 함수 이름
    parameters = event.get('parameters', [])  # 파라미터 리스트

    # 파라미터를 딕셔너리로 변환
    # [{'name': 'key', 'value': 'val'}] → {'key': 'val'}
    params = {p['name']: p['value'] for p in parameters}

    # 디버깅을 위한 함수 호출 정보 로깅
    print(f"Action: {action_group}, Function: {function}")
    print(f"Parameters: {params}")

    # 함수 라우팅: 함수 이름에 따라 적절한 핸들러 호출
    if function == 'get_reservation':
        result = get_reservation(params)
    elif function == 'create_reservation':
        result = create_reservation(params)
    elif function == 'list_reservations':
        result = list_reservations(params)
    elif function == 'cancel_reservation':
        result = cancel_reservation(params)
    else:
        # 알 수 없는 함수 이름인 경우 오류 반환
        result = {
            'error': f'Unknown function: {function}'
        }

    # Amazon Bedrock Agent 응답 형식으로 변환
    # Agent는 이 형식을 파싱하여 사용자에게 응답 생성
    response = {
        'messageVersion': '1.0',  # 메시지 버전 (필수)
        'response': {
            'actionGroup': action_group,  # Action Group 이름 (필수)
            'function': function,  # 실행된 함수 이름 (필수)
            'functionResponse': {
                'responseBody': {
                    'TEXT': {
                        # 결과를 JSON 문자열로 변환
                        # ensure_ascii=False: 한글 유지
                        'body': json.dumps(result, ensure_ascii=False)
                    }
                }
            }
        }
    }

    # 디버깅을 위한 응답 로깅
    print(f"Response: {json.dumps(response, ensure_ascii=False)}")
    return response

def get_reservation(params):
    """
    예약 번호로 예약 정보를 조회합니다.

    Args:
        params (dict): 함수 파라미터
            - reservationId (str): 조회할 예약 번호 (예: RES001)

    Returns:
        dict: 조회 결과
            성공 시:
                - success (bool): True
                - reservation (dict): 예약 정보
                    - reservationId (str): 예약 번호
                    - customerName (str): 고객 이름
                    - date (str): 예약 날짜 (YYYY-MM-DD)
                    - time (str): 예약 시간 (HH:MM)
                    - partySize (int): 인원수
                    - status (str): 예약 상태 (confirmed/cancelled)
            실패 시:
                - success (bool): False
                - message (str): 오류 메시지
                - error (str): 예외 메시지 (예외 발생 시)

    Example:
        >>> get_reservation({'reservationId': 'RES001'})
        {
            'success': True,
            'reservation': {
                'reservationId': 'RES001',
                'customerName': '김철수',
                'date': '2024-02-15',
                'time': '19:00',
                'partySize': 4,
                'status': 'confirmed'
            }
        }
    """
    # 파라미터에서 예약 번호 추출
    reservation_id = params.get('reservationId')

    try:
        # Amazon DynamoDB에서 예약 정보 조회
        # get_item: Primary Key로 단일 항목 조회 (빠름)
        response = table.get_item(Key={'reservationId': reservation_id})

        # 조회 결과 확인
        if 'Item' in response:
            # 예약이 존재하는 경우
            item = response['Item']
            return {
                'success': True,
                'reservation': {
                    'reservationId': item['reservationId'],
                    'customerName': item['customerName'],
                    'date': item['date'],
                    'time': item['time'],
                    'partySize': int(item['partySize']),  # Decimal → int 변환
                    'status': item['status']
                }
            }
        else:
            # 예약이 존재하지 않는 경우
            return {
                'success': False,
                'message': f'예약 번호 {reservation_id}를 찾을 수 없습니다.'
            }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def create_reservation(params):
    """
    새로운 예약을 생성합니다.

    Args:
        params (dict): 함수 파라미터
            - customerName (str): 고객 이름
            - date (str): 예약 날짜 (YYYY-MM-DD)
            - time (str): 예약 시간 (HH:MM)
            - partySize (str|int): 인원수 (기본값: 2)

    Returns:
        dict: 생성 결과
            성공 시:
                - success (bool): True
                - message (str): 성공 메시지
                - reservation (dict): 생성된 예약 정보
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지

    Example:
        >>> create_reservation({
        ...     'customerName': '김철수',
        ...     'date': '2024-02-15',
        ...     'time': '19:00',
        ...     'partySize': '4'
        ... })
        {
            'success': True,
            'message': '김철수님의 예약이 완료되었습니다.',
            'reservation': {
                'reservationId': 'RESABC12345',
                'customerName': '김철수',
                'date': '2024-02-15',
                'time': '19:00',
                'partySize': 4,
                'status': 'confirmed'
            }
        }
    """
    import uuid

    # 고유한 예약 번호 생성
    # RES + UUID 앞 8자리 (대문자)
    # 예: RESABC12345
    reservation_id = f"RES{str(uuid.uuid4())[:8].upper()}"

    # 파라미터에서 예약 정보 추출
    customer_name = params.get('customerName')
    date = params.get('date')
    time = params.get('time')
    party_size = int(params.get('partySize', 2))  # 기본값: 2명

    try:
        # Amazon DynamoDB에 예약 정보 저장
        # put_item: 새 항목 생성 또는 기존 항목 덮어쓰기
        table.put_item(Item={
            'reservationId': reservation_id,  # Primary Key
            'customerName': customer_name,
            'date': date,
            'time': time,
            'partySize': party_size,
            'status': 'confirmed',  # 초기 상태: 확정
            'createdAt': datetime.now().isoformat()  # 생성 시간 (ISO 8601 형식)
        })

        # 성공 응답 반환
        return {
            'success': True,
            'message': f'{customer_name}님의 예약이 완료되었습니다.',
            'reservation': {
                'reservationId': reservation_id,
                'customerName': customer_name,
                'date': date,
                'time': time,
                'partySize': party_size,
                'status': 'confirmed'
            }
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def list_reservations(params):
    """
    예약 목록을 조회합니다.

    특정 날짜의 예약만 조회하거나 모든 예약을 조회할 수 있습니다.

    Args:
        params (dict): 함수 파라미터
            - date (str, optional): 조회할 날짜 (YYYY-MM-DD)
                                   지정하지 않으면 모든 예약 조회

    Returns:
        dict: 조회 결과
            성공 시:
                - success (bool): True
                - count (int): 예약 개수
                - reservations (list): 예약 목록
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지

    Note:
        - 날짜 필터링은 scan 연산을 사용하므로 성능이 낮습니다
        - 프로덕션 환경에서는 GSI (Global Secondary Index)를 사용해야 합니다

    Example:
        >>> list_reservations({'date': '2024-02-15'})
        {
            'success': True,
            'count': 3,
            'reservations': [
                {'reservationId': 'RES001', 'customerName': '김철수', ...},
                {'reservationId': 'RES002', 'customerName': '이영희', ...},
                {'reservationId': 'RES003', 'customerName': '박민수', ...}
            ]
        }
    """
    # 파라미터에서 날짜 추출 (선택사항)
    date = params.get('date')

    try:
        if date:
            # 특정 날짜의 예약 조회
            # scan: 전체 테이블 스캔 (느림, 비용 높음)
            # FilterExpression: 스캔 후 필터링
            # 주의: 프로덕션에서는 GSI 사용 권장
            response = table.scan(
                FilterExpression='#d = :date',
                # ExpressionAttributeNames: 예약어 회피
                # 'date'는 Amazon DynamoDB 예약어이므로 #d로 대체
                ExpressionAttributeNames={'#d': 'date'},
                ExpressionAttributeValues={':date': date}
            )
        else:
            # 모든 예약 조회
            # scan: 전체 테이블 스캔
            response = table.scan()

        # 조회 결과에서 항목 추출
        items = response.get('Items', [])

        # 각 항목을 표준 형식으로 변환
        reservations = [
            {
                'reservationId': item['reservationId'],
                'customerName': item['customerName'],
                'date': item['date'],
                'time': item['time'],
                'partySize': int(item['partySize']),  # Decimal → int 변환
                'status': item['status']
            }
            for item in items
        ]

        # 성공 응답 반환
        return {
            'success': True,
            'count': len(reservations),
            'reservations': reservations
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def cancel_reservation(params):
    """
    예약을 취소합니다.

    예약 상태를 'cancelled'로 변경합니다.
    실제로 항목을 삭제하지 않고 상태만 변경하여 이력을 유지합니다.

    Args:
        params (dict): 함수 파라미터
            - reservationId (str): 취소할 예약 번호

    Returns:
        dict: 취소 결과
            성공 시:
                - success (bool): True
                - message (str): 성공 메시지
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지

    Note:
        - 예약이 존재하지 않아도 update_item은 성공합니다
        - 실제 환경에서는 예약 존재 여부를 먼저 확인해야 합니다

    Example:
        >>> cancel_reservation({'reservationId': 'RES001'})
        {
            'success': True,
            'message': '예약 번호 RES001가 취소되었습니다.'
        }
    """
    # 파라미터에서 예약 번호 추출
    reservation_id = params.get('reservationId')

    try:
        # Amazon DynamoDB에서 예약 상태 업데이트
        # update_item: 특정 속성만 업데이트 (효율적)
        table.update_item(
            Key={'reservationId': reservation_id},  # Primary Key
            # UpdateExpression: 업데이트할 속성 지정
            # SET: 속성 값 설정
            UpdateExpression='SET #status = :status',
            # ExpressionAttributeNames: 예약어 회피
            # 'status'는 Amazon DynamoDB 예약어이므로 #status로 대체
            ExpressionAttributeNames={'#status': 'status'},
            # ExpressionAttributeValues: 업데이트할 값
            ExpressionAttributeValues={':status': 'cancelled'}
        )

        # 성공 응답 반환
        return {
            'success': True,
            'message': f'예약 번호 {reservation_id}가 취소되었습니다.'
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }
```

33. [[Deploy]] 버튼을 클릭합니다.
34. 배포가 완료될 때까지 기다립니다.

✅ **태스크 완료**: AWS Lambda 함수가 생성되고 코드가 배포되었습니다.

## 태스크 3: AWS Lambda 실행 역할에 Amazon DynamoDB 권한 추가

이 태스크에서는 AWS Lambda 함수가 Amazon DynamoDB 테이블에 접근할 수 있도록 권한을 추가합니다.

35. **Configuration** 탭을 선택합니다.
36. 왼쪽 메뉴에서 **Permissions**를 선택합니다.
37. **Execution role** 섹션에서 역할 이름을 클릭합니다.
38. AWS IAM 역할 페이지에서 [[Add permissions]] 버튼을 클릭합니다.
39. `Attach policies`를 선택합니다.
40. 검색창에 `DynamoDB`를 입력합니다.
41. `AmazonDynamoDBFullAccess` 정책을 체크합니다.

> [!NOTE]
> 프로덕션 환경에서는 특정 테이블에만 접근할 수 있는 커스텀 정책을 사용해야 합니다.

42. [[Add permissions]] 버튼을 클릭합니다.
43. AWS Lambda 콘솔로 이동합니다.
44. `BedrockAgentReservationHandler` 함수를 선택합니다.
45. **Configuration** 탭을 선택합니다.
46. 왼쪽 메뉴에서 **Environment variables**를 선택합니다.
47. [[Edit]] 버튼을 클릭합니다.
48. [[Add environment variable]] 버튼을 클릭하여 다음 환경 변수를 추가합니다:

| 변수명       | 값                       | 설명                 |
| ------------ | ------------------------ | -------------------- |
| `TABLE_NAME` | `RestaurantReservations` | Amazon DynamoDB 테이블 이름 |

49. [[Save]] 버튼을 클릭합니다.
50. 왼쪽 메뉴에서 **Tags**를 선택합니다.
51. [[Manage tags]] 버튼을 클릭합니다.
52. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-3`    |
| `CreatedBy` | `Student` |

53. [[Save changes]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS Lambda 함수에 Amazon DynamoDB 권한이 추가되고 환경 변수가 설정되었습니다.

## 태스크 4: QuickTable Amazon Bedrock Agent 생성

이 태스크에서는 QuickTable 챗봇의 핵심인 Amazon Bedrock Agent를 생성합니다.

54. Amazon Bedrock 콘솔로 이동합니다.
55. 왼쪽 메뉴에서 **Build** > **Agents**를 선택합니다.
56. [[Create Agent]] 버튼을 클릭합니다.
57. **Agent name**에 `QuickTableAssistant`를 입력합니다.
58. **Agent description**에 `QuickTable 레스토랑 예약을 관리하는 AI 어시스턴트`를 입력합니다.
59. [[Create]] 버튼을 클릭합니다.

> [!NOTE]
> Agent가 생성되고 Agent builder 페이지로 자동 이동합니다.

60. **Agent resource role**을 `Create and use a new service role`로 선택합니다.
61. **Select model**에서 최신 Claude 모델을 선택합니다 (예: `Anthropic Claude Sonnet 4.6` 또는 `Anthropic Claude Opus 4.6`).

> [!NOTE]
> AWS 콘솔 UI는 지속적으로 업데이트됩니다.
> "Select model" 대신 "Choose model" 또는 다른 이름으로 표시될 수 있습니다.
> 기본적으로 Amazon Bedrock Agents에 최적화된 모델만 표시됩니다.
> 모든 모델을 보려면 "Amazon Bedrock Agents optimized" 체크를 해제합니다.
> 
> **권장 모델 (2026년 3월 기준)**:
> - **Claude Sonnet 4.6**: 성능과 비용의 균형 (권장, 2026년 2월 출시)
> - **Claude Opus 4.6**: 최고 성능, 복잡한 대화에 최적 (2026년 2월 출시)
> - **Claude Haiku 4.5**: 빠른 응답 속도, 저렴한 비용
>
> 한국어 대화의 경우 Claude Sonnet 4.6 또는 Claude Opus 4.6이 권장됩니다.

62. **Instructions for the Agent** 섹션에 다음 프롬프트를 입력합니다:

```
당신은 QuickTable 레스토랑 예약 시스템을 관리하는 친절한 AI 어시스턴트입니다.

주요 역할:
63. 고객의 예약 요청을 받아 새로운 예약을 생성합니다.
64. 예약 번호로 기존 예약을 조회합니다.
65. 특정 날짜의 예약 목록을 확인합니다.
66. 예약 취소 요청을 처리합니다.

대화 규칙:
- 항상 정중하고 친절하게 응답합니다
- 예약 생성 시 고객 이름, 날짜, 시간, 인원수를 반드시 확인합니다
- 날짜는 YYYY-MM-DD 형식으로 저장합니다
- 시간은 HH:MM 형식(24시간)으로 저장합니다
- 예약이 완료되면 예약 번호를 안내합니다
- 정보가 부족하면 고객에게 추가 정보를 요청합니다

응답 스타일:
- 간결하고 명확하게 답변합니다
- 이모지를 적절히 사용하여 친근감을 표현합니다
- 예약 정보는 구조화된 형식으로 제공합니다
```

67. [[Next]] 버튼을 클릭합니다.

> [!NOTE]
> Agent builder에서 Action groups, Knowledge bases, Guardrails 등을 설정할 수 있습니다.

68. **Action groups** 섹션에서 [[Add]] 버튼을 클릭합니다.
69. **Action group details**에서 다음을 입력합니다:
	- **Action group name**: `QuickTableReservationActions`
	- **Action group description**: `QuickTable 예약 관리 기능`
70. **Action group type**에서 `Define with function details`를 선택합니다.

> [!NOTE]
> AWS 콘솔 UI는 지속적으로 업데이트됩니다.
> "Define with function details" 옵션이 보이지 않는 경우:
>
> - "Define with API schemas" 대신 사용 가능한 옵션을 선택합니다
> - 또는 OpenAPI 스키마 파일을 업로드하는 방식을 사용할 수 있습니다 (참고 섹션 참조)

71. **Action group invocation**에서 `Select an existing AWS Lambda function`을 선택합니다.
72. **AWS Lambda function**에서 `BedrockAgentReservationHandler`를 선택합니다.

> [!NOTE]
> AWS Lambda 함수를 선택하면 Amazon Bedrock Agent가 AWS Lambda를 호출할 수 있도록 리소스 기반 정책이 자동으로 추가됩니다.
> 자동 추가가 실패하는 경우, AWS Lambda 콘솔의 Configuration > Permissions > Resource-based policy statements에서 수동으로 추가해야 합니다.
> 참고 섹션에서 리소스 기반 정책 예시를 확인할 수 있습니다.

73. **Action group functions** 섹션에서 [[Add function]] 버튼을 클릭합니다.

**함수 1: get_reservation**

- **Function name**: `get_reservation`
- **Function description**: `예약 번호로 예약 정보를 조회합니다`
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

| Parameter Name  | Type   | Required | Description            |
| --------------- | ------ | -------- | ---------------------- |
| `reservationId` | string | ✅ 필수  | 예약 번호 (예: RES001) |

74. [[Add function]] 버튼을 다시 클릭하여 두 번째 함수를 추가합니다:

**함수 2: create_reservation**

- **Function name**: `create_reservation`
- **Function description**: `새로운 예약을 생성합니다`
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터들을 하나씩 추가합니다:

| Parameter Name | Type    | Required | Description                    |
| -------------- | ------- | -------- | ------------------------------ |
| `customerName` | string  | ✅ 필수  | 고객 이름                      |
| `date`         | string  | ✅ 필수  | 예약 날짜 (YYYY-MM-DD 형식)    |
| `time`         | string  | ✅ 필수  | 예약 시간 (HH:MM 형식, 24시간) |
| `partySize`    | integer | ✅ 필수  | 예약 인원수                    |

75. [[Add function]] 버튼을 다시 클릭하여 세 번째 함수를 추가합니다:

**함수 3: list_reservations**

- **Function name**: `list_reservations`
- **Function description**: `예약 목록을 조회합니다`
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

| Parameter Name | Type   | Required | Description                                                   |
| -------------- | ------ | -------- | ------------------------------------------------------------- |
| `date`         | string | ❌ 선택  | 조회할 날짜 (YYYY-MM-DD 형식, 지정하지 않으면 모든 예약 조회) |

76. 마지막으로 네 번째 함수를 추가합니다:

**함수 4: cancel_reservation**

- **Function name**: `cancel_reservation`
- **Function description**: `예약을 취소합니다`
- **Parameters**: [[Add parameter]] 버튼을 클릭하여 다음 파라미터를 추가합니다:

| Parameter Name  | Type   | Required | Description                   |
| --------------- | ------ | -------- | ----------------------------- |
| `reservationId` | string | ✅ 필수  | 취소할 예약 번호 (예: RES001) |

77. 모든 함수 추가가 완료되면 [[Create]] 버튼을 클릭합니다.
78. Action group이 추가되었는지 확인합니다.

> [!NOTE]
> Action group 생성 후 Agent builder 페이지로 이동합니다.

79. **Knowledge bases** 섹션에서 [[Add]] 버튼을 클릭합니다 (Week 14-2 완료 시).

> [!IMPORTANT]
> 이 단계는 Week 14-2를 완료한 경우에만 수행합니다.
> Week 14-2에서 생성한 Knowledge Base를 연결하여 레스토랑 정보 질문에 답변할 수 있도록 합니다.
> 14-2 실습을 완료하지 않았다면 이 단계(23-27)를 건너뛰고 28번으로 이동합니다.

80. **Select knowledge base**에서 `quicktable-restaurant-kb`를 선택합니다 (14-2에서 생성).
81. **Knowledge base instructions for Agent**에 다음을 입력합니다:

```
이 Knowledge Base는 QuickTable 레스토랑의 메뉴, 가격, 영업 시간, 위치, FAQ 정보를 포함합니다.
고객이 메뉴, 가격, 영업 시간, 위치, 주차, 특별 서비스 등에 대해 질문하면 이 Knowledge Base를 검색하여 답변합니다.
```

82. [[Add]] 버튼을 클릭합니다.
83. Knowledge base가 추가되었는지 확인합니다.

> [!NOTE]
> Knowledge Base를 연결하면 Agent가 예약 관리뿐만 아니라 레스토랑 정보 질문에도 답변할 수 있습니다.

84. 페이지 상단의 [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Agent 설정이 저장됩니다. 이제 Agent를 준비하고 테스트할 수 있습니다.

✅ **태스크 완료**: Amazon Bedrock Agent가 생성되고 Action Group이 설정되었습니다.

## 태스크 5: Agent 준비 및 테스트

이 태스크에서는 Agent를 준비하고 테스트 콘솔에서 대화를 시도합니다.

85. Agent 상세 페이지에서 [[Prepare]] 버튼을 클릭합니다.
86. Agent 준비가 완료될 때까지 기다립니다.

> [!NOTE]
> Agent 준비에 30초-1분이 소요됩니다. 이 과정에서 Agent의 프롬프트와 Action Group이 최적화됩니다.

> [!IMPORTANT]
> Action Group, Knowledge Base, 또는 Instructions를 수정한 경우 반드시 [[Prepare]] 버튼을 다시 클릭해야 변경사항이 반영됩니다.
> Prepare를 실행하지 않으면 이전 버전의 Agent가 계속 사용됩니다.

87. 준비가 완료되면 오른쪽에 **Test** 패널이 표시됩니다.
88. Test 패널의 입력창에 다음 메시지를 입력합니다:

```
안녕합니다! 2월 15일 저녁 7시에 4명 예약하고 싶습니다.
```

89. Enter 키를 누르거나 전송 버튼을 클릭합니다.
90. Agent의 응답을 확인합니다.

> [!OUTPUT]
> Agent 응답 예시:
>
> ```
> 안녕합니다! 😊 예약을 도와드리겠습니다.
>
> 예약 정보를 확인합니다:
> - 날짜: 2024-02-15
> - 시간: 19:00
> - 인원: 4명
>
> 고객님의 성함을 알려주시겠어요?
> ```

91. 다음 메시지를 입력합니다:

```
김철수입니다.
```

92. Agent가 예약을 생성하고 예약 번호를 제공하는지 확인합니다.

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
> - 고객명: 김철수
> - 날짜: 2024-02-15
> - 시간: 19:00
> - 인원: 4명
> - 상태: 확정
>
> 예약 번호를 꼭 기억합니다!
> ```

93. 예약 조회를 테스트합니다:

```
방금 만든 예약 정보를 확인하고 싶어요.
```

94. Agent가 예약 번호를 요청하는지 확인합니다.
95. 이전에 받은 예약 번호를 입력합니다.
96. Agent가 예약 정보를 정확히 조회하는지 확인합니다.

> [!NOTE]
> 예약 번호는 UUID 기반으로 생성되므로 실제 응답의 예약 번호는 위 예시와 다릅니다.
> 또한 생성형 AI의 특성상 날짜 해석이 다를 수 있습니다 (예: "2월 15일" → "2026-02-15" 또는 "2024-02-15").
> 실제 저장된 날짜는 Amazon DynamoDB 테이블에서 확인할 수 있습니다.

97. **Show trace** 토글을 활성화합니다.
98. 새로운 메시지를 입력합니다:

```
2월 15일 예약 목록을 보여주세요.
```

98. Trace 패널에서 Agent의 사고 과정을 확인합니다:
	- **Pre-processing**: 사용자 입력 분석
	- **Orchestration**: 어떤 함수를 호출할지 결정
	- **Action invocation**: AWS Lambda 함수 호출
	- **Post-processing**: 응답 생성

> [!NOTE]
> Trace를 통해 Agent가 어떻게 의사결정을 하는지 이해할 수 있습니다.

100. 예약 취소를 테스트합니다:

```
예약을 취소하고 싶어요.
```

101. Agent가 예약 번호를 요청하는지 확인합니다.
102. 예약 번호를 입력하고 취소가 정상적으로 처리되는지 확인합니다.

> [!NOTE]
> `cancel_reservation` 함수는 예약이 존재하지 않아도 성공 응답을 반환합니다.
> 이는 Amazon DynamoDB의 `update_item` 동작 특성 때문입니다.
> 프로덕션 환경에서는 예약 존재 여부를 먼저 확인하는 로직을 추가해야 합니다.

103. Knowledge Base 연동을 테스트합니다 (14-2 완료 시):

```
안심 스테이크 가격이 얼마인가요?
```

104. Agent가 Knowledge Base를 검색하여 메뉴 가격을 답변하는지 확인합니다.

> [!OUTPUT]
> Agent 응답 예시:
>
> ```
> 안심 스테이크(200g)는 38,000원입니다. 😊
> 미디엄 레어로 추천되며, 감자 퓨레와 구운 야채가 포함되어 있습니다.
> ```

105. 추가 질문을 테스트합니다:

```
주차가 가능한가요?
```

106. Agent가 Knowledge Base에서 주차 정보를 검색하여 답변하는지 확인합니다.

✅ **태스크 완료**: Agent가 정상적으로 작동하며 예약 관리 기능을 수행합니다.

## 태스크 6: Agent 별칭 생성 및 배포

이 태스크에서는 Agent의 버전을 관리하고 프로덕션 환경에 배포하기 위한 별칭을 생성합니다.

107. Agent 상세 페이지 상단에서 **Aliases** 탭을 선택합니다.
108. [[Create alias]] 버튼을 클릭합니다.
109. **Alias details**에서 다음을 입력합니다:
	- **Alias name**: `production`
	- **Alias description**: `프로덕션 환경용 Agent`
110. **Version** 섹션에서 `Create a new version`을 선택합니다.
111. [[Create alias]] 버튼을 클릭합니다.
112. 별칭 생성이 완료될 때까지 기다립니다.

> [!NOTE]
> 별칭을 사용하면 Agent의 여러 버전을 관리하고 안전하게 배포할 수 있습니다.

113. 생성된 별칭을 클릭합니다.
114. **Alias ARN**을 복사하여 메모장에 저장합니다.

> [!NOTE]
> 이 ARN은 애플리케이션에서 Agent를 호출할 때 사용됩니다.

✅ **태스크 완료**: Agent 별칭이 생성되고 배포되었습니다.

## 태스크 7: AWS Lambda 함수로 Agent 호출 테스트

이 태스크에서는 AWS Lambda 함수를 생성하여 프로그래밍 방식으로 Agent를 호출하는 방법을 학습합니다.

115. AWS Lambda 콘솔로 이동합니다.
116. [[Create function]] 버튼을 클릭합니다.
117. **Function name**에 `BedrockAgentInvoker`를 입력합니다.
118. **Runtime**에서 `Python 3.12`를 선택합니다.
119. [[Create function]] 버튼을 클릭합니다.
120. 함수 생성이 완료되면 **Configuration** 탭을 선택합니다.
121. 왼쪽 메뉴에서 **General configuration**을 선택합니다.
122. [[Edit]] 버튼을 클릭합니다.
123. **Timeout**을 `30` 초로 변경합니다.

> [!NOTE]
> Amazon Bedrock Agent 호출은 응답 생성에 시간이 걸립니다 (일반적으로 5-30초).
> AWS Lambda 기본 타임아웃(3초)으로는 부족하므로 최소 30초 이상으로 설정해야 합니다.
> Agent가 Knowledge Base를 검색하거나 여러 Action을 수행하는 경우 더 긴 시간이 필요할 수 있습니다.

124. [[Save]] 버튼을 클릭합니다.
125. **Code** 탭을 선택합니다.
126. 코드 편집기에 다음 코드를 입력합니다:

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
    user_input = event.get('input', '안녕합니다')

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

127. [[Deploy]] 버튼을 클릭합니다.
128. **Configuration** 탭을 선택합니다.
129. 왼쪽 메뉴에서 **Permissions**를 선택합니다.
130. 실행 역할에 Amazon Bedrock 권한을 추가합니다:

- [[Add permissions]] > `Attach policies`
- `AmazonBedrockFullAccess` 검색 및 체크
- [[Add permissions]] 클릭

> [!NOTE]
> 프로덕션 환경에서는 `bedrock:InvokeAgent` 권한만 포함하는 커스텀 정책을 사용해야 합니다.
> 참고 섹션에서 최소 권한 정책 예시를 확인할 수 있습니다.

131. 왼쪽 메뉴에서 **Environment variables**를 선택합니다.
132. [[Edit]] 버튼을 클릭합니다.
133. [[Add environment variable]] 버튼을 클릭하여 다음 환경 변수들을 추가합니다:

| 변수명           | 값               | 설명                                                                  |
| ---------------- | ---------------- | --------------------------------------------------------------------- |
| `AGENT_ID`       | (Agent ID 입력)  | Amazon Bedrock Agent ID (Agent 상세 페이지의 Agent overview에서 확인) |
| `AGENT_ALIAS_ID` | (별칭 ID 입력)   | 별칭 ID (별칭 상세 페이지에서 확인, ARN이 아닌 ID만 입력)             |
| `BEDROCK_REGION` | `ap-northeast-2` | Amazon Bedrock Agent가 배포된 리전                                           |

134. [[Save]] 버튼을 클릭합니다.

> [!IMPORTANT]
> `AGENT_ALIAS_ID`는 별칭 ARN 전체가 아닌 ID 부분만 입력합니다.
>
> **올바른 예시**:
>
> - 별칭 ARN: `arn:aws:bedrock:ap-northeast-2:123456789012:agent-alias/ABCDEFGHIJ/TSTALIASID`
> - 입력할 값: `TSTALIASID` (ARN의 마지막 부분만)
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

135. [[Save]] 버튼을 클릭합니다.
136. [[Manage tags]] 버튼을 클릭합니다.
137. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `14-3`    |
| `CreatedBy` | `Student` |

138. [[Save changes]] 버튼을 클릭합니다.

139. **Test** 탭을 선택합니다.
140. [[Test]] 버튼을 클릭합니다.
141. **Event name**에 `TestEvent`를 입력합니다.
142. 다음 테스트 이벤트를 입력합니다:

```json
{
  "session_id": "test-001",
  "input": "2026-02-20 저녁 8시에 2명 예약하고 싶어요. 이름은 이영희입니다."
}
```

> [!NOTE]
> 테스트 이벤트의 날짜는 실습 당일 이후 날짜로 변경합니다.
> 위 예시는 2026-02-20으로 설정되어 있습니다.
> 과거 날짜로 예약을 생성하면 실제 시스템에서는 거부될 수 있습니다.

143. [[Save]] 버튼을 클릭합니다.
144. [[Test]] 버튼을 클릭하여 함수를 실행합니다.
145. 실행 결과를 확인합니다.

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

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon DynamoDB 테이블을 생성하고 QuickTable 예약 데이터를 저장했습니다
- AWS Lambda 함수로 QuickTable 예약 관리 기능을 구현했습니다
- Amazon Bedrock Agent를 생성하고 QuickTable Action Group을 설정했습니다
- Week 14-2에서 생성한 Knowledge Base를 Agent에 연결했습니다
- Agent를 테스트하고 대화형 QuickTable 예약 시스템을 확인했습니다
- Agent 별칭을 생성하여 프로덕션 환경에 배포했습니다
- AWS Lambda 함수로 Agent를 프로그래밍 방식으로 호출했습니다

Week 14-2에서 구축한 Knowledge Base와 14-3의 Agent를 결합하여 QuickTable 레스토랑 예약 시스템이 완성되었습니다. 고객은 자연어로 대화하며 예약을 생성하고 관리할 수 있으며, 레스토랑 정보에 대한 질문에도 답변받을 수 있습니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `14-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### 1. Amazon Bedrock Agent 삭제

8. AWS Management Console에 로그인한 후 상단 검색창에 `Bedrock`을 입력하고 선택합니다.
9. 왼쪽 메뉴에서 **Orchestration** > **Agents**를 선택합니다.
10. `QuickTableAssistant` Agent를 선택합니다.
11. [[Delete]] 버튼을 클릭합니다.
12. 확인 창에서 `delete`를 입력합니다.
13. [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Agent를 삭제하면 모든 별칭과 버전도 함께 삭제됩니다.

#### 2. AWS Lambda 함수 삭제

14. AWS Management Console에 로그인한 후 상단 검색창에 `Lambda`을 입력하고 선택합니다.
15. `BedrockAgentReservationHandler` 함수를 선택합니다.
16. **Actions** > `Delete`를 선택합니다.
17. 확인 창에서 `delete`를 입력합니다.
18. [[Delete]] 버튼을 클릭합니다.
19. 같은 방식으로 `BedrockAgentInvoker` 함수도 삭제합니다.

#### 3. Amazon DynamoDB 테이블 삭제

20. AWS Management Console에 로그인한 후 상단 검색창에 `DynamoDB`을 입력하고 선택합니다.
21. 왼쪽 메뉴에서 **Tables**를 선택합니다.
22. `RestaurantReservations` 테이블을 선택합니다.
23. [[Delete]] 버튼을 클릭합니다.
24. 확인 창에서 `confirm`을 입력합니다.
25. [[Delete]] 버튼을 클릭합니다.

#### 4. AWS IAM 역할 삭제

26. AWS Management Console에 로그인한 후 상단 검색창에 `IAM`을 입력하고 선택합니다.
27. 왼쪽 메뉴에서 **Roles**를 선택합니다.
28. 검색창에 `BedrockAgent`를 입력합니다.
29. Amazon Bedrock Agent가 생성한 역할들을 선택합니다.
30. [[Delete]] 버튼을 클릭합니다.
31. 확인 창에서 역할 이름을 입력합니다.
32. [[Delete]] 버튼을 클릭합니다.
33. 같은 방식으로 AWS Lambda 함수의 실행 역할들도 삭제합니다.

> [!NOTE]
> AWS IAM 역할 이름은 `AmazonBedrockExecutionRoleForAgents_` 또는 `BedrockAgentReservationHandler-role-` 형식입니다.
> 역할을 삭제하기 전에 다른 Agent나 AWS Lambda 함수에서 사용 중인지 확인합니다.

#### 5. Amazon CloudWatch Log Group 삭제

34. AWS Management Console에 로그인한 후 상단 검색창에 `CloudWatch`을 입력하고 선택합니다.
35. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
36. 검색창에 `/aws/lambda/BedrockAgent`를 입력합니다.
37. 다음 로그 그룹들을 선택합니다:
	- `/aws/lambda/BedrockAgentReservationHandler`
	- `/aws/lambda/BedrockAgentInvoker`
38. **Actions** > `Delete log group(s)`를 선택합니다.
39. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon CloudWatch Log Group은 자동으로 생성되며, 삭제하지 않으면 로그 저장 비용이 계속 발생합니다.

#### 6. Week 14-2 리소스 삭제 (Knowledge Base 연결 시)

> [!IMPORTANT]
> Week 14-2에서 생성한 Knowledge Base와 OpenSearch Serverless 컬렉션을 삭제하지 않았다면 반드시 삭제합니다.
> OpenSearch Serverless는 시간당 $0.48 (월 $346) 비용이 계속 발생합니다.

40. Amazon Bedrock 콘솔로 이동합니다.
41. 왼쪽 메뉴에서 **Orchestration** > **Knowledge bases**를 선택합니다.
42. `quicktable-restaurant-kb`를 선택합니다.
43. [[Delete]] 버튼을 클릭합니다.
44. 확인 창에서 `delete`를 입력합니다.
45. [[Delete]] 버튼을 클릭합니다.
46. AWS Management Console에 로그인한 후 상단 검색창에 `OpenSearch`을 입력하고 선택합니다.
47. 왼쪽 메뉴에서 **Serverless** > **Collections**를 선택합니다.
48. Knowledge Base와 연결된 컬렉션을 선택합니다.

> [!NOTE]
> Quick create로 생성된 OpenSearch Serverless 컬렉션은 `bedrock-knowledge-base-` 접두사로 시작하는 이름을 가질 수 있습니다.
> 컬렉션 이름을 확인한 후 선택합니다.

49. [[Delete]] 버튼을 클릭합니다.
50. 확인 창에서 `confirm`을 입력합니다.
51. [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Knowledge Base를 삭제하면 Amazon S3 버킷의 문서는 삭제되지 않습니다.
> Amazon S3 버킷도 삭제하려면 Amazon S3 콘솔에서 `quicktable-kb-documents-YOUR-INITIALS` 버킷을 삭제합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon Bedrock Agents 개요](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents.html)
- [Amazon Bedrock Agents Action Groups](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents-action-groups.html)
- [Amazon Bedrock Agents Knowledge Bases](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/knowledge-base.html)
- [Claude 3 모델 가이드](https://docs.anthropic.com/claude/docs/models-overview)
- [Amazon Bedrock 요금](https://aws.amazon.com/ko/bedrock/pricing/)
- [AWS Lambda와 Amazon Bedrock 통합](https://docs.aws.amazon.com/ko_kr/bedrock/latest/userguide/agents-lambda.html)

## 📚 참고: Amazon Bedrock Agent 핵심 개념

### Amazon Bedrock Agent 아키텍처

Amazon Bedrock Agent는 다음 구성 요소로 이루어져 있습니다:

**기반 모델 (Foundation Model)**

- QuickTable Agent의 두뇌 역할을 하는 대규모 언어 모델입니다
- Claude 3 Sonnet, Haiku 등 다양한 모델 선택 가능합니다
- 사용자 입력을 이해하고 적절한 응답을 생성합니다

**Instructions (지침)**

- Agent의 역할과 행동 방식을 정의합니다
- 대화 스타일, 응답 형식, 제약사항 등을 명시합니다
- 프롬프트 엔지니어링의 핵심 요소입니다

**Action Groups (액션 그룹)**

- Agent가 수행할 수 있는 작업들의 집합입니다
- AWS Lambda 함수와 연결되어 실제 작업을 실행합니다
- OpenAPI 스키마 또는 함수 정의로 작업을 명시합니다

**Knowledge Bases (지식 베이스)**

- Agent가 참조할 수 있는 문서 저장소입니다
- RAG (Retrieval-Augmented Generation) 방식으로 동작합니다
- Amazon S3에 저장된 문서를 벡터화하여 검색합니다

### Action Group vs Knowledge Base

**Action Group 사용 시기:**

- 데이터베이스 조회/수정이 필요한 경우
- 외부 API 호출이 필요한 경우
- 실시간 데이터 처리가 필요한 경우
- 트랜잭션 작업이 필요한 경우

**예시**: 예약 생성, 주문 처리, 결제 실행

**Knowledge Base 사용 시기:**

- 문서 기반 질의응답이 필요한 경우
- 정적 정보 검색이 필요한 경우
- 컨텍스트가 많은 답변이 필요한 경우
- 자주 변경되지 않는 정보를 다루는 경우

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
52. 고객의 예약 요청을 받아 새로운 예약을 생성합니다.
53. 예약 번호로 기존 예약을 조회합니다.
54. 특정 날짜의 예약 목록을 확인합니다.
55. 예약 취소 요청을 처리합니다.
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

- 대화의 연속성을 유지하는 고유 식별자입니다
- 같은 세션 ID로 여러 요청을 보내면 이전 대화를 기억합니다
- 새로운 대화를 시작하려면 새로운 세션 ID를 사용합니다

**컨텍스트 윈도우**

- Agent는 최근 대화 내역을 기억합니다
- Claude 3 Sonnet: 최대 200K 토큰 (약 150,000 단어)
- 긴 대화에서는 중요한 정보를 요약하여 전달합니다

**세션 속성 (Session Attributes)**

- 세션 간 유지해야 할 정보를 저장합니다
- 사용자 선호도, 임시 데이터 등을 저장할 수 있습니다

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
      "value": "2024-02-15"
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

**1. 모델 선택 최적화 (2026년 3월 기준)**

- **Claude Haiku 4.5**: 빠른 응답, 저렴한 비용 (간단한 작업)
- **Claude Sonnet 4.6**: 균형잡힌 성능 (일반적인 작업, 권장)
- **Claude Opus 4.6**: 최고 성능 (복잡한 작업)

**2. 프롬프트 최적화**

- 불필요한 지침 제거하여 토큰 수 감소
- 간결하고 명확한 표현 사용
- 예시는 필요한 경우에만 포함

**3. 캐싱 활용**

- 자주 사용되는 응답은 Amazon DynamoDB에 캐싱
- 동일한 질문에 대해 Agent 호출 최소화
- TTL 설정으로 오래된 캐시 자동 삭제

**4. 배치 처리**

- 여러 작업을 하나의 요청으로 묶어 처리
- 불필요한 왕복 통신 최소화

### 프로덕션 환경 권장사항

**1. 보안**

- AWS IAM 역할에 최소 권한 원칙 적용
- AWS Lambda 함수에 Amazon VPC 엔드포인트 사용
- 민감한 정보는 AWS Secrets Manager에 저장
- API 키와 자격증명은 환경 변수로 관리

**2. 모니터링**

- Amazon CloudWatch Logs로 Agent 대화 기록
- AWS Lambda 함수 성능 메트릭 추적
- 오류율과 응답 시간 모니터링
- Amazon CloudWatch Alarms로 이상 징후 감지

**3. 확장성**

- AWS Lambda 동시 실행 제한 설정
- Amazon DynamoDB Amazon EC2 Auto Scaling 활성화
- Agent 별칭으로 버전 관리
- 트래픽 증가에 대비한 용량 계획

**4. 테스트**

- 단위 테스트: AWS Lambda 함수 로직 검증
- 통합 테스트: Agent와 AWS Lambda 연동 확인
- 부하 테스트: 동시 사용자 처리 능력 검증
- A/B 테스트: 프롬프트 최적화

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

- 이전 대화에서 수집한 정보를 기억
- 부족한 정보만 추가로 요청
- 사용자가 정보를 수정하면 업데이트
- 대화가 길어지면 중요 정보 요약

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

- AWS Lambda 함수 타임아웃을 충분히 설정 (최소 30초)
- 긴 작업은 AWS Step Functions로 분리
- 비동기 처리 패턴 고려

**3. Agent 응답 오류**

- Agent가 잘못된 함수를 호출하는 경우
- 파라미터가 누락되거나 잘못된 경우
- 프롬프트를 더 명확하게 수정
- 함수 설명을 더 상세하게 작성

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

- Agent의 사고 과정을 단계별로 확인
- 어떤 함수를 호출했는지 추적
- 프롬프트 최적화에 활용
- 디버깅 및 문제 해결에 유용

**3. 멀티 Action Group**

- 여러 AWS Lambda 함수를 Action Group으로 연결
- 각 Action Group은 독립적인 기능 제공
- 예: 예약 관리 + 메뉴 조회 + 리뷰 관리

**4. Knowledge Base 통합**

- Action Group과 Knowledge Base 동시 사용
- 문서 검색 + 실시간 작업 처리
- RAG 기반 질의응답 + 트랜잭션 처리

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
                  example: '2024-02-15'
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

56. Agent builder에서 Action Group 생성 시 **Action group type**에서 `Define with API schemas`를 선택합니다.
57. **Action group schema**에서 `Upload API schema`를 선택합니다.
58. [[Choose file]] 버튼을 클릭하여 OpenAPI YAML 파일을 업로드합니다.
59. **Action group invocation**에서 AWS Lambda 함수를 선택합니다.

**OpenAPI 스키마의 장점**

- **표준화**: OpenAPI 3.0 표준 준수로 다른 도구와 호환
- **재사용**: 기존 API 문서를 그대로 사용 가능
- **검증**: 스키마 기반 자동 검증으로 오류 방지
- **문서화**: API 문서가 자동으로 생성됨
- **버전 관리**: Git으로 스키마 버전 관리 가능

### 문제 해결 가이드

**문제 1: Agent가 함수를 호출하지 않음**

**증상**: Agent가 대화만 하고 AWS Lambda 함수를 호출하지 않습니다.

**원인**:

- 함수 설명이 불명확하여 Agent가 언제 호출해야 할지 모름
- 프롬프트에 함수 사용 지침이 부족함
- 사용자 입력이 함수 호출 조건을 만족하지 않음

**해결**:

60. 함수 설명을 더 명확하고 구체적으로 작성합니다.
61. 프롬프트에 "예약 요청 시 create_reservation 함수를 호출합니다" 같은 명시적 지침을 추가합니다.
62. 사용자에게 더 구체적인 정보를 요청하도록 프롬프트를 수정합니다.
63. Agent 테스트 시 Trace를 활성화하여 Agent의 사고 과정을 확인합니다.

**문제 2: AWS Lambda 함수 응답 파싱 오류**

**증상**: Agent가 AWS Lambda 함수 응답을 이해하지 못하고 오류를 반환합니다.

**원인**:

- AWS Lambda 함수가 잘못된 형식으로 응답을 반환함
- JSON 직렬화 오류
- 응답 구조가 Amazon Bedrock Agent 요구사항과 맞지 않음

**해결**:

64. AWS Lambda 함수 응답이 올바른 형식인지 확인합니다:

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

65. Amazon CloudWatch Logs에서 AWS Lambda 함수 로그를 확인합니다.
66. 응답 데이터가 JSON 직렬화 가능한지 확인합니다 (datetime 객체는 문자열로 변환).

**문제 3: "Access Denied" 오류**

**증상**: Agent가 AWS Lambda 함수를 호출할 때 권한 오류가 발생합니다.

**원인**:

- Amazon Bedrock Agent에 AWS Lambda 함수 호출 권한이 없음
- AWS Lambda 함수에 리소스 기반 정책이 설정되지 않음

**해결**:

67. AWS Lambda 함수 콘솔로 이동합니다.
68. **Configuration** 탭을 선택합니다.
69. 왼쪽 메뉴에서 **Permissions**를 선택합니다.
70. **Resource-based policy statements** 섹션에서 Amazon Bedrock Agent 권한을 확인합니다.
71. 권한이 없으면 다음 명령어로 추가합니다:

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

- 문서 청킹이 적절하지 않음
- 임베딩 모델이 한국어를 잘 지원하지 않음
- 검색 쿼리가 모호함

**해결**:

72. Knowledge Base 설정에서 청크 크기를 조정합니다 (300 → 500 토큰).
73. 임베딩 모델을 Cohere Embed Multilingual v3로 변경합니다.
74. 문서에 메타데이터를 추가하여 필터링을 활성화합니다.
75. 사용자 질문을 더 구체적으로 유도하도록 프롬프트를 수정합니다.

**문제 5: 응답 속도가 느림**

**증상**: Agent 응답에 10초 이상 소요됩니다.

**원인**:

- AWS Lambda 함수 콜드 스타트
- Amazon DynamoDB 쿼리 최적화 부족
- Knowledge Base 검색 시간
- 프롬프트가 너무 길어 토큰 처리 시간 증가

**해결**:

76. AWS Lambda 함수에 Provisioned Concurrency를 설정하여 콜드 스타트 방지합니다.
77. Amazon DynamoDB 테이블에 적절한 인덱스를 생성합니다.
78. Knowledge Base 검색 결과 수를 줄입니다 (기본 5개 → 3개).
79. 프롬프트를 간결하게 수정하여 토큰 수를 줄입니다.
80. 더 빠른 모델(Claude 3 Haiku)을 사용합니다.

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
