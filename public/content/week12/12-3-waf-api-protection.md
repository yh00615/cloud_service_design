---
title: 'AWS WAF와 AWS Shield를 활용한 웹 애플리케이션 보안'
week: 12
session: 3
awsServices:
  - AWS WAF
  - AWS Shield
  - Amazon GuardDuty
  - AWS Security Hub
learningObjectives:
  - AWS WAF의 구성 요소와 동작 방식을 이해하고 Web ACL과 규칙을 구성할 수 있습니다.
  - AWS Shield Standard와 Advanced의 차이를 이해하고 DDoS 방어 아키텍처를 설명할 수 있습니다.
  - Amazon GuardDuty의 위협 탐지 방식과 AWS Security Hub를 활용한 통합 보안 관리 방법을 설명할 수 있습니다.

prerequisites:
  - Week 4-2 Amazon API Gateway 인증 구성 이해.
  - REST API 기본 개념 이해.
---

이 실습에서는 Week 4-2에서 구축한 QuickTable 레스토랑 예약 API를 AWS WAF로 보호합니다. QuickTable 예약 API는 전 세계 사용자가 접근하는 퍼블릭 서비스이므로, SQL Injection, XSS(Cross-Site Scripting), 봇 공격, 과도한 요청 등 다양한 웹 공격에 노출될 수 있습니다. 이 실습에서는 AWS WAF를 사용하여 Amazon API Gateway 앞단에서 악성 요청을 필터링하고, AWS Shield Standard의 자동 DDoS 방어와 함께 다층 방어 아키텍처를 구현합니다.

> [!NOTE]
> 이 실습에서는 Amazon API Gateway, AWS Lambda, Amazon DynamoDB 등 사전 인프라가 AWS CloudFormation 템플릿으로 제공됩니다. 학생이 직접 수행하는 것은 AWS WAF Web ACL 생성, 규칙 구성, 공격 시뮬레이션 테스트입니다.
>
> **리전**: 이 실습은 `ap-northeast-2` (서울) 리전에서 진행됩니다.

> [!DOWNLOAD]
> [week12-3-waf-api-protection.zip](/files/week12/week12-3-waf-api-protection.zip)
>
> - `week12-3-waf-api-protection.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB, AWS Lambda, Amazon API Gateway 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week12-3-waf-api-protection.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: AWS CloudFormation 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 서버리스 API 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

**Amazon DynamoDB 테이블: Week12-3-QuickTableReservations**

- **파티션 키**: `visitorId` (String) - 요청 IP 기반 방문자 ID
- **정렬 키**: `reservationId` (String) - UUID 형식 예약 ID
- **속성**: restaurantName, date, time, partySize, phoneNumber, status, createdAt

**AWS Lambda 함수: Week12-3-CreateReservation**

- **트리거**: Amazon API Gateway POST /reservations
- **입력 파라미터**: restaurantName, date, time, partySize, phoneNumber
- **자동 생성**: visitorId (요청 IP), reservationId (UUID), status (pending), createdAt

**AWS Lambda 함수: Week12-3-GetReservations**

- **트리거**: Amazon API Gateway GET /reservations
- **동작**: visitorId 기반으로 해당 방문자의 예약만 조회

**Amazon API Gateway: Week12-3-QuickTableAPI**

- **리소스**: /reservations
- **메서드**: POST, GET
- **통합**: AWS Lambda 프록시 통합
- **인증**: 없음 (WAF로 보호)

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week12-3-waf-api-protection.zip` 파일의 압축을 해제합니다.
2. `week12-3-waf-api-protection.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week12-3-waf-api-protection.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week12-3-waf-api-protection-stack`을 입력합니다.

> [!NOTE]
> **Parameters** 섹션의 기본값을 유지합니다.

10. [[Next]] 버튼을 클릭합니다.
11. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.

> [!NOTE]
> AWS CloudFormation 템플릿에 이미 태그가 정의되어 있으므로 추가 태그 설정은 불필요합니다.

12. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
13. [[Next]] 버튼을 클릭합니다.
14. **Review and create** 페이지에서 설정을 확인합니다.
15. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

16. **Outputs** 탭을 선택합니다.
17. 출력값들을 확인하고 메모장에 복사합니다:
    - `ApiGatewayInvokeUrl`: Amazon API Gateway Invoke URL (예: https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod)
    - `ApiGatewayStageArn`: API Gateway Stage ARN (WAF 연결에 사용)

