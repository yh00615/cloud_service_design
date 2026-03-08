---
title: 'AWS IAM 정책 Condition 요소 활용'
week: 2
session: 1
awsServices:
  - AWS IAM
learningObjectives:
  - AWS IAM 정책의 구조(Effect, Action, Resource, Condition)를 이해할 수 있습니다.
  - MFA 강제, IP 주소 제한, 시간 기반 Condition 정책을 생성할 수 있습니다.
  - 신뢰 정책과 권한 정책을 각각 생성하고 차이점을 비교할 수 있습니다.
  - Condition 정책의 동작을 테스트하고 검증할 수 있습니다.
prerequisites:
  - Week 1 완료
  - AWS IAM 정책 기본 문법 이해
  - JSON 형식 이해
---

이 실습에서는 **AWS IAM Policy의 Condition 요소**를 활용하여 **세밀한 권한 제어**를 구현하는 방법을 학습합니다.

먼저 **테스트용 Amazon S3 버킷**을 생성하고, **MFA(Multi-Factor Authentication) 기반 정책**을 구현하여 민감한 작업(삭제, 쓰기)에는 MFA 인증을 필수로 요구하도록 설정합니다. 그런 다음 **IP 주소 기반 정책**을 작성하여 특정 IP에서만 Amazon S3 접근을 허용합니다.

**시간 기반 정책**을 작성하여 특정 기간에만 리소스 접근을 허용하고, 마지막으로 **복합 조건**을 사용하여 여러 조건을 조합한 고급 정책을 작성하며, **최소 권한 원칙**과 **Zero Trust 보안 모델**을 실무에 적용하는 방법을 익힙니다.

> [!DOWNLOAD]
> [week2-1-iam-policy-condition.zip](/files/week2/week2-1-iam-policy-condition.zip)
>
> - `mfa-policy.json` - MFA Condition 정책 JSON 샘플 (태스크 2 참고용)
> - `ip-restriction-policy.json` - IP 제한 정책 JSON 샘플 (태스크 3 참고용)
> - `time-based-policy.json` - 시간 기반 정책 JSON 샘플 (태스크 4 참고용)
>
> **관련 태스크:**
>
> - 태스크 2: MFA 강제 정책 생성 (mfa-policy.json 참고)
> - 태스크 3: IP 주소 제한 정책 생성 (ip-restriction-policy.json 참고)
> - 태스크 4: 시간 기반 정책 생성 (time-based-policy.json 참고)

> [!WARNING]
> 이 실습에서 생성하는 정책은 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 1: 테스트용 Amazon S3 버킷 생성

