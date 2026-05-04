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
  - Week 4-2 Amazon API Gateway 인증 구성 이해
  - REST API 기본 개념 이해
---

이 실습에서는 Week 4-2에서 구축한 QuickTable 레스토랑 예약 API를 AWS WAF로 보호합니다. QuickTable 예약 API는 전 세계 사용자가 접근하는 퍼블릭 서비스이므로, SQL Injection, XSS(Cross-Site Scripting), 봇 공격, 과도한 요청 등 다양한 웹 공격에 노출될 수 있습니다. 이 실습에서는 AWS WAF를 사용하여 Amazon API Gateway 앞단에서 악성 요청을 필터링하고, AWS Shield Standard의 자동 DDoS 방어와 함께 다층 방어 아키텍처를 구현합니다.

> [!NOTE]
> 이 실습에서는 Amazon API Gateway, AWS Lambda, Amazon DynamoDB 등 사전 인프라가 AWS CloudFormation 템플릿으로 제공됩니다. 학생이 직접 수행하는 것은 AWS WAF Web ACL 생성, 규칙 구성, 공격 시뮬레이션 테스트입니다.

> [!DOWNLOAD]
> [week12-3-waf-api-protection.zip](/files/week12/week12-3-waf-api-protection.zip)
>
> - `week12-3-waf-api-protection.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon DynamoDB, AWS Lambda, Amazon API Gateway 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week12-3-waf-api-protection.yaml 사용)

> [!CONCEPT] 웹 애플리케이션 보안 아키텍처
>
> 웹 애플리케이션은 다양한 공격에 노출됩니다:
>
> - **SQL Injection**: 입력 필드에 SQL 구문을 삽입하여 데이터베이스를 조작하는 공격
> - **XSS (Cross-Site Scripting)**: 악성 스크립트를 삽입하여 다른 사용자의 브라우저에서 실행시키는 공격
> - **DDoS (Distributed Denial of Service)**: 대량의 요청으로 서비스를 마비시키는 공격
> - **봇 공격**: 자동화된 프로그램으로 과도한 요청을 보내는 공격
>
> AWS WAF는 Amazon API Gateway 앞단에서 악성 요청을 필터링하고, AWS Shield Standard는 L3/L4 DDoS 공격을 자동으로 방어합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제**해야 합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 서버리스 API 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon DynamoDB 테이블**: QuickTable 예약 데이터 저장
- **AWS Lambda 함수 2개**: 예약 생성(POST), 예약 조회(GET)
- **Amazon API Gateway REST API**: /reservations 엔드포인트 (POST, GET)
- **AWS IAM 역할**: AWS Lambda 실행 역할 (Amazon DynamoDB 접근 권한 포함)

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 생성)은 동일합니다.

1. 다운로드한 `week12-3-waf-api-protection.zip` 파일의 압축을 해제합니다.
2. `week12-3-waf-api-protection.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

   <img src="/images/week12/12-3-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week12-3-waf-api-protection.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task0-step8-upload.png" alt="CloudFormation 템플릿 파일 업로드" class="guide-img-md" />

9. **Stack name**에 `week12-3-waf-api-protection-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **EnvironmentName**: `week12-3-quicktable-api` (기본값 유지)
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `12-3` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)

> [!NOTE]
> Parameters에서 설정한 태그 값(Project, Week, CreatedBy)은 모든 리소스에 자동으로 적용됩니다. 별도로 Tags 섹션에서 추가할 필요가 없습니다.

11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task0-step11-options.png" alt="CloudFormation Configure stack options" class="guide-img-md" />

12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week12/12-3-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "CREATE_COMPLETE"로 변경될 때까지 기다립니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. **Outputs** 탭을 선택합니다.
19. 출력값들을 확인하고 메모장에 복사합니다:
    - `ApiGatewayInvokeUrl`: Amazon API Gateway Invoke URL (예: https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod)
    - `ApiGatewayStageArn`: Amazon API Gateway Stage ARN (AWS WAF 연결에 사용)

    <img src="/images/week12/12-3-task0-step18-outputs.png" alt="CloudFormation Outputs 탭" class="guide-img-md" />

> [!IMPORTANT]
> 이 출력값들은 이후 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon API Gateway 보호 전 취약점 확인

이 태스크에서는 AWS WAF 적용 전에 API가 악성 요청에 취약한 상태임을 확인합니다.

### 태스크 1.1: 정상 요청 테스트

20. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> AWS CloudShell이 시작될 때까지 기다립니다.

21. 다음 명령어로 환경 변수를 설정합니다:

    <img src="/images/week12/12-3-task1-step21-cloudshell.png" alt="AWS CloudShell" class="guide-img-md" />

```bash
# API URL 설정 (태스크 0에서 복사한 Invoke URL로 변경)
export API_URL="<ApiGatewayInvokeUrl>"
```

> [!IMPORTANT]
> `<ApiGatewayInvokeUrl>`을 태스크 0에서 복사한 실제 Invoke URL로 변경합니다.
>
> 예: `export API_URL="https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod"`

> [!NOTE]
> 환경 변수가 올바르게 설정되었는지 확인합니다:
>
> ```bash
> echo $API_URL
> ```
>
> URL이 출력되면 정상입니다. 출력이 없으면 `export` 명령어를 다시 실행합니다.

22. 정상적인 예약 생성 요청을 보냅니다:

    <img src="/images/week12/12-3-task1-step22-request.png" alt="정상 요청 테스트" class="guide-img-md" />

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "강남 맛집", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}' \
  | jq .
```