> [!IMPORTANT]
> 이 출력값은 이후 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon API Gateway 보호 전 취약점 확인

이 태스크에서는 WAF 적용 전에 API가 악성 요청에 취약한 상태임을 확인합니다.

> [!CONCEPT] 웹 애플리케이션 공격 유형
> 웹 애플리케이션은 다양한 공격에 노출됩니다:
>
> - **SQL Injection**: 입력 필드에 SQL 구문을 삽입하여 데이터베이스를 조작하는 공격
> - **XSS (Cross-Site Scripting)**: 악성 스크립트를 삽입하여 다른 사용자의 브라우저에서 실행시키는 공격
> - **DDoS (Distributed Denial of Service)**: 대량의 요청으로 서비스를 마비시키는 공격
> - **봇 공격**: 자동화된 프로그램으로 과도한 요청을 보내는 공격

### 태스크 1.1: 정상 요청 테스트

18. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell이 시작될 때까지 기다립니다.

19. 다음 명령어로 환경 변수를 설정합니다:

```bash
# API URL 설정 (태스크 0에서 복사한 Invoke URL로 변경)
export API_URL="https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod"
```

> [!IMPORTANT]
> `API_URL`을 태스크 0에서 복사한 실제 Invoke URL로 변경합니다.

20. 정상적인 예약 생성 요청을 보냅니다:

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "강남 맛집", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}' \
  | python3 -m json.tool
```

> [!OUTPUT]
>
> ```json
> {
>     "visitorId": "<your-ip-address>",
>     "reservationId": "<uuid-format>",
>     "restaurantName": "강남 맛집",
>     "date": "2026-04-15",
>     "time": "18:00",
>     "partySize": 4,
>     "phoneNumber": "010-1234-5678",
>     "status": "pending",
>     "createdAt": "<current-timestamp>"
> }
> ```

### 태스크 1.2: SQL Injection 공격 시뮬레이션

21. SQL Injection 패턴이 포함된 요청을 보냅니다:

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "test'\'' OR 1=1; DROP TABLE reservations; --", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}'
```

> [!NOTE]
> WAF가 적용되지 않은 상태에서는 이 요청이 그대로 AWS Lambda 함수에 전달됩니다. DynamoDB는 SQL을 사용하지 않으므로 실제 SQL Injection 피해는 없지만, 악성 데이터가 저장될 수 있습니다.

### 태스크 1.3: XSS 공격 시뮬레이션

