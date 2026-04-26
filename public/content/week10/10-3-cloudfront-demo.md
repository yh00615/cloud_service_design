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

이번 데모에서는 Amazon CloudFront를 사용하여 QuickTable 레스토랑 예약 시스템을 전 세계 사용자에게 빠르고 안전하게 제공하는 방법을 학습합니다. Week 9-3에서 구축한 Amazon S3 정적 웹사이트를 CloudFront를 통해 글로벌 배포하고, 캐싱과 HTTPS를 적용하여 성능과 보안을 개선합니다.

QuickTable은 전 세계 사용자가 레스토랑을 검색하고 예약할 수 있는 글로벌 서비스입니다. Amazon CloudFront CDN을 활용하면 서울, 도쿄, 뉴욕, 런던 등 전 세계 어디서나 빠른 응답 속도로 QuickTable 웹사이트에 접근할 수 있습니다. 사용자와 가장 가까운 엣지 로케이션에서 콘텐츠를 제공하여 지연 시간을 최소화하고, OAC(Origin Access Control)를 통해 Amazon S3 버킷을 안전하게 보호합니다.

> [!DOWNLOAD]
> [week10-3-cloudfront-demo.zip](/files/week10/week10-3-cloudfront-demo.zip)
>
> - `index.html` - QuickTable 메인 페이지 (레스토랑 검색 UI, Week 9-3에서 구축한 프론트엔드)
> - `about.html` - QuickTable 소개 페이지 (서비스 설명, 글로벌 아키텍처)
> - `style.css` - QuickTable 스타일시트 (캐싱 테스트용, 버전 관리 예시)
> - `script.js` - QuickTable 인터랙티브 기능 (Week 4-3 API 호출, 캐싱 테스트, 지역별 레스토랑 필터링)
>
> **관련 태스크:**
>
> - 태스크 1: Amazon S3 오리진 준비 (QuickTable 프론트엔드 파일 업로드)
> - 태스크 2: Amazon CloudFront 배포 생성 (4단계 위자드, OAC 자동 설정)
> - 태스크 3: 배포 테스트 및 캐싱 확인 (엣지 로케이션 성능 측정)
> - 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화 (버전 관리 전략)
> - 태스크 5: CloudFront Functions로 URL 리다이렉트 (엣지 컴퓨팅)

> [!NOTE]
> 이 데모는 비용이 거의 발생하지 않습니다. Amazon CloudFront 프리 티어에서 매월 1TB 데이터 전송과 10,000,000건의 요청을 무료로 제공합니다.

## 태스크 1: QuickTable 프론트엔드 Amazon S3 오리진 준비

이 태스크에서는 CloudFront의 오리진으로 사용할 Amazon S3 버킷을 생성하고 QuickTable 프론트엔드 콘텐츠를 업로드합니다. `about.html` 파일은 QuickTable 서비스 소개 페이지로, 글로벌 아키텍처와 서비스 특징을 설명합니다. 이 파일을 통해 CloudFront의 다중 경로 라우팅 기능을 테스트할 수 있습니다.

1. 다운로드한 `week10-3-cloudfront-demo.zip` 파일의 압축을 해제합니다.
2. AWS Management Console에 로그인한 후 상단 검색창에 `S3`을 입력하고 선택합니다.
3. [[Create bucket]] 버튼을 클릭합니다.
4. **Bucket name**에 `quicktable-cloudfront-origin-YOUR-INITIALS-12345`를 입력합니다.

> [!TIP]
> 버킷 이름은 전 세계적으로 고유해야 합니다. `YOUR-INITIALS`를 본인의 이니셜로, `12345`를 랜덤 숫자로 변경합니다 (예: `quicktable-cloudfront-origin-jdoe-98765`).

5. **Region**에서 `Asia Pacific (Seoul) ap-northeast-2`를 선택합니다.
6. **Block Public Access settings**는 모두 체크된 상태로 유지합니다.

> [!CONCEPT] Amazon S3 퍼블릭 액세스 차단 (S3 Block Public Access)
> Amazon CloudFront는 OAC(Origin Access Control)를 통해 비공개 Amazon S3 버킷에 접근합니다.
> 따라서 버킷을 퍼블릭으로 만들 필요가 없으며, 보안을 유지할 수 있습니다.

7. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-3`    |
| `CreatedBy` | `Student` |

8. [[Create bucket]] 버튼을 클릭합니다.
9. 생성된 버킷을 선택합니다.
10. [[Upload]] 버튼을 클릭합니다.
11. [[Add files]] 버튼을 클릭합니다.
12. 압축 해제한 폴더에서 `index.html`, `about.html`, `style.css`, `script.js` 파일을 선택합니다.
13. [[Upload]] 버튼을 클릭합니다.

> [!NOTE]
> QuickTable 프론트엔드는 Week 9-3에서 구축한 정적 웹사이트를 기반으로 합니다. 레스토랑 검색, 예약 가능 시간대 조회 등의 기능이 포함되어 있습니다.

✅ **태스크 완료**: QuickTable 프론트엔드 Amazon S3 오리진 버킷이 준비되었습니다.

## 태스크 2: QuickTable Amazon CloudFront 배포 생성

이 태스크에서는 Amazon S3 버킷을 오리진으로 하는 Amazon CloudFront 배포를 생성하여 QuickTable을 전 세계에 배포합니다. CloudFront 배포 생성은 5단계 위자드로 진행됩니다.

14. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFront`을 입력하고 선택합니다.
15. [[Create distribution]] 버튼을 클릭합니다.

> [!NOTE]
> CloudFront 콘솔에 "Flat-rate security and delivery plans" 배너가 표시될 수 있습니다. 이 실습에서는 사용량 기반(pay-as-you-go) 배포를 사용하므로 배너를 닫고 [[Create distribution]] 버튼을 클릭합니다. "Create a flat-rate distribution"은 선택하지 않습니다.

### Step 1: Get started