이 태스크에서는 **Condition 정책**을 테스트하기 위한 **Amazon S3 버킷**을 생성합니다. **Amazon S3 버킷**은 다양한 **Condition 키**를 지원하므로 정책 테스트에 적합합니다. **버킷 이름**은 전 세계적으로 고유해야 하므로 본인의 이름이나 고유 식별자를 추가하여 생성합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `S3`을 입력하고 선택합니다.
2. 오른쪽 상단에서 현재 리전이 `Asia Pacific (Seoul) ap-northeast-2`인지 확인합니다.
3. [[Create bucket]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task1-step2-region-check.png" alt="AWS 콘솔 리전 확인" class="guide-img-md" />

4. **Bucket name**에 `iam-condition-lab-YOUR-INITIALS-12345`를 입력합니다.

> [!TIP]
> **중요**: `YOUR-INITIALS`를 본인의 이니셜(소문자)로, `12345`를 랜덤 숫자로 변경합니다 (예: `iam-condition-lab-jdoe-98765`). Amazon S3 버킷 이름은 소문자, 숫자, 하이픈(-)만 사용할 수 있습니다. **이 이름을 메모해둡니다.** 이후 실습에서 동일한 이름을 계속 사용합니다.

5. 아래로 스크롤하여 **Tags - optional** 섹션을 찾습니다.

> [!TIP]
> **태그 추가 방법**: 이 실습에서는 버킷 생성 시 태그를 추가합니다. 생성 후에도 버킷의 **Properties** 탭 → **Tags** 섹션에서 언제든지 태그를 추가하거나 수정할 수 있습니다.

6. [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

7. 나머지 설정은 기본값을 유지합니다.
8. 페이지 하단의 [[Create bucket]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task1-step8-bucket-region.png" alt="S3 버킷 생성 화면" class="guide-img-sm" />

> [!NOTE]
> 버킷 생성은 즉시 완료되며 별도의 대기 시간이 없습니다. 버킷 목록 페이지로 자동 이동합니다.

9. 생성한 버킷이 목록에 표시되는지 확인합니다.
10. 버킷 이름 옆에 **리전**이 `ap-northeast-2`로 표시되는지 확인합니다.
11. 생성한 버킷을 클릭합니다.

    <img src="/images/week2/2-1-task1-step9-bucket-click.png" alt="S3 버킷 목록에서 생성한 버킷 선택" class="guide-img-md" />

12. **Properties** 탭을 선택합니다.
13. **Tags** 섹션으로 스크롤하여 태그가 올바르게 생성되었는지 확인합니다:
    - `Project: AWS-Lab`
    - `Week: 2-1`
    - `CreatedBy: Student`

    <img src="/images/week2/2-1-task1-step14-tags-verify.png" alt="S3 버킷 Properties 탭의 Tags 섹션에서 태그 확인" class="guide-img-md" />

> [!TIP]
> **태그 관리**: 버킷 생성 후에도 이 **Tags** 섹션에서 [[Edit]] 버튼을 클릭하여 언제든지 태그를 추가, 수정, 삭제할 수 있습니다. 태그는 리소스 관리, 비용 추적, 접근 제어 등에 활용됩니다.

✅ **태스크 완료**: 테스트용 Amazon S3 버킷이 생성되었습니다.

## 태스크 2: MFA 강제 정책 생성

이 태스크에서는 **MFA(Multi-Factor Authentication)** 인증을 요구하는 정책을 생성합니다. **Condition 요소**의 **aws:MultiFactorAuthPresent** 키를 사용하면 민감한 작업(삭제, 쓰기)에 **MFA 인증**을 필수로 요구할 수 있습니다. 이 정책은 **버킷 목록 조회**는 허용하지만, **객체 업로드**나 **삭제**는 MFA 인증이 있어야만 가능하도록 제한합니다.

> [!CONCEPT] BoolIfExists 조건 연산자와 aws:MultiFactorAuthPresent
> **aws:MultiFactorAuthPresent** 키는 **임시 자격증명(temporary credentials)을 사용할 때만** 요청 컨텍스트에 포함됩니다. AWS IAM 사용자의 장기 자격증명(Access Key)으로 API를 호출하면 이 키 자체가 요청에 포함되지 않습니다.
>
> **장기 자격증명 vs 임시 자격증명**:
>
> - **장기 자격증명**: AWS IAM 사용자의 Access Key (만료되지 않음, MFA 정보 없음)
> - **임시 자격증명**: AWS STS(Security Token Service)로 발급받은 자격증명 (세션 토큰 포함, MFA 정보 포함 가능)
>
> **요청 컨텍스트 예시**:
>
> ```json
> // 장기 자격증명 (Access Key) 사용 시
> { "aws:userid": "AIDAI...", "aws:username": "lab-user" }
> // aws:MultiFactorAuthPresent 키가 아예 존재하지 않음
>
> // 임시 자격증명 (STS 토큰) 사용 시
> { "aws:userid": "AIDAI...", "aws:MultiFactorAuthPresent": "false" }
> ```
>
> **Bool vs BoolIfExists 차이**:
>
> - **Bool**: 키가 있을 때만 값을 비교하고, 키가 없으면 조건을 건너뜀 (무시)
> - **BoolIfExists**: 키가 있으면 값을 비교하고, 키가 없으면 조건을 true로 평가 (키가 없는 경우를 false로 간주)
>
> **Bool 사용 시 문제점**:
>
> ```json
> {
>   "Effect": "Deny",
>   "Condition": { "Bool": { "aws:MultiFactorAuthPresent": "false" } }
> }
> ```
>
> **동작**:
>
> - 장기 자격증명: 키가 없음 → 조건 평가 건너뜀 → Deny 미적용 (보안 취약!)
> - 임시 자격증명 + MFA 없음: 키 값 false → Deny 적용
>
> **BoolIfExists 사용 시 (권장)**:
>
> ```json
> {
>   "Effect": "Deny",
>   "Condition": { "BoolIfExists": { "aws:MultiFactorAuthPresent": "false" } }
> }
> ```
>
> **동작**:
>
> - 장기 자격증명: 키가 없음 → false로 간주 → Deny 적용 (보안 강화!)
> - 임시 자격증명 + MFA 없음: 키 값 false → Deny 적용
>
> **이 정책의 동작**:
>
> - **AllowS3WriteWithMFA** Statement: MFA가 있을 때(키 값이 true) 쓰기 작업을 허용합니다.
> - **DenyS3ActionsWithoutMFA** Statement: MFA가 없을 때(키 값이 false) 또는 키가 아예 없을 때(장기 자격증명 사용) 쓰기 작업을 차단합니다.
> - BoolIfExists를 사용하면 장기 자격증명(Access Key)으로 API를 호출할 때도 Deny가 적용되어 보안이 강화됩니다.

14. AWS IAM 콘솔로 이동합니다.
15. 왼쪽 메뉴에서 **Policies**를 선택합니다.
16. [[Create policy]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task2-step3-create-policy.png" alt="IAM Policies 페이지에서 Create policy 버튼" class="guide-img-md" />

17. **JSON** 탭을 선택합니다.
18. 기존 정책 코드를 모두 삭제한 후 다음 정책을 입력합니다:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowListBucketWithoutMFA",
         "Effect": "Allow",
         "Action": [
           "s3:ListAllMyBuckets",
           "s3:ListBucket",
           "s3:GetBucketLocation"
         ],
         "Resource": "*"
       },
       {
         "Sid": "AllowS3WriteWithMFA",
         "Effect": "Allow",
         "Action": ["s3:PutObject", "s3:DeleteObject", "s3:DeleteBucket"],
         "Resource": "*",
         "Condition": {
           "BoolIfExists": {
             "aws:MultiFactorAuthPresent": "true"
           }
         }
       },
       {
         "Sid": "DenyS3ActionsWithoutMFA",
         "Effect": "Deny",
         "Action": ["s3:PutObject", "s3:DeleteObject", "s3:DeleteBucket"],
         "Resource": "*",
         "Condition": {
           "BoolIfExists": {
             "aws:MultiFactorAuthPresent": "false"
           }
         }
       }
     ]
   }
   ```
   > [!NOTE]
   > 이 정책은 버킷 목록 조회는 허용하고, 객체 업로드/삭제는 MFA 인증이 있을 때만 허용합니다. MFA 없이 쓰기 작업을 시도하면 Deny가 적용됩니다.
   >
   > **Allow와 Deny 구조 설명**:
   >
   > - **AllowListBucketWithoutMFA** Statement는 MFA 없이도 버킷 목록 조회를 허용합니다.
   > - **AllowS3WriteWithMFA** Statement는 MFA가 있을 때 Amazon S3 쓰기 작업을 허용합니다. 이 Statement가 없으면 condition-test-user는 다른 Amazon S3 권한이 없으므로 MFA가 있어도 쓰기 작업을 수행할 수 없습니다.
   > - **DenyS3ActionsWithoutMFA** Statement는 다른 정책에서 부여한 Amazon S3 권한도 MFA 없이는 차단합니다.
   > - **Deny는 항상 Allow보다 우선**하므로, 다른 정책이 s3:\*를 허용하더라도 MFA 없이는 쓰기 작업이 차단됩니다.
   > - 이 세 Statement를 함께 사용하면 "MFA가 있을 때만 Amazon S3 쓰기 작업이 가능하다"는 강력한 제한을 구현할 수 있습니다.
   >
   > **이 실습의 테스트 제한사항**: 태스크 8에서는 AWS IAM 사용자의 Access Key(장기 자격증명)를 사용하므로 `aws:MultiFactorAuthPresent` 키가 요청에 포함되지 않습니다. BoolIfExists는 키가 없을 때 조건을 true로 평가하지만, Deny Statement의 조건이 "false"를 요구하므로 결과적으로 Deny가 적용됩니다. 따라서 이 실습에서는 "MFA 없이 쓰기 차단"만 테스트하고, "MFA 있을 때 쓰기 허용"은 테스트하지 않습니다. MFA 있을 때의 동작을 테스트하려면 AWS STS GetSessionToken으로 임시 자격증명을 발급받거나, AWS 콘솔에 MFA 인증으로 로그인한 후 Amazon S3 콘솔에서 직접 파일을 업로드해야 합니다.
19. [[Next]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task2-step6-next-button.png" alt="IAM 정책 JSON 입력 후 Next 버튼" class="guide-img-md" />

20. **Policy name**에 `S3MFARequiredPolicy`를 입력합니다.
21. **Description**에 `Requires MFA for Amazon S3 write operations`를 입력합니다.
22. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

23. [[Create policy]] 버튼을 클릭합니다.

    <img src="/images/week2/2-1-task2-step10-create-policy.png" alt="IAM 정책 생성 완료 버튼" class="guide-img-md" />

24. 정책 생성이 완료되면 **Policies** 페이지로 자동 이동합니다.
25. 화면 상단에 녹색 배너로 "Policy S3MFARequiredPolicy created."라는 성공 메시지가 표시됩니다.

    <img src="/images/week2/2-1-task2-step12-success-banner.png" alt="IAM 정책 생성 성공 배너" class="guide-img-sm" />

> [!TIP]
> 녹색 배너 오른쪽의 [[View policy]] 버튼을 클릭하면 생성된 정책의 상세 페이지를 바로 확인할 수 있습니다.

26. 정책 목록에서 `S3MFARequiredPolicy`를 검색하여 생성된 정책을 확인합니다.

> [!NOTE]
> 정책 목록에서 **Policy name** 열에 `S3MFARequiredPolicy`가 표시되고, **Type** 열에 "Customer managed"로 표시됩니다. 이는 사용자가 직접 생성한 정책임을 의미합니다.

27. 생성한 정책을 클릭합니다.

    <img src="/images/week2/2-1-task2-step13-policy-list.png" alt="IAM 정책 목록에서 생성된 정책 확인" class="guide-img-sm" />

28. **Permissions** 탭에서 JSON 형식의 정책 내용을 확인합니다.

    <img src="/images/week2/2-1-task2-step15-permissions-tab.png" alt="IAM 정책 Permissions 탭의 JSON 내용" class="guide-img-sm" />

> [!TIP]
> 생성한 정책의 **Permissions** 탭에서 JSON 형식으로 입력한 정책 내용을 언제든지 확인할 수 있습니다.

✅ **태스크 완료**: MFA 강제 정책이 생성되었습니다.

## 태스크 3: IP 주소 제한 정책 생성

이 태스크에서는 **IP 주소 기반 접근 제어** 정책을 생성합니다. **aws:SourceIp** Condition 키를 사용하면 **특정 네트워크**에서만 AWS 리소스에 접근할 수 있도록 제한합니다. **CIDR 표기법**을 사용하여 **IP 범위**를 지정하며, 여러 IP 범위를 배열로 지정할 수 있습니다. 이를 통해 회사 네트워크나 **VPN IP 범위**만 허용하고 다른 IP는 차단할 수 있습니다.

> [!WARNING]
> **학교/회사 네트워크 IP 제한 주의사항**: 학교나 회사 네트워크에서 실습하는 경우, 네트워크 관리자가 설정한 방화벽이나 프록시로 인해 IP 기반 정책이 예상과 다르게 동작할 수 있습니다. 특히 NAT(Network Address Translation)를 사용하는 환경에서는 여러 사용자가 동일한 공인 IP를 공유하므로, 본인의 IP만 허용하려고 해도 같은 네트워크의 다른 사용자도 접근할 수 있습니다. 또한 학교/회사에서 특정 AWS 서비스나 포트를 차단하는 경우 정책과 무관하게 접근이 불가능할 수 있습니다. 이러한 환경에서는 개인 네트워크(집, 카페 등)에서 테스트하는 것을 권장합니다.

29. 새 브라우저 탭을 엽니다.
30. 주소창에 `https://checkip.amazonaws.com`을 입력하고 Enter를 누릅니다.
31. 표시된 IP 주소를 메모장에 복사합니다.

> [!IMPORTANT]
> 이 IP 주소는 다음 단계에서 정책에 입력해야 합니다. 반드시 메모장에 저장합니다.

32. AWS IAM 콘솔 탭으로 이동합니다.
33. [[Create policy]] 버튼을 다시 클릭합니다.
34. **JSON** 탭을 선택합니다.
35. 기존 정책 코드를 모두 삭제한 후 다음 정책을 입력합니다 (`YOUR_IP_ADDRESS`를 메모장의 IP로 변경):

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowFromSpecificIP",
         "Effect": "Allow",
         "Action": "s3:*",
         "Resource": "*",
         "Condition": {
           "IpAddress": {
             "aws:SourceIp": ["YOUR_IP_ADDRESS/32"]
           }
         }
       },
       {
         "Sid": "DenyFromOtherIPs",
         "Effect": "Deny",
         "Action": "s3:*",
         "Resource": "*",
         "Condition": {
           "NotIpAddress": {
             "aws:SourceIp": ["YOUR_IP_ADDRESS/32"]
           }
         }
       }
     ]
   }
   ```

> [!IMPORTANT]
> **필수 확인**: `YOUR_IP_ADDRESS`를 실제 IP 주소로 변경했는지 반드시 확인합니다. 플레이스홀더를 그대로 사용하면 모든 Amazon S3 접근이 차단됩니다.
>
> **예시**: 본인의 IP가 `1.2.3.4`라면 `"YOUR_IP_ADDRESS/32"`를 `"1.2.3.4/32"`로 변경합니다.
>
> **CIDR 표기법 설명**: `/32`는 단일 IP 주소를 의미합니다. 여러 IP를 허용하려면 배열로 추가할 수 있습니다: `["1.2.3.4/32", "5.6.7.8/32"]`

> [!NOTE]
> **Allow와 Deny 구조 설명**:
>
> - **AllowFromSpecificIP** Statement는 지정된 IP에서의 Amazon S3 접근을 허용합니다.
> - **DenyFromOtherIPs** Statement는 다른 정책에서 부여한 Amazon S3 권한도 지정된 IP 외에서는 차단합니다.
> - **Deny는 항상 Allow보다 우선**하므로, 다른 정책이 s3:\*를 허용하더라도 IP 외부에서는 차단됩니다.
> - 이 두 Statement를 함께 사용하면 "이 IP에서만 Amazon S3를 사용할 수 있다"는 강력한 제한을 구현할 수 있습니다.

36. [[Next]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task3-step8-next-button.png" alt="IAM 정책 JSON 입력 후 Next 버튼" class="guide-img-md" />

37. **Policy name**에 `S3IPRestrictionPolicy`를 입력합니다.
38. **Description**에 `Restricts Amazon S3 access to specific IP addresses`를 입력합니다.
39. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

40. [[Create policy]] 버튼을 클릭합니다.

    <img src="/images/week2/2-1-task3-step12-create-policy.png" alt="IAM 정책 생성 완료 버튼" class="guide-img-md" />

41. 정책 생성이 완료되면 **Policies** 페이지로 자동 이동합니다.
42. 화면 상단에 녹색 배너로 "Policy S3IPRestrictionPolicy created."라는 성공 메시지가 표시됩니다.

> [!TIP]
> 녹색 배너 오른쪽의 [[View policy]] 버튼을 클릭하면 생성된 정책의 상세 페이지를 바로 확인할 수 있습니다.  
> 또는 정책 목록에서 `S3IPRestrictionPolicy`를 검색하여 확인할 수 있습니다.

> [!NOTE]
> 정책 목록에서 **Policy name** 열에 `S3IPRestrictionPolicy`가 표시되고, **Type** 열에 "Customer managed"로 표시됩니다.

✅ **태스크 완료**: IP 주소 제한 정책이 생성되었습니다.

## 태스크 4: 시간 기반 정책 생성

이 태스크에서는 **시간 기반 정책**을 생성합니다. **aws:CurrentTime** Condition 키를 사용하여 **특정 기간**에만 리소스 접근을 허용하며, **UTC 시간대**를 기준으로 합니다. 이를 통해 **특정 날짜 범위**에만 민감한 작업을 허용하고, 기간 외에는 차단하여 **보안**을 강화할 수 있습니다.

> [!CONCEPT] aws:CurrentTime 조건 키와 시간대 처리
> **aws:CurrentTime**은 날짜와 시간을 모두 포함한 전체 타임스탬프를 비교합니다. 이 정책은 **특정 기간**(예: 2026년 1월 1일부터 12월 31일까지)에만 접근을 허용하는 데 적합합니다.
>
> **시간대 처리**:
>
> - AWS IAM 정책의 시간 조건은 항상 **UTC(협정 세계시)** 기준입니다.
> - 한국 시간(KST)은 UTC+9이므로, 한국 시간 09:00는 UTC 00:00입니다.
> - 예: 한국 시간 2026-01-01 09:00 → UTC 2026-01-01 00:00
> - 정책 작성 시 반드시 UTC로 변환하여 입력해야 합니다.
>
> **매일 반복되는 업무 시간 제한의 한계**:
>
> - **aws:CurrentTime**은 특정 날짜 범위 제한에 적합합니다.
> - 매일 반복되는 시간대 제한(예: 매일 09:00-18:00)에는 적합하지 않습니다.
> - 이유: 날짜와 시간을 함께 비교하므로, "매일 09:00-18:00"을 표현할 수 없습니다.
> - 대안: AWS Lambda 함수 + Amazon EventBridge 스케줄러, AWS Config 규칙, 또는 서드파티 솔루션 사용
>
> **실무 활용 시나리오**:
>
> - ✅ 프로젝트 기간 제한 (2026-01-01 ~ 2026-12-31)
> - ✅ 임시 계약직 직원 접근 기간 제한
> - ✅ 특정 이벤트 기간 동안만 리소스 접근 허용
> - ✅ 감사(Audit) 기간 동안 특정 작업 차단
> - ❌ 매일 업무 시간(09:00-18:00)만 접근 허용 (불가능)

43. [[Create policy]] 버튼을 다시 클릭합니다.
44. **JSON** 탭을 선택합니다.
45. 기존 정책 코드를 모두 삭제한 후 다음 정책을 입력합니다 (`YYYY`를 현재 연도로 변경):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowDuringSpecificPeriod",
         "Effect": "Allow",
         "Action": "s3:*",
         "Resource": "*",
         "Condition": {
           "DateGreaterThan": {
             "aws:CurrentTime": "YYYY-01-01T00:00:00Z"
           },
           "DateLessThan": {
             "aws:CurrentTime": "YYYY-12-31T23:59:59Z"
           }
         }
       },
       {
         "Sid": "DenyOutsideSpecificPeriod",
         "Effect": "Deny",
         "Action": "s3:*",
         "Resource": "*",
         "Condition": {
           "DateLessThan": {
             "aws:CurrentTime": "YYYY-01-01T00:00:00Z"
           }
         }
       },
       {
         "Sid": "DenyAfterSpecificPeriod",
         "Effect": "Deny",
         "Action": "s3:*",
         "Resource": "*",
         "Condition": {
           "DateGreaterThan": {
             "aws:CurrentTime": "YYYY-12-31T23:59:59Z"
           }
         }
       }
     ]
   }
   ```