22. XSS 패턴이 포함된 요청을 보냅니다:

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "<script>alert(document.cookie)</script>", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}'
```

> [!NOTE]
> WAF 없이는 악성 스크립트가 포함된 데이터가 그대로 저장됩니다. 이 데이터가 웹 프론트엔드에서 렌더링되면 XSS 공격이 실행될 수 있습니다.

> [!IMPORTANT]
> 이 태스크에서 확인한 것처럼, WAF 없이는 API가 악성 요청에 무방비 상태입니다. 다음 태스크에서 AWS WAF를 적용하여 이러한 공격을 차단합니다.

✅ **태스크 완료**: WAF 적용 전 API의 취약점을 확인했습니다.

## 태스크 2: AWS WAF Web ACL 생성

이 태스크에서는 AWS WAF Web ACL을 생성합니다.

> [!CONCEPT] AWS WAF 핵심 구성 요소
> AWS WAF는 3가지 핵심 구성 요소로 이루어져 있습니다:
>
> - **Web ACL (Web Access Control List)**: 보호할 AWS 리소스에 연결되는 최상위 컨테이너. 규칙과 규칙 그룹을 포함합니다.
> - **규칙 (Rule)**: 요청을 검사하는 조건과 조건 충족 시 수행할 동작(Allow, Block, Count)을 정의합니다.
> - **규칙 그룹 (Rule Group)**: 여러 규칙을 묶어 재사용 가능한 단위로 관리합니다. AWS 관리형 규칙 그룹은 AWS가 유지보수합니다.
>
> **요청 처리 순서**: Web ACL에 추가된 규칙은 우선순위(Priority)에 따라 순서대로 평가됩니다. 첫 번째로 매칭되는 규칙의 동작이 적용되며, 어떤 규칙에도 매칭되지 않으면 기본 동작(Default Action)이 적용됩니다.

23. AWS Management Console 상단 검색창에 `WAF`를 입력하고 **WAF & Shield**를 선택합니다.

> [!NOTE]
> AWS WAF와 AWS Shield는 동일한 콘솔에서 관리됩니다.

> [!WARNING]
> AWS WAF 콘솔은 기존 콘솔과 새 콘솔(Protection packs) 두 가지 버전이 있습니다. 이 실습은 기존 콘솔 기준으로 진행합니다.
> 기존 콘솔에서는 왼쪽 메뉴에 **Web ACLs** 메뉴가 표시되고, "Switch to the new WAF console" 배너가 나타납니다.
> 새 콘솔이 표시되는 경우 왼쪽 메뉴에서 **Switch to AWS WAF Classic** 또는 기존 콘솔 전환 링크를 클릭합니다.

24. 왼쪽 메뉴에서 **Web ACLs**를 선택합니다.
25. **Region**에서 `Asia Pacific (Seoul)`을 선택합니다.

> [!IMPORTANT]
> Amazon API Gateway (REST API)에 WAF를 연결하려면 Web ACL을 해당 API Gateway와 동일한 리전에 생성해야 합니다. Amazon CloudFront에 연결하는 경우에는 `Global (CloudFront)` 리전을 선택합니다.

26. [[Create web ACL]] 버튼을 클릭합니다.

### 태스크 2.1: Web ACL 기본 설정

27. **Resource type**에서 `Regional resources (Application Load Balancers, Amazon API Gateway REST APIs, Amazon App Runner services, AWS AppSync APIs, Amazon Cognito user pools and AWS Verified Access Instances)`를 선택합니다.
28. **Region**에서 `Asia Pacific (Seoul)`을 확인합니다.
29. **Name**에 `QuickTable-WAF-WebACL`을 입력합니다.

> [!NOTE]
> **CloudWatch metric name**은 자동으로 입력됩니다.

30. **Description**에 `WAF Web ACL for QuickTable API protection`을 입력합니다.

### 태스크 2.2: 연결할 AWS 리소스 추가

31. **Associated AWS resources** 섹션에서 [[Add AWS resources]] 버튼을 클릭합니다.
32. **Resource type**에서 `Amazon API Gateway REST API`를 선택합니다.
33. 목록에서 `Week12-3-QuickTableAPI` 옆의 체크박스를 선택합니다.

> [!NOTE]
> 태스크 0에서 생성한 API Gateway가 표시됩니다. 표시되지 않으면 리전이 `Asia Pacific (Seoul)`인지 확인합니다.

34. [[Add]] 버튼을 클릭합니다.
35. [[Next]] 버튼을 클릭합니다.

✅ **태스크 완료**: Web ACL 기본 설정이 완료되었습니다. 다음 태스크에서 규칙을 추가합니다.

## 태스크 3: AWS WAF 관리형 규칙 그룹 추가

이 태스크에서는 AWS가 관리하는 규칙 그룹을 추가하여 SQL Injection과 XSS 공격을 방어합니다.

> [!CONCEPT] AWS 관리형 규칙 그룹
> AWS 관리형 규칙 그룹은 AWS Threat Research Team이 관리하는 사전 구성된 규칙 세트입니다:
>
> - **자동 업데이트**: AWS가 새로운 위협에 대응하여 규칙을 지속적으로 업데이트합니다.
> - **추가 비용 없음**: AWS 관리형 규칙 그룹은 WAF 기본 요금에 포함됩니다.
> - **즉시 적용**: 복잡한 규칙을 직접 작성할 필요 없이 바로 사용할 수 있습니다.
>
> 주요 관리형 규칙 그룹:
>
> | 규칙 그룹 | 설명 |
> |-----------|------|
> | Core rule set (CRS) | OWASP Top 10 등 일반적인 웹 취약점 방어 |
> | SQL database | SQL Injection 공격 패턴 탐지 |
> | Known bad inputs | 알려진 악성 입력 패턴 차단 |
> | Amazon IP reputation list | 악성 IP 주소 차단 |
> | Anonymous IP list | VPN, 프록시, Tor 등 익명 IP 차단 |
> | Bot Control | 봇 트래픽 관리 (추가 비용 발생) |

### 태스크 3.1: SQL Injection 방어 규칙 추가

36. **Add rules and rule groups** 페이지(Step 2)에서 [[Add rules]] 드롭다운을 클릭합니다.
37. **Add managed rule groups**를 선택합니다.
38. **AWS managed rule groups** 섹션을 확장합니다.
39. **Free rule groups** 목록에서 `SQL database`를 찾습니다.
40. `SQL database` 오른쪽의 **Add to web ACL** 토글을 활성화합니다.

> [!NOTE]
> **SQL database** 규칙 그룹은 SQL Injection 공격 패턴을 탐지합니다. 요청 본문, 쿼리 문자열, URI, 헤더에서 SQL 구문을 검사합니다.

### 태스크 3.2: Core Rule Set (CRS) 추가

41. **Free rule groups** 목록에서 `Core rule set`을 찾습니다.
42. `Core rule set` 오른쪽의 **Add to web ACL** 토글을 활성화합니다.

> [!NOTE]
> **Core rule set (CRS)**는 OWASP Top 10에 포함된 일반적인 웹 취약점을 방어합니다. XSS, 파일 포함(File Inclusion), 경로 탐색(Path Traversal) 등의 공격 패턴을 탐지합니다.

### 태스크 3.3: Known Bad Inputs 추가

43. **Free rule groups** 목록에서 `Known bad inputs`를 찾습니다.
44. `Known bad inputs` 오른쪽의 **Add to web ACL** 토글을 활성화합니다.

> [!NOTE]
> **Known bad inputs**는 Log4j/Log4Shell 취약점 등 알려진 악성 입력 패턴을 차단합니다.

45. [[Add rules]] 버튼을 클릭합니다.

> [!NOTE]
> 3개의 관리형 규칙 그룹이 추가되었습니다. 각 규칙 그룹의 WCU(Web ACL Capacity Unit)가 표시됩니다:
>
> | 규칙 그룹 | WCU |
> |-----------|-----|
> | Core rule set (CRS) | 700 |
> | SQL database | 200 |
> | Known bad inputs | 200 |
> | **합계** | **1,100** |
>
> Web ACL의 최대 WCU는 5,000입니다. 현재 1,100 WCU를 사용하므로 여유가 충분합니다.

46. 페이지 하단의 **Default web ACL action for requests that don't match any rules**에서 `Allow`가 선택되어 있는지 확인합니다.

> [!NOTE]
> 기본 동작을 Allow로 설정하면, 규칙에 매칭되지 않는 정상 요청은 모두 허용됩니다. 규칙에 매칭되는 악성 요청만 차단(Block)합니다.

✅ **태스크 완료**: AWS 관리형 규칙 그룹이 추가되었습니다.

## 태스크 4: AWS WAF Rate-based 규칙 생성

이 태스크에서는 과도한 요청을 차단하는 Rate-based 규칙을 추가합니다.

> [!CONCEPT] Rate-based 규칙
> Rate-based 규칙은 동일한 IP 주소에서 일정 시간 내에 허용된 요청 수를 초과하면 자동으로 차단합니다:
>
> - **평가 주기**: 5분 단위로 요청 수를 집계합니다.
> - **임계값**: 10~2,000,000,000 범위에서 설정 가능합니다.
> - **자동 해제**: 요청 수가 임계값 아래로 떨어지면 자동으로 차단이 해제됩니다.
> - **DDoS 방어**: 단순한 DDoS 공격과 봇 공격을 효과적으로 차단합니다.

### 태스크 4.1: Rate-based 규칙 추가

47. **Add rules and rule groups** 페이지에서 [[Add rules]] 드롭다운을 클릭합니다.
48. **Add my own rules and rule groups**를 선택합니다.
49. **Rule type**에서 `Rate-based rule`을 선택합니다.
50. **Name**에 `QuickTable-RateLimit-Rule`을 입력합니다.
51. **Rate limit**에 `100`을 입력합니다.

> [!NOTE]
> Rate limit 100은 동일 IP에서 5분 동안 100개 이상의 요청이 오면 차단한다는 의미입니다. 2024년 8월부터 최소 10까지 설정 가능합니다. 프로덕션 환경에서는 서비스 특성에 맞게 조정합니다 (예: 일반 웹사이트 2,000, API 서비스 1,000).
>
> 이 실습에서는 테스트 편의를 위해 낮은 값(100)을 설정합니다.

52. **IP address to use for rate limiting**에서 `Source IP address`를 선택합니다.
53. **Action**에서 `Block`을 선택합니다.
54. [[Add rule]] 버튼을 클릭합니다.

### 태스크 4.2: 규칙 우선순위 설정

55. 규칙 목록에서 우선순위를 확인합니다.

> [!NOTE]
> 규칙은 우선순위(Priority) 순서대로 평가됩니다. 숫자가 낮을수록 먼저 평가됩니다.
>
> 권장 우선순위:
>
> | 우선순위 | 규칙 | 설명 |
> |----------|------|------|
> | 0 | QuickTable-RateLimit-Rule | Rate limiting을 먼저 적용하여 대량 요청 차단 |
> | 1 | AWS-AWSManagedRulesKnownBadInputsRuleSet | 알려진 악성 입력 차단 |
> | 2 | AWS-AWSManagedRulesSQLiRuleSet | SQL Injection 차단 |
> | 3 | AWS-AWSManagedRulesCommonRuleSet | 일반 웹 취약점 차단 |
>
> Rate-based 규칙을 가장 먼저 평가하면 대량 요청을 조기에 차단하여 후속 규칙의 처리 부하를 줄일 수 있습니다.

56. 필요시 [[Move up]] / [[Move down]] 버튼을 사용하여 우선순위를 조정합니다.
57. [[Next]] 버튼을 클릭합니다.

### 태스크 4.3: 메트릭 설정 및 Web ACL 생성

58. **Set rule priority** 페이지에서 우선순위를 확인합니다.
59. [[Next]] 버튼을 클릭합니다.
60. **Configure metrics** 페이지에서 기본 Amazon CloudWatch 메트릭 설정을 확인합니다.

> [!NOTE]
> 각 규칙 그룹별로 Amazon CloudWatch 메트릭이 자동 생성됩니다. 이 메트릭으로 차단된 요청 수, 허용된 요청 수 등을 모니터링할 수 있습니다.

61. [[Next]] 버튼을 클릭합니다.
62. **Review and create web ACL** 페이지에서 설정을 검토합니다.
63. [[Create web ACL]] 버튼을 클릭합니다.

> [!NOTE]
> Web ACL 생성에 1-2분이 소요됩니다. 생성이 완료되면 Web ACL 상세 페이지로 이동합니다.
> 태스크 2에서 이미 API Gateway를 연결했으므로, Web ACL 생성과 동시에 API Gateway에 자동으로 적용됩니다.

✅ **태스크 완료**: Rate-based 규칙이 추가되고 Web ACL이 생성되었습니다.

## 태스크 5: AWS WAF 보호 테스트

이 태스크에서는 WAF가 적용된 상태에서 악성 요청이 차단되는지 확인합니다.

### 태스크 5.1: 정상 요청 확인

64. CloudShell에서 정상적인 예약 생성 요청을 보냅니다:

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "서울 레스토랑", "date": "2026-04-20", "time": "19:00", "partySize": 2, "phoneNumber": "010-5678-1234"}' \
  | python3 -m json.tool
```