16. **Distribution name**에 `quicktable-cloudfront`를 입력합니다.
17. **Distribution type**에서 `Single website or app`을 선택합니다.
18. **Route 53 managed domain** 필드는 비워둡니다.
19. **Tags - optional** 섹션에서 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-3`    |
| `CreatedBy` | `Student` |

20. [[Next]] 버튼을 클릭합니다.

### Step 2: Specify origin

21. **Origin type**에서 `Amazon S3`를 선택합니다.

> [!CONCEPT] Amazon CloudFront 오리진 (CloudFront Origin)
> 오리진은 원본 콘텐츠가 저장된 위치입니다. Amazon S3, Elastic Load Balancer, API Gateway, VPC origin 또는 커스텀 HTTP 서버를 사용할 수 있습니다.
> Amazon CloudFront는 캐시 미스가 발생하면 오리진에서 콘텐츠를 가져옵니다.

22. **S3 origin**에서 태스크 1에서 생성한 Amazon S3 버킷을 선택합니다.
23. **Allow private S3 bucket access to CloudFront** 체크박스를 확인합니다.

> [!CONCEPT] OAC (Origin Access Control)
> "Allow private S3 bucket access to CloudFront"를 활성화하면 CloudFront가 자동으로 OAC를 생성하고 Amazon S3 버킷 정책을 업데이트합니다.
> Amazon S3 버킷을 비공개로 유지하면서 CloudFront만 접근할 수 있도록 하는 보안 기능입니다.

24. **Origin settings**에서 `Use recommended origin settings`를 선택합니다.
25. **Cache settings**에서 `Use recommended cache settings tailored to serving S3 content`를 선택합니다.

> [!CONCEPT] Amazon CloudFront 캐시 정책 (Amazon CloudFront Cache Policy)
> 권장 캐시 설정은 Amazon S3 정적 콘텐츠에 최적화된 캐싱을 자동으로 적용합니다.
>
> - **CachingOptimized**: 정적 콘텐츠에 최적화, 최대 캐싱
> - **CachingDisabled**: 동적 콘텐츠용, 캐싱 안 함
> - **Custom**: 사용자 정의 TTL 및 캐시 키 설정
>
> 배포 생성 후 **Behaviors** 탭에서 캐시 정책, Viewer protocol policy, Allowed HTTP methods 등을 커스터마이즈할 수 있습니다.

26. [[Next]] 버튼을 클릭합니다.

### Step 3: Enable security

27. **Web Application Firewall (WAF)** 에서 `Do not enable security protections`를 선택합니다.

> [!NOTE]
> WAF를 활성화하면 추가 비용이 발생합니다. 이 데모에서는 비용 절감을 위해 비활성화합니다. 프로덕션 환경에서는 WAF 활성화를 권장합니다. WAF에 대한 자세한 내용은 Week 12-3에서 학습합니다.

28. [[Next]] 버튼을 클릭합니다.

### Step 4: Get TLS certificate

> [!NOTE]
> 이 실습에서는 커스텀 도메인을 사용하지 않으므로 기본 설정을 유지합니다. 커스텀 도메인을 사용하는 경우 이 단계에서 AWS Certificate Manager(ACM)를 통해 TLS 인증서를 프로비저닝할 수 있습니다. 이 실습에서는 CloudFront 기본 도메인(`d1234abcd.cloudfront.net`)을 사용하므로 별도 설정이 필요 없습니다.

29. [[Next]] 버튼을 클릭합니다.

### Step 5: Review and create

30. **General configuration**, **Origin**, **Cache settings**, **Security** 설정을 검토합니다.
31. **Grant CloudFront access to origin**이 `Yes`로 표시되는지 확인합니다.
32. [[Create distribution]] 버튼을 클릭합니다.

> [!NOTE]
> CloudFront가 자동으로 Amazon S3 버킷 정책을 업데이트하여 OAC 접근을 허용합니다. 별도로 버킷 정책을 수동 설정할 필요가 없습니다.
> 배포 생성에 5-15분이 소요됩니다. 상태가 "Deploying"에서 "Enabled"로 변경될 때까지 기다립니다. 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다. 페이지를 새로고침하여 최신 상태를 확인합니다.

✅ **태스크 완료**: Amazon CloudFront 배포가 생성되고 Amazon S3 버킷 정책이 자동으로 업데이트되었습니다.

## 태스크 3: 배포 테스트 및 캐싱 확인

이 태스크에서는 CloudFront를 통해 콘텐츠에 접근하고 캐싱 동작을 확인합니다.

33. **Distribution domain name**을 복사합니다.

> [!NOTE]
> 배포 상태가 `Enabled`인지 확인합니다. 도메인 이름은 `d1234abcd.cloudfront.net` 형식입니다.

34. 새 브라우저 탭을 엽니다.
35. 주소창에 복사한 도메인을 붙여넣고 Enter를 누릅니다.

> [!OUTPUT]
> QuickTable 웹사이트가 정상적으로 로드됩니다. 레스토랑 검색 UI와 메인 페이지가 표시되면 CloudFront를 통한 콘텐츠 제공이 정상 동작하는 것입니다.

> [!CONCEPT] 엣지 로케이션 (Edge Location)
> Amazon CloudFront는 전 세계 400개 이상의 엣지 로케이션에서 콘텐츠를 캐싱합니다.
> 사용자는 가장 가까운 엣지 로케이션에서 콘텐츠를 받아 빠른 속도를 경험합니다.

36. 브라우저 개발자 도구를 엽니다 (F12 키).
37. **Network** 탭을 선택합니다.
38. **Disable cache** 체크박스를 체크합니다.

> [!IMPORTANT]
> 브라우저 캐시를 비활성화하지 않으면 CloudFront 캐시 헤더를 정확히 확인할 수 없습니다. 브라우저가 로컬 캐시를 사용하여 CloudFront에 요청을 보내지 않을 수 있습니다.

39. 페이지를 새로고침합니다 (Ctrl+R 또는 Cmd+R).
40. `index.html` 요청을 선택합니다.
41. **Headers** 섹션에서 **Response Headers**를 확인합니다.
42. `x-cache` 헤더를 찾습니다.

> [!NOTE]
> 첫 요청에서 `Miss from cloudfront`가 아닌 `Hit from cloudfront`가 표시될 수 있습니다. 이는 다른 사용자가 동일 엣지 로케이션에서 이미 해당 콘텐츠를 요청하여 캐시에 저장된 경우입니다. 이것은 정상 동작입니다.

> [!CONCEPT] Amazon CloudFront 캐시 헤더
>
> - **x-cache: Miss from cloudfront** - 오리진에서 가져옴 (첫 요청)
> - **x-cache: Hit from cloudfront** - 엣지에서 캐시 제공 (이후 요청)
> - **x-amz-cf-pop** - 요청을 처리한 엣지 로케이션 (예: ICN54-C1은 서울)
> - **age** - 캐시된 시간 (초 단위)

43. 페이지를 다시 새로고침합니다.
44. `x-cache` 헤더가 `Hit from cloudfront`로 변경되었는지 확인합니다.
45. `age` 헤더 값이 증가하는 것을 확인합니다.
46. 주소창에 `http://` + 복사한 도메인을 입력합니다.

