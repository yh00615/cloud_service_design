---
title: 'AWS X-Ray를 활용한 서버리스 애플리케이션 추적'
week: 13
session: 2
awsServices:
  - AWS X-Ray
learningObjectives:
  - 분산 추적의 개념과 AWS X-Ray의 트레이스 구조를 이해할 수 있습니다.
  - AWS Lambda 함수에 통합된 AWS X-Ray SDK 코드 패턴을 이해하고 Active tracing 설정을 확인할 수 있습니다.
  - AWS X-Ray 서비스 맵으로 애플리케이션 구조를 시각화할 수 있습니다.
  - 트레이스를 분석하여 병목 지점과 오류를 파악할 수 있습니다.

prerequisites:
  - Week 1-12 완료
  - 시스템 모니터링 기본 개념 이해
  - AWS Lambda 함수 기본 지식
---

이 실습에서는 AWS X-Ray를 사용하여 QuickTable 레스토랑 예약 시스템의 분산 추적을 구현합니다. Week 4에서 구축한 QuickTable API에 AWS X-Ray SDK를 통합하고, 서비스 맵과 트레이스를 분석하여 예약 생성 및 조회 과정의 성능과 병목 지점을 식별하는 방법을 학습합니다.  
Amazon API Gateway → AWS Lambda → Amazon DynamoDB로 이어지는 전체 요청 흐름을 추적하고, 각 단계의 실행 시간과 오류를 시각화합니다.

> [!CONCEPT] 분산 추적 (Distributed Tracing)
> 분산 추적은 마이크로서비스 아키텍처에서 하나의 요청이 여러 서비스를 거치는 과정을 추적하는 기술입니다. 각 서비스에서 소요된 시간, 발생한 오류, 호출 순서를 시각화하여 성능 병목 지점과 장애 원인을 빠르게 파악할 수 있습니다.
>
> **AWS X-Ray**는 AWS에서 제공하는 분산 추적 서비스로, 애플리케이션의 요청 흐름을 서비스 맵과 트레이스 타임라인으로 시각화합니다.
>
> **주요 구성 요소**:
>
> - **트레이스 (Trace)**: 하나의 요청이 시작부터 끝까지 거치는 전체 경로
> - **세그먼트 (Segment)**: 각 서비스(Amazon API Gateway, AWS Lambda 등)에서 처리한 작업 단위
> - **서브세그먼트 (Subsegment)**: 세그먼트 내 세부 작업 (Amazon DynamoDB 호출, 비즈니스 로직 등)
> - **어노테이션 (Annotation)**: 검색 가능한 키-값 메타데이터
> - **서비스 맵 (Service Map)**: 서비스 간 연결과 상태를 보여주는 시각적 다이어그램

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
> - 태스크 1: AWS Lambda 함수 코드 확인 (AWS X-Ray SDK 통합 패턴 확인)
> - 태스크 2: AWS X-Ray 추적 활성화 확인 (AWS Lambda 함수의 Active tracing 설정 확인)
> - 태스크 3~4: API 호출 및 트레이스 생성 (예약 생성/조회 API 호출하여 AWS X-Ray 트레이스 데이터 생성)
> - 태스크 5~6: 서비스 맵 확인 및 트레이스 분석
> - 태스크 7: AWS X-Ray Insights 및 Analytics 활용

> [!NOTE]
> 이 실습에서는 `aws_xray_sdk` (AWS X-Ray SDK for Python)를 사용합니다.
> AWS X-Ray SDK/Daemon은 2026년 2월 25일부터 유지보수 모드에 진입하여 보안 패치만 제공되고 있습니다.
> 새로운 프로젝트에서는 [OpenTelemetry 기반 계측](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html)이 권장되지만, 기존 X-Ray SDK 코드는 계속 동작합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 QuickTable 레스토랑 예약 시스템의 AWS X-Ray 추적 환경을 자동으로 생성합니다. Week 4에서 구축한 QuickTable API를 재생성하고, AWS X-Ray SDK를 통합한 AWS Lambda 함수를 배포합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon DynamoDB 테이블**: Reservations (사용자별 예약 데이터 저장, userId/reservationId 키)
- **AWS Lambda Layer**: aws-xray-sdk (Custom Resource로 자동 빌드, AWS X-Ray SDK 패키지 포함)
- **AWS Lambda 함수**: CreateReservation, GetReservations (AWS X-Ray SDK 통합, 예약 생성/조회 처리)
- **AWS IAM 역할**: AWS Lambda 실행 역할 (Amazon DynamoDB 접근 + AWS X-Ray 추적 권한 포함)
- **Amazon API Gateway**: QuickTableXRayAPI (REST API, /reservations 리소스 및 POST/GET 메서드, AWS X-Ray 추적 활성화)

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week13-2-xray-lab.zip` 파일의 압축을 해제합니다.
2. `week13-2-xray-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

    <img src="/images/week13/13-2-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week13-2-xray-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-task0-step8-upload.png" alt="CloudFormation 템플릿 업로드" class="guide-img-md" />