> [!OUTPUT]
>
> ```json
> {
>     "visitorId": "<your-ip-address>",
>     "reservationId": "<uuid-format>",
>     "restaurantName": "서울 레스토랑",
>     "date": "2026-04-20",
>     "time": "19:00",
>     "partySize": 2,
>     "phoneNumber": "010-5678-1234",
>     "status": "pending",
>     "createdAt": "<current-timestamp>"
> }
> ```

> [!NOTE]
> 정상 요청은 WAF 규칙에 매칭되지 않으므로 기본 동작(Allow)에 의해 허용됩니다.

### 태스크 5.2: SQL Injection 차단 확인

65. SQL Injection 패턴이 포함된 요청을 보냅니다:

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "test'\'' OR 1=1; DROP TABLE reservations; --", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}'
```

> [!OUTPUT]
>
> ```
> HTTP Status: 403
> ```

> [!SUCCESS]
> HTTP 403 (Forbidden) 응답이 반환되면 AWS WAF가 SQL Injection 공격을 성공적으로 차단한 것입니다.

66. 응답 본문을 확인합니다:

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "test'\'' OR 1=1; DROP TABLE reservations; --", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}'
```

> [!OUTPUT]
>
> ```json
> {"message": "Forbidden"}
> ```

### 태스크 5.3: XSS 차단 확인