> [!NOTE]
> 예: `http://d1234abcd.cloudfront.net`

47. 자동으로 `https://`로 리다이렉트되는지 확인합니다.
48. **Network** 탭에서 301 또는 302 리다이렉트 응답을 확인합니다.

> [!NOTE]
> CloudFront 권장 설정은 기본적으로 HTTP를 HTTPS로 리다이렉트합니다. 모든 HTTP 요청은 자동으로 HTTPS로 리다이렉트됩니다.

✅ **태스크 완료**: Amazon CloudFront 캐싱 및 HTTPS 리다이렉트가 정상적으로 동작합니다.

## 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화

이 태스크에서는 QuickTable 콘텐츠를 업데이트하고 캐시된 콘텐츠를 강제로 갱신하는 방법을 학습합니다.

49. 텍스트 에디터에서 `index.html` 파일을 엽니다.
50. 제목을 "QuickTable v2.0 - 더 빠른 예약 경험"으로 변경합니다.
51. 파일을 저장합니다.
52. Amazon S3 콘솔에서 버킷을 선택합니다.
53. [[Upload]] 버튼을 클릭합니다.
54. 수정한 `index.html` 파일을 선택합니다.

> [!NOTE]
> 동일한 파일명으로 업로드하면 기존 파일을 덮어씁니다. Amazon S3는 자동으로 버전 관리를 하지 않으므로 이전 버전은 삭제됩니다.

55. [[Upload]] 버튼을 클릭합니다.
56. Amazon CloudFront 도메인으로 다시 접속합니다.

> [!NOTE]
> 여전히 이전 버전이 표시됩니다. 권장 캐시 설정의 기본 TTL 동안 CloudFront는 캐시된 콘텐츠를 제공합니다. Amazon S3에 새 파일을 업로드해도 TTL이 만료되기 전까지는 이전 버전이 제공됩니다. 이것이 캐시 무효화가 필요한 이유입니다.

> [!CONCEPT] 캐시 무효화 (Invalidation)
> 캐시된 콘텐츠를 즉시 갱신하려면 무효화를 생성해야 합니다.
> 무효화는 모든 엣지 로케이션의 캐시를 제거하여 다음 요청 시 오리진에서 새 콘텐츠를 가져오도록 합니다.

57. Amazon CloudFront 콘솔에서 배포를 선택합니다.
58. **Invalidations** 탭을 선택합니다.
59. [[Create invalidation]] 버튼을 클릭합니다.
60. **Object paths**에 `/index.html`을 입력합니다.

> [!NOTE]
> 모든 파일을 무효화하려면 `/*`를 입력합니다. 매월 처음 1,000개 경로는 무료이며, 이후 경로당 $0.005가 부과됩니다.

61. [[Create invalidation]] 버튼을 클릭합니다.

> [!NOTE]
> 무효화는 1-2분 소요됩니다. 상태가 `Completed`가 될 때까지 기다립니다.

62. 브라우저 개발자 도구(F12)에서 **Network** 탭을 선택합니다.
63. **Disable cache** 체크박스가 활성화되어 있는지 확인합니다.
64. 강력 새로고침을 수행합니다 (Ctrl+Shift+R 또는 Cmd+Shift+R).
65. `index.html` 요청을 선택합니다.
66. `x-cache` 헤더가 `Miss from cloudfront`로 표시되는지 확인합니다.

> [!NOTE]
> 무효화 직후 첫 요청은 반드시 `Miss from cloudfront`여야 합니다. 이는 캐시가 제거되어 오리진에서 새 콘텐츠를 가져오는 것을 의미합니다.

> [!OUTPUT]
> 변경된 제목 "QuickTable v2.0 - 더 빠른 예약 경험"이 표시됩니다.

67. 페이지를 다시 새로고침합니다.
68. `x-cache` 헤더가 `Hit from cloudfront`로 변경되는지 확인합니다.

✅ **태스크 완료**: 캐시 무효화를 통해 QuickTable 콘텐츠를 갱신했습니다.

## 태스크 5: CloudFront Functions로 URL 리다이렉트

