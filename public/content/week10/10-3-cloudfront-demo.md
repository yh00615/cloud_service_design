---
title: 'Amazon CloudFront CDN 배포 및 캐싱 전략'
week: 10
session: 3
awsServices:
  - Amazon CloudFront
  - Amazon S3
learningObjectives:
  - CDN의 개념과 Amazon CloudFront의 엣지 로케이션 동작 원리를 이해할 수 있습니다.
  - Amazon S3 오리진을 준비하고 Amazon CloudFront 배포를 생성할 수 있습니다.
  - 캐시 정책을 구성하고 TTL을 설정할 수 있습니다.
  - 캐시 무효화를 수행하고 Amazon CloudFront 성능을 확인할 수 있습니다.
prerequisites:
  - Amazon S3 기본 개념 이해
  - HTTP/HTTPS 프로토콜 이해
---

이번 데모에서는 Amazon CloudFront를 사용하여 QuickTable 레스토랑 예약 시스템을 전 세계 사용자에게 빠르고 안전하게 제공하는 방법을 학습합니다. Week 9-3에서 구축한 Amazon S3 정적 웹사이트를 Amazon CloudFront를 통해 글로벌 배포하고, 캐싱과 HTTPS를 적용하여 성능과 보안을 개선합니다.

QuickTable은 전 세계 사용자가 레스토랑을 검색하고 예약할 수 있는 글로벌 서비스입니다. Amazon CloudFront CDN을 활용하면 서울, 도쿄, 뉴욕, 런던 등 전 세계 어디서나 빠른 응답 속도로 QuickTable 웹사이트에 접근할 수 있습니다. 사용자와 가장 가까운 엣지 로케이션에서 콘텐츠를 제공하여 지연 시간을 최소화하고, OAC(Origin Access Control)를 통해 Amazon S3 버킷을 안전하게 보호합니다.

> [!DOWNLOAD]
> [week10-3-cloudfront-demo.zip](/files/week10/week10-3-cloudfront-demo.zip)
>
> - `index.html` - QuickTable 메인 페이지 (레스토랑 예약 서비스 소개, 캐싱 테스트 UI)
> - `about.html` - QuickTable 소개 페이지 (글로벌 아키텍처, 캐싱 전략 가이드, 문제 해결)
> - `style.css` - QuickTable 스타일시트 (반응형 디자인, 캐싱 테스트용)
> - `script.js` - QuickTable 인터랙티브 기능 (캐싱 테스트, 리소스 로딩 정보 표시)
>
> **관련 태스크:**
>
> - 태스크 1: Amazon S3 오리진 준비 (QuickTable 프론트엔드 파일 업로드)
> - 태스크 2: Amazon CloudFront 배포 생성 (5단계 구성, OAC 자동 설정)
> - 태스크 3: 배포 테스트 및 캐싱 확인 (엣지 로케이션 성능 측정)
> - 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화 (버전 관리 전략)
> - 태스크 5: Amazon CloudFront Functions로 URL 리다이렉트 (엣지 컴퓨팅)

> [!NOTE]
> 이 데모는 비용이 거의 발생하지 않습니다. Amazon CloudFront 프리 티어에서 매월 1TB 데이터 전송과 10,000,000건의 요청을 무료로 제공합니다.

## 태스크 1: QuickTable 프론트엔드 Amazon S3 오리진 준비

이 태스크에서는 Amazon CloudFront의 오리진으로 사용할 Amazon S3 버킷을 생성하고 QuickTable 프론트엔드 콘텐츠를 업로드합니다. `about.html` 파일은 QuickTable 서비스 소개 페이지로, 글로벌 아키텍처와 캐싱 전략 가이드를 설명합니다. 이 파일을 통해 Amazon CloudFront의 다중 경로 라우팅 기능을 테스트할 수 있습니다.