> [!OUTPUT]
>
> ```json
> {
>   "visitorId": "<your-ip-address>",
>   "reservationId": "<uuid-format>",
>   "restaurantName": "강남 맛집",
>   "date": "2026-04-15",
>   "time": "18:00",
>   "partySize": 4,
>   "phoneNumber": "010-1234-5678",
>   "status": "pending",
>   "createdAt": "<current-timestamp>"
> }
> ```

### 태스크 1.2: SQL Injection 공격 시뮬레이션

23. SQL Injection 패턴이 포함된 요청을 보냅니다:

    <img src="/images/week12/12-3-task1-step23-sqli.png" alt="SQL Injection 공격 시뮬레이션" class="guide-img-md" />

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "test'\'' OR 1=1; DROP TABLE reservations; --", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}' \
  | jq .
```

> [!OUTPUT]
>
> ```json
> {
>   "visitorId": "<your-ip-address>",
>   "reservationId": "<uuid-format>",
>   "restaurantName": "test' OR 1=1; DROP TABLE reservations; --",
>   "date": "2026-04-15",
>   "time": "18:00",
>   "partySize": 4,
>   "phoneNumber": "010-0000-0000",
>   "status": "pending",
>   "createdAt": "<current-timestamp>"
> }
> ```

> [!NOTE]
> AWS WAF가 적용되지 않은 상태에서는 이 요청이 그대로 AWS Lambda 함수에 전달됩니다. Amazon DynamoDB는 SQL을 사용하지 않으므로 실제 SQL Injection 피해는 없지만, 악성 데이터가 그대로 저장됩니다.

### 태스크 1.3: XSS 공격 시뮬레이션

24. XSS 패턴이 포함된 요청을 보냅니다:

    <img src="/images/week12/12-3-task1-step24-xss.png" alt="XSS 공격 시뮬레이션" class="guide-img-md" />

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "<script>alert(document.cookie)</script>", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}' \
  | jq .
```

> [!OUTPUT]
>
> ```json
> {
>   "visitorId": "<your-ip-address>",
>   "reservationId": "<uuid-format>",
>   "restaurantName": "<script>alert(document.cookie)</script>",
>   "date": "2026-04-15",
>   "time": "18:00",
>   "partySize": 4,
>   "phoneNumber": "010-0000-0000",
>   "status": "pending",
>   "createdAt": "<current-timestamp>"
> }
> ```

> [!NOTE]
> AWS WAF 없이는 악성 스크립트가 포함된 데이터가 그대로 저장됩니다. 이 데이터가 웹 프론트엔드에서 렌더링되면 XSS 공격이 실행될 수 있습니다.

> [!IMPORTANT]
> 이 태스크에서 확인한 것처럼, AWS WAF 없이는 API가 악성 요청에 무방비 상태입니다. 다음 태스크에서 AWS WAF를 적용하여 이러한 공격을 차단합니다.

### 태스크 1.4: Amazon DynamoDB에서 악성 데이터 확인