67. XSS 패턴이 포함된 요청을 보냅니다:

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "<script>alert(document.cookie)</script>", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}'
```

> [!OUTPUT]
>
> ```
> HTTP Status: 403
> ```

> [!SUCCESS]
> XSS 공격도 AWS WAF Core rule set에 의해 차단되었습니다.

### 태스크 5.4: 추가 공격 패턴 테스트

68. 경로 탐색(Path Traversal) 공격을 테스트합니다:

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
  "$API_URL/reservations?file=../../../etc/passwd"
```

> [!OUTPUT]
>
> ```
> HTTP Status: 403
> ```

69. 정상 조회 요청이 여전히 동작하는지 확인합니다:

```bash
curl -s -X GET $API_URL/reservations | python3 -m json.tool
```

> [!OUTPUT]
>
> ```json
> [
>     {
>         "visitorId": "<your-ip-address>",
>         "reservationId": "<uuid-format>",
>         "restaurantName": "서울 레스토랑",
>         ...
>     }
> ]
> ```

> [!NOTE]
> 정상 요청은 모두 허용되고, 악성 요청만 차단됩니다. 이것이 WAF의 핵심 가치입니다.

✅ **태스크 완료**: AWS WAF가 SQL Injection, XSS, 경로 탐색 공격을 성공적으로 차단했습니다.