9. **Stack name**에 `week13-2-xray-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **EnvironmentName**: `week13-2-xray-lab` (기본값 유지)
    - **ProjectTag**: `AWS-Lab` (기본값 유지)
    - **WeekTag**: `13-2` (기본값 유지)
    - **CreatedByTag**: `CloudFormation` (기본값 유지)

> [!NOTE]
> Parameters에서 설정한 태그 값(Project, Week, CreatedBy)은 모든 리소스에 자동으로 적용됩니다. 별도로 Tags 섹션에서 추가할 필요가 없습니다.

11. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-task0-step11-options.png" alt="CloudFormation Configure stack options" class="guide-img-md" />

12. **Configure stack options** 페이지에서 기본값을 유지합니다.
13. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.

    <img src="/images/week13/13-2-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

14. [[Next]] 버튼을 클릭합니다.
15. **Review and create** 페이지에서 설정을 확인합니다.
16. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. AWS X-Ray SDK Lambda Layer 자동 빌드 과정이 포함되어 있어 일반 스택보다 시간이 더 걸릴 수 있습니다. 상태가 "CREATE_IN_PROGRESS"로 표시되며, "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

17. **Outputs** 탭을 선택합니다.
18. 출력값들을 확인하고 메모장에 복사합니다:
    - `ApiUrl`: Amazon API Gateway Invoke URL (예: https://abc123.execute-api.ap-northeast-2.amazonaws.com/prod)
    - `CreateFunctionName`: 예약 생성 AWS Lambda 함수 이름
    - `GetFunctionName`: 예약 조회 AWS Lambda 함수 이름
    - `TableName`: Amazon DynamoDB 테이블 이름 (Reservations)

    <img src="/images/week13/13-2-task0-step18-outputs.png" alt="CloudFormation Outputs 탭" class="guide-img-md" />

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

> [!NOTE]
> AWS CloudFormation 스택은 AWS X-Ray SDK(`aws_xray_sdk`)를 포함하는 AWS Lambda Layer를 Custom Resource로 자동 빌드합니다. 이 Layer가 CreateReservation, GetReservations 함수에 연결되어 `from aws_xray_sdk.core import patch_all, xray_recorder` 코드가 정상 동작합니다.
> AWS Lambda 런타임에는 AWS X-Ray SDK가 기본 포함되어 있지 않으므로, Layer 없이는 `No module named 'aws_xray_sdk'` 오류가 발생합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: AWS Lambda 함수 코드 확인

이 태스크에서는 AWS CloudFormation으로 배포된 AWS Lambda 함수의 코드를 확인합니다. AWS X-Ray SDK가 통합되어 있으며, 예약 생성 및 조회 작업을 추적합니다.

19. AWS Management Console에 로그인한 후 상단 검색창에 `Lambda`을 입력하고 선택합니다.
20. 왼쪽 메뉴에서 **Functions**를 선택합니다.
21. 함수 목록에서 `CreateReservation`으로 시작하는 함수를 선택합니다.

    <img src="/images/week13/13-2-task1-step21-lambda.png" alt="Lambda 함수 목록" class="guide-img-md" />

22. **Code** 탭을 선택합니다.

    <img src="/images/week13/13-2-task1-step22-code.png" alt="Lambda Code 탭" class="guide-img-md" />

23. 코드 편집기에서 AWS X-Ray SDK 통합 부분을 확인합니다.

> [!NOTE]
> AWS CloudFormation 템플릿에서 AWS X-Ray SDK가 포함된 AWS Lambda 함수 코드가 자동으로 배포되었습니다.
> 코드에는 `aws_xray_sdk` 라이브러리를 사용하여 Amazon DynamoDB 호출을 추적하는 로직이 포함되어 있습니다.
>
> **다음 코드 패턴을 확인합니다**:
>
> - `from aws_xray_sdk.core import patch_all, xray_recorder` - SDK 임포트
> - `patch_all()` - boto3 Amazon DynamoDB 호출 자동 추적
> - `xray_recorder.begin_subsegment()` / `xray_recorder.end_subsegment()` - 커스텀 서브세그먼트 생성
> - `subsegment.put_annotation()` - 검색 가능한 어노테이션 추가
> - `subsegment.put_metadata()` - 상세 메타데이터 추가
>
> **주요 코드 패턴**:
>
> ```python
> from aws_xray_sdk.core import patch_all, xray_recorder
> patch_all()  # boto3 Amazon DynamoDB 호출 자동 추적
>
> # 커스텀 서브세그먼트 생성
> subsegment = xray_recorder.begin_subsegment('create_dynamodb_item')
> subsegment.put_annotation('reservation_id', reservation_id)
> subsegment.put_metadata('item', item)
> xray_recorder.end_subsegment()
> ```

24. `GetReservations`로 시작하는 함수도 동일하게 확인합니다.

    <img src="/images/week13/13-2-task1-step24-layer.png" alt="GetReservations 함수 확인" class="guide-img-md" />

✅ **태스크 완료**: AWS Lambda 함수 코드를 확인했습니다.

## 태스크 2: AWS X-Ray 추적 활성화 확인

이 태스크에서는 AWS Lambda 함수의 AWS X-Ray 추적이 활성화되어 있는지 확인합니다.

25. AWS Lambda 콘솔에서 `CreateReservation` 함수를 선택합니다.
26. **Configuration** 탭을 선택합니다.
27. 왼쪽 메뉴에서 **Monitoring and operations tools**를 선택합니다.
28. **CloudWatch Application Signals and AWS X-Ray** 섹션에서 **Lambda service traces**가 활성화되어 있는지 확인합니다.

    <img src="/images/week13/13-2-task2-step28-xray-active.png" alt="X-Ray Active tracing 확인" class="guide-img-md" />

> [!NOTE]
> AWS CloudFormation 템플릿에서 Lambda service traces(Active tracing)가 자동으로 활성화되었습니다.
> 이 설정으로 AWS Lambda 함수의 모든 호출이 AWS X-Ray에 자동으로 추적됩니다.

29. `GetReservations` 함수도 동일하게 확인합니다.

    <img src="/images/week13/13-2-task2-step29-env.png" alt="GetReservations X-Ray 확인" class="guide-img-md" />

✅ **태스크 완료**: AWS X-Ray 추적이 활성화되어 있습니다.

## 태스크 3: 예약 생성 API 호출 및 트레이스 생성

이 태스크에서는 QuickTable 예약 생성 API를 호출하여 AWS X-Ray 트레이스를 생성합니다.

30. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> AWS CloudShell이 시작될 때까지 기다립니다.

31. 환경 변수를 설정합니다:

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

32. 환경 변수가 올바르게 설정되었는지 확인합니다:

```bash
echo $API_URL
```

<img src="/images/week13/13-2-task3-step32-cloudshell.png" alt="CloudShell 환경 변수 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> https://abc123def4.execute-api.ap-northeast-2.amazonaws.com/prod
> ```