> [!IMPORTANT]
> **필수 확인**: `YYYY`를 현재 연도로 변경했는지 반드시 확인합니다. 플레이스홀더를 그대로 사용하면 정책이 작동하지 않습니다.
>
> **예시**: 2026년에 실습하는 경우 `YYYY-01-01T00:00:00Z`를 `2026-01-01T00:00:00Z`로, `YYYY-12-31T23:59:59Z`를 `2026-12-31T23:59:59Z`로 변경합니다.

> [!NOTE]
> 이 정책은 지정된 연도(1월 1일부터 12월 31일까지)에만 Amazon S3 접근을 허용합니다. 기간 외에는 명시적 Deny로 모든 Amazon S3 작업이 차단됩니다.
>
> **Allow와 Deny 구조 설명**:
>
> - **AllowDuringSpecificPeriod** Statement는 지정된 기간 내에 Amazon S3 접근을 허용합니다.
> - **DenyOutsideSpecificPeriod**와 **DenyAfterSpecificPeriod** Statement는 다른 정책에서 부여한 Amazon S3 권한도 기간 외에는 차단합니다.
> - **Deny는 항상 Allow보다 우선**하므로, 다른 정책이 s3:\*를 허용하더라도 기간 외에는 차단됩니다.
> - 이 세 Statement를 함께 사용하면 "이 기간에만 Amazon S3를 사용할 수 있다"는 강력한 제한을 구현할 수 있습니다.

46. [[Next]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task4-step4-next-button.png" alt="IAM 정책 JSON 입력 후 Next 버튼" class="guide-img-md" />

47. **Policy name**에 `S3TimeBasedPolicy`를 입력합니다.
48. **Description**에 `Restricts Amazon S3 access to specific date range`를 입력합니다.
49. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다.:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

50. [[Create policy]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task4-step8-create-policy.png" alt="IAM 정책 생성 완료 버튼" class="guide-img-md" />

51. 정책 생성이 완료되면 **Policies** 페이지로 자동 이동합니다.
52. 화면 상단에 녹색 배너로 "Policy S3TimeBasedPolicy created."라는 성공 메시지가 표시됩니다.

> [!TIP]
> 녹색 배너 오른쪽의 [[View policy]] 버튼을 클릭하면 생성된 정책의 상세 페이지를 바로 확인할 수 있습니다.  
> 또는 정책 목록에서 `S3TimeBasedPolicy`를 검색하여 확인할 수 있습니다.

> [!NOTE]
> 정책 목록에서 **Policy name** 열에 `S3TimeBasedPolicy`가 표시되고, **Type** 열에 "Customer managed"로 표시됩니다.

✅ **태스크 완료**: 시간 기반 정책이 생성되었습니다.

## 태스크 5: 복합 조건 정책 생성

이 태스크에서는 **복합 조건 정책**을 생성합니다. 여러 **Condition 키**를 동시에 사용하여 매우 세밀한 **권한 제어**를 구현합니다. 모든 조건을 만족해야만 접근이 허용되므로(**AND 조건**), **암호화 필수**, **IP 제한**, **MFA 인증** 등을 조합하여 **Zero Trust 보안 모델**을 구현할 수 있습니다.

> [!CONCEPT] 복합 조건의 AND 연산
> 하나의 Condition 블록 내에 여러 조건 키를 나열하면, **모든 조건을 만족해야** 접근이 허용됩니다. (AND 연산)
>
> 예를 들어, 암호화 필수 + IP 제한 + MFA 인증을 모두 만족해야만 Amazon S3 접근이 가능합니다.

53. [[Create policy]] 버튼을 다시 클릭합니다.
54. **JSON** 탭을 선택합니다.
55. 기존 정책 코드를 모두 삭제한 후 다음 정책을 입력합니다.(`YOUR_IP_ADDRESS`를 실제 IP로 변경):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "AllowS3WithMultipleConditions",
         "Effect": "Allow",
         "Action": "s3:PutObject",
         "Resource": "arn:aws:s3:::iam-condition-lab-*/*",
         "Condition": {
           "StringEquals": {
             "s3:x-amz-server-side-encryption": "AES256"
           },
           "IpAddress": {
             "aws:SourceIp": "YOUR_IP_ADDRESS/32"
           },
           "BoolIfExists": {
             "aws:MultiFactorAuthPresent": "true"
           }
         }
       }
     ]
   }
   ```

> [!IMPORTANT]
> **필수 확인**: `YOUR_IP_ADDRESS`를 실제 IP 주소로 변경했는지 반드시 확인합니다. 현재 IP는 `https://checkip.amazonaws.com`에서 확인할 수 있습니다.