## 태스크 6: Amazon CloudWatch에서 AWS WAF 메트릭 확인

이 태스크에서는 AWS WAF 콘솔에서 차단된 요청을 확인합니다.

### 태스크 6.1: Web ACL 대시보드 확인

70. AWS WAF 콘솔로 이동합니다.
71. 왼쪽 메뉴에서 **Web ACLs**를 선택합니다.
72. **Region**에서 `Asia Pacific (Seoul)`을 선택합니다.
73. `QuickTable-WAF-WebACL`을 클릭합니다.
74. **Overview** 탭에서 다음 정보를 확인합니다:
    - **AllowedRequests**: 허용된 요청 수
    - **BlockedRequests**: 차단된 요청 수

> [!NOTE]
> 메트릭이 표시되기까지 1-2분이 소요될 수 있습니다. 그래프가 비어 있으면 잠시 기다린 후 새로고침합니다.

### 태스크 6.2: 규칙별 메트릭 확인

75. **Overview** 탭에서 아래로 스크롤하여 규칙별 메트릭을 확인합니다.

> [!NOTE]
> 각 규칙 그룹별로 차단된 요청 수가 표시됩니다:
>
> - **AWS-AWSManagedRulesSQLiRuleSet**: SQL Injection 차단 횟수
> - **AWS-AWSManagedRulesCommonRuleSet**: XSS 등 일반 공격 차단 횟수
> - **AWS-AWSManagedRulesKnownBadInputsRuleSet**: 알려진 악성 입력 차단 횟수
> - **QuickTable-RateLimit-Rule**: Rate limiting 차단 횟수

### 태스크 6.3: Sampled requests 확인

76. **Overview** 탭에서 **Sampled requests** 섹션을 확인합니다.

> [!NOTE]
> Sampled requests에서는 최근 요청의 샘플을 확인할 수 있습니다. 각 요청에 대해 다음 정보가 표시됩니다:
>
> - **Source IP**: 요청 출발지 IP
> - **URI**: 요청 URI
> - **Matching rule**: 매칭된 규칙 이름
> - **Action**: 수행된 동작 (Allow/Block)
> - **Time**: 요청 시간

77. 차단된 요청(Block)을 클릭하여 상세 정보를 확인합니다.

> [!TIP]
> Sampled requests는 최대 3시간 동안의 요청 샘플을 보여줍니다. 전체 로그가 필요한 경우 WAF 로깅을 활성화하여 Amazon S3, Amazon CloudWatch Logs, 또는 Amazon Kinesis Data Firehose로 전송할 수 있습니다.

✅ **태스크 완료**: AWS WAF 메트릭과 차단된 요청을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- QuickTable 예약 API의 보안 취약점을 확인했습니다
- AWS WAF Web ACL을 생성하고 Amazon API Gateway에 연결했습니다
- AWS 관리형 규칙으로 SQL Injection, XSS, 알려진 악성 입력을 차단했습니다
- Rate-based 규칙으로 과도한 요청을 차단하는 설정을 구성했습니다
- WAF 메트릭을 통해 차단된 요청을 모니터링했습니다

Week 4-2에서 구축한 QuickTable API를 AWS WAF로 보호하여, 인증(Week 4-2 Cognito) + 규정 준수(Week 12-2 Config) + 웹 방어(Week 12-3 WAF)로 이어지는 다층 보안 아키텍처를 완성했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