33. 다음 명령어를 실행하여 예약을 생성합니다:

```bash
curl -s -X POST ${API_URL}/reservations \
  -H "Content-Type: application/json" \
  -d '{"userId": "anonymous", "restaurantName": "강남 맛집", "date": "2026-05-20", "time": "18:00", "partySize": 4, "phoneNumber": "010-1234-5678"}' | jq .
```

<img src="/images/week13/13-2-task3-step33-post.png" alt="예약 생성 요청" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "message": "Reservation created",
>   "reservationId": "RSV-20260520-a1b2c3d4"
> }
> ```

> [!NOTE]
> 요청 본문의 `userId`는 Amazon DynamoDB 테이블의 파티션 키입니다.
> 태스크 3에서는 `"anonymous"`로, 34번에서는 `"user-kim"`, `"user-lee"`, `"user-park"` 등 다양한 사용자로 예약을 생성합니다.
> 태스크 4에서 쿼리 파라미터로 특정 사용자의 예약만 조회할 수 있습니다.

34. 다양한 사용자와 레스토랑 데이터로 여러 건의 예약을 생성하여 추가 트레이스를 생성합니다:

```bash
curl -s -X POST ${API_URL}/reservations -H "Content-Type: application/json" \
  -d '{"userId": "user-kim", "restaurantName": "이태원 파스타", "date": "2026-05-21", "time": "19:00", "partySize": 2, "phoneNumber": "010-2345-6789"}' | jq .

curl -s -X POST ${API_URL}/reservations -H "Content-Type: application/json" \
  -d '{"userId": "user-lee", "restaurantName": "홍대 스시", "date": "2026-05-22", "time": "12:30", "partySize": 6, "phoneNumber": "010-3456-7890"}' | jq .

curl -s -X POST ${API_URL}/reservations -H "Content-Type: application/json" \
  -d '{"userId": "user-park", "restaurantName": "서초 한정식", "date": "2026-05-23", "time": "17:30", "partySize": 8, "phoneNumber": "010-4567-8901"}' | jq .

curl -s -X POST ${API_URL}/reservations -H "Content-Type: application/json" \
  -d '{"userId": "user-kim", "restaurantName": "종로 갈비", "date": "2026-05-24", "time": "18:30", "partySize": 4, "phoneNumber": "010-5678-9012"}' | jq .

curl -s -X POST ${API_URL}/reservations -H "Content-Type: application/json" \
  -d '{"userId": "user-lee", "restaurantName": "강남 맛집", "date": "2026-05-25", "time": "20:00", "partySize": 3, "phoneNumber": "010-6789-0123"}' | jq .