> [!NOTE]
> 이 정책은 여러 조건을 동시에 만족해야 Amazon S3 객체 업로드가 가능합니다.: 암호화 필수(AES256), 특정 IP 범위, MFA 인증. 모든 조건이 AND 연산으로 결합되어 있습니다.

56. [[Next]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task5-step4-next-button.png" alt="IAM 정책 JSON 입력 후 Next 버튼" class="guide-img-md" />

57. **Policy name**에 `S3ComplexConditionPolicy`를 입력합니다.
58. **Description**에 `Amazon S3 access with multiple conditions`를 입력합니다.
59. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

60. [[Create policy]] 버튼을 클릭합니다.

   <img src="/images/week2/2-1-task5-step8-create-policy.png" alt="IAM 정책 생성 최종 확인 화면에서 Create policy 버튼" class="guide-img-md" />

61. 정책 생성이 완료되면 **Policies** 페이지로 자동 이동합니다.
62. 화면 상단에 녹색 배너로 "Policy S3ComplexConditionPolicy created."라는 성공 메시지가 표시됩니다.

> [!TIP]
> 녹색 배너 오른쪽의 [[View policy]] 버튼을 클릭하면 생성된 정책의 상세 페이지를 바로 확인할 수 있습니다.  
> 또는 정책 목록에서 `S3ComplexConditionPolicy`를 검색하여 확인할 수 있습니다.

> [!NOTE]
> 정책 목록에서 **Policy name** 열에 `S3ComplexConditionPolicy`가 표시되고, **Type** 열에 "Customer managed"로 표시됩니다. 이제 4개의 Condition 정책이 모두 생성되었습니다.

✅ **태스크 완료**: 복합 조건 정책이 생성되었습니다.

## 태스크 6: 테스트용 AWS IAM 사용자 생성 및 정책 연결

이 태스크에서는 생성한 **Condition 정책**들을 실제로 테스트하기 위해 **테스트용 AWS IAM 사용자**를 생성합니다. 이 사용자에게 **MFA 강제 정책**을 연결하여 정책이 올바르게 작동하는지 확인할 수 있습니다. 실제 환경에서는 기존 사용자에게 정책을 연결하지만, 실습에서는 안전하게 테스트하기 위해 별도의 사용자를 생성합니다.

63. AWS IAM 콘솔로 이동합니다.
64. 왼쪽 메뉴에서 **Users**를 선택합니다.
65. [[Create user]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task6-step3-create-user.png" alt="IAM Create user 버튼" class="guide-img-md" />

66. **User name**에 `condition-test-user`를 입력합니다.
67. **Provide user access to the AWS Management Console** 체크박스는 체크하지 않습니다.

> [!NOTE]
> 이 실습에서는 AWS CLI만 사용하므로 콘솔 로그인 권한이 필요하지 않습니다. Access Key만 생성하여 CLI에서 사용합니다.
>
> **CloudShell 사용 방식 설명**: 태스크 7에서 AWS CloudShell을 사용하지만, CloudShell은 현재 로그인한 관리자 계정의 자격증명을 사용합니다. condition-test-user의 자격증명은 `--profile condition-test` 옵션으로 별도로 지정하여 테스트하므로, condition-test-user에게 콘솔 접근 권한이 필요하지 않습니다.

68. [[Next]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task6-step6-next-button.png" alt="IAM 사용자 생성 화면에서 Next 버튼" class="guide-img-md" />

69. **Set permissions** 페이지가 표시됩니다.
70. **Permissions options** 섹션에서 `Attach policies directly` 라디오 버튼을 선택합니다.

> [!NOTE]
> **Permissions options** 섹션에는 세 가지 옵션이 있습니다:
>
> - **Add user to group**: 사용자를 그룹에 추가하여 그룹의 정책을 상속받습니다 (권장 방식)
> - **Copy permissions**: 기존 사용자의 권한을 복사합니다
> - **Attach policies directly**: 사용자에게 직접 정책을 연결합니다 (이 실습에서 사용)

71. **Permissions policies** 섹션으로 스크롤합니다.
72. 검색창에 `S3MFARequiredPolicy`를 입력합니다.
73. 검색 결과에서 `S3MFARequiredPolicy` 정책 왼쪽의 체크박스를 선택합니다.

> [!NOTE]
> 정책이 선택되면 체크박스에 파란색 체크 표시가 나타나고, 정책 행 전체가 파란색으로 강조됩니다. 화면 상단의 "Filter by Type" 옆에 "1 match"라고 표시되며, 정책 테이블에서 선택된 정책을 확인할 수 있습니다.

74. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task6-step10-next-button.png" alt="IAM 정책 연결 후 Next 버튼" class="guide-img-md" />

75. **Review and create** 페이지가 표시됩니다.
76. **User details** 섹션에서 **User name**이 `condition-test-user`인지 확인합니다.
77. **Permissions summary** 섹션에서 `S3MFARequiredPolicy`가 연결되어 있는지 확인합니다.
78. **Tags - optional** 섹션으로 스크롤합니다.
79. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `2-1`     |
| `CreatedBy` | `Student` |

> [!TIP]
> **Tags** 섹션에서 사용자 생성 시 태그를 미리 추가하면, 생성 후 별도로 태그를 추가할 필요가 없어 효율적입니다. 각 태그를 추가한 후 [[Add new tag]] 버튼을 클릭하여 다음 태그를 입력합니다.

80. [[Create user]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task6-step18-create-user.png" alt="IAM 사용자 생성 최종 확인 후 Create user 버튼" class="guide-img-md" />

81. 사용자 생성이 완료되면 **Users** 페이지로 자동 이동합니다.
82. 화면 상단에 녹색 배너로 "User created successfully"라는 성공 메시지가 표시됩니다.

> [!NOTE]
> 녹색 배너에는 "You can view and download the user's password and email instructions for signing in to the AWS Management Console"이라는 메시지와 [[View user]] 버튼이 표시됩니다. 이 실습에서는 콘솔 접근 권한을 부여하지 않았으므로 이 버튼은 사용하지 않습니다.

83. 사용자 목록에서 `condition-test-user`가 표시되는지 확인합니다.
    <img src="/images/week2/2-1-task6-step21-user-list.png" alt="IAM Users 목록에서 condition-test-user 확인" class="guide-img-md" />

> [!TIP]
> 사용자 목록에서 다음 정보를 확인할 수 있습니다:
>
> - **User name**: `condition-test-user`
> - **Path**: `/`
> - **Groups**: `0` (그룹에 속하지 않음)
> - **Last activity**: `-` (아직 활동 없음)
> - **MFA**: `-` (MFA 설정 안 됨)
> - **Password age**: `-` (콘솔 비밀번호 없음)
> - **Console last sign-in**: `-` (콘솔 로그인 안 함)
>
> 사용자를 클릭하면 **Permissions** 탭에서 `S3MFARequiredPolicy`가 연결되어 있고, **Tags** 탭에서 추가한 태그를 확인할 수 있습니다.

✅ **태스크 완료**: 테스트용 사용자가 생성되었습니다.

## 태스크 7: MFA 정책 동작 테스트

이 태스크에서는 생성한 **MFA 강제 정책**이 올바르게 작동하는지 테스트합니다. **condition-test-user**의 **Access Key**를 생성하고 **AWS CLI 프로파일**로 구성하여, **MFA 인증 없이는 객체 업로드나 삭제가 차단**되는 것을 확인합니다.

### 7-1: Access Key 생성

84. AWS IAM 콘솔로 이동합니다.
85. 왼쪽 메뉴에서 **Users**를 선택합니다.
86. 사용자 목록에서 `condition-test-user`를 검색합니다.
87. `condition-test-user`를 클릭합니다.
   <img src="/images/week2/2-1-task7-step4-user-details.png" alt="IAM 사용자 목록에서 condition-test-user 선택" class="guide-img-md" />

88. **Security credentials** 탭을 선택합니다.
89. **Access keys** 섹션으로 스크롤합니다.
90. [[Create access key]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task7-step7-create-access-key.png" alt="IAM Security credentials 탭에서 Create access key 버튼" class="guide-img-md" />

91. **Use case**에서 `Command Line Interface (CLI)`를 선택합니다.

> [!NOTE]
> AWS 콘솔에서 "We recommend that you don't create access keys for your root user or AWS IAM users. Instead, use AWS IAM Identity Center" 같은 권장 메시지가 표시될 수 있습니다. 이는 AWS가 장기 자격증명(Access Key) 대신 AWS IAM Identity Center 사용을 권장하기 때문입니다. 이 실습에서는 Condition 정책 학습 목적으로 Access Key를 사용하며, 실습 종료 후 반드시 삭제합니다.

92. 하단의 체크박스 `I understand the above recommendation and want to proceed to create an access key`를 체크합니다.
93. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task7-step10-next-button.png" alt="Access key 사용 사례 선택 후 Next 버튼" class="guide-img-md" />

94. **Description tag value**에 `MFA policy test`를 입력합니다.
95. [[Create access key]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task7-step12-create-access-key.png" alt="Description tag 입력 후 Create access key 버튼" class="guide-img-md" />

96. **Access key** 페이지가 표시됩니다.
97. **Access key**와 **Secret access key** 값을 메모장에 복사합니다.

> [!IMPORTANT]
> Secret access key는 이 화면에서만 확인할 수 있습니다. 반드시 메모장에 저장합니다.

> [!WARNING]
> **보안 주의사항**:
>
> - **메모장 저장**: Access Key와 Secret Access Key를 평문 메모장에 저장하는 것은 보안 위험이 있습니다. 실습 목적으로 불가피하게 메모장을 사용하지만, 실습 종료 후 메모장의 키 정보를 반드시 삭제합니다.
> - **CSV 다운로드**: [[Download .csv file]] 버튼으로 CSV 파일을 다운로드할 수 있지만, 파일이 로컬 컴퓨터에 저장되어 보안 위험이 더 큽니다. 이 실습에서는 CSV 다운로드 대신 복사 기능을 사용하는 것을 권장합니다.
> - **실무 권장사항**: 실무에서는 장기 자격증명 (Access Key) 대신 IAM Role과 임시 자격증명을 사용하는 것이 권장됩니다. AWS IAM Identity Center를 통해 임시 자격증명을 발급받거나, Amazon EC2/AWS Lambda 등에서는 IAM Role을 연결하여 자격증명 관리 없이 AWS 서비스에 접근할 수 있습니다.

98. [[Done]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task7-step15-done-button.png" alt="Access key 생성 완료 후 Done 버튼" class="guide-img-md" />

### 7-2: AWS CLI 프로파일 구성

99. AWS Management Console 왼쪽 하단의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell은 AWS CLI가 사전 설치되어 있고 현재 로그인한 AWS IAM 사용자 자격증명이 자동으로 구성된 브라우저 기반 셸 환경입니다. 첫 실행 시 환경 초기화에 1-2분이 소요될 수 있습니다.

> [!WARNING]
> **AWS CloudShell 세션 지속성**: AWS CloudShell 세션은 브라우저 탭을 닫거나 일정 시간(약 20분) 동안 활동이 없으면 자동으로 종료됩니다. 세션이 종료되면 환경 변수(AWS_ACCESS_KEY_ID 등)도 함께 사라집니다. 하지만 홈 디렉토리(/home/cloudshell-user)의 파일과 AWS CLI 프로파일 설정(~/.aws/config, ~/.aws/credentials)은 유지됩니다. 따라서 이 태스크에서 설정한 condition-test 프로파일은 세션이 종료되어도 보존되며, 다음에 CloudShell을 열면 다시 사용할 수 있습니다.

100. 다음 명령어를 실행하여 condition-test 프로파일을 구성합니다:

```bash
aws configure --profile condition-test
```

101. 프롬프트가 나타나면 다음 값을 입력합니다:
    - **AWS Access Key ID**: 메모장에 저장한 Access Key 입력
    - **AWS Secret Access Key**: 메모장에 저장한 Secret Access Key 입력
    - **Default region name**: `ap-northeast-2` 입력
   - **Default output format**: `json` 입력

   <img src="/images/week2/2-1-task7-step3-configure-profile.png" alt="AWS CLI 프로파일 구성 프롬프트" class="guide-img-md" />

> [!TIP]
> 프로파일 이름은 IAM 사용자 이름과 달라도 됩니다. 이 실습에서는 간결하게 `condition-test`를 사용합니다.

> [!NOTE]
> 각 항목을 입력한 후 Enter 키를 누릅니다.

### 7-3: MFA 없이 권한 테스트

102. 현재 자격증명을 확인합니다:

```bash
aws sts get-caller-identity --profile condition-test
```

> [!OUTPUT]
>
> ```json
> {
>   "UserId": "AIDAI...",
>   "Account": "123456789012",
>   "Arn": "arn:aws:iam::123456789012:user/condition-test-user"
> }
> ```

103. Amazon S3 버킷 목록을 조회합니다 (읽기 권한 - 성공 예상):

```bash
aws s3 ls --profile condition-test
```

> [!OUTPUT]
>
> ```
> 2026-02-21 11:39:19 cf-templates-146idipdkxm9-ap-northeast-2
> 2026-03-02 16:24:37 iam-condition-lab-demo-12345
> ```

> [!NOTE]
> 날짜와 버킷 목록은 실습 환경에 따라 다를 수 있습니다. 버킷 목록 조회는 MFA 없이도 성공합니다. S3MFARequiredPolicy의 AllowListBucketWithoutMFA Statement가 `s3:ListAllMyBuckets`, `s3:ListBucket`, `s3:GetBucketLocation` 작업을 허용합니다.
>
> **보안 관점 설명**: `s3:ListAllMyBuckets`는 `Resource: "*"`로 설정되어 있어 계정 내 모든 버킷 목록을 조회할 수 있습니다. 이는 AWS Amazon S3 서비스의 설계상 버킷 목록 조회는 계정 수준 작업이기 때문입니다. 태스크 1에서 생성한 버킷뿐만 아니라 계정에 존재하는 다른 버킷도 모두 표시됩니다. 특정 버킷만 보이도록 제한하려면 버킷별 정책이나 AWS IAM 권한 경계 (Permission Boundary)를 사용해야 합니다.

104. 테스트 파일을 생성합니다:

```bash
echo "test content" > test.txt
```

105. 태스크 1에서 생성한 버킷에 파일 업로드를 시도합니다 (본인의 버킷 이름으로 변경):

```bash
aws s3 cp test.txt s3://iam-condition-lab-YOUR-INITIALS-12345/ --profile condition-test
```

> [!OUTPUT]
>
> ```
> upload failed: ./test.txt to s3://iam-condition-lab-demo-12345/test.txt An error occurred (AccessDenied) when calling the PutObject operation: User: arn:aws:iam::123456789012:user/condition-test-user is not authorized to perform: s3:PutObject on resource: "arn:aws:s3:::iam-condition-lab-demo-12345/test.txt" with an explicit deny in an identity-based policy
> ```

> [!IMPORTANT]
> **AccessDenied** 오류가 나와야 정상입니다. 이는 S3MFARequiredPolicy의 DenyS3ActionsWithoutMFA Statement가 MFA 없는 쓰기 작업을 차단했음을 의미합니다. 오류 메시지에 "with an explicit deny in an identity-based policy"라고 표시되어 정책의 Deny Statement가 작동했음을 확인할 수 있습니다.

   <img src="/images/week2/2-1-task7-step4-upload-denied.png" alt="MFA 없이 S3 업로드 시도 시 AccessDenied 오류" class="guide-img-md" />

106. 버킷에서 객체 삭제를 시도합니다 (실패 예상):

```bash
aws s3 rm s3://iam-condition-lab-YOUR-INITIALS-12345/test.txt --profile condition-test
```

> [!OUTPUT]
>
> ```
> delete failed: s3://iam-condition-lab-demo-12345/test.txt An error occurred (AccessDenied) when calling the DeleteObject operation: User: arn:aws:iam::123456789012:user/condition-test-user is not authorized to perform: s3:DeleteObject on resource: "arn:aws:s3:::iam-condition-lab-demo-12345/test.txt" with an explicit deny in an identity-based policy
> ```

   <img src="/images/week2/2-1-task7-step5-delete-denied.png" alt="MFA 없이 S3 삭제 시도 시 AccessDenied 오류" class="guide-img-md" />

> [!NOTE]
> 삭제 작업도 MFA 없이는 차단됩니다.
>
> **Amazon S3 보안 설계 설명**: 이전 단계에서 업로드가 실패했으므로 `test.txt` 객체는 버킷에 존재하지 않습니다. 그러나 Amazon S3는 권한이 없는 요청에 대해 객체 존재 여부를 노출하지 않기 위해 항상 `AccessDenied`를 반환합니다. 이는 보안 설계의 일부로, 권한이 없는 사용자가 객체의 존재 여부를 추측하지 못하도록 합니다. 만약 권한이 있는 상태에서 존재하지 않는 객체를 삭제하려고 하면 `NoSuchKey` 또는 `404 Not Found` 오류가 반환됩니다.
>
> 이로써 MFA 강제 정책이 올바르게 작동함을 확인했습니다.

> [!TIP]
> **MFA 있을 때 테스트 방법 (옵션)**:
>
> 이 실습에서는 Access Key(장기 자격증명)를 사용하므로 "MFA 없이 차단"만 테스트했습니다. "MFA 있을 때 허용"을 테스트하려면 다음 방법을 사용할 수 있습니다:
>
> - **방법 1 (AWS CLI)**: `aws sts get-session-token --serial-number arn:aws:iam::ACCOUNT-ID:mfa/USER-NAME --token-code MFA-CODE` 명령어로 MFA 인증된 임시 자격증명을 발급받아 테스트합니다. 이 방법은 AWS IAM 사용자에 MFA 디바이스를 먼저 연결해야 합니다.
> - **방법 2 (AWS 콘솔)**: AWS Management Console에 MFA 인증으로 로그인한 후 Amazon S3 콘솔에서 직접 파일을 업로드합니다. 콘솔 세션은 MFA 인증된 임시 자격증명을 사용하므로 업로드가 성공합니다.
>
> 실무에서는 민감한 작업(삭제, 쓰기)에 MFA를 필수로 요구하여 보안을 강화합니다.

✅ **태스크 완료**: MFA 정책이 올바르게 작동함을 확인했습니다.

## 태스크 8: IP 제한 정책 동작 테스트

이 태스크에서는 **IP 주소 기반 접근 제어 정책**이 올바르게 작동하는지 테스트합니다. 태스크 3에서 현재 IP를 허용 목록에 추가했으므로, 정책 연결 후 접근 성공과 차단을 모두 확인할 수 있습니다.

### 8-1: IP 제한 정책 연결

107. AWS IAM 콘솔로 이동합니다.
108. 왼쪽 메뉴에서 **Users**를 선택합니다.
109. 사용자 목록에서 `condition-test-user`를 검색합니다.
110. `condition-test-user`를 클릭합니다.
111. **Permissions** 탭을 선택합니다.
112. [[Add permissions]] 드롭다운 버튼을 클릭합니다.
113. 드롭다운 메뉴에서 `Add permissions`를 선택합니다.
   <img src="/images/week2/2-1-task8-step7-add-permissions.png" alt="Add permissions 드롭다운 메뉴" class="guide-img-md" />

114. **Permissions options** 섹션에서 `Attach policies directly` 라디오 버튼을 선택합니다.
115. **Permissions policies** 섹션으로 스크롤합니다.
116. 정책 검색창에 `S3IPRestrictionPolicy`를 입력합니다.
117. `S3IPRestrictionPolicy` 정책 왼쪽의 체크박스를 선택합니다.
118. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task8-step12-next-button.png" alt="정책 선택 후 Next 버튼" class="guide-img-md" />

119. [[Add permissions]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task8-step13-add-permissions.png" alt="Add permissions 버튼" class="guide-img-md" />
    <img src="/images/week2/2-1-task8-step13-add-permissions-2.png" alt="정책 연결 완료 화면" class="guide-img-md" />

> [!NOTE]
> 이제 condition-test-user에는 S3MFARequiredPolicy와 S3IPRestrictionPolicy 두 개의 정책이 연결되어 있습니다.

### 8-2: 현재 IP에서 접근 테스트 (성공 예상)

120. AWS CloudShell로 이동합니다.
121. 다음 명령어를 실행하여 CloudShell의 IP 주소를 확인합니다:

```bash
curl https://checkip.amazonaws.com
```

> [!NOTE]
> AWS CloudShell은 AWS 데이터센터에서 실행되므로 로컬 컴퓨터의 IP 주소와 다릅니다. 태스크 3에서 정책에 추가한 IP 주소가 로컬 컴퓨터의 IP라면, CloudShell의 IP는 다를 수 있습니다.
>
> **IP 주소 차이**:
>
> - **로컬 컴퓨터 IP**: 집, 회사, 카페 등의 공인 IP. (태스크 3에서 확인한 IP)
> - **CloudShell IP**: AWS 리전 데이터센터의 IP. (위 명령어로 확인한 IP)
>
> 두 IP가 다르다면 S3IPRestrictionPolicy에 CloudShell IP도 추가해야 합니다. 다음 단계에서 정책을 수정합니다.

122. 출력된 CloudShell IP 주소를 메모장에 복사합니다.

> [!TIP]
> AWS IAM은 글로벌 서비스이므로 새 브라우저 탭에서 작업하는 것이 좋습니다. CloudShell 탭은 열어둔 채로 IAM 콘솔을 별도 탭에서 열면 두 서비스를 동시에 사용할 수 있습니다.

123. 새 브라우저 탭을 엽니다.
124. 새 탭에서 AWS Management Console에 로그인한 후 상단 검색창에서 `IAM`을 검색하고 선택합니다.
125. 왼쪽 메뉴에서 **Policies**를 선택합니다.
126. 정책 목록에서 `S3IPRestrictionPolicy`를 검색합니다.
127. `S3IPRestrictionPolicy`를 클릭합니다.
128. **Permissions** 탭에서 [[Edit]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task8-step9-edit-policy.png" alt="정책 편집 버튼" class="guide-img-md" />

129. **JSON** 탭을 선택합니다.
130. 기존 정책의 `aws:SourceIp` 배열에 CloudShell IP를 추가합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowFromSpecificIP",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["YOUR_LOCAL_IP/32", "CLOUDSHELL_IP/32"]
        }
      }
    },
    {
      "Sid": "DenyFromOtherIPs",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "NotIpAddress": {
          "aws:SourceIp": ["YOUR_LOCAL_IP/32", "CLOUDSHELL_IP/32"]
        }
      }
    }
  ]
}
```

> [!IMPORTANT]
> **필수 확인**:
>
> - `YOUR_LOCAL_IP`는 태스크 3에서 추가한 로컬 컴퓨터의 IP 주소입니다. (그대로 유지)
> - `CLOUDSHELL_IP`를 위에서 확인한 실제 CloudShell IP로 변경합니다.
> - 두 Statement 모두 동일한 IP 배열을 사용해야 합니다.
> - JSON 배열 형식을 정확히 지켜야 합니다. (쉼표, 대괄호 확인)

131. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task8-step12-next-button.png" alt="정책 수정 후 Next 버튼" class="guide-img-md" />

132. [[Save changes]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-task8-step13-save-changes.png" alt="정책 저장 버튼" class="guide-img-md" />

133. 정책 수정이 완료되면 화면 상단에 녹색 배너로 "Policy S3IPRestrictionPolicy updated."라는 성공 메시지가 표시됩니다.
    <img src="/images/week2/2-1-task8-step14-policy-updated.png" alt="정책 수정 완료 메시지" class="guide-img-sm" />

> [!TIP]
> **JSON 배열 형식 설명**:
>
> - 단일 IP: `["1.2.3.4/32"]`
> - 여러 IP: `["1.2.3.4/32", "5.6.7.8/32"]`
> - 마지막 항목 뒤에는 쉼표를 붙이지 않습니다.

134. CloudShell 탭으로 이동합니다.
135. 버킷 목록 조회를 시도합니다:

```bash
aws s3 ls --profile condition-test
```

> [!OUTPUT]
>
> ```
> YYYY-MM-DD HH:MM:SS iam-condition-lab-[이니셜]-[숫자]
> ```

   <img src="/images/week2/2-1-task8-step16-bucket-list.png" alt="CloudShell IP 추가 후 버킷 목록 조회 성공" class="guide-img-md" />

> [!NOTE]
> 현재 IP가 태스크 3에서 허용 목록에 추가되었으므로 접근이 성공합니다.

> [!TIP]
> **접근 실패 시 확인 사항**:
>
> - CloudShell 리전이 `ap-northeast-2 (서울)`인지 확인합니다. (리전이 다르면 IP 주소가 달라집니다)
> - CloudShell IP 주소가 정책에 정확히 반영되었는지 확인합니다. (확인한 IP와 정책의 IP가 일치해야 함)
> - 정책 수정 후 저장이 완료되었는지 확인합니다. (성공 메시지 확인)
> - CloudShell을 재시작한 경우 IP 주소가 변경될 수 있으므로 다시 확인합니다.

### 8-3: IP 제한 정책 분리

136. AWS IAM 콘솔의 `condition-test-user` 페이지로 이동합니다.
137. **Permissions** 탭을 선택합니다.
138. **Permissions policies** 섹션에서 `S3IPRestrictionPolicy` 정책 왼쪽의 체크박스를 선택합니다.
139. [[Remove]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task8-step4-remove-button.png" alt="정책 제거 버튼" class="guide-img-md" />

140. 확인 창에서 [[Remove policy]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-task8-step5-remove-policy.png" alt="정책 제거 확인 대화상자" class="guide-img-sm" />

> [!NOTE]
> IP 제한 정책 테스트가 완료되었으므로 정책을 분리합니다. 이제 condition-test-user에는 S3MFARequiredPolicy만 남아있습니다.

✅ **태스크 완료**: IP 제한 정책이 올바르게 작동함을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS IAM Policy의 Condition 요소 구조를 이해했습니다.
- MFA 강제 정책을 작성하고 테스트했습니다.
- IP 주소 기반 접근 제어 정책을 작성하고 테스트했습니다.
- 시간 기반 정책을 작성했습니다.
- 복합 조건을 사용하는 정책을 작성했습니다.
- 다양한 Condition 키의 사용법을 학습했습니다.

> [!NOTE]
> 이 실습에서는 MFA 정책과 IP 제한 정책을 실제로 테스트했습니다. 시간 기반 정책과 복합 조건 정책은 정책 구조를 학습하기 위해 작성했으며, 실제 동작을 테스트하려면 condition-test-user에 각 정책을 순차적으로 연결/해제하며 확인할 수 있습니다.
>
> **추가 학습 과제 (옵션)**:
>
> - **시간 기반 정책 (S3TimeBasedPolicy)**: 태스크 4에서 생성한 정책의 JSON을 다시 열어보고, `DateGreaterThan`과 `DateLessThan` 조건이 어떻게 조합되어 특정 기간만 허용하는지 분석합니다. 현재 시간이 정책에서 지정한 기간 내에 있다면 condition-test-user에 연결하여 동작을 테스트할 수 있습니다.
> - **복합 조건 정책 (S3ComplexConditionPolicy)**: 태스크 5에서 생성한 정책의 JSON을 다시 열어보고, 암호화 필수(`s3:x-amz-server-side-encryption`), IP 제한(`aws:SourceIp`), MFA 인증(`aws:MultiFactorAuthPresent`)이 어떻게 AND 조건으로 결합되어 있는지 분석합니다. 세 조건을 모두 만족해야만 Amazon S3 객체 업로드가 가능합니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 리소스를 정리합니다.

### 단계 1: Tag Editor로 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `All regions`를 선택합니다.

> [!NOTE]
> AWS IAM 사용자와 정책은 글로벌 리소스이므로 `All regions`를 선택해야 검색 결과에 표시됩니다.

4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `2-1`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 Amazon S3 버킷 1개, AWS IAM 사용자 1개, AWS IAM 정책 4개가 표시됩니다.
   <img src="/images/week2/2-1-cleanup-step7-tag-search.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Access Key 삭제

8. AWS IAM 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Users**를 선택합니다.
10. 사용자 목록에서 `condition-test-user`를 검색합니다.
11. `condition-test-user`를 클릭합니다.
12. **Security credentials** 탭을 선택합니다.
13. **Access keys** 섹션으로 스크롤합니다.
14. **Access keys** 섹션에서 생성한 Access Key를 선택합니다.
15. **Actions** > `Deactivate`를 선택합니다.
   <img src="/images/week2/2-1-cleanup-step8-deactivate.png" alt="Access Key 비활성화 확인 창" class="guide-img-md" />

16. 확인 창에서 [[Deactivate]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step9-deactivate-complete.png" alt="Access Key 비활성화 완료 화면" class="guide-img-sm" />
   <img src="/images/week2/2-1-cleanup-step9-deactivate-complete-2.png" alt="비활성화된 Access Key 상태" class="guide-img-md" />

17. 다시 **Actions** > `Delete`를 선택합니다.
    <img src="/images/week2/2-1-cleanup-step10-delete.png" alt="Access Key 삭제 확인 창" class="guide-img-md" />

18. 확인 창에서 **Access key ID**를 입력 필드에 입력합니다.
19. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week2/2-1-cleanup-step12-delete-complete.png" alt="Access Key 삭제 완료 메시지" class="guide-img-sm" />

> [!NOTE]
> Access Key를 삭제하면 복구할 수 없습니다. 삭제 전 해당 키를 사용하는 애플리케이션이나 스크립트가 없는지 확인합니다.

### 단계 3: AWS CLI 프로파일 삭제

20. AWS CloudShell로 이동합니다.
21. 다음 명령어를 실행하여 condition-test 프로파일이 존재하는지 확인합니다:

```bash
aws configure list --profile condition-test
```

> [!NOTE]
> 프로파일이 존재하면 프로파일 정보가 표시됩니다. 다음 단계로 진행하여 프로파일을 삭제합니다.

22. 다음 명령어를 실행하여 credentials 파일에서 프로파일을 삭제합니다:

```bash
sed -i.bak '/^\[condition-test\]/,/^\[/{/^\[condition-test\]/d;/^\[/!d;}' ~/.aws/credentials
```

23. 다음 명령어를 실행하여 config 파일에서 프로파일을 삭제합니다:

```bash
sed -i.bak '/^\[profile condition-test\]/,/^\[/{/^\[profile condition-test\]/d;/^\[/!d;}' ~/.aws/config
```

> [!NOTE]
> 이 명령어는 다음 섹션 헤더(`[`)가 나타날 때까지만 삭제하므로 다른 프로파일이 보존됩니다. `.bak` 파일은 백업 파일입니다.

24. 삭제를 확인합니다:

```bash
aws configure list --profile condition-test
```

> [!OUTPUT]
>
> ```
> The config profile (condition-test) could not be found
> ```

25. 백업 파일을 삭제합니다:

```bash
rm ~/.aws/credentials.bak ~/.aws/config.bak
```

<img src="/images/week2/2-1-cleanup-step3-profile-deleted.png" alt="AWS CLI 프로파일 삭제 완료" class="guide-img-md" />

> [!NOTE]
> AWS CloudShell의 홈 디렉토리는 세션 간 유지되므로, 프로파일을 삭제하지 않으면 다음에 CloudShell을 열었을 때도 condition-test 프로파일이 남아있습니다. 보안을 위해 반드시 삭제해야 합니다.

### 단계 4: AWS IAM 사용자 삭제

26. AWS IAM 콘솔로 이동합니다.
27. 왼쪽 메뉴에서 **Users**를 선택합니다.
28. 사용자 목록에서 `condition-test-user`를 검색합니다.
29. `condition-test-user`를 선택합니다.
30. [[Delete]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step5-delete-user.png" alt="IAM 사용자 삭제 확인 창" class="guide-img-md" />

31. 확인 창이 나타나면 입력 필드에 `confirm`을 입력합니다.

> [!NOTE]
> AWS는 실수로 인한 삭제를 방지하기 위해 "confirm"을 입력하도록 요구합니다. 사용자를 삭제하면 연결된 정책도 자동으로 분리됩니다.

32. [[Delete user]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step7-user-deleted.png" alt="IAM 사용자 삭제 완료 메시지" class="guide-img-sm" />

33. 화면 상단에 녹색 배너로 "User "condition-test-user" deleted."라는 성공 메시지가 표시됩니다.
   <img src="/images/week2/2-1-cleanup-step8-success.png" alt="IAM 사용자 삭제 성공 배너" class="guide-img-sm" />

### 단계 5: AWS IAM 정책 삭제

34. 왼쪽 메뉴에서 **Policies**를 선택합니다.
35. 정책 목록에서 `S3MFARequiredPolicy`를 검색합니다.
36. `S3MFARequiredPolicy` 정책 왼쪽의 라디오 버튼을 선택합니다.

> [!NOTE]
> 정책이 선택되면 라디오 버튼에 점이 표시되고, 상단의 [[Delete]] 버튼이 활성화됩니다.

37. 상단의 [[Delete]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step4-delete-button.png" alt="IAM 정책 삭제 버튼" class="guide-img-md" />

38. 확인 창이 나타나면 입력 필드에 `S3MFARequiredPolicy`를 입력합니다.
39. [[Delete]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step6-delete-confirm.png" alt="IAM 정책 삭제 확인 창" class="guide-img-sm" />

40. 화면 상단에 녹색 배너로 "Policy deleted."라는 성공 메시지가 표시됩니다.
   <img src="/images/week2/2-1-cleanup-step7-policy-deleted.png" alt="IAM 정책 삭제 성공 메시지" class="guide-img-sm" />

41. 동일한 방법으로 다음 정책들을 각각 삭제합니다:
    - `S3IPRestrictionPolicy`
    - `S3TimeBasedPolicy`
    - `S3ComplexConditionPolicy`

> [!NOTE]
> 각 정책 삭제 시마다 정책 이름을 정확히 입력해야 합니다. 4개의 정책을 모두 삭제하면 정책 목록에서 더 이상 표시되지 않습니다.

### 단계 6: Amazon S3 버킷 삭제

42. Amazon S3 콘솔로 이동합니다.
43. 버킷 목록에서 `iam-condition-lab-YOUR-INITIALS-12345` 버킷을 검색합니다.
44. 버킷 이름 왼쪽의 라디오 버튼을 선택합니다.
45. [[Delete]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step4-delete-bucket-button.png" alt="S3 버킷 삭제 버튼" class="guide-img-md" />

46. 확인 창이 나타나면 입력 필드에 버킷 이름 전체를 입력합니다.

> [!NOTE]
> 버킷 이름을 정확히 입력해야 [[Delete bucket]] 버튼이 활성화됩니다.

47. [[Delete bucket]] 버튼을 클릭합니다.
   <img src="/images/week2/2-1-cleanup-step6-delete-bucket.png" alt="S3 버킷 삭제 확인 창" class="guide-img-md" />

48. 화면 상단에 녹색 배너로 "Successfully deleted bucket"이라는 성공 메시지가 표시됩니다.
   <img src="/images/week2/2-1-cleanup-step7-bucket-success.png" alt="S3 버킷 삭제 성공 메시지" class="guide-img-sm" />

49. 버킷 목록에서 해당 버킷이 더 이상 표시되지 않는지 확인합니다.

> [!TIP]
> **버킷에 객체가 있는 경우**:
>
> 정상적으로 실습을 진행했다면 태스크 7에서 파일 업로드가 실패했으므로 버킷은 비어있습니다. 하지만 만약 버킷에 객체가 있다면 다음 단계를 먼저 수행해야 합니다:
>
> 1. 버킷을 선택한 후 [[Empty]] 버튼을 클릭합니다.
> 2. 확인 창에서 `permanently delete`를 입력합니다.
> 3. [[Empty]] 버튼을 클릭하여 버킷을 비웁니다.
> 4. "Successfully emptied bucket" 메시지가 표시되면 위의 삭제 단계를 진행합니다.

### 단계 7: Tag Editor로 최종 확인

50. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
51. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
52. **Regions**에서 `All regions`를 선택합니다.
53. **Resource types**에서 `All supported resource types`를 선택합니다.
54. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `2-1`
55. [[Search resources]] 버튼을 클릭합니다.
56. 검색 결과에 리소스가 표시되지 않는지 확인합니다.
   <img src="/images/week2/2-1-cleanup-step7-no-resources.png" alt="Tag Editor 검색 결과 - 리소스 없음" class="guide-img-md" />

> [!NOTE]
> 모든 리소스가 정상적으로 삭제되었다면 검색 결과에 아무것도 표시되지 않습니다. 만약 리소스가 남아있다면 해당 리소스를 수동으로 삭제해야 합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS IAM JSON 정책 요소: Condition](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_policies_elements_condition.html)
- [AWS 전역 조건 컨텍스트 키](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_policies_condition-keys.html)
- [AWS IAM 정책 예제](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/access_policies_examples.html)

## 📚 참고: Condition 키 종류

다음은 자주 사용되는 Condition 키들입니다:

### 문자열 조건(String Conditions)

```json
"Condition": {
  "StringEquals": {
    "s3:x-amz-server-side-encryption": "AES256"
  },
  "StringLike": {
    "s3:prefix": "documents/*"
  }
}
```

### 숫자 조건(Numeric Conditions)

```json
"Condition": {
  "NumericLessThan": {
    "s3:max-keys": "100"
  },
  "NumericGreaterThanEquals": {
    "aws:MultiFactorAuthAge": "3600"
  }
}
```

### 날짜/시간 조건(Date/Time Conditions)

```json
"Condition": {
  "DateGreaterThan": {
    "aws:CurrentTime": "2026-01-01T00:00:00Z"
  },
  "DateLessThan": {
    "aws:CurrentTime": "2026-12-31T23:59:59Z"
  }
}
```

### Boolean 조건(Boolean Conditions)

```json
"Condition": {
  "BoolIfExists": {
    "aws:SecureTransport": "true",
    "aws:MultiFactorAuthPresent": "true"
  }
}
```

> [!NOTE]
> 태스크 2에서 설명한 것처럼, **aws:MultiFactorAuthPresent** 키는 **임시 자격증명을 사용할 때만** 요청에 포함됩니다. **BoolIfExists**를 사용하면 키가 없을 때(장기 자격증명 사용 시) 조건을 true로 평가하지만, Deny Statement에서 "false"를 요구하므로 결과적으로 접근이 차단됩니다. 이를 통해 MFA 없는 접근을 효과적으로 차단할 수 있습니다.

### IP 주소 조건(IP Address Conditions)

```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": [
      "203.0.113.0/24",   // 예시 IP (RFC 5737 문서용)
      "198.51.100.0/24"   // 실제 사용 시 본인의 IP로 변경
    ]
  },
  "NotIpAddress": {
    "aws:SourceIp": "192.0.2.0/24"  // 예시 IP (RFC 5737 문서용)
  }
}
```

> [!NOTE]
> 위 예시의 IP 주소는 RFC 5737 문서용 예시 IP입니다. 실제 정책 작성 시 본인의 IP 주소로 변경해야 합니다.

### 시간 기반 접근 제어 실무 활용

#### 1. 프로젝트 기간 제한

**시나리오**: 외부 컨설턴트에게 프로젝트 기간(3개월)만 AWS 리소스 접근 권한 부여

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-01-01T00:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2026-03-31T23:59:59Z"
        }
      }
    }
  ]
}
```

**장점**: 프로젝트 종료 후 수동으로 권한을 회수할 필요 없이 자동으로 접근이 차단됩니다.

#### 2. 임시 계약직 직원 접근 제한

**시나리오**: 6개월 계약직 직원에게 계약 기간 동안만 특정 Amazon S3 버킷 접근 허용

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::project-bucket",
        "arn:aws:s3:::project-bucket/*"
      ],
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-01-01T00:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2026-06-30T23:59:59Z"
        }
      }
    }
  ]
}
```

**모범 사례**: 계약 종료일보다 1-2일 여유를 두고 설정하여 업무 인수인계 시간을 확보합니다.

#### 3. 이벤트 기간 한정 리소스 접근

**시나리오**: 블랙 프라이데이 이벤트 기간(11월 한 달)만 마케팅 팀에게 프로모션 AWS Lambda 함수 실행 권한 부여

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["lambda:InvokeFunction"],
      "Resource": "arn:aws:lambda:ap-northeast-2:*:function:BlackFridayPromotion",
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-11-01T00:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2026-11-30T23:59:59Z"
        }
      }
    }
  ]
}
```