이 태스크에서는 CloudFront Functions를 사용하여 엣지 로케이션에서 URL 리다이렉트를 처리하는 함수를 생성합니다. CloudFront Functions는 뷰어 요청/응답 시점에 경량 JavaScript 코드를 실행하여 헤더 조작, URL 리다이렉트, 요청 인증 등을 수행할 수 있습니다.

69. Amazon CloudFront 콘솔의 왼쪽 메뉴에서 **Functions**를 선택합니다.
70. [[Create function]] 버튼을 클릭합니다.
71. **Name**에 `quicktable-redirect`를 입력합니다.
72. **Description**에 `Redirect /old to /about.html`을 입력합니다.
73. **Runtime**에서 `cloudfront-js-2.0`을 선택합니다.

> [!CONCEPT] CloudFront Functions 런타임
> CloudFront Functions는 두 가지 JavaScript 런타임을 지원합니다.
>
> - **cloudfront-js-1.0**: ECMAScript 5.1 호환 (레거시)
> - **cloudfront-js-2.0**: async/await 등 최신 JavaScript 지원 (권장)

74. [[Create function]] 버튼을 클릭합니다.
75. **Function code** 섹션에서 기본 코드를 삭제하고 다음 코드를 붙여넣습니다:

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
                'location': { value: '/about.html' },
                // 커스텀 헤더 (CloudFront Functions 응답임을 식별)
                'cloudfront-functions': { value: 'quicktable-redirect' }
            }
        };
    }

    // 리다이렉트 대상이 아닌 요청은 그대로 오리진으로 전달
    return request;
}
```

> [!CONCEPT] CloudFront Functions 동작 방식
> CloudFront Functions는 뷰어 요청(Viewer Request) 또는 뷰어 응답(Viewer Response) 이벤트에서 실행됩니다.
> 위 코드는 `/old` 경로로 들어오는 요청을 `/about.html`로 302 리다이렉트합니다.
> 리다이렉트가 아닌 일반 요청은 그대로 오리진으로 전달됩니다.

76. [[Save changes]] 버튼을 클릭합니다.

### 함수 테스트

77. **Test** 탭을 선택합니다.
78. **Event type**에서 `Viewer request`를 선택합니다.
79. **Request** 섹션에서 **URL path**를 `/old`로 변경합니다.
80. [[Test function]] 버튼을 클릭합니다.
81. **Output** 섹션에서 결과를 확인합니다:
    - **Status code**: `302`
    - **Location** 헤더: `/about.html`
    - **cloudfront-functions** 헤더: `quicktable-redirect`

> [!NOTE]
> Compute utilization 값이 표시됩니다. 이 값이 100에 가까우면 함수가 시간 제한에 근접한 것입니다. 일반적으로 30 이하면 충분한 여유가 있습니다.

82. **URL path**를 `/index.html`로 변경합니다.
83. [[Test function]] 버튼을 클릭합니다.

> [!OUTPUT]
> 리다이렉트 없이 원래 요청이 그대로 반환됩니다.

> [!TIP]
> `/old` 경로만 리다이렉트되고 다른 경로는 정상 처리되는 것을 테스트로 확인했습니다. Publish 전에 테스트하면 잘못된 함수가 프로덕션에 배포되는 것을 방지할 수 있습니다.

### 함수 배포 및 연결

84. **Publish** 탭을 선택합니다.
85. [[Publish function]] 버튼을 클릭합니다.

> [!IMPORTANT]
> 함수를 배포에 연결하려면 반드시 먼저 Publish해야 합니다. Development 상태에서는 연결할 수 없습니다.

86. **Publish** 탭에서 [[Add association]] 버튼을 클릭합니다.
87. **Distribution**에서 태스크 2에서 생성한 배포를 선택합니다.
88. **Event type**에서 `Viewer request`를 선택합니다.
89. **Cache behavior**에서 `Default (*)`를 선택합니다.
90. [[Add association]] 버튼을 클릭합니다.

> [!NOTE]
> 함수 연결 후 배포가 업데이트됩니다. 상태가 "Deployed"가 될 때까지 잠시 기다립니다.

91. 브라우저에서 `https://` + CloudFront 도메인 + `/old`를 입력합니다.

> [!NOTE]
> 예: `https://d1234abcd.cloudfront.net/old`