```

<img src="/images/week13/13-2-task3-step34-get.png" alt="다양한 예약 생성" class="guide-img-md" />

> [!TIP]
> userId, 레스토랑 이름, 날짜, 인원 수가 각각 다르게 생성되므로 태스크 6에서 어노테이션 기반 필터링을 테스트할 때 유용합니다.

✅ **태스크 완료**: 예약 생성 트레이스가 생성되었습니다.

## 태스크 4: 예약 조회 API 호출 및 트레이스 생성

이 태스크에서는 QuickTable 예약 조회 API를 호출하여 AWS X-Ray 트레이스를 생성합니다.

35. AWS CloudShell에서 다음 명령어를 실행하여 anonymous 사용자의 예약을 조회합니다:

```bash
curl -s -X GET "${API_URL}/reservations" | jq .
```

<img src="/images/week13/13-2-task4-step35-get-anon.png" alt="anonymous 사용자 예약 조회" class="guide-img-md" />

> [!NOTE]
> 쿼리 파라미터 없이 호출하면 기본값인 `anonymous` 사용자의 예약이 조회됩니다.

36. 특정 사용자의 예약을 조회합니다:

```bash
curl -s -X GET "${API_URL}/reservations?userId=user-kim" | jq .
```

<img src="/images/week13/13-2-task4-step36-get-user.png" alt="user-kim 예약 조회" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> [
>   {
>     "userId": "user-kim",
>     "reservationId": "RSV-20260521-a1b2c3d4",
>     "restaurantName": "이태원 파스타",
>     "date": "2026-05-21",
>     "time": "19:00",
>     "partySize": 2,
>     "status": "confirmed",
>     "createdAt": "2026-05-03T10:30:00.123456"
>   },
>   {
>     "userId": "user-kim",
>     "reservationId": "RSV-20260524-e5f6g7h8",
>     "restaurantName": "종로 갈비",
>     "date": "2026-05-24",
>     "time": "18:30",
>     "partySize": 4,
>     "status": "confirmed",
>     "createdAt": "2026-05-03T10:31:00.456789"
>   }
> ]
> ```

37. 다른 사용자의 예약도 조회하여 추가 트레이스를 생성합니다:

```bash
curl -s -X GET "${API_URL}/reservations?userId=user-lee" | jq .
curl -s -X GET "${API_URL}/reservations?userId=user-park" | jq .
```

<img src="/images/week13/13-2-task4-step37-get-all.png" alt="다른 사용자 예약 조회" class="guide-img-md" />

✅ **태스크 완료**: 예약 조회 트레이스가 생성되었습니다.

## 태스크 5: 서비스 맵 확인

이 태스크에서는 AWS X-Ray 콘솔에서 QuickTable API의 서비스 맵을 확인합니다.

38. AWS Management Console에 로그인한 후 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.

> [!NOTE]
> AWS X-Ray는 Amazon CloudWatch 콘솔에 통합되어 있습니다.
> 왼쪽 메뉴의 **Application Signals (APM)** 섹션에서 AWS X-Ray 관련 기능을 사용할 수 있습니다.

39. 왼쪽 메뉴에서 **Application Signals (APM)** > **Trace Map**을 선택합니다.
40. 서비스 맵에서 다음 구성 요소를 확인합니다:
    - **Client**: 요청을 보낸 클라이언트 (AWS CloudShell/curl)
    - **ApiGateway Stage**: QuickTableXRayAPI/prod
    - **Lambda Context / Lambda Function**: CreateReservation, GetReservations (각각 2개 노드)
    - **DynamoDB Table**: Reservations

    <img src="/images/week13/13-2-task5-step40-tracemap.png" alt="X-Ray Trace Map" class="guide-img-md" />

> [!NOTE]
> 서비스 맵이 표시되는 데 최대 5분이 소요될 수 있습니다. 페이지를 새로고침하여 확인합니다.
>
> **서비스 맵 구성 요소**:
>
> - **Client 노드**: 요청을 보낸 클라이언트(AWS CloudShell/curl)를 나타냅니다.
> - **ApiGateway Stage 노드**: QuickTableXRayAPI/prod REST API Stage를 나타냅니다.
> - **Lambda Context / Lambda Function**: AWS Lambda 함수가 Context(초기화/호출 관리)와 Function(실제 코드 실행) 두 개 노드로 분리되어 표시됩니다.
> - **DynamoDB Table 노드**: Reservations 테이블을 나타냅니다.

41. AWS Lambda 함수 노드를 클릭합니다.
42. 하단 패널에서 **Metrics** 탭의 요약 정보를 확인합니다:
    - **Latency (avg)**: 평균 응답 시간 (예: 266ms)
    - **Requests**: 분당 요청 수 (예: 1.20/min)
    - **Faults**: 분당 오류 수 (예: 0.00/min)

    <img src="/images/week13/13-2-task5-step42-traces.png" alt="Trace Map Metrics" class="guide-img-md" />