25. 상단 검색창에 `DynamoDB`를 입력하고 선택합니다.
26. 왼쪽 메뉴에서 **Explore items**를 선택합니다.
27. 왼쪽 테이블 목록에서 `Week12-3-QuickTableReservations`를 선택합니다.
28. **Scan or query items**에서 `Scan`이 선택된 상태에서 [[Run]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task1-step28-dynamodb.png" alt="DynamoDB Explore items" class="guide-img-md" />

29. 저장된 항목에서 `restaurantName`에 SQL Injection 문자열(`test' OR 1=1; DROP TABLE reservations; --`)과 XSS 스크립트(`<script>alert(document.cookie)</script>`)가 그대로 저장되어 있는지 확인합니다.

> [!NOTE]
> 악성 데이터가 필터링 없이 그대로 Amazon DynamoDB에 저장된 것을 확인할 수 있습니다. AWS WAF를 적용하면 이러한 요청이 Amazon API Gateway에 도달하기 전에 차단됩니다.

✅ **태스크 완료**: AWS WAF 적용 전 API의 취약점을 확인했습니다.

## 태스크 2: AWS WAF Protection Pack (Web ACL) 생성

이 태스크에서는 AWS WAF Protection Pack (Web ACL)을 생성하고, 규칙을 추가하여 Amazon API Gateway를 보호합니다.

> [!CONCEPT] AWS WAF 핵심 구성 요소
>
> AWS WAF는 3가지 핵심 구성 요소로 이루어져 있습니다:
>
> - **Web ACL (Web Access Control List)**: 보호할 AWS 리소스에 연결되는 최상위 컨테이너. 규칙과 규칙 그룹을 포함합니다. 새 콘솔에서는 **Protection Pack**이라고도 합니다.
> - **규칙 (Rule)**: 요청을 검사하는 조건과 조건 충족 시 수행할 동작(Allow, Block, Count)을 정의합니다.
> - **규칙 그룹 (Rule Group)**: 여러 규칙을 묶어 재사용 가능한 단위로 관리합니다. AWS 관리형 규칙 그룹은 AWS가 유지보수합니다.
>
> **요청 처리 순서**: Web ACL에 추가된 규칙은 우선순위(Priority)에 따라 순서대로 평가됩니다. 첫 번째로 매칭되는 규칙의 동작이 적용되며, 어떤 규칙에도 매칭되지 않으면 기본 동작(Default Action)이 적용됩니다.

30. 상단 검색창에 `WAF`를 입력하고 **WAF & Shield**를 선택합니다.

> [!NOTE]
> AWS WAF와 AWS Shield는 동일한 콘솔에서 관리됩니다.
> 2025년 6월부터 AWS WAF 콘솔이 새롭게 개편되었습니다. 기존의 다단계 위자드 방식 대신, 한 페이지에서 앱 유형 선택 → 리소스 연결 → 규칙 추가 → 이름 설정 → 생성까지 처리하는 간소화된 방식으로 변경되었습니다. 기존 콘솔은 왼쪽 메뉴 하단의 **Switch to the old WAF console**에서 전환할 수 있습니다.

31. 왼쪽 메뉴에서 **Protection packs (web ACLs)**를 선택합니다.
32. [[Create protection pack (web ACL)]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step32-create.png" alt="WAF Create protection pack" class="guide-img-md" />

### 태스크 2.1: Tell us about your app

33. **App category**에서 `Other`를 선택합니다.
34. **App focus**에서 `API`를 선택합니다.

> [!NOTE]
> QuickTable 예약 시스템은 REST API 기반이므로 `API`를 선택합니다. App category와 App focus 설정은 AWS WAF가 적절한 보호 규칙을 추천하는 데 사용됩니다.

### 태스크 2.2: Select resources to protect

35. **Select resources to protect** 섹션에서 [[Add resources]] 드롭다운을 클릭합니다.
36. **Regional** > **Add regional resources**를 선택합니다.

    <img src="/images/week12/12-3-task2-step36-regional.png" alt="Add regional resources" class="guide-img-md" />

> [!NOTE]
> Amazon API Gateway REST API는 리전 리소스이므로 **Regional** > **Add regional resources**를 선택합니다. Amazon CloudFront를 보호하는 경우에는 **Global** > **Add CloudFront or Amplify resources**를 선택합니다.

37. 모달 창에서 `Week12-3-QuickTableAPI - prod` 옆의 체크박스를 선택합니다.

> [!NOTE]
> 태스크 0에서 생성한 Amazon API Gateway가 `Amazon API Gateway REST API` 타입으로 표시됩니다. 표시되지 않으면 스택 생성이 완료되었는지 확인합니다.

38. [[Add]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step38-add.png" alt="리소스 추가 완료" class="guide-img-md" />

39. **Select resources to protect** 섹션에 `Week12-3-QuickTableAPI - prod`가 추가되었는지 확인합니다.

### 태스크 2.3: Choose initial protections

> [!CONCEPT] AWS 관리형 규칙 그룹
>
> AWS 관리형 규칙 그룹은 AWS Threat Research Team이 관리하는 사전 구성된 규칙 세트입니다:
>
> - **자동 업데이트**: AWS가 새로운 위협에 대응하여 규칙을 지속적으로 업데이트합니다.
> - **추가 비용 없음**: AWS 관리형 규칙 그룹은 AWS WAF 기본 요금에 포함됩니다.
> - **즉시 적용**: 복잡한 규칙을 직접 작성할 필요 없이 바로 사용할 수 있습니다.
>
> 주요 관리형 규칙 그룹:
>
> - **Core rule set (CRS)**: OWASP Top 10 등 일반적인 웹 취약점 방어
> - **SQL database**: SQL Injection 공격 패턴 탐지
> - **Known bad inputs**: 알려진 악성 입력 패턴 차단
> - **Amazon IP reputation list**: 악성 IP 주소 차단
> - **Anonymous IP list**: VPN, 프록시, Tor 등 익명 IP 차단
> - **Bot Control**: 봇 트래픽 관리 (추가 비용 발생)

40. **Choose initial protections** 섹션에서 `You build it`을 선택합니다.

> [!NOTE]
> **Recommended**와 **Essentials**는 사전 구성된 규칙 패키지입니다. 이 실습에서는 학습 목적으로 `You build it`을 선택하여 규칙을 직접 추가합니다.
> `You build it`은 추가하는 규칙 수에 따라 예상 비용이 증가합니다. 실습은 짧은 시간만 사용하고 바로 삭제하므로 실제 청구 금액은 미미합니다.

41. 오른쪽 **Add rules** 패널에서 `AWS-managed rule group`을 선택합니다.

    <img src="/images/week12/12-3-task2-step41-sqldatabase.png" alt="AWS-managed rule group 선택" class="guide-img-md" />

42. **Free** 목록에서 `SQL database`를 클릭합니다.

    <img src="/images/week12/12-3-task2-rule-detail.png" alt="SQL database 규칙 상세" class="guide-img-sm" />

43. 기본 설정을 유지하고 [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step47-addrule.png" alt="SQL database 추가 완료" class="guide-img-sm" />

    <img src="/images/week12/12-3-task2-step47-addrule.png" alt="SQL database 추가" class="guide-img-sm" />

> [!NOTE]
> **SQL database** 규칙 그룹(200 WCU)은 SQL Injection 공격 패턴을 탐지합니다. 요청 본문, 쿼리 문자열, URI, 헤더에서 SQL 구문을 검사합니다.

44. 다시 [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step48-addrule.png" alt="Add rule 클릭" class="guide-img-sm" />

45. `AWS-managed rule group`을 선택합니다.

    <img src="/images/week12/12-3-task2-rule-list.png" alt="AWS-managed rule group 목록" class="guide-img-sm" />

46. **Free** 목록에서 `Core rule set`을 클릭합니다.

    <img src="/images/week12/12-3-task2-rule-detail.png" alt="Core rule set 규칙 상세" class="guide-img-sm" />

47. 기본 설정을 유지하고 [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step47-corerule-added.png" alt="Core rule set 추가 완료" class="guide-img-sm" />

> [!NOTE]
> **Core rule set (CRS)** (700 WCU)는 OWASP Top 10에 포함된 일반적인 웹 취약점을 방어합니다. XSS, 파일 포함(File Inclusion), 경로 탐색(Path Traversal) 등의 공격 패턴을 탐지합니다.

48. 다시 [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step48-addrule.png" alt="Add rule 클릭" class="guide-img-sm" />

49. `AWS-managed rule group`을 선택합니다.

    <img src="/images/week12/12-3-task2-rule-list.png" alt="AWS-managed rule group 목록" class="guide-img-sm" />

50. **Free** 목록에서 `Known bad inputs`를 클릭합니다.

    <img src="/images/week12/12-3-task2-rule-detail.png" alt="Known bad inputs 규칙 상세" class="guide-img-sm" />

51. 기본 설정을 유지하고 [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step51-badinputs-added.png" alt="Known bad inputs 추가 완료" class="guide-img-sm" />

> [!NOTE]
> **Known bad inputs** (200 WCU)는 Log4j/Log4Shell 취약점 등 알려진 악성 입력 패턴을 차단합니다.

### 태스크 2.4: Rate-based 규칙 추가

> [!CONCEPT] Rate-based 규칙
>
> Rate-based 규칙은 동일한 IP 주소에서 일정 시간 내에 허용된 요청 수를 초과하면 자동으로 차단합니다:
>
> - **평가 주기**: 5분 단위로 요청 수를 집계합니다.
> - **임계값**: 10~2,000,000,000 범위에서 설정 가능합니다.
> - **자동 해제**: 요청 수가 임계값 아래로 떨어지면 자동으로 차단이 해제됩니다.
> - **DDoS 방어**: 단순한 DDoS 공격과 봇 공격을 효과적으로 차단합니다.

52. 다시 [[Add rule]] 버튼을 클릭합니다.
53. `Custom rule`을 선택합니다.

    <img src="/images/week12/12-3-task2-step53-customrule.png" alt="Custom rule 선택" class="guide-img-sm" />

54. `Rate-based rule`을 선택하고 [[Next]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step54-ratebased.png" alt="Rate-based rule 선택" class="guide-img-sm" />

55. **Action**에서 `Block`을 확인합니다.
56. **Rule name**에 `QuickTable-RateLimit-Rule`을 입력합니다.
57. **Rate limit**에 `100`을 입력합니다.
58. **Evaluation window**는 `5 minutes` (기본값)을 유지합니다.

> [!NOTE]
> Rate limit 100은 동일 IP에서 5분 동안 100개 이상의 요청이 오면 차단한다는 의미입니다. 프로덕션 환경에서는 서비스 특성에 맞게 조정합니다 (예: 일반 웹사이트 2,000, API 서비스 1,000).
>
> 이 실습에서는 테스트 편의를 위해 낮은 값(100)을 설정합니다.

59. **Rule configuration**은 기본값을 유지합니다:
    - **Request aggregation**: `Source IP address`
    - **Scope of inspection and rate limiting**: `Consider all requests`

60. [[Add rule]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step60-ratelimit.png" alt="Rate-based rule 추가 완료" class="guide-img-sm" />

> [!NOTE]
> 4개의 규칙이 추가되었습니다. 각 규칙의 WCU(Web ACL Capacity Unit)가 표시됩니다:
>
> | 규칙                                     | WCU       |
> | ---------------------------------------- | --------- |
> | AWS-AWSManagedRulesSQLiRuleSet           | 200       |
> | AWS-AWSManagedRulesCommonRuleSet         | 700       |
> | AWS-AWSManagedRulesKnownBadInputsRuleSet | 200       |
> | QuickTable-RateLimit-Rule                | 2         |
> | **합계**                                 | **1,102** |
>
> Web ACL의 최대 WCU는 5,000입니다. 현재 1,102 WCU를 사용하므로 여유가 충분합니다.

61. 추가된 규칙 목록을 확인합니다.

    <img src="/images/week12/12-3-task2-step60-rules.png" alt="4개 규칙 추가 완료" class="guide-img-sm" />

### 태스크 2.5: Name and describe

62. **Name**에 `QuickTable-WAF-WebACL`을 입력합니다.
63. **Description**에 `WAF Web ACL for QuickTable API protection`을 입력합니다.

    <img src="/images/week12/12-3-task2-step63-name.png" alt="Name and describe" class="guide-img-md" />

### 태스크 2.6: Customize protection pack (web ACL)

64. **Logging destination**은 이 실습에서는 설정하지 않습니다.

> [!NOTE]
> 프로덕션 환경에서는 Amazon CloudWatch Logs, Amazon S3, 또는 Amazon Data Firehose로 로깅을 설정하여 차단된 요청을 분석할 수 있습니다.

65. [[Create protection pack (web ACL)]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-task2-step65-create.png" alt="Create protection pack" class="guide-img-md" />

> [!NOTE]
> Protection Pack (Web ACL) 생성에 1-2분이 소요됩니다. 생성이 완료되면 상세 페이지로 이동합니다.
> 태스크 2.2에서 이미 Amazon API Gateway를 연결했으므로, 생성과 동시에 Amazon API Gateway에 자동으로 적용됩니다.

✅ **태스크 완료**: AWS WAF Protection Pack (Web ACL)이 생성되고 Amazon API Gateway에 적용되었습니다.

## 태스크 3: AWS WAF 보호 테스트

이 태스크에서는 AWS WAF가 적용된 상태에서 악성 요청이 차단되는지 확인합니다.

> [!IMPORTANT]
> AWS CloudShell 세션이 종료되면 환경 변수가 초기화됩니다. 다음 명령어로 확인합니다:
>
> ```bash
> echo $API_URL
> ```
>
> 출력이 없으면 환경 변수를 다시 설정합니다:
>
> ```bash
> export API_URL="<ApiGatewayInvokeUrl>"
> ```

### 태스크 3.1: 정상 요청 확인

66. AWS CloudShell에서 정상적인 예약 생성 요청을 보냅니다:

    <img src="/images/week12/12-3-task3-step66-normal.png" alt="정상 요청 확인" class="guide-img-md" />

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "서울 레스토랑", "date": "2026-04-20", "time": "19:00", "partySize": 2, "phoneNumber": "010-5678-1234"}' \
  | jq .
```

> [!OUTPUT]
>
> ```json
> {
>   "visitorId": "<your-ip-address>",
>   "reservationId": "<uuid-format>",
>   "restaurantName": "서울 레스토랑",
>   "date": "2026-04-20",
>   "time": "19:00",
>   "partySize": 2,
>   "phoneNumber": "010-5678-1234",
>   "status": "pending",
>   "createdAt": "<current-timestamp>"
> }
> ```

> [!NOTE]
> 정상 요청은 AWS WAF 규칙에 매칭되지 않으므로 기본 동작(Allow)에 의해 허용됩니다.

### 태스크 3.2: SQL Injection 차단 확인

67. SQL Injection 패턴이 포함된 요청을 보냅니다:

    <img src="/images/week12/12-3-task3-step67-sqli403.png" alt="SQL Injection 차단 403" class="guide-img-md" />

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

> [!NOTE]
> HTTP 403 (Forbidden) 응답이 반환되면 AWS WAF가 SQL Injection 공격을 성공적으로 차단한 것입니다.

68. 응답 본문을 확인합니다:

    <img src="/images/week12/12-3-task3-step68-forbidden.png" alt="Forbidden 응답" class="guide-img-md" />

```bash
curl -s -X POST $API_URL/reservations \
  -H "Content-Type: application/json" \
  -d '{"restaurantName": "test'\'' OR 1=1; DROP TABLE reservations; --", "date": "2026-04-15", "time": "18:00", "partySize": 4, "phoneNumber": "010-0000-0000"}' \
  | jq .
```

> [!OUTPUT]
>
> ```json
> { "message": "Forbidden" }
> ```

### 태스크 3.3: XSS 차단 확인

69. XSS 패턴이 포함된 요청을 보냅니다:

    <img src="/images/week12/12-3-task3-step69-xss403.png" alt="XSS 차단 403" class="guide-img-md" />

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

> [!NOTE]
> XSS 공격도 AWS WAF Core rule set에 의해 차단되었습니다.

### 태스크 3.4: 추가 공격 패턴 테스트

70. 경로 탐색(Path Traversal) 공격을 테스트합니다:

    <img src="/images/week12/12-3-task3-step70-path403.png" alt="Path Traversal 차단 403" class="guide-img-md" />

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
  "$API_URL/reservations?file=../../../etc/passwd"
```

> [!OUTPUT]
>
> ```
> HTTP Status: 403
> ```

71. 정상 조회 요청이 여전히 동작하는지 확인합니다:

    <img src="/images/week12/12-3-task3-step71-get.png" alt="정상 GET 요청" class="guide-img-md" />

```bash
curl -s -X GET $API_URL/reservations | jq .
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
> 정상 요청은 모두 허용되고, 악성 요청만 차단됩니다. 이것이 AWS WAF의 핵심 가치입니다.

✅ **태스크 완료**: AWS WAF가 SQL Injection, XSS, 경로 탐색 공격을 성공적으로 차단했습니다.

## 태스크 4: Amazon CloudWatch에서 AWS WAF 메트릭 확인

이 태스크에서는 AWS WAF 콘솔에서 차단된 요청을 확인합니다.

### 태스크 4.1: Web ACL 대시보드 확인

72. AWS WAF 콘솔의 왼쪽 메뉴에서 **Protection packs (web ACLs)**를 선택합니다.
73. `QuickTable-WAF-WebACL` 행에서 **Dashboard** 열의 **View**를 클릭합니다.

    <img src="/images/week12/12-3-task4-step73-dashboard.png" alt="WAF Dashboard" class="guide-img-md" />

> [!NOTE]
> 또는 `QuickTable-WAF-WebACL`을 선택한 후 [[Actions]] 드롭다운에서 **View dashboard**를 선택합니다.
>
> <img src="/images/week12/12-3-task4-step73-actions.png" alt="WAF Actions 드롭다운" class="guide-img-sm" />

74. 대시보드에서 다음 정보를 확인합니다:
    - **Summary**: Total, Allowed, Blocked 요청 수
    - **Protection pack (web ACL) activity**: 규칙별 트래픽 흐름 (Sequential rules view)
    - **Action totals**: 시간대별 Allow/Block 요청 그래프

    <img src="/images/week12/12-3-task4-step74-summary.png" alt="WAF Dashboard Summary" class="guide-img-md" />

    <img src="/images/week12/12-3-task4-step74-activity.png" alt="WAF Protection pack activity" class="guide-img-md" />

> [!NOTE]
> 메트릭이 표시되기까지 1-2분이 소요될 수 있습니다. 그래프가 비어 있으면 잠시 기다린 후 새로고침합니다.

### 태스크 4.2: 규칙별 메트릭 확인

75. **All rules** 섹션에서 규칙별 메트릭을 확인합니다.

    <img src="/images/week12/12-3-task4-step75-allrules.png" alt="All rules 메트릭" class="guide-img-md" />

> [!NOTE]
> 각 규칙 그룹별로 차단된 요청 수가 표시됩니다:
>
> - **AWS-AWSManagedRulesSQLiRuleSet - BlockedRequests**: SQL Injection 차단 횟수
> - **AWS-AWSManagedRulesCommonRuleSet - BlockedRequests**: XSS 등 일반 공격 차단 횟수
> - **ALL - BlockedRequests**: 전체 차단 횟수
> - **ALL - AllowedRequests**: 전체 허용 횟수

### 태스크 4.3: Overview에서 트래픽 특성 확인

76. **Overview** 섹션에서 **Traffic characteristics**를 선택합니다.

    <img src="/images/week12/12-3-task4-step76-traffic.png" alt="Traffic characteristics" class="guide-img-md" />

77. **Attack types**에서 탐지된 공격 유형(SQLi, XSS, GenericLFI 등)을 확인합니다.
78. **Top 10 countries**에서 요청 출발지 국가를 확인합니다.

> [!NOTE]
> Overview에서는 다음 카테고리별로 트래픽을 분석할 수 있습니다:
>
> - **Traffic characteristics**: 공격 유형, 요청 위치, 클라이언트 디바이스
> - **Rule characteristics**: 규칙별 차단 통계
> - **Bots**: 봇 트래픽 탐지 현황
> - **Anti-DDoS**: L7 DDoS 공격 탐지 현황

### 태스크 4.4: Sampled requests 확인

79. 같은 Dashboard 페이지 하단으로 스크롤하여 **Sampled requests** 섹션을 확인합니다.

    <img src="/images/week12/12-3-task4-step79-sampled.png" alt="Sampled requests" class="guide-img-md" />

> [!NOTE]
> **Protection packs (web ACLs)** 목록에서 `QuickTable-WAF-WebACL`의 **Sampled requ...** 열의 **View**를 클릭하거나, [[Actions]] 드롭다운에서 **View sampled requests**를 선택해도 동일한 화면으로 이동할 수 있습니다.

80. Sampled requests에서 다음 정보를 확인합니다:
    - **Source IP**: 요청 출발지 IP
    - **URI**: 요청 URI
    - **Matching rule**: 매칭된 규칙 이름
    - **Action**: 수행된 동작 (Allow/Block)
    - **Time**: 요청 시간

81. 차단된 요청(Block)을 클릭하여 상세 정보를 확인합니다.

    <img src="/images/week12/12-3-task4-step81-detail1.png" alt="차단된 요청 상세 1" class="guide-img-md" />

    <img src="/images/week12/12-3-task4-step81-detail2.png" alt="차단된 요청 상세 2" class="guide-img-md" />

> [!TIP]
> Sampled requests는 최대 3시간 동안의 요청 샘플을 보여줍니다. 전체 로그가 필요한 경우 AWS WAF 로깅을 활성화하여 Amazon S3, Amazon CloudWatch Logs, 또는 Amazon Data Firehose로 전송할 수 있습니다.

✅ **태스크 완료**: AWS WAF 메트릭과 차단된 요청을 확인했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> AWS WAF Web ACL은 AWS CloudFormation 스택에 포함되지 않으므로 **수동으로 먼저 삭제**해야 합니다. Web ACL을 삭제하기 전에 연결된 리소스를 먼저 해제해야 합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `12-3`
6. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: AWS WAF Web ACL 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS CloudShell에서 Web ACL ID와 Lock Token을 확인합니다:

```bash
aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2 --query "WebACLs[?Name=='QuickTable-WAF-WebACL'].[Id,LockToken]" --output text
```

<img src="/images/week12/12-3-cleanup-step7-webacl-id.png" alt="Web ACL ID 확인" class="guide-img-md" />

8. Amazon API Gateway 연결을 해제합니다:

```bash
API_STAGE_ARN=$(aws cloudformation describe-stacks --stack-name week12-3-waf-api-protection-stack --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayStageArn'].OutputValue" --output text --region ap-northeast-2)
WEB_ACL_ARN=$(aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2 --query "WebACLs[?Name=='QuickTable-WAF-WebACL'].ARN | [0]" --output text)
aws wafv2 disassociate-web-acl --resource-arn $API_STAGE_ARN --region ap-northeast-2
```

<img src="/images/week12/12-3-cleanup-step8-disassociate.png" alt="API Gateway 연결 해제" class="guide-img-md" />

9. Web ACL을 삭제합니다:

```bash
WEB_ACL_ID=$(aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2 --query "WebACLs[?Name=='QuickTable-WAF-WebACL'].Id | [0]" --output text)
LOCK_TOKEN=$(aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2 --query "WebACLs[?Name=='QuickTable-WAF-WebACL'].LockToken | [0]" --output text)
aws wafv2 delete-web-acl --name QuickTable-WAF-WebACL --scope REGIONAL --id $WEB_ACL_ID --lock-token $LOCK_TOKEN --region ap-northeast-2
```

<img src="/images/week12/12-3-cleanup-step9-delete.png" alt="Web ACL 삭제" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws wafv2 list-web-acls --scope REGIONAL --region ap-northeast-2 --query "WebACLs[?Name=='QuickTable-WAF-WebACL']" --output text
> ```
>
> 출력이 없으면 삭제 완료입니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

10. 상단 검색창에 `WAF`를 입력하고 **WAF & Shield**를 선택합니다.
11. 왼쪽 메뉴에서 **Protection packs (web ACLs)**를 선택합니다.
12. `QuickTable-WAF-WebACL`을 선택합니다.
13. [[Actions]] 드롭다운에서 **Delete protection pack (web ACL)**을 선택합니다.

    <img src="/images/week12/12-3-cleanup-step13-actions.png" alt="Actions 드롭다운에서 Delete 선택" class="guide-img-md" />

14. 확인 창에 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step14-delete.png" alt="delete 입력 후 삭제" class="guide-img-sm" />

### 단계 3: AWS CloudFormation 스택 삭제

15. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
16. `week12-3-waf-api-protection-stack` 스택을 선택합니다.
17. [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step17-delete-stack.png" alt="Delete stack 버튼" class="guide-img-md" />

18. 확인 창에서 스택 이름 `week12-3-waf-api-protection-stack`을 입력하고 [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step18-confirm.png" alt="스택 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 Amazon DynamoDB 테이블, AWS Lambda 함수, Amazon API Gateway, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

### 단계 4: Amazon CloudWatch Log Group 삭제

19. 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
20. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
21. 검색창에 `Week12-3`을 입력합니다.
22. 다음 로그 그룹의 체크박스를 선택합니다:
    - `/aws/lambda/Week12-3-CreateReservation`
    - `/aws/lambda/Week12-3-GetReservations`
23. **Actions** > `Delete log group(s)`를 선택합니다.

    <img src="/images/week12/12-3-cleanup-step23-loggroup.png" alt="Delete log group 선택" class="guide-img-md" />

24. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step24-delete.png" alt="Delete 확인" class="guide-img-sm" />

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다. 이 외에 이번 실습과 관련된 로그 그룹이 남아있다면 함께 삭제합니다.

> [!NOTE]
> AWS CLI로 삭제하려면 AWS CloudShell에서 다음 명령어를 실행합니다:
>
> ```bash
> aws logs delete-log-group --log-group-name /aws/lambda/Week12-3-CreateReservation --region ap-northeast-2
> aws logs delete-log-group --log-group-name /aws/lambda/Week12-3-GetReservations --region ap-northeast-2
> ```
>
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/Week12-3 --query "logGroups[*].logGroupName" --output text --region ap-northeast-2
> ```
>
> 출력이 없으면 삭제 완료입니다.
>
> <img src="/images/week12/12-3-cleanup-step24-cli.png" alt="CLI 로그 그룹 삭제" class="guide-img-md" />

### 단계 5: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

25. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
26. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
27. **Regions**에서 `ap-northeast-2`를 선택합니다.
28. **Resource types**에서 `All supported resource types`를 선택합니다.
29. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `12-3`
30. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week12/12-3-cleanup-step30-tageditor.png" alt="Tag Editor 최종 확인" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS WAF 개발자 가이드](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/)
- [AWS WAF 관리형 규칙 그룹](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/aws-managed-rule-groups-list.html)
- [AWS Shield 개발자 가이드](https://docs.aws.amazon.com/ko_kr/waf/latest/developerguide/shield-chapter.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 📚 참고: AWS WAF 및 AWS Shield 아키텍처

### AWS WAF 동작 원리

**요청 처리 흐름**:

- 클라이언트가 API 요청을 전송합니다.
- AWS WAF가 Web ACL의 규칙을 우선순위 순서대로 평가합니다.
- 규칙에 매칭되면 해당 규칙의 동작(Block/Allow/Count)을 수행합니다.
- 어떤 규칙에도 매칭되지 않으면 기본 동작(Default Action)을 수행합니다.
- Allow된 요청만 Amazon API Gateway로 전달됩니다.

**AWS WAF 규칙 유형**:

| 규칙 유형          | 설명                    | 사용 사례                        |
| ------------------ | ----------------------- | -------------------------------- |
| Regular rule       | 조건 기반 매칭          | 특정 IP 차단, 특정 URI 패턴 차단 |
| Rate-based rule    | 요청 빈도 기반          | DDoS 방어, 봇 차단               |
| Managed rule group | AWS/마켓플레이스 관리형 | SQL Injection, XSS 방어          |

**AWS WAF 연결 가능 리소스**:

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

**AWS Shield Standard vs Advanced 비교**:

| 기능        | Standard | Advanced   |
| ----------- | -------- | ---------- |
| 비용        | 무료     | 월 $3,000+ |
| L3/L4 방어  | ✅       | ✅         |
| L7 방어     | ❌       | ✅         |
| SRT 지원    | ❌       | ✅ (24/7)  |
| 비용 보호   | ❌       | ✅         |
| 상세 보고서 | ❌       | ✅         |

### 다층 방어 아키텍처 (Defense in Depth)

**계층별 보안 서비스**:

| 계층         | 서비스                       | 방어 대상                                    |
| ------------ | ---------------------------- | -------------------------------------------- |
| 엣지 (L3/L4) | AWS Shield Standard          | SYN Flood, UDP Reflection, DNS Amplification |
| 엣지 (L7)    | AWS WAF + Amazon CloudFront  | SQL Injection, XSS, 봇 공격                  |
| 네트워크     | 보안 그룹, NACL              | 포트 스캔, 비인가 접근                       |
| 애플리케이션 | Amazon Cognito, AWS IAM      | 인증/인가                                    |
| 데이터       | AWS KMS, AWS Secrets Manager | 데이터 암호화, 자격증명 관리                 |

**QuickTable 보안 아키텍처 전체 흐름**:

- AWS Shield Standard → L3/L4 DDoS 자동 방어
- AWS WAF → SQL Injection, XSS, Rate limiting
- Amazon API Gateway → 요청 검증, 스로틀링
- Amazon Cognito (Week 4-2) → JWT 토큰 인증
- AWS Lambda → 비즈니스 로직 처리
- Amazon DynamoDB → 데이터 저장

### 프로덕션 환경 개선사항

**AWS WAF 로깅 활성화**:

- Amazon S3, Amazon CloudWatch Logs, 또는 Amazon Data Firehose로 전체 요청 로그 전송
- 차단된 요청의 상세 분석 및 오탐(False Positive) 확인

**사용자 정의 규칙 추가**:

- 특정 국가 IP 차단 (Geo-match)
- 특정 User-Agent 차단
- 요청 크기 제한 (Size constraint)

**Amazon CloudFront 연동**:

- 엣지 로케이션에서 AWS WAF 적용 (지연 시간 감소)
- AWS Shield Standard 자동 적용 범위 확대
- 캐싱으로 오리진 부하 감소

**모니터링 및 알림**:

- Amazon CloudWatch 알람으로 차단 급증 시 알림
- AWS Security Hub 통합
- Amazon SNS로 보안 담당자 알림

**AWS Firewall Manager**:

- 멀티 계정 환경에서 AWS WAF 정책 중앙 관리
- 조직 전체에 일관된 보안 정책 적용

### 보안 모범 사례

**AWS WAF 규칙 관리**:

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