92. QuickTable 소개 페이지(`about.html`)로 리다이렉트되는지 확인합니다.
93. 브라우저 개발자 도구(F12)의 **Network** 탭에서 `/old` 요청을 선택합니다.
94. **Response Headers**에서 `302 Found` 상태 코드를 확인합니다.
95. `cloudfront-functions: quicktable-redirect` 커스텀 헤더를 확인합니다.
96. `x-cache: FunctionGeneratedResponse from cloudfront` 헤더를 확인합니다.

> [!CONCEPT] FunctionGeneratedResponse
> `x-cache` 헤더가 `FunctionGeneratedResponse from cloudfront`로 표시되면 응답이 오리진이 아닌 CloudFront Functions에서 직접 생성된 것입니다. 오리진에 요청을 보내지 않으므로 지연 시간이 매우 짧습니다.

### 성능 비교: CloudFront Functions vs 오리진 응답

97. **Network** 탭에서 `/old` 요청의 **Time** 열을 확인합니다.

> [!NOTE]
> Time 열이 보이지 않으면 Network 탭의 열 헤더를 우클릭하여 **Time**을 활성화합니다.

98. `/about.html` 요청의 **Time** 열을 확인하고 `/old` 요청과의 차이를 확인합니다.

> [!CONCEPT] CloudFront Functions 성능 이점
> `/old` 요청은 CloudFront Functions가 엣지 로케이션에서 직접 302 응답을 생성합니다. 오리진(Amazon S3)에 요청을 보내지 않으므로 응답 시간이 매우 짧습니다.
>
> | 요청 | 처리 위치 | x-cache 헤더 | 응답 시간 |
> | --- | --- | --- | --- |
> | `/old` | 엣지 (CloudFront Functions) | FunctionGeneratedResponse | 매우 빠름 |
> | `/about.html` (첫 요청) | 오리진 (Amazon S3) | Miss from cloudfront | 상대적으로 느림 |
> | `/about.html` (이후 요청) | 엣지 (캐시) | Hit from cloudfront | 빠름 |
>
> CloudFront Functions는 서브밀리초 단위로 실행되어 캐시 히트보다도 빠를 수 있습니다.

✅ **태스크 완료**: CloudFront Functions로 엣지 로케이션에서 URL 리다이렉트를 구현했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- QuickTable 프론트엔드를 Amazon S3 오리진 버킷에 업로드
- Amazon CloudFront 배포 생성 및 OAC 자동 설정으로 전 세계 배포
- 캐싱 동작 확인 및 응답 헤더 분석
- 캐시 무효화를 통한 QuickTable 콘텐츠 갱신
- CloudFront Functions로 엣지 로케이션에서 URL 리다이렉트 구현

Week 9-3에서 구축한 QuickTable 정적 웹사이트가 이제 CloudFront를 통해 전 세계 사용자에게 빠르게 제공됩니다. Week 10-2의 ElastiCache와 결합하여 QuickTable은 글로벌 규모의 고성능 레스토랑 예약 시스템으로 발전했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `10-3`
6. [[Search resources]] 버튼을 클릭합니다.

> [!OUTPUT]
> Amazon S3 버킷이 표시됩니다.

> [!NOTE]
> CloudFront 배포를 Tag Editor로 찾으려면 **Regions**에서 `us-east-1 (버지니아 북부)`를 선택하거나 `All regions`를 선택합니다. CloudFront는 글로벌 서비스로 us-east-1에 등록됩니다. ap-northeast-2만 선택하면 CloudFront가 표시되지 않습니다.
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### CloudFront 배포 삭제

7. Amazon CloudFront 콘솔의 왼쪽 메뉴에서 **Functions**를 선택합니다.
8. `quicktable-redirect` 함수를 선택합니다.
9. **Publish** 탭에서 연결된 배포의 체크박스를 선택합니다.
10. [[Remove association]] 버튼을 클릭합니다.
11. [[Delete function]] 버튼을 클릭합니다.

> [!NOTE]
> 배포 업데이트가 완료될 때까지 기다린 후 함수를 삭제합니다.

12. 왼쪽 메뉴에서 **Distributions**를 선택합니다.
13. 배포를 선택합니다.
14. [[Disable]] 버튼을 클릭합니다.
15. 확인 창에서 [[Disable]] 버튼을 클릭합니다.

> [!NOTE]
> 배포 상태가 `Disabled`가 될 때까지 기다립니다.