> [!NOTE]
> **Latency** 그래프에 "No data available"이 표시될 수 있습니다. 시간 범위를 조정하거나 데이터가 충분히 수집될 때까지 기다립니다.
> 노드 하단의 **View logs**, **View traces**, **Analyze traces**, **View dashboard** 버튼으로 상세 분석 페이지로 이동할 수 있습니다.

✅ **태스크 완료**: 서비스 맵을 확인했습니다.

## 태스크 6: 트레이스 분석

이 태스크에서는 AWS X-Ray 트레이스를 분석하여 예약 생성 및 조회 과정의 성능을 확인합니다.

43. 왼쪽 메뉴에서 **Application Signals (APM)** > **Traces**를 선택합니다.
44. 상단의 시간 범위를 `1h` 또는 `6h`로 변경합니다.
45. 검색창을 비운 상태에서 [[Run query]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-task5-step45-trace-list.png" alt="Traces 목록" class="guide-img-md" />

    <img src="/images/week13/13-2-task5-step45-trace-detail.png" alt="Traces 상세" class="guide-img-md" />

> [!NOTE]
> 기본 시간 범위가 `5m`으로 설정되어 있어 API 호출 시점이 5분 이전이면 트레이스가 표시되지 않습니다. `1h` 이상으로 변경하면 수집된 트레이스가 표시됩니다.

> [!TIP]
> 검색창에 쿼리를 입력하여 특정 트레이스만 필터링할 수 있습니다. 다음 쿼리를 입력하고 [[Run query]]를 클릭해봅니다:
>
> - 특정 레스토랑 예약만 조회: `annotation.restaurantName = "강남 맛집"`
> - 응답 시간이 1초 이상인 트레이스: `responsetime > 1`
> - 오류가 발생한 트레이스: `!OK`

46. 트레이스 목록에서 트레이스 ID를 클릭하여 상세 페이지로 이동합니다.

47. 트레이스 타임라인(**Segments Timeline**)에서 다음 정보를 확인합니다:
    - **QuickTableXRayAPI/prod** (AWS::ApiGateway::Stage): API 요청 수신 및 AWS Lambda 호출
    - **week13-2-xray-lab-CreateReservation** (AWS::Lambda): Lambda Context (초기화/호출 관리)
    - **week13-2-xray-lab-CreateReservation** (AWS::Lambda::Function): 실제 함수 코드 실행, `validate_input`, `create_dynamodb_item` 서브세그먼트
    - **DynamoDB** (AWS::DynamoDB::Table): PutItem 작업

    <img src="/images/week13/13-2-task5-step47-timeline1.png" alt="Segments Timeline 1" class="guide-img-md" />

    <img src="/images/week13/13-2-task5-step47-timeline2.png" alt="Segments Timeline 2" class="guide-img-md" />

> [!NOTE]
> 상단의 **Trace details** 탭에서는 해당 트레이스의 서비스 맵을 확인할 수 있습니다.  
> Client → ApiGateway Stage → Lambda Context → Lambda Function → DynamoDB Table 흐름이 시각적으로 표시됩니다.

48. Segments Timeline에서 `validate_input` 또는 `create_dynamodb_item` 서브세그먼트를 클릭합니다.

    <img src="/images/week13/13-2-task5-step48-subsegment1.png" alt="서브세그먼트 1" class="guide-img-md" />

    <img src="/images/week13/13-2-task5-step48-subsegment2.png" alt="서브세그먼트 2" class="guide-img-md" />

49. **Annotations** 탭에서 커스텀 어노테이션을 확인합니다.

> [!NOTE]
> 어노테이션에는 `operation`, `restaurantName`, `date`, `reservation_id`, `status` 등의 정보가 포함되어 있습니다.

50. **Metadata** 탭에서 예약 데이터를 확인합니다.

    <img src="/images/week13/13-2-task5-step50-metadata.png" alt="Metadata 탭" class="guide-img-md" />

> [!NOTE]
> 하단의 **Logs** 섹션에서 해당 트레이스와 연결된 Amazon CloudWatch 로그를 바로 확인할 수 있습니다.

51. 트레이스 목록으로 돌아가서 GET /reservations 요청도 동일하게 분석합니다.

    <img src="/images/week13/13-2-task5-step51-get-trace1.png" alt="GET 트레이스 분석 1" class="guide-img-md" />

    <img src="/images/week13/13-2-task5-step51-get-trace2.png" alt="GET 트레이스 분석 2" class="guide-img-md" />

✅ **태스크 완료**: 트레이스를 분석했습니다.

## 태스크 7: Application Insights 확인

이 태스크에서는 Amazon CloudWatch Application Insights를 사용하여 자동 이상 탐지 기능을 확인합니다.

52. Amazon CloudWatch 콘솔 왼쪽 메뉴에서 **Application Signals (APM)** > **Application Insights**를 선택합니다.

    <img src="/images/week13/13-2-task6-step52-filter.png" alt="Application Insights" class="guide-img-md" />

53. **Overview** 탭에서 **Problems detected** 섹션을 확인합니다.

> [!NOTE]
> "There are no problems"가 표시되면 정상입니다. Application Insights는 **충분한 트레이스 데이터(수백에서 수천 건)**가 있어야 이상 탐지가 작동합니다.
> 실습에서는 트레이스 수가 적어(수 건에서 수십 건) 이상이 표시되지 않을 가능성이 높습니다.
>
> **프로덕션 환경에서의 Insights 활용**:
>
> - 응답 시간이나 오류율이 평소와 다른 패턴을 보이는 경우 자동으로 이상을 탐지합니다.
> - **Detected problems summary**에서 최근 30일간 감지된 문제를 확인할 수 있습니다.
> - **Top recurrent problems**에서 반복적으로 발생하는 문제를 식별할 수 있습니다.

✅ **태스크 완료**: Application Insights의 자동 이상 탐지 기능을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 QuickTable 예약 시스템의 AWS X-Ray 추적 환경을 구축했습니다.
- AWS X-Ray SDK가 통합된 AWS Lambda 함수 코드를 확인했습니다.
- 예약 생성 및 조회 API를 호출하여 트레이스를 생성했습니다.
- 서비스 맵에서 Client → Amazon API Gateway → AWS Lambda → Amazon DynamoDB 흐름을 확인했습니다.
- 트레이스를 분석하여 예약 생성 및 조회 과정의 성능을 확인했습니다.
- AWS X-Ray Insights를 활용하여 자동 이상 탐지 기능을 확인했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택에 포함되지 않으므로 **수동으로 삭제**해야 합니다.
> 로그 그룹을 삭제하지 않으면 스토리지 비용(GB당 월 $0.50)이 계속 부과됩니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `13-2`
6. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Amazon CloudWatch Log Group 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. AWS CloudShell에서 Amazon CloudWatch Log Group을 삭제합니다:

```bash
aws logs delete-log-group --log-group-name /aws/lambda/week13-2-xray-lab-CreateReservation --region ap-northeast-2
aws logs delete-log-group --log-group-name /aws/lambda/week13-2-xray-lab-GetReservations --region ap-northeast-2
aws logs delete-log-group --log-group-name /aws/lambda/week13-2-xray-lab-LayerBuilder --region ap-northeast-2
```

<img src="/images/week13/13-2-cleanup-step7-cli-log.png" alt="CLI 로그 그룹 삭제" class="guide-img-md" />

> [!NOTE]
> 삭제가 성공하면 출력이 없습니다. 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/week13-2-xray-lab --query "logGroups[*].logGroupName" --output text --region ap-northeast-2
> ```
>
> 출력이 없으면 삭제 완료입니다.

> [!TIP]
> 특정 접두사로 시작하는 로그 그룹을 한번에 삭제하려면 다음 명령어를 사용합니다:
>
> ```bash
> aws logs describe-log-groups --log-group-name-prefix /aws/lambda/week13-2-xray-lab --query "logGroups[*].logGroupName" --output text --region ap-northeast-2 | tr '\t' '\n' | while read lg; do aws logs delete-log-group --log-group-name "$lg" --region ap-northeast-2; echo "삭제: $lg"; done
> ```
>
> 이전 차시에서 남아있는 로그 그룹까지 전체 삭제하려면 다음 명령어를 사용합니다:
>
> ```bash
> aws logs describe-log-groups --query "logGroups[*].logGroupName" --output text --region ap-northeast-2 | tr '\t' '\n' | while read lg; do aws logs delete-log-group --log-group-name "$lg" --region ap-northeast-2; echo "삭제: $lg"; done
> ```
>
> ⚠️ 위 명령어는 해당 리전의 **모든** 로그 그룹을 삭제합니다. 실습 전용 계정에서만 사용하세요.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

8. AWS Management Console 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
9. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
10. 검색창에 `week13-2-xray-lab`을 입력합니다.
11. 다음 로그 그룹의 체크박스를 선택합니다:
    - `/aws/lambda/week13-2-xray-lab-CreateReservation`
    - `/aws/lambda/week13-2-xray-lab-GetReservations`
    - `/aws/lambda/week13-2-xray-lab-LayerBuilder`
12. **Actions** > `Delete log group(s)`를 선택합니다.

    <img src="/images/week13/13-2-cleanup-step12-loggroup.png" alt="Delete log group 선택" class="guide-img-md" />

13. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-cleanup-step13-delete.png" alt="Delete 확인" class="guide-img-sm" />

> [!NOTE]
> AWS Lambda 함수가 실행되면 Amazon CloudWatch Log Group이 자동으로 생성됩니다.
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

### 단계 3: AWS CloudFormation 스택 삭제

14. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
15. `week13-2-xray-lab-stack` 스택을 선택합니다.
16. [[Delete stack]] 버튼을 클릭합니다.
17. 확인 창에서 스택 이름 `week13-2-xray-lab-stack`을 입력하고 [[Delete stack]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-cleanup-step17-delete-stack.png" alt="스택 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 Amazon DynamoDB 테이블, AWS Lambda 함수, AWS Lambda Layer, Amazon API Gateway, AWS IAM 역할이 모두 자동으로 삭제됩니다.
> AWS X-Ray 트레이스 데이터는 자동으로 삭제되지 않지만, 30일 후 자동으로 만료됩니다.

### 단계 4: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

18. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
19. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
20. **Regions**에서 `ap-northeast-2`를 선택합니다.
21. **Resource types**에서 `All supported resource types`를 선택합니다.
22. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `13-2`
23. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week13/13-2-cleanup-step23-tageditor-final.png" alt="Tag Editor 최종 확인" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

24. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
25. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
26. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
27. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
28. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/aws-xray.html)
- [AWS X-Ray SDK for Python](https://docs.aws.amazon.com/xray-sdk-for-python/latest/reference/)
- [AWS Lambda와 AWS X-Ray 통합](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/services-xray.html)
- [AWS X-Ray 서비스 맵](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-console-servicemap.html)
- [AWS X-Ray Insights](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-insights.html)
- [AWS X-Ray SDK에서 OpenTelemetry로 마이그레이션](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html)
- [AWS X-Ray SDK/Daemon 지원 타임라인](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-daemon-timeline.html)

## 📚 참고: QuickTable 예약 시스템의 AWS X-Ray 추적

### 분산 추적 아키텍처

QuickTable 레스토랑 예약 시스템에서 AWS X-Ray는 다음과 같은 분산 추적을 제공합니다:

**요청 흐름**:

- 클라이언트가 Amazon API Gateway에 예약 생성 요청을 전송합니다.
- Amazon API Gateway가 CreateReservation AWS Lambda 함수를 호출합니다.
- AWS Lambda 함수가 Amazon DynamoDB Reservations 테이블에 예약 데이터를 저장합니다.
- 응답이 역순으로 클라이언트에게 전달됩니다.

**추적 정보**:

- 전체 요청 시간: Amazon API Gateway 수신부터 클라이언트 응답까지
- AWS Lambda 실행 시간: 함수 초기화 + 비즈니스 로직 실행
- Amazon DynamoDB 작업 시간: PutItem/Query 작업 소요 시간

### AWS X-Ray 구성 요소

**세그먼트 (Segment)**:

- **ApiGateway Stage 세그먼트**: QuickTableXRayAPI/prod - API 요청 수신 및 AWS Lambda 호출
- **Lambda Context 세그먼트**: AWS Lambda 함수 초기화 및 호출 관리
- **Lambda Function 세그먼트**: CreateReservation 또는 GetReservations 함수 코드 실행
- **DynamoDB Table 세그먼트**: Reservations 테이블 읽기/쓰기 작업

**서브세그먼트 (Subsegment)**:

- **validate_input**: 입력 데이터 검증 (어노테이션: operation, restaurantName, date)
- **create_dynamodb_item**: Amazon DynamoDB PutItem 작업 (어노테이션: reservation_id, status)
- **get_reservations**: Amazon DynamoDB Query 작업 (어노테이션: operation, user_id)
- **DynamoDB**: `patch_all()`에 의해 자동 생성되는 Amazon DynamoDB 호출 서브세그먼트

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
Client → ApiGateway Stage → Lambda Context (CreateReservation) → Lambda Function (CreateReservation) → DynamoDB Table (Reservations)
                          → Lambda Context (GetReservations) → Lambda Function (GetReservations) → DynamoDB Table (Reservations)
```

**성능 지표**:

- **평균 응답 시간**: 전체 요청 처리 시간
- **요청 수**: 시간당 예약 생성/조회 요청 수
- **오류율**: 실패한 요청 비율
- **스로틀링**: Amazon DynamoDB 용량 초과로 제한된 요청

**병목 지점 식별**:

- AWS Lambda 콜드 스타트: 첫 요청 시 초기화 시간 증가
- Amazon DynamoDB 쓰기 지연: 대량 예약 생성 시 지연 발생

### Amazon CloudWatch의 AWS X-Ray 관련 뷰

Amazon CloudWatch 콘솔의 **Application Signals (APM)** 섹션에서 AWS X-Ray 트레이스 데이터를 다양한 관점으로 확인할 수 있습니다.

- **Trace Map**: 서비스 간 트레이스 흐름을 시각화합니다. 각 노드의 Latency, Requests, Faults 메트릭을 확인할 수 있습니다.
- **Traces**: 개별 트레이스를 검색하고 Segments Timeline에서 세그먼트/서브세그먼트별 실행 시간, Annotations, Metadata를 분석합니다.
- **Application Map**: 애플리케이션 단위로 서비스를 그룹화하여 전체 아키텍처를 보여줍니다. 관련 서비스 간 요청 수와 상태를 한눈에 파악할 수 있습니다.
- **Services**: SLI(Service Level Indicator) 상태, fault rate, 서비스별 의존성 경로를 운영 관점에서 모니터링합니다.
- **Application Insights**: 충분한 트레이스 데이터가 수집되면 응답 시간 이상, 오류율 증가 등을 자동으로 탐지합니다.

### AWS X-Ray SDK 사용 패턴

**자동 추적**:

```python
from aws_xray_sdk.core import patch_all
patch_all()  # boto3 Amazon DynamoDB 호출 자동 추적
```

**커스텀 서브세그먼트**:

```python
from aws_xray_sdk.core import xray_recorder

# 서브세그먼트 수동 생성
subsegment = xray_recorder.begin_subsegment('create_dynamodb_item')
subsegment.put_annotation('reservation_id', reservation_id)
subsegment.put_metadata('item', item)
xray_recorder.end_subsegment()
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
- Amazon DynamoDB Auto Scaling 설정으로 용량 자동 조정

**4. 사용자 경험 개선**:

- 평균 응답 시간 분석으로 느린 API 식별
- AWS Lambda 메모리 증가로 실행 시간 단축

### 모범 사례

**어노테이션 활용**:

- 검색 가능한 정보는 어노테이션으로 저장합니다.
- 레스토랑 이름, 날짜, 상태 등을 어노테이션으로 추가합니다.
- 필터링 및 그룹화에 활용합니다.

**서브세그먼트 세분화**:

- 병목 지점을 정확히 식별하기 위해 서브세그먼트를 세분화합니다.
- 입력 검증, 비즈니스 로직, Amazon DynamoDB 작업을 별도 서브세그먼트로 추적합니다.

**오류 처리**:

- 오류 발생 시 세그먼트에 오류 정보를 기록합니다.
- 오류 원인과 스택 트레이스를 메타데이터로 저장합니다.

**샘플링 규칙**:

- 프로덕션 환경에서는 샘플링 규칙을 사용하여 비용을 절감합니다.
- 중요한 요청은 100% 추적하고, 일반 요청은 샘플링합니다.
- 예: 예약 생성은 100%, 예약 조회는 10% 샘플링
- **기본 샘플링**: 초당 1개 요청 + 추가 요청의 5% (Reservoir + Fixed rate)
- **커스텀 규칙**: AWS X-Ray 콘솔에서 URL 패턴, HTTP 메서드, 서비스별로 샘플링 비율 설정 가능

### AWS X-Ray SDK 유지보수 모드 및 OpenTelemetry 마이그레이션

AWS X-Ray SDK/Daemon은 2026년 2월 25일부터 유지보수 모드에 진입했습니다. 유지보수 모드에서는 보안 패치만 제공되며, 새로운 기능은 추가되지 않습니다.

**타임라인**:

- **2026년 2월 25일**: 유지보수 모드 진입 (보안 패치만 제공) ← 현재
- **2027년 2월 25일**: 지원 종료 (End of Support)

**권장 사항**:

- 이 실습에서 사용한 `aws_xray_sdk`는 계속 동작하지만, 새로운 프로젝트에서는 OpenTelemetry 기반 계측을 권장합니다.
- OpenTelemetry는 벤더 중립적인 오픈소스 표준으로, AWS X-Ray뿐 아니라 다양한 백엔드(Jaeger, Zipkin 등)로 트레이스를 전송할 수 있습니다.
- AWS는 AWS Distro for OpenTelemetry(ADOT)를 통해 OpenTelemetry를 지원합니다.

**X-Ray SDK와 OpenTelemetry 비교**:

| 항목            | AWS X-Ray SDK            | OpenTelemetry (ADOT)               |
| --------------- | ------------------------ | ---------------------------------- |
| 상태            | 유지보수 모드 (2026.02~) | 활발히 개발 중                     |
| 표준            | AWS 전용                 | 벤더 중립 오픈소스 표준            |
| 백엔드          | AWS X-Ray만 지원         | X-Ray, Jaeger, Zipkin 등 다중 지원 |
| 자동 계측       | `patch_all()`            | OpenTelemetry Auto-Instrumentation |
| AWS Lambda 지원 | Active tracing           | ADOT Lambda Layer                  |

**OpenTelemetry 마이그레이션 예시** (참고용):

```python
# 기존 X-Ray SDK 방식
from aws_xray_sdk.core import patch_all, xray_recorder
patch_all()

# OpenTelemetry 방식 (권장)
from opentelemetry import trace
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
BotocoreInstrumentor().instrument()
tracer = trace.get_tracer(__name__)
```