1. 다운로드한 `week10-3-cloudfront-demo.zip` 파일의 압축을 해제합니다.
2. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
3. 상단 검색창에 `S3`을 입력하고 선택한 후 왼쪽 메뉴에서 **General purpose buckets**를 선택합니다.
4. [[Create bucket]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task0-step4-s3-bucket.png" alt="S3 Create bucket" class="guide-img-md" />

5. **General configuration** 섹션에서 **AWS Region**이 `Asia Pacific (Seoul) ap-northeast-2`로 설정되어 있는지 확인합니다.
6. **Bucket namespace**에서 `Global namespace`가 선택되어 있는지 확인합니다.

> [!NOTE]
> **Bucket namespace** 옵션이 표시될 수 있습니다.
>
> - **Global namespace (기본값)**: 버킷 이름이 전 세계 모든 AWS 계정에서 고유해야 합니다. 기존 Amazon S3 방식과 동일합니다.
> - **Account Regional namespace (권장)**: 버킷 이름이 내 계정 + 리전 내에서만 고유하면 됩니다. 다른 계정에서 같은 이름을 사용해도 충돌하지 않습니다.
>
> 이 실습에서는 기본값인 Global namespace를 사용합니다.

7. **Bucket name**에 `quicktable-cloudfront-origin-{Initials}-{StudentId}`를 입력합니다.

    <img src="/images/week10/10-3-task0-step7-bucket-name.png" alt="Bucket name 입력" class="guide-img-md" />

> [!TIP]
> `{Initials}`를 본인의 이니셜로, `{StudentId}`를 본인의 학번으로 변경합니다 (예: `quicktable-cloudfront-origin-jdoe-20240001`).
> 버킷 이름은 전 세계적으로 고유해야 합니다.

8. **Block Public Access settings**는 모두 체크된 상태로 유지합니다.

    <img src="/images/week10/10-3-task0-step8-block-public.png" alt="Block Public Access 설정 유지" class="guide-img-md" />

> [!CONCEPT] Amazon S3 퍼블릭 액세스 차단 (S3 Block Public Access)
> Amazon CloudFront는 OAC(Origin Access Control)를 통해 비공개 Amazon S3 버킷에 접근합니다.
> 따라서 버킷을 퍼블릭으로 만들 필요가 없으며, 보안을 유지할 수 있습니다.

9. 아래로 스크롤하여 **Tags - optional** 섹션을 확인합니다.
10. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-3`    |
| `CreatedBy` | `Student` |

<img src="/images/week10/10-3-task0-step10-create-bucket.png" alt="Tags 추가 및 Create bucket" class="guide-img-md" />

11. [[Create bucket]] 버튼을 클릭합니다.
12. 생성된 버킷을 선택합니다.
13. [[Upload]] 버튼을 클릭합니다.
14. 압축 해제한 폴더에서 `index.html`, `about.html`, `style.css`, `script.js` 파일을 업로드 영역으로 드래그 앤 드롭합니다.

    <img src="/images/week10/10-3-task0-step14-upload.png" alt="S3 파일 업로드" class="guide-img-md" />

> [!TIP]
> 드래그 앤 드롭 대신 [[Add files]] 버튼을 클릭하여 파일 탐색기에서 4개 파일을 선택할 수도 있습니다.

> [!NOTE]
> 4개 파일이 모두 선택되었는지 확인합니다. **Files and folders** 목록에 4개 파일이 표시되어야 합니다. `README.md`는 실습 안내 파일이므로 업로드하지 않아도 됩니다.

15. [[Upload]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task0-step15-upload-complete.png" alt="Upload 완료" class="guide-img-md" />

> [!NOTE]
> QuickTable 프론트엔드는 레스토랑 예약 서비스 소개와 Amazon CloudFront 캐싱 테스트 기능이 포함되어 있습니다.

✅ **태스크 완료**: QuickTable 프론트엔드 Amazon S3 오리진 버킷이 준비되었습니다.

## 태스크 2: QuickTable Amazon CloudFront 배포 생성

이 태스크에서는 Amazon S3 버킷을 오리진으로 하는 Amazon CloudFront 배포를 생성하여 QuickTable을 전 세계에 배포합니다. Amazon CloudFront 배포 생성은 Choose a plan, Get started, Specify origin, Enable security, Review and create의 5단계로 진행됩니다.

16. 상단 검색창에 `CloudFront`을 입력하고 선택합니다.
17. [[Create distribution]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step17-cloudfront-console.png" alt="CloudFront Create distribution" class="guide-img-md" />

### Step 1: Choose a plan

18. **Choose a plan** 페이지에서 `Pay as you go`를 선택합니다.

> [!NOTE]
> **Free** 플랜($0/month)도 표시되지만, 이 실습에서는 `Pay as you go`를 선택합니다. Pay as you go는 사용한 만큼만 비용이 부과되며, Amazon CloudFront 프리 티어(매월 1TB 데이터 전송, 10,000,000건 요청 무료)가 적용되므로 실습 수준에서는 비용이 거의 발생하지 않습니다.

19. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step19-origin-domain.png" alt="Origin domain 설정" class="guide-img-md" />

### Step 2: Get started

20. **Distribution name**에 `quicktable-cloudfront`를 입력합니다.
21. **Description - optional**에 `Single website or app`이 표시되어 있는지 확인합니다.
22. **Distribution type**에서 `Single website or app`이 선택되어 있는지 확인합니다.

> [!NOTE]
> **Distribution type**은 기본값으로 `Single website or app`이 선택되어 있습니다. `Multi-tenant architecture`는 여러 도메인이 설정을 공유하는 SaaS 아키텍처용이므로 이 실습에서는 기본값을 유지합니다.

23. **Domain** 섹션의 **Route 53 managed domain - optional** 필드는 비워둡니다.
24. **Tags - optional** 섹션을 클릭하여 펼칩니다.
25. 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-3`    |
| `CreatedBy` | `Student` |

26. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step26-oac.png" alt="OAC 설정 후 Next" class="guide-img-md" />

### Step 3: Specify origin

27. **Origin type**에서 `Amazon S3`를 선택합니다.

> [!CONCEPT] Amazon CloudFront 오리진 (CloudFront Origin)
> 오리진은 원본 콘텐츠가 저장된 위치입니다. Amazon S3, Elastic Load Balancing, Amazon API Gateway, VPC origin 또는 커스텀 HTTP 서버를 사용할 수 있습니다.
> Amazon CloudFront는 캐시 미스가 발생하면 오리진에서 콘텐츠를 가져옵니다.

28. **S3 origin**에서 태스크 1에서 생성한 Amazon S3 버킷을 선택합니다.
29. **Allow private S3 bucket access to CloudFront** 체크박스를 확인합니다.

> [!CONCEPT] OAC (Origin Access Control)
> "Allow private S3 bucket access to CloudFront"를 활성화하면 Amazon CloudFront가 자동으로 OAC를 생성하고 Amazon S3 버킷 정책을 업데이트합니다.
> Amazon S3 버킷을 비공개로 유지하면서 Amazon CloudFront만 접근할 수 있도록 하는 보안 기능입니다.

30. **Origin settings**에서 `Use recommended origin settings`를 선택합니다.
31. **Cache settings**에서 `Use recommended cache settings tailored to serving S3 content`를 선택합니다.

> [!CONCEPT] Amazon CloudFront 캐시 정책 (Amazon CloudFront Cache Policy)
> 권장 캐시 설정은 Amazon S3 정적 콘텐츠에 최적화된 캐싱을 자동으로 적용합니다.
>
> - **CachingOptimized**: 정적 콘텐츠에 최적화, 최대 캐싱
> - **CachingDisabled**: 동적 콘텐츠용, 캐싱 안 함
> - **Custom**: 사용자 정의 TTL 및 캐시 키 설정
>
> 배포 생성 후 **Behaviors** 탭에서 캐시 정책, Viewer protocol policy, Allowed HTTP methods 등을 커스터마이즈할 수 있습니다.

32. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step32-origin-settings.png" alt="Origin 설정 완료" class="guide-img-md" />

### Step 4: Enable security

33. **Web Application Firewall (WAF)** 에서 `Do not enable security protections`를 선택합니다.

> [!NOTE]
> WAF를 활성화하면 추가 비용이 발생합니다. 이 데모에서는 비용 절감을 위해 비활성화합니다. 프로덕션 환경에서는 WAF 활성화를 권장합니다. WAF에 대한 자세한 내용은 Week 12-3에서 학습합니다.

34. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step34-security.png" alt="Security 설정 후 Next" class="guide-img-md" />

### Step 5: Review and create

35. **General configuration**, **Origin**, **Cache settings**, **Security** 설정을 검토합니다.
36. **Grant CloudFront access to origin**이 `Yes`로 표시되는지 확인합니다.
37. [[Create distribution]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step37-review.png" alt="Review and Create distribution" class="guide-img-md" />

> [!NOTE]
> Amazon CloudFront가 자동으로 Amazon S3 버킷 정책을 업데이트하여 OAC 접근을 허용합니다. 별도로 버킷 정책을 수동 설정할 필요가 없습니다.
> 배포 생성에 5-15분이 소요됩니다. 상태가 "Deploying"에서 "Enabled"로 변경될 때까지 기다립니다. 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다. 페이지를 새로고침하여 최신 상태를 확인합니다.

38. 배포가 생성되면 **General** 탭의 **Settings** 섹션에서 [[Edit]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task1-step38-default-root.png" alt="Settings Edit - Default root object" class="guide-img-md" />

39. **Default root object - optional** 필드에 `index.html`을 입력합니다.

    <img src="/images/week10/10-3-task1-step39-root-object.png" alt="Default root object 입력" class="guide-img-md" />

> [!CONCEPT] 기본 루트 객체 (Default Root Object)
> 사용자가 `https://d1234abcd.cloudfront.net`처럼 도메인만 입력하면 Amazon CloudFront는 오리진에 `/`를 요청합니다. Amazon S3는 `/`에 해당하는 객체가 없으므로 `AccessDenied` 오류를 반환합니다.
> Default root object를 `index.html`로 설정하면 `/` 요청이 자동으로 `/index.html`로 변환됩니다.

40. [[Save changes]] 버튼을 클릭합니다.

> [!NOTE]
> 설정 변경 후 배포 업데이트에 몇 분이 소요됩니다. 상태가 다시 "Enabled"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: Amazon CloudFront 배포가 생성되고 Amazon S3 버킷 정책이 자동으로 업데이트되었습니다.

## 태스크 3: 배포 테스트 및 캐싱 확인

이 태스크에서는 Amazon CloudFront를 통해 콘텐츠에 접근하고 캐싱 동작을 확인합니다.

41. **Distribution domain name**을 복사합니다.

> [!NOTE]
> 배포 상태가 `Enabled`인지 확인합니다. 도메인 이름은 `d1234abcd.cloudfront.net` 형식입니다.

42. 새 브라우저 탭을 엽니다.
43. 주소창에 복사한 도메인을 붙여넣고 Enter를 누릅니다.

    <img src="/images/week10/10-3-task2-step43-browser.png" alt="CloudFront 도메인으로 웹사이트 접속" class="guide-img-md" />

> [!OUTPUT]
> QuickTable 웹사이트가 정상적으로 로드됩니다. "🍽️ QuickTable" 제목과 서비스 소개가 표시되면 Amazon CloudFront를 통한 콘텐츠 제공이 정상 동작하는 것입니다.

> [!TROUBLESHOOTING]
> **문제**: `AccessDenied` XML 오류가 표시됨
>
> **원인**: Default root object가 설정되지 않았거나 배포 업데이트가 아직 완료되지 않았습니다.
>
> **해결**:
>
> 1. Amazon CloudFront 콘솔에서 배포를 선택합니다.
> 2. **General** 탭의 **Settings** 섹션에서 [[Edit]] 버튼을 클릭합니다.
> 3. **Default root object**가 `index.html`로 설정되어 있는지 확인합니다.
> 4. 설정 변경 후 배포 상태가 "Enabled"로 변경될 때까지 기다린 후 다시 접속합니다.

> [!TROUBLESHOOTING]
> **문제**: 페이지는 표시되지만 스타일(CSS)이 적용되지 않아 디자인이 깨져 보임
>
> **원인**: `style.css` 파일이 Amazon S3 버킷에 업로드되지 않았거나, Content-Type이 올바르게 설정되지 않았습니다.
>
> **해결**:
>
> 1. Amazon S3 콘솔에서 버킷을 선택하고 `style.css` 파일이 존재하는지 확인합니다.
> 2. `style.css`를 선택하고 **Properties** 탭에서 **Content-Type**이 `text/css`인지 확인합니다.
> 3. Content-Type이 `binary/octet-stream`으로 되어 있다면 파일을 삭제하고 다시 업로드합니다.
> 4. 4개 파일(`index.html`, `about.html`, `style.css`, `script.js`)이 모두 버킷 루트에 업로드되어 있는지 확인합니다.

> [!CONCEPT] 엣지 로케이션 (Edge Location)
> Amazon CloudFront는 전 세계 600개 이상의 엣지 로케이션(PoP)에서 콘텐츠를 캐싱합니다.
> 사용자는 가장 가까운 엣지 로케이션에서 콘텐츠를 받아 빠른 속도를 경험합니다.

44. 브라우저 개발자 도구를 엽니다 (F12 키).
45. **Network** 탭을 선택합니다.
46. **Disable cache** 체크박스를 체크합니다.

    <img src="/images/week10/10-3-task2-step46-cache-test.png" alt="개발자 도구 Network 탭 - Disable cache" class="guide-img-sm" />

> [!IMPORTANT]
> 브라우저 캐시를 비활성화하지 않으면 Amazon CloudFront 캐시 헤더를 정확히 확인할 수 없습니다. 브라우저가 로컬 캐시를 사용하여 Amazon CloudFront에 요청을 보내지 않을 수 있습니다.

47. 페이지를 새로고침합니다 (Ctrl+R 또는 Cmd+R).
48. Network 탭에서 Status가 `200`인 두 번째 요청(도메인 이름 또는 `index.html`)을 선택합니다.

    <img src="/images/week10/10-3-task2-step48-cache-miss.png" alt="Network 탭 - 캐시 헤더 확인" class="guide-img-md" />

    <img src="/images/week10/10-3-task2-step48-cache-miss-headers.png" alt="Network 탭 - Response Headers 확인" class="guide-img-md" />

    <img src="/images/week10/10-3-task2-step48-cache-miss2.png" alt="Network 탭 - 캐시 헤더 상세" class="guide-img-md" />

> [!NOTE]
> `http://`로 접속한 경우 첫 번째 요청은 `307` 리다이렉트(HTTP→HTTPS)이고, 두 번째 요청이 실제 `200` 응답입니다. `https://`로 직접 접속한 경우에는 `200` 응답만 표시됩니다.
> 도메인 루트(`https://d1234abcd.cloudfront.net/`)로 접속한 경우 요청 이름이 `index.html`이 아닌 도메인 전체 경로로 표시됩니다.

49. **Headers** 섹션에서 **Response Headers**를 확인합니다.
50. `x-cache` 헤더를 찾습니다.

> [!NOTE]
> 첫 요청에서 `Miss from cloudfront`가 아닌 `Hit from cloudfront`가 표시될 수 있습니다. 이는 다른 사용자가 동일 엣지 로케이션에서 이미 해당 콘텐츠를 요청하여 캐시에 저장된 경우입니다. 이것은 정상 동작입니다.
>
> <img src="/images/week10/10-3-task2-step50-cache-hit.png" alt="x-cache 헤더 확인" class="guide-img-sm" />

> [!CONCEPT] Amazon CloudFront 캐시 헤더
>
> - **x-cache: Miss from cloudfront** - 오리진에서 가져옴 (첫 요청)
> - **x-cache: Hit from cloudfront** - 엣지에서 캐시 제공 (이후 요청)
> - **x-amz-cf-pop** - 요청을 처리한 엣지 로케이션 (예: ICN54-C1은 서울)
> - **age** - 캐시된 시간 (초 단위)

51. 페이지를 다시 새로고침합니다.
52. `x-cache` 헤더가 `Hit from cloudfront`로 변경되었는지 확인합니다.
53. `age` 헤더 값이 증가하는 것을 확인합니다.

    <img src="/images/week10/10-3-task2-step53-cache-hit.png" alt="x-cache Hit 및 age 헤더 확인" class="guide-img-md" />

54. 주소창에 `http://` + 복사한 도메인을 입력합니다.

> [!NOTE]
> 예: `http://d1234abcd.cloudfront.net`

55. 자동으로 `https://`로 리다이렉트되는지 확인합니다.
56. **Network** 탭에서 `3xx` 리다이렉트 응답을 확인합니다.

    <img src="/images/week10/10-3-task2-step56-invalidation.png" alt="Network 탭 - 3xx 리다이렉트 응답 확인" class="guide-img-md" />

> [!NOTE]
> Amazon CloudFront 권장 설정은 기본적으로 HTTP를 HTTPS로 리다이렉트합니다. 모든 HTTP 요청은 자동으로 HTTPS로 리다이렉트됩니다. 리다이렉트 상태 코드는 `301`, `302`, `307` 등 3xx 응답으로 표시됩니다.

✅ **태스크 완료**: Amazon CloudFront 캐싱 및 HTTPS 리다이렉트가 정상적으로 동작합니다.

## 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화

이 태스크에서는 QuickTable 콘텐츠를 업데이트하고 캐시된 콘텐츠를 강제로 갱신하는 방법을 학습합니다.

57. 텍스트 에디터에서 `index.html` 파일을 엽니다.
58. `<p class="version">Version: 1.0</p>` 부분을 `<p class="version">Version: 2.0</p>`으로 변경합니다.
59. 파일을 저장합니다.
60. Amazon S3 콘솔에서 버킷을 선택합니다.
61. [[Upload]] 버튼을 클릭합니다.
62. 수정한 `index.html` 파일을 선택합니다.

    <img src="/images/week10/10-3-task4-step62-upload.png" alt="S3 파일 업로드 선택" class="guide-img-md" />

> [!NOTE]
> 동일한 파일명으로 업로드하면 기존 파일을 덮어씁니다. Amazon S3는 자동으로 버전 관리를 하지 않으므로 이전 버전은 삭제됩니다.

63. [[Upload]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task4-step63-upload-complete.png" alt="S3 파일 업로드 완료" class="guide-img-md" />

64. Amazon CloudFront 도메인으로 다시 접속합니다.

    <img src="/images/week10/10-3-task4-step64-stale-cache.png" alt="CloudFront 캐시된 이전 버전 표시" class="guide-img-md" />

> [!NOTE]
> 여전히 이전 버전이 표시됩니다. 권장 캐시 설정의 기본 TTL 동안 Amazon CloudFront는 캐시된 콘텐츠를 제공합니다. Amazon S3에 새 파일을 업로드해도 TTL이 만료되기 전까지는 이전 버전이 제공됩니다. 이것이 캐시 무효화가 필요한 이유입니다.

> [!CONCEPT] 캐시 무효화 (Invalidation)
> 캐시된 콘텐츠를 즉시 갱신하려면 무효화를 생성해야 합니다.
> 무효화는 모든 엣지 로케이션의 캐시를 제거하여 다음 요청 시 오리진에서 새 콘텐츠를 가져오도록 합니다.

65. Amazon CloudFront 콘솔에서 배포를 선택합니다.
66. **Invalidations** 탭을 선택합니다.
67. [[Create invalidation]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task4-step67-create-invalidation.png" alt="CloudFront Create invalidation 클릭" class="guide-img-md" />

68. **Object paths**에 `/index.html`을 입력합니다.

> [!NOTE]
> 모든 파일을 무효화하려면 `/*`를 입력합니다. 매월 처음 1,000개 경로는 무료이며, 이후 경로당 $0.005가 부과됩니다.

69. [[Create invalidation]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task4-step69-invalidation-path.png" alt="Invalidation 경로 입력 및 생성" class="guide-img-md" />

    <img src="/images/week10/10-3-task4-step69-invalidation-complete.png" alt="Invalidation 완료 상태" class="guide-img-md" />

> [!NOTE]
> 무효화는 1-2분 소요됩니다. 상태가 `Completed`가 될 때까지 기다립니다.

70. 브라우저 개발자 도구(F12)에서 **Network** 탭을 선택합니다.
71. **Disable cache** 체크박스가 활성화되어 있는지 확인합니다.
72. 강력 새로고침을 수행합니다 (Ctrl+Shift+R 또는 Cmd+Shift+R).
73. 첫 번째 요청(도메인 이름 또는 `index.html`)을 선택합니다.
74. `x-cache` 헤더가 `Miss from cloudfront`로 표시되는지 확인합니다.

    <img src="/images/week10/10-3-task4-step74-cache-miss-after-invalidation.png" alt="무효화 후 x-cache Miss from cloudfront 확인" class="guide-img-md" />

> [!NOTE]
> 무효화 직후 첫 요청은 반드시 `Miss from cloudfront`여야 합니다. 이는 캐시가 제거되어 오리진에서 새 콘텐츠를 가져오는 것을 의미합니다.

> [!OUTPUT]
> 변경된 버전 "Version: 2.0"이 표시됩니다.

75. 페이지를 다시 새로고침합니다.
76. `x-cache` 헤더가 `Hit from cloudfront`로 변경되는지 확인합니다.

    <img src="/images/week10/10-3-task4-step76-cache-hit-after-invalidation.png" alt="무효화 후 x-cache Hit from cloudfront 확인" class="guide-img-md" />

✅ **태스크 완료**: 캐시 무효화를 통해 QuickTable 콘텐츠를 갱신했습니다.

## 태스크 5: Amazon CloudFront Functions로 URL 리다이렉트

이 태스크에서는 Amazon CloudFront Functions를 사용하여 엣지 로케이션에서 URL 리다이렉트를 처리하는 함수를 생성합니다. Amazon CloudFront Functions는 뷰어 요청/응답 시점에 경량 JavaScript 코드를 실행하여 헤더 조작, URL 리다이렉트, 요청 인증 등을 수행할 수 있습니다.

77. Amazon CloudFront 콘솔의 왼쪽 메뉴에서 **Functions**를 선택합니다.
78. [[Create function]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step78-functions.png" alt="CloudFront Functions - Create function 클릭" class="guide-img-md" />

79. **Name**에 `quicktable-redirect`를 입력합니다.
80. **Description**에 `Redirect /old to /about.html`을 입력합니다.
81. **Runtime**에서 `cloudfront-js-2.0`을 선택합니다.

> [!CONCEPT] Amazon CloudFront Functions 런타임
> Amazon CloudFront Functions는 두 가지 JavaScript 런타임을 지원합니다.
>
> - **cloudfront-js-1.0**: ECMAScript 5.1 호환 (레거시)
> - **cloudfront-js-2.0**: async/await 등 최신 JavaScript 지원 (권장)

82. [[Create function]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step82-function-code.png" alt="CloudFront Function 생성 완료" class="guide-img-md" />

83. **Build** 탭의 **Function code** 섹션에서 기본 코드를 삭제하고 다음 코드를 붙여넣습니다:

```javascript
/**
 * CloudFront Functions - URL 리다이렉트 핸들러
 *
 * 이벤트 타입: Viewer Request
 * 동작: /old 경로 요청을 /about.html로 302 리다이렉트
 * 그 외 경로는 오리진(S3)으로 정상 전달
 */
function handler(event) {
  // 뷰어 요청 객체에서 URI 추출
  var request = event.request;
  var uri = request.uri;

  // /old 경로 → /about.html 리다이렉트
  if (uri === '/old') {
    // 오리진에 요청을 보내지 않고 엣지에서 직접 응답 생성
    return {
      statusCode: 302,
      statusDescription: 'Found',
      headers: {
        // 리다이렉트 대상 URL
        location: { value: '/about.html' },
        // 커스텀 헤더 (CloudFront Functions 응답임을 식별)
        'cloudfront-functions': { value: 'quicktable-redirect' },
      },
    };
  }

  // 리다이렉트 대상이 아닌 요청은 그대로 오리진으로 전달
  return request;
}
```

> [!CONCEPT] Amazon CloudFront Functions 동작 방식
> Amazon CloudFront Functions는 뷰어 요청(Viewer Request) 또는 뷰어 응답(Viewer Response) 이벤트에서 실행됩니다.
> 위 코드는 `/old` 경로로 들어오는 요청을 `/about.html`로 302 리다이렉트합니다.
> 리다이렉트가 아닌 일반 요청은 그대로 오리진으로 전달됩니다.

84. [[Save changes]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step84-save-changes.png" alt="CloudFront Function 코드 저장" class="guide-img-md" />

    <img src="/images/week10/10-3-task5-step84-function-saved.png" alt="CloudFront Function 저장 완료" class="guide-img-md" />

### 함수 테스트

85. **Test** 탭을 선택합니다.
86. **Event type**에서 `Viewer request`가 선택되어 있는지 확인합니다.
87. **Stage**에서 `Development`가 선택되어 있는지 확인합니다.
88. **Request** 섹션에서 **URL path**를 `/old`로 변경합니다.
89. [[Test function]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step89-test-function.png" alt="CloudFront Function 테스트 실행" class="guide-img-md" />

90. **Output** 섹션에서 결과를 확인합니다:
    - **Status code**: `302`
    - **Location** 헤더: `/about.html`
    - **cloudfront-functions** 헤더: `quicktable-redirect`

    <img src="/images/week10/10-3-task5-step90-test-result.png" alt="CloudFront Function 테스트 결과 - 302 리다이렉트" class="guide-img-md" />

> [!NOTE]
> Compute utilization 값이 표시됩니다. 이 값이 100에 가까우면 함수가 시간 제한에 근접한 것입니다. 일반적으로 30 이하면 충분한 여유가 있습니다.

91. **URL path**를 `/index.html`로 변경합니다.

    <img src="/images/week10/10-3-task5-step91-test-no-redirect.png" alt="URL path를 /index.html로 변경" class="guide-img-md" />

92. [[Test function]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step92-test-result-pass.png" alt="CloudFront Function 테스트 결과 - 정상 통과" class="guide-img-md" />

> [!OUTPUT]
> 리다이렉트 없이 원래 요청이 그대로 반환됩니다. Output에 `"uri": "/index.html"`이 표시되고, Status가 `Succeeded`로 나오면 정상입니다.

> [!TIP]
> `/old` 경로만 리다이렉트되고 다른 경로는 정상 처리되는 것을 테스트로 확인했습니다. Publish 전에 테스트하면 잘못된 함수가 프로덕션에 배포되는 것을 방지할 수 있습니다.

### 함수 배포 및 연결

93. **Publish** 탭을 선택합니다.

    <img src="/images/week10/10-3-task5-step93-publish-tab.png" alt="CloudFront Function Publish 탭 선택" class="guide-img-md" />

94. [[Publish function]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step94-publish-function.png" alt="CloudFront Function Publish 완료" class="guide-img-md" />

> [!IMPORTANT]
> 함수를 배포에 연결하려면 반드시 먼저 Publish해야 합니다. Development 상태에서는 연결할 수 없습니다.

95. **Publish** 탭 하단의 **Associated distributions** 섹션에서 [[Add association]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step95-add-association.png" alt="Associated distributions - Add association 클릭" class="guide-img-md" />

96. **Distribution**에서 태스크 2에서 생성한 배포를 선택합니다.
97. **Event type**에서 `Viewer request`를 선택합니다.
98. **Cache behavior**에서 `Default (*)`를 선택합니다.
99. [[Add association]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-task5-step99-association-complete.png" alt="Function association 설정 완료" class="guide-img-sm" />

    <img src="/images/week10/10-3-task5-step99-association-added.png" alt="Function association 추가 확인" class="guide-img-md" />

> [!NOTE]
> 함수 연결 후 배포가 업데이트됩니다. 상태가 "Deployed"가 될 때까지 잠시 기다립니다.

100. 브라우저에서 `https://` + Amazon CloudFront 도메인 + `/old`를 입력합니다.

> [!NOTE]
> 예: `https://d1234abcd.cloudfront.net/old`

101. QuickTable 소개 페이지(`about.html`)로 리다이렉트되는지 확인합니다.
102. 브라우저 개발자 도구(F12)의 **Network** 탭에서 `/old` 요청을 선택합니다.

     <img src="/images/week10/10-3-task5-step102-redirect-test.png" alt="Network 탭 - /old 리다이렉트 요청 확인" class="guide-img-md" />

103. **Response Headers**에서 `302 Found` 상태 코드를 확인합니다.
104. `cloudfront-functions: quicktable-redirect` 커스텀 헤더를 확인합니다.
105. `x-cache: FunctionGeneratedResponse from cloudfront` 헤더를 확인합니다.

> [!CONCEPT] FunctionGeneratedResponse
> `x-cache` 헤더가 `FunctionGeneratedResponse from cloudfront`로 표시되면 응답이 오리진이 아닌 Amazon CloudFront Functions에서 직접 생성된 것입니다. 오리진에 요청을 보내지 않으므로 지연 시간이 매우 짧습니다.

### 성능 비교: Amazon CloudFront Functions vs 오리진 응답

106. **Network** 탭에서 `/old` 요청의 **Time** 열을 확인합니다.

     <img src="/images/week10/10-3-task5-step106-timing-redirect.png" alt="Network 탭 - /old 요청 응답 시간 확인" class="guide-img-md" />

> [!NOTE]
> Time 열이 보이지 않으면 Network 탭의 열 헤더를 우클릭하여 **Time**을 활성화합니다.

107. `/about.html` 요청의 **Time** 열을 확인하고 `/old` 요청과의 차이를 확인합니다.

     <img src="/images/week10/10-3-task5-step107-timing-origin.png" alt="Network 탭 - /about.html 요청 응답 시간 비교" class="guide-img-md" />

> [!CONCEPT] Amazon CloudFront Functions 성능 이점
> `/old` 요청은 Amazon CloudFront Functions가 엣지 로케이션에서 직접 302 응답을 생성합니다. 오리진(Amazon S3)에 요청을 보내지 않으므로 응답 시간이 매우 짧습니다.
>
> | 요청                      | 처리 위치                          | x-cache 헤더              | 응답 시간       |
> | ------------------------- | ---------------------------------- | ------------------------- | --------------- |
> | `/old`                    | 엣지 (Amazon CloudFront Functions) | FunctionGeneratedResponse | 매우 빠름       |
> | `/about.html` (첫 요청)   | 오리진 (Amazon S3)                 | Miss from cloudfront      | 상대적으로 느림 |
> | `/about.html` (이후 요청) | 엣지 (캐시)                        | Hit from cloudfront       | 빠름            |
>
> Amazon CloudFront Functions는 서브밀리초 단위로 실행되어 캐시 히트보다도 빠를 수 있습니다.

✅ **태스크 완료**: Amazon CloudFront Functions로 엣지 로케이션에서 URL 리다이렉트를 구현했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- QuickTable 프론트엔드를 Amazon S3 오리진 버킷에 업로드했습니다.
- Amazon CloudFront 배포 생성 및 OAC 자동 설정으로 전 세계 배포했습니다.
- 캐싱 동작 확인 및 응답 헤더 분석을 수행했습니다.
- 캐시 무효화를 통한 QuickTable 콘텐츠 갱신을 수행했습니다.
- Amazon CloudFront Functions로 엣지 로케이션에서 URL 리다이렉트를 구현했습니다.

Week 9-3에서 구축한 QuickTable 정적 웹사이트가 이제 Amazon CloudFront를 통해 전 세계 사용자에게 빠르게 제공됩니다. Week 10-2의 Amazon ElastiCache와 결합하여 QuickTable은 글로벌 규모의 고성능 레스토랑 예약 시스템으로 발전했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> 리소스 간 의존성이 있으므로 아래 순서대로 삭제해야 합니다.
>
> 1. Amazon CloudFront Functions association 제거 → 배포 업데이트 대기 → 함수 삭제
> 2. Amazon CloudFront 배포 Disable → 대기 → Delete
> 3. Amazon S3 버킷 Empty → Delete

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `10-3`
6. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step6-disable-distribution.png" alt="Tag Editor 리소스 검색 결과" class="guide-img-md" />

> [!OUTPUT]
> Amazon S3 버킷이 표시됩니다.

> [!NOTE]
> Amazon CloudFront 배포를 Tag Editor로 찾으려면 **Regions**에서 `us-east-1 (버지니아 북부)`를 선택하거나 `All regions`를 선택합니다. Amazon CloudFront는 글로벌 서비스로 us-east-1에 등록됩니다. ap-northeast-2만 선택하면 Amazon CloudFront가 표시되지 않습니다.
>
> Amazon CloudFront Functions는 태그를 지원하지 않으므로 Tag Editor에 표시되지 않습니다. 단계 2에서 별도로 삭제해야 합니다.
>
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Amazon CloudFront Functions, Amazon CloudFront 배포, Amazon S3 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. CloudShell에서 Amazon CloudFront 배포 ID를 확인합니다:

```bash
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='quicktable-cloudfront' || contains(DomainName, 'cloudfront.net')].Id | [0]" --output text)
echo "Distribution ID: $DISTRIBUTION_ID"
```

<img src="/images/week10/10-3-cleanup-step7-disable.png" alt="CloudShell 배포 ID 확인 결과" class="guide-img-md" />

> [!NOTE]
> `DISTRIBUTION_ID`가 `None`으로 출력되면 Amazon CloudFront 콘솔에서 배포 ID를 직접 확인하여 입력합니다:
>
> ```bash
> DISTRIBUTION_ID=<your-distribution-id>
> ```

8. 배포의 현재 설정을 가져옵니다:

```bash
aws cloudfront get-distribution-config --id $DISTRIBUTION_ID --output json > /tmp/cf-config.json
ETAG=$(cat /tmp/cf-config.json | jq -r '.ETag')
echo "ETag: $ETAG"
```

<img src="/images/week10/10-3-cleanup-step8-delete.png" alt="배포 설정 및 ETag 확인 결과" class="guide-img-md" />

> [!NOTE]
> `ETag` 값이 출력되면 설정을 정상적으로 가져온 것입니다. 출력이 없거나 오류가 발생하면 `DISTRIBUTION_ID`가 올바른지 확인합니다.

9. Amazon CloudFront Functions association을 제거하고 배포를 업데이트합니다:

```bash
cat /tmp/cf-config.json | jq '.DistributionConfig.DefaultCacheBehavior.FunctionAssociations = {"Quantity": 0, "Items": []}' | jq '.DistributionConfig' > /tmp/cf-update.json
aws cloudfront update-distribution --id $DISTRIBUTION_ID --if-match $ETAG --distribution-config file:///tmp/cf-update.json
```

<img src="/images/week10/10-3-cleanup-step9-remove-association.png" alt="Function association 제거 명령 실행" class="guide-img-md" />

<img src="/images/week10/10-3-cleanup-step9-update-distribution.png" alt="배포 업데이트 결과" class="guide-img-sm" />

> [!NOTE]
> 배포 업데이트에 5-10분이 소요됩니다. 상태를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.Status" --output text
> ```
>
> `Deployed`가 출력되면 업데이트 완료입니다.
>
> <img src="/images/week10/10-3-cleanup-step9-deployed.png" alt="배포 상태 Deployed 확인" class="guide-img-md" />

10. Amazon CloudFront Functions를 삭제합니다:

```bash
FUNCTION_ETAG=$(aws cloudfront describe-function --name quicktable-redirect --query "ETag" --output text)
aws cloudfront delete-function --name quicktable-redirect --if-match $FUNCTION_ETAG
```

<img src="/images/week10/10-3-cleanup-step10-delete-function.png" alt="CloudFront Function 삭제 실행" class="guide-img-md" />

> [!NOTE]
> 삭제가 성공하면 출력이 없습니다. 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws cloudfront describe-function --name quicktable-redirect 2>&1 || echo "삭제 완료"
> ```
>
> `NoSuchFunctionExists` 오류가 나오면 삭제 완료입니다.

11. 배포를 비활성화합니다:

```bash
ETAG=$(aws cloudfront get-distribution-config --id $DISTRIBUTION_ID --query "ETag" --output text)
aws cloudfront get-distribution-config --id $DISTRIBUTION_ID --query "DistributionConfig" --output json | jq '.Enabled = false' > /tmp/cf-disable.json
aws cloudfront update-distribution --id $DISTRIBUTION_ID --if-match $ETAG --distribution-config file:///tmp/cf-disable.json
```

<img src="/images/week10/10-3-cleanup-step11-disable-distribution.png" alt="배포 비활성화 명령 실행" class="guide-img-md" />

> [!NOTE]
> 배포 비활성화에 5-15분이 소요됩니다. 상태를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.Status" --output text
> ```
>
> - `InProgress`: 비활성화 처리 중입니다. 몇 분 후 다시 실행합니다.
> - `Deployed`: 비활성화 완료입니다. 다음 단계로 진행합니다.
>
> <img src="/images/week10/10-3-cleanup-step11-deployed.png" alt="배포 비활성화 Deployed 상태 확인" class="guide-img-md" />

12. 배포를 삭제합니다:

```bash
ETAG=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "ETag" --output text)
aws cloudfront delete-distribution --id $DISTRIBUTION_ID --if-match $ETAG
```

<img src="/images/week10/10-3-cleanup-step12-delete-distribution.png" alt="배포 삭제 명령 실행" class="guide-img-md" />

> [!NOTE]
> 삭제가 성공하면 출력이 없습니다. 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws cloudfront get-distribution --id $DISTRIBUTION_ID 2>&1 || echo "삭제 완료"
> ```
>
> `NoSuchDistribution` 오류가 나오면 삭제 완료입니다.

13. Amazon S3 버킷을 비우고 삭제합니다:

```bash
BUCKET_NAME=<버킷이름>
```

> [!NOTE]
> `<버킷이름>`을 태스크 1에서 생성한 버킷 이름으로 변경합니다 (예: `BUCKET_NAME=quicktable-cloudfront-origin-jdoe-20240001`).

```bash
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3api delete-bucket --bucket $BUCKET_NAME --region ap-northeast-2
```

<img src="/images/week10/10-3-cleanup-step13-delete-bucket.png" alt="S3 버킷 비우기 및 삭제 실행" class="guide-img-md" />

> [!NOTE]
> 삭제를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws s3api head-bucket --bucket $BUCKET_NAME --region ap-northeast-2 2>&1 || echo "삭제 완료"
> ```
>
> `404` 또는 `NoSuchBucket` 오류가 나오면 삭제 완료입니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

14. Amazon CloudFront 콘솔의 왼쪽 메뉴에서 **Functions**를 선택합니다.
15. `quicktable-redirect` 함수 이름을 클릭하여 상세 페이지로 이동합니다.
16. **Publish** 탭을 선택합니다.
17. **Associated distributions** 섹션에서 연결된 배포의 체크박스를 선택합니다.

    <img src="/images/week10/10-3-cleanup-step17-functions-console.png" alt="Associated distributions 체크박스 선택" class="guide-img-md" />

18. [[Remove association]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step18-delete-function.png" alt="Remove association 클릭" class="guide-img-sm" />

> [!NOTE]
> Association 제거 후 배포 업데이트가 시작됩니다. Amazon CloudFront 콘솔의 **Distributions** 페이지에서 배포 상태가 `Enabled`로 돌아올 때까지 기다립니다. 배포 업데이트 중에는 함수를 삭제할 수 없습니다.

19. 배포 업데이트가 완료되면 왼쪽 메뉴에서 **Functions**를 선택하여 목록으로 돌아갑니다.
20. `quicktable-redirect` 함수의 라디오 버튼을 선택합니다.
21. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step21-disable-distribution.png" alt="CloudFront Function 삭제" class="guide-img-md" />

22. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step22-confirm-delete.png" alt="Function 삭제 확인" class="guide-img-sm" />

23. 왼쪽 메뉴에서 **Distributions**를 선택합니다.
24. 배포의 체크박스를 선택합니다.
25. [[Disable]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step25-disable.png" alt="배포 Disable 클릭" class="guide-img-md" />

26. 확인 창에서 [[Disable]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step26-confirm-disable.png" alt="배포 Disable 확인" class="guide-img-sm" />

> [!NOTE]
> 배포 비활성화에 5-15분이 소요됩니다. 상태가 `Disabled`로 변경될 때까지 기다립니다. 페이지를 새로고침하여 최신 상태를 확인합니다.

27. 상태가 `Disabled`로 변경되면 배포의 체크박스를 다시 선택합니다.
28. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step28-delete-distribution.png" alt="배포 Delete 클릭" class="guide-img-md" />

29. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step29-confirm-delete.png" alt="배포 삭제 확인" class="guide-img-sm" />

> [!TROUBLESHOOTING]
> **문제**: "Distribution must be disabled before deleting" 오류 발생
>
> **원인**: 배포가 아직 비활성화 처리 중입니다. 상태가 `Disabled`로 표시되더라도 내부적으로 처리가 완료되지 않았을 수 있습니다.
>
> **해결**: 5-10분 추가 대기 후 페이지를 새로고침하고 다시 시도합니다.

30. Amazon S3 콘솔로 이동합니다.
31. 버킷을 선택합니다.
32. [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step32-empty-button.png" alt="S3 버킷 Empty 클릭" class="guide-img-md" />

33. 확인 창에서 `permanently delete`를 입력합니다.

    <img src="/images/week10/10-3-cleanup-step33-empty-bucket.png" alt="S3 버킷 비우기 확인 입력" class="guide-img-md" />

34. [[Empty]] 버튼을 클릭합니다.
35. 버킷을 다시 선택합니다.
36. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step32-empty-button.png" alt="S3 버킷 Delete 클릭" class="guide-img-md" />

37. 확인 창에서 버킷 이름을 입력합니다.
38. [[Delete bucket]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step38-delete-bucket.png" alt="S3 버킷 삭제 확인" class="guide-img-md" />

> [!NOTE]
> Amazon CloudFront 배포를 삭제해도 OAC가 추가한 Amazon S3 버킷 정책은 자동으로 제거되지 않습니다. 하지만 버킷 자체를 삭제하면 버킷 정책도 함께 삭제되므로 별도 정리가 필요 없습니다.

### 단계 3: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

39. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
40. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
41. **Regions**에서 `All regions`를 선택합니다.
42. **Resource types**에서 `All supported resource types`를 선택합니다.
43. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `10-3`
44. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week10/10-3-cleanup-step44-tageditor.png" alt="Tag Editor 최종 삭제 확인 결과" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.
> Amazon CloudFront Functions는 태그를 지원하지 않으므로 Tag Editor에 표시되지 않습니다. Amazon CloudFront 콘솔의 **Functions** 페이지에서 `quicktable-redirect` 함수가 삭제되었는지 직접 확인합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon CloudFront 개발자 가이드](https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/)
- [Amazon CloudFront Functions 가이드](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-functions.html)
- [Amazon CloudFront 가격](https://aws.amazon.com/ko/cloudfront/pricing/)

### QuickTable 시리즈 연결

- **Week 4-3**: AWS Lambda + Amazon API Gateway로 QuickTable 예약 API 구축
- **Week 9-3**: Amazon S3로 QuickTable 정적 웹사이트 호스팅
- **Week 10-2**: Amazon ElastiCache로 API 성능 최적화
- **Week 10-3**: Amazon CloudFront로 글로벌 배포 ← 현재
- **Week 13-2**: AWS X-Ray로 성능 추적
- **Week 14-2**: Amazon Bedrock Knowledge Bases로 레스토랑 메뉴 RAG
- **Week 14-3**: Amazon Bedrock Agent로 예약 챗봇 완성

## 📚 참고: Amazon CloudFront 핵심 개념

### CDN (Content Delivery Network)

Amazon CloudFront는 AWS의 글로벌 CDN 서비스입니다. 전 세계에 분산된 엣지 로케이션을 통해 사용자에게 콘텐츠를 빠르게 전달합니다.

### 아키텍처 구성 요소

**엣지 로케이션 (Edge Location)**

- 전 세계 600개 이상의 캐시 서버
- 사용자와 가장 가까운 위치에서 콘텐츠 제공
- 캐시 저장소 역할

**오리진 (Origin)**

- 원본 콘텐츠가 저장된 위치
- Amazon S3, Amazon EC2, ALB, 커스텀 HTTP 서버 지원
- 캐시 미스 시 Amazon CloudFront가 접근

**리전별 엣지 캐시 (Regional Edge Cache)**

- 엣지 로케이션과 오리진 사이의 중간 캐시
- 더 큰 캐시 용량
- 덜 자주 요청되는 콘텐츠 저장

### 캐싱 동작

**TTL (Time To Live)**

- 캐시 유효 시간 (기본값: 24시간)
- Cache-Control 헤더로 제어 가능
- 파일 유형별로 다르게 설정 권장

**캐시 키 (Cache Key)**

- URL 경로 (필수)
- 쿼리 스트링 (선택)
- 헤더 (선택)
- 쿠키 (선택)

### 보안 기능

**OAC (Origin Access Control)**

- Amazon S3 버킷을 비공개로 유지
- Amazon CloudFront만 접근 가능
- 서명된 요청 사용
- OAI의 후속 기능 (더 많은 Amazon S3 기능 지원)

**HTTPS 지원**

- Amazon CloudFront 기본 인증서 (무료)
- AWS Certificate Manager 커스텀 인증서
- HTTP를 HTTPS로 자동 리다이렉트

### 비용 최적화

**무효화 비용**

- 매월 처음 1,000개 경로: 무료
- 이후: 경로당 $0.005

**대안 방법**

- 파일명 변경: `style-v2.css` (가장 간단, 별도 설정 불필요)
- 버전 관리: `style.css?v=2` (캐시 정책에서 쿼리 스트링을 캐시 키에 포함해야 함)
- 짧은 TTL 설정

> [!NOTE]
> **쿼리 스트링 버전 관리 주의사항**:
>
> `style.css?v=2` 방식을 사용하려면 Amazon CloudFront 캐시 정책에서 쿼리 스트링을 캐시 키에 포함해야 합니다. 기본 CachingOptimized 정책은 쿼리 스트링을 무시합니다.
>
> **설정 방법**:
>
> 1. 커스텀 캐시 정책 생성
> 2. Cache key settings → Query strings → Include → "v" 추가
>
> **가장 간단한 방법**: 파일명 변경 (`style-v2.css`) → 별도 설정 없이 즉시 새 파일로 인식됩니다

**Price Class**

- All edge locations: 최고 성능, 최고 비용
- Price Class 200 — 북미, 유럽, 아시아, 중동, 아프리카: 중간 비용
- Price Class 100 — 북미, 유럽만: 최저 비용

### 엣지 컴퓨팅: Amazon CloudFront Functions vs AWS Lambda@Edge

Amazon CloudFront Functions와 AWS Lambda@Edge는 모두 Amazon CloudFront 이벤트에 응답하여 코드를 실행하는 엣지 컴퓨팅 기능입니다.

**Amazon CloudFront Functions 적합 사례**

- 캐시 키 정규화 (헤더, 쿼리 스트링 변환)
- 헤더 조작 (추가, 수정, 삭제)
- URL 리다이렉트 또는 리라이트
- 요청 인증 (JWT 토큰 검증)

**AWS Lambda@Edge 적합 사례**

- 수 밀리초 이상 소요되는 함수
- 외부 네트워크 접근이 필요한 함수
- 서드파티 라이브러리 (AWS SDK 포함) 사용
- 요청 본문 접근이 필요한 함수

| 항목           | Amazon CloudFront Functions     | AWS Lambda@Edge                 |
| -------------- | ------------------------------- | ------------------------------- |
| 언어           | JavaScript (ECMAScript 5.1+)    | Node.js, Python                 |
| 이벤트 소스    | Viewer request, Viewer response | Viewer/Origin request/response  |
| 실행 시간      | 서브밀리초                      | 최대 30초                       |
| 메모리         | 2 MB                            | 최대 10 GB                      |
| 코드 크기      | 10 KB                           | 50 MB                           |
| 네트워크 접근  | 불가                            | 가능                            |
| 요청 본문 접근 | 불가                            | 가능                            |
| 처리량         | 초당 수백만 요청                | 리전당 초당 10,000 요청         |
| 배포 리전      | 모든 엣지 로케이션              | us-east-1에서 생성, 엣지로 복제 |