**장점**: 이벤트 종료 후 자동으로 권한이 회수되어 보안 위험을 최소화합니다.

#### 4. 감사 기간 동안 삭제 작업 차단

**시나리오**: 연말 감사 기간(12월 1일~31일) 동안 모든 삭제 작업 차단

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteBucket",
        "dynamodb:DeleteTable",
        "rds:DeleteDBInstance"
      ],
      "Resource": "*",
      "Condition": {
        "DateGreaterThan": {
          "aws:CurrentTime": "2026-12-01T00:00:00Z"
        },
        "DateLessThan": {
          "aws:CurrentTime": "2026-12-31T23:59:59Z"
        }
      }
    }
  ]
}
```

**중요**: Deny는 모든 Allow보다 우선하므로, 관리자 권한이 있어도 감사 기간에는 삭제가 차단됩니다.

#### 5. 시간대 변환 예시

**한국 시간(KST)을 UTC로 변환하는 방법**:

| 한국 시간 (KST, UTC+9) | UTC 시간         | 정책에 입력할 값       |
| ---------------------- | ---------------- | ---------------------- |
| 2026-01-01 09:00       | 2026-01-01 00:00 | `2026-01-01T00:00:00Z` |
| 2026-01-01 18:00       | 2026-01-01 09:00 | `2026-01-01T09:00:00Z` |
| 2026-12-31 23:59       | 2026-12-31 14:59 | `2026-12-31T14:59:59Z` |

**변환 공식**: UTC 시간 = 한국 시간 - 9시간

**온라인 도구**: [https://www.timeanddate.com/worldclock/converter.html](https://www.timeanddate.com/worldclock/converter.html)

#### 6. 매일 반복되는 업무 시간 제한 (대안 솔루션)

**문제**: AWS IAM 정책만으로는 "매일 09:00-18:00"을 구현할 수 없습니다.

**대안 1: AWS Lambda + Amazon EventBridge**

```python
# AWS Lambda 함수로 매일 09:00에 정책 연결, 18:00에 정책 분리
import boto3