---

## 1단계: 생성된 리소스 확인 (Tag Editor)

실습에서 생성한 모든 리소스를 확인합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `12-3`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 2단계에서 수행합니다.

---

## 2단계: 리소스 삭제

### AWS WAF Web ACL 삭제

7. AWS WAF 콘솔로 이동합니다.
8. 왼쪽 메뉴에서 **Web ACLs**를 선택합니다.
9. **Region**에서 `Asia Pacific (Seoul)`을 선택합니다.
10. `QuickTable-WAF-WebACL`을 선택합니다.
11. **Associated AWS resources** 탭을 선택합니다.
12. 연결된 API Gateway를 선택하고 [[Disassociate]] 버튼을 클릭합니다.
13. 확인 창에서 [[Disassociate]] 버튼을 클릭합니다.

> [!IMPORTANT]
> Web ACL을 삭제하기 전에 연결된 리소스를 먼저 해제해야 합니다.

14. [[Delete]] 버튼을 클릭합니다.
15. 확인 창에 `delete`를 입력합니다.
16. [[Delete]] 버튼을 클릭합니다.

### Amazon CloudWatch Log Groups 삭제

17. Amazon CloudWatch 콘솔로 이동합니다.
18. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
19. 다음 Log Group들을 선택합니다:
    - `/aws/lambda/Week12-3-CreateReservation`
    - `/aws/lambda/Week12-3-GetReservations`
20. **Actions** > `Delete log group(s)`를 선택합니다.
21. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

---

## 3단계: AWS CloudFormation 스택 삭제

22. AWS Management Console에서 `CloudFormation`을 검색하고 선택합니다.
23. 스택 목록에서 `week12-3-waf-api-protection-stack`을 선택합니다.
24. [[Delete]] 버튼을 클릭합니다.
25. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. **Events** 탭에서 삭제 과정을 확인할 수 있습니다.

26. 스택이 목록에서 사라졌는지 확인합니다.

---

## 4단계: 최종 삭제 확인 (Tag Editor 활용)

27. `Resource Groups & Tag Editor`로 이동합니다.
28. Tag key: `Week`, Tag value: `12-3`으로 검색합니다.
29. 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 📚 참고: AWS WAF 및 AWS Shield 아키텍처

### AWS WAF 동작 원리

**요청 처리 흐름**:

30. 클라이언트가 API 요청을 전송합니다.
31. AWS WAF가 Web ACL의 규칙을 우선순위 순서대로 평가합니다.
32. 규칙에 매칭되면 해당 규칙의 동작(Block/Allow/Count)을 수행합니다.
33. 어떤 규칙에도 매칭되지 않으면 기본 동작(Default Action)을 수행합니다.
34. Allow된 요청만 Amazon API Gateway로 전달됩니다.

**WAF 규칙 유형**:

| 규칙 유형 | 설명 | 사용 사례 |
|-----------|------|-----------|
| Regular rule | 조건 기반 매칭 | 특정 IP 차단, 특정 URI 패턴 차단 |
| Rate-based rule | 요청 빈도 기반 | DDoS 방어, 봇 차단 |
| Managed rule group | AWS/마켓플레이스 관리형 | SQL Injection, XSS 방어 |

**WAF 연결 가능 리소스**:

- Amazon CloudFront 배포
- Amazon API Gateway REST API
- Application Load Balancer (ALB)
- AWS AppSync GraphQL API
- Amazon Cognito User Pool
- AWS App Runner 서비스
- AWS Verified Access 인스턴스

### AWS Shield 개요

**AWS Shield Standard**:

- 모든 AWS 계정에 자동 적용 (추가 비용 없음)
- L3/L4 DDoS 공격 자동 방어 (SYN Flood, UDP Reflection 등)
- Amazon CloudFront, Amazon Route 53, Elastic Load Balancing에 자동 적용
- 실시간 탐지 및 인라인 완화

**AWS Shield Advanced**:

- 월 $3,000 + 데이터 전송 비용
- L3/L4/L7 DDoS 공격 방어
- 24/7 AWS Shield Response Team (SRT) 지원
- DDoS 비용 보호 (공격으로 인한 스케일링 비용 환불)
- 상세한 공격 진단 및 보고서
- AWS WAF 비용 포함

**Shield Standard vs Advanced 비교**:

| 기능 | Standard | Advanced |
|------|----------|----------|
| 비용 | 무료 | 월 $3,000+ |
| L3/L4 방어 | ✅ | ✅ |
| L7 방어 | ❌ | ✅ |
| SRT 지원 | ❌ | ✅ (24/7) |
| 비용 보호 | ❌ | ✅ |
| 상세 보고서 | ❌ | ✅ |

### 다층 방어 아키텍처 (Defense in Depth)

**계층별 보안 서비스**:

| 계층 | 서비스 | 방어 대상 |
|------|--------|-----------|
| 엣지 (L3/L4) | AWS Shield Standard | SYN Flood, UDP Reflection, DNS Amplification |
| 엣지 (L7) | AWS WAF + Amazon CloudFront | SQL Injection, XSS, 봇 공격 |
| 네트워크 | 보안 그룹, NACL | 포트 스캔, 비인가 접근 |
| 애플리케이션 | Amazon Cognito, IAM | 인증/인가 |
| 데이터 | AWS KMS, Secrets Manager | 데이터 암호화, 자격증명 관리 |

**QuickTable 보안 아키텍처 전체 흐름**:

35. AWS Shield Standard → L3/L4 DDoS 자동 방어
36. AWS WAF → SQL Injection, XSS, Rate limiting
37. Amazon API Gateway → 요청 검증, 스로틀링
38. Amazon Cognito (Week 4-2) → JWT 토큰 인증
39. AWS Lambda → 비즈니스 로직 처리
40. Amazon DynamoDB → 데이터 저장

### 프로덕션 환경 개선사항

**1. WAF 로깅 활성화**:

- Amazon S3, Amazon CloudWatch Logs, 또는 Amazon Kinesis Data Firehose로 전체 요청 로그 전송
- 차단된 요청의 상세 분석 및 오탐(False Positive) 확인

**2. 사용자 정의 규칙 추가**:

- 특정 국가 IP 차단 (Geo-match)
- 특정 User-Agent 차단
- 요청 크기 제한 (Size constraint)

**3. Amazon CloudFront 연동**:

- 엣지 로케이션에서 WAF 적용 (지연 시간 감소)
- Shield Standard 자동 적용 범위 확대
- 캐싱으로 오리진 부하 감소

**4. 모니터링 및 알림**:

- Amazon CloudWatch 알람으로 차단 급증 시 알림
- AWS Security Hub 통합
- Amazon SNS로 보안 담당자 알림

**5. AWS Firewall Manager**:

- 멀티 계정 환경에서 WAF 정책 중앙 관리
- 조직 전체에 일관된 보안 정책 적용

### 보안 모범 사례

**WAF 규칙 관리**:

- Count 모드로 먼저 테스트한 후 Block으로 전환 (오탐 방지)
- 관리형 규칙 그룹의 업데이트 알림 구독
- 정기적으로 Sampled requests 검토

**Rate Limiting**:

- 서비스 특성에 맞는 임계값 설정
- API 엔드포인트별 차별화된 Rate limit 적용
- 정상 트래픽 패턴 분석 후 임계값 조정

**비용 최적화**:

- AWS 관리형 규칙 그룹 활용 (추가 비용 없음)
- Bot Control, Account Takeover Prevention은 추가 비용 발생 → 필요시에만 활성화
- Web ACL 수와 규칙 수 최적화

## 추가 학습 리소스

- [AWS WAF 개발자 가이드](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/)
- [AWS WAF 관리형 규칙 그룹](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/aws-managed-rule-groups-list.html)
- [AWS Shield 개발자 가이드](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/shield-chapter.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## QuickTable 시리즈 연결

- **Week 4-2**: Amazon Cognito + Amazon API Gateway로 QuickTable 예약 API 인증 구축
- **Week 10-2**: Amazon ElastiCache로 API 성능 최적화 (데모)
- **Week 12-3**: AWS WAF + AWS Shield로 웹 애플리케이션 보안 ← 현재
- **Week 13-2**: AWS X-Ray로 성능 추적
- **Week 14-2**: Amazon Bedrock Knowledge Base로 레스토랑 메뉴 RAG
- **Week 14-3**: Amazon Bedrock Agent로 예약 챗봇 완성

---

© 2026 한양대학교 클라우드 서비스 설계

이 가이드와 스크립트는 Agentic IDE Kiro로 만들어졌습니다.