> [!TROUBLESHOOTING]
> **문제**: "Distribution must be disabled before deleting" 오류 발생
>
> **원인**: Disabled 상태에서도 즉시 Delete가 안 될 수 있습니다
>
> **해결**:
>
> 1. 5-10분 추가 대기 후 재시도합니다.
> 2. 배포를 다시 선택합니다.
> 3. [[Delete]] 버튼을 클릭합니다.
> 4. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

#### Amazon S3 버킷 삭제

16. Amazon S3 콘솔로 이동합니다.
17. 버킷을 선택합니다.
18. [[Empty]] 버튼을 클릭합니다.
19. 확인 창에서 `permanently delete`를 입력합니다.
20. [[Empty]] 버튼을 클릭합니다.
21. 버킷을 다시 선택합니다.
22. [[Delete]] 버튼을 클릭합니다.
23. 확인 창에서 버킷 이름을 입력합니다.
24. [[Delete bucket]] 버튼을 클릭합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon CloudFront 개발자 가이드](https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/)
- [Amazon CloudFront 모범 사례](https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/best-practices.html)
- [Amazon CloudFront 가격](https://aws.amazon.com/ko/cloudfront/pricing/)

### QuickTable 시리즈 연결

- **Week 4-3**: AWS Lambda + Amazon API Gateway로 QuickTable 예약 API 구축
- **Week 9-3**: Amazon S3로 QuickTable 정적 웹사이트 호스팅
- **Week 10-2**: ElastiCache로 API 성능 최적화
- **Week 10-3**: CloudFront로 글로벌 배포 ← 현재
- **Week 13-2**: AWS X-Ray로 성능 추적
- **Week 14-2**: Amazon Bedrock Knowledge Bases로 레스토랑 메뉴 RAG
- **Week 14-3**: Amazon Bedrock Agent로 예약 챗봇 완성

## 📚 참고: Amazon CloudFront 핵심 개념

### CDN (Content Delivery Network)

CloudFront는 AWS의 글로벌 CDN 서비스입니다. 전 세계에 분산된 엣지 로케이션을 통해 사용자에게 콘텐츠를 빠르게 전달합니다.

### 아키텍처 구성 요소

**엣지 로케이션 (Edge Location)**

- 전 세계 400개 이상의 캐시 서버
- 사용자와 가장 가까운 위치에서 콘텐츠 제공
- 캐시 저장소 역할

**오리진 (Origin)**

- 원본 콘텐츠가 저장된 위치
- Amazon S3, Amazon EC2, ALB, 커스텀 HTTP 서버 지원
- 캐시 미스 시 CloudFront가 접근

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
- CloudFront만 접근 가능
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
> `style.css?v=2` 방식을 사용하려면 CloudFront 캐시 정책에서 쿼리 스트링을 캐시 키에 포함해야 합니다. 기본 CachingOptimized 정책은 쿼리 스트링을 무시합니다.
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

### 엣지 컴퓨팅: CloudFront Functions vs Lambda@Edge

CloudFront Functions와 Lambda@Edge는 모두 CloudFront 이벤트에 응답하여 코드를 실행하는 엣지 컴퓨팅 기능입니다.

**CloudFront Functions 적합 사례**

- 캐시 키 정규화 (헤더, 쿼리 스트링 변환)
- 헤더 조작 (추가, 수정, 삭제)
- URL 리다이렉트 또는 리라이트
- 요청 인증 (JWT 토큰 검증)

**Lambda@Edge 적합 사례**

- 수 밀리초 이상 소요되는 함수
- 외부 네트워크 접근이 필요한 함수
- 서드파티 라이브러리 (AWS SDK 포함) 사용
- 요청 본문 접근이 필요한 함수

| 항목 | CloudFront Functions | Lambda@Edge |
| --- | --- | --- |
| 언어 | JavaScript (ECMAScript 5.1+) | Node.js, Python |
| 이벤트 소스 | Viewer request, Viewer response | Viewer/Origin request/response |
| 실행 시간 | 서브밀리초 | 최대 30초 |
| 메모리 | 2 MB | 최대 10 GB |
| 코드 크기 | 10 KB | 50 MB |
| 네트워크 접근 | 불가 | 가능 |
| 요청 본문 접근 | 불가 | 가능 |
| 처리량 | 초당 수백만 요청 | 리전당 초당 10,000 요청 |
| 배포 리전 | 모든 엣지 로케이션 | us-east-1에서 생성, 엣지로 복제 |