def lambda_handler(event, context):
    iam = boto3.client('iam')
    action = event['action']  # 'attach' or 'detach'

    if action == 'attach':
        iam.attach_user_policy(
            UserName='employee-user',
            PolicyArn='arn:aws:iam::123456789012:policy/WorkHoursPolicy'
        )
    elif action == 'detach':
        iam.detach_user_policy(
            UserName='employee-user',
            PolicyArn='arn:aws:iam::123456789012:policy/WorkHoursPolicy'
        )
```

**Amazon EventBridge 규칙**:

- 09:00 KST (00:00 UTC): AWS Lambda 함수 호출 (action=attach)
- 18:00 KST (09:00 UTC): AWS Lambda 함수 호출 (action=detach)

**대안 2: AWS Config 규칙**

- AWS Config로 업무 시간 외 API 호출을 감지하고 알림
- 실시간 차단은 불가능하지만, 사후 감사 및 경고 가능

**대안 3: 서드파티 솔루션**

- HashiCorp Vault: 시간 기반 동적 자격증명 발급
- AWS IAM Identity Center: 세션 시간 제한 설정

#### 7. 시간 기반 정책 모범 사례

**1. 여유 시간 확보**

- 시작 시간: 실제 필요 시간보다 1-2시간 일찍 설정
- 종료 시간: 실제 필요 시간보다 1-2시간 늦게 설정
- 이유: 시간대 변환 오류, 업무 지연 등을 고려

**2. 명시적 Deny 사용**

- Allow만 사용하면 다른 정책의 Allow가 우선될 수 있음
- Deny를 함께 사용하여 기간 외 접근을 확실히 차단

**3. 알림 설정**

- Amazon CloudWatch Events로 정책 만료 7일 전 알림
- AWS Lambda로 자동 연장 또는 관리자 승인 워크플로우 구현

**4. 테스트**

- 정책 적용 전 테스트 사용자로 충분히 테스트
- 시간대 변환이 올바른지 확인
- 기간 시작/종료 시점에 실제 동작 확인

**5. 문서화**

- 정책 Description에 기간 및 목적 명시
- 태그로 만료일 표시 (예: `ExpiryDate=2026-12-31`)
- 정책 검토 주기 설정 (월 1회 권장)
