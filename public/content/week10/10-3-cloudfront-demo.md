---
title: 'Amazon CloudFront CDN 배포 및 캐싱 전략'
week: 10
session: 3
awsServices:
  - Amazon CloudFront
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
> - 태스크 2: Amazon CloudFront 배포 생성 (글로벌 CDN 구성, OAC 보안 설정)
> - 태스크 3: 배포 테스트 및 캐싱 확인 (엣지 로케이션 성능 측정)
> - 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화 (버전 관리 전략)

> [!NOTE]
> 이 데모는 비용이 거의 발생하지 않습니다. Amazon CloudFront 프리 티어에서 매월 50GB 데이터 전송과 2,000,000건의 요청을 무료로 제공합니다.

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

이 태스크에서는 Amazon S3 버킷을 오리진으로 하는 Amazon CloudFront 배포를 생성하여 QuickTable을 전 세계에 배포합니다.

14. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFront`을 입력하고 선택합니다.
15. [[Create distribution]] 버튼을 클릭합니다.
16. **Origin domain**에서 방금 생성한 Amazon S3 버킷을 선택합니다.

> [!CONCEPT] Amazon CloudFront 오리진 (CloudFront Origin)
> 오리진은 원본 콘텐츠가 저장된 위치입니다. Amazon S3, Amazon EC2, ALB 또는 커스텀 HTTP 서버를 사용할 수 있습니다.
> Amazon CloudFront는 캐시 미스가 발생하면 오리진에서 콘텐츠를 가져옵니다.

17. **Origin access**에서 `Origin access control settings (recommended)`를 선택합니다.
18. [[Create control setting]] 버튼을 클릭합니다.
19. **Name**에 `demo-oac`를 입력합니다.
20. [[Create]] 버튼을 클릭합니다.

> [!CONCEPT] OAC (Origin Access Control)
> OAC는 Amazon S3 버킷을 비공개로 유지하면서 Amazon CloudFront만 접근할 수 있도록 하는 보안 기능입니다.
> 이전 방식인 OAI(Origin Access Identity)보다 더 많은 Amazon S3 기능을 지원합니다.

21. **Viewer protocol policy**에서 `Redirect HTTP to HTTPS`를 선택합니다.
22. **Allowed HTTP methods**에서 `GET, HEAD`를 선택합니다.
23. **Cache policy**에서 `CachingOptimized`를 선택합니다.

> [!CONCEPT] Amazon CloudFront 캐시 정책 (Amazon CloudFront Cache Policy)
>
> - **CachingOptimized**: 정적 콘텐츠에 최적화, 최대 캐싱
> - **CachingDisabled**: 동적 콘텐츠용, 캐싱 안 함
> - **Custom**: 사용자 정의 TTL 및 캐시 키 설정

24. **Price class**에서 `Use North America, Europe, Asia, Middle East, and Africa`를 선택합니다.

> [!TIP]
> 비용 절감을 위해 "Use all edge locations" 대신 주요 지역만 선택합니다. 대부분의 사용자에게 충분한 성능을 제공하면서 비용을 약 30% 절감할 수 있습니다.

25. **Default root object**에 `index.html`을 입력합니다.
26. [[Create distribution]] 버튼을 클릭합니다.
27. 상단에 표시되는 파란색 배너를 확인합니다.

> [!IMPORTANT]
> 파란색 배너는 배포 생성 직후 일시적으로 표시됩니다. 다른 페이지로 이동하면 사라질 수 있으므로 즉시 정책을 복사해야 합니다.

28. Copy policy 버튼을 클릭합니다.

> [!NOTE]
> 파란색 배너가 표시되지 않거나 놓친 경우, 다음 방법으로 정책을 확인할 수 있습니다:
>
> 1. Amazon CloudFront 콘솔에서 배포를 선택합니다.
> 2. **Origins** 탭을 선택합니다.
> 3. 오리진을 선택한 후 Edit 버튼을 클릭합니다.
> 4. **Origin access** 섹션 하단의 "Go to Amazon S3 bucket permissions" 링크를 클릭하거나 Copy policy 버튼을 클릭합니다.

29. Amazon S3 콘솔로 이동합니다.
30. 버킷을 선택합니다.
31. **Permissions** 탭을 클릭합니다.
32. **Bucket policy** 섹션에서 Edit 버튼을 클릭합니다.
33. 복사한 정책을 붙여넣습니다.
34. [[Save changes]] 버튼을 클릭합니다.
35. Amazon CloudFront 콘솔로 이동합니다.
36. 배포를 선택합니다.
37. **Tags** 탭을 선택합니다.
38. [[Manage tags]] 버튼을 클릭합니다.
39. 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-3`    |
| `CreatedBy` | `Student` |

40. [[Save changes]] 버튼을 클릭합니다.

> [!NOTE]
> 배포 생성에 5-15분이 소요됩니다. 상태가 "Deploying"에서 "Enabled"로 변경될 때까지 기다립니다.
> 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다. 페이지를 새로고침하여 최신 상태를 확인할 수 있습니다.

41. 배포 상태가 "Enabled"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: Amazon CloudFront 배포가 생성되고 Amazon S3 버킷 정책이 업데이트되었습니다.

## 태스크 3: 배포 테스트 및 캐싱 확인

이 태스크에서는 CloudFront를 통해 콘텐츠에 접근하고 캐싱 동작을 확인합니다.

42. Amazon CloudFront 콘솔에서 배포 상태가 `Enabled`가 될 때까지 기다립니다.
43. **Distribution domain name**을 복사합니다 (예: `d1234abcd.cloudfront.net`).
44. 새 브라우저 탭을 엽니다.
45. 주소창에 복사한 도메인을 붙여넣고 Enter를 누릅니다.
46. QuickTable 웹사이트가 정상적으로 로드되는지 확인합니다.

> [!CONCEPT] 엣지 로케이션 (Edge Location)
> Amazon CloudFront는 전 세계 400개 이상의 엣지 로케이션에서 콘텐츠를 캐싱합니다.
> 사용자는 가장 가까운 엣지 로케이션에서 콘텐츠를 받아 빠른 속도를 경험합니다.

47. 브라우저 개발자 도구를 엽니다 (F12 키).
48. **Network** 탭을 선택합니다.
49. **Disable cache** 체크박스를 체크합니다.

> [!IMPORTANT]
> 브라우저 캐시를 비활성화하지 않으면 CloudFront 캐시 헤더를 정확히 확인할 수 없습니다. 브라우저가 로컬 캐시를 사용하여 CloudFront에 요청을 보내지 않을 수 있습니다.

50. 페이지를 새로고침합니다 (Ctrl+R 또는 Cmd+R).
51. `index.html` 요청을 선택합니다.
52. **Headers** 섹션에서 **Response Headers**를 확인합니다.
53. `x-cache` 헤더를 찾습니다.

> [!NOTE]
> 첫 요청에서 `Miss from cloudfront`가 아닌 `Hit from cloudfront`가 표시될 수 있습니다. 이는 다른 사용자가 동일 엣지 로케이션에서 이미 해당 콘텐츠를 요청하여 캐시에 저장된 경우입니다. 이것은 정상 동작입니다.

> [!CONCEPT] Amazon CloudFront 캐시 헤더
>
> - **x-cache: Miss from cloudfront** - 오리진에서 가져옴 (첫 요청)
> - **x-cache: Hit from cloudfront** - 엣지에서 캐시 제공 (이후 요청)
> - **x-amz-cf-pop** - 요청을 처리한 엣지 로케이션 (예: ICN54-C1은 서울)
> - **age** - 캐시된 시간 (초 단위)

54. 페이지를 다시 새로고침합니다.
55. `x-cache` 헤더가 `Hit from cloudfront`로 변경되었는지 확인합니다.
56. `age` 헤더 값이 증가하는 것을 확인합니다.
57. 주소창에 `http://` + 복사한 도메인을 입력합니다 (예: `http://d1234abcd.cloudfront.net`).
58. 자동으로 `https://`로 리다이렉트되는지 확인합니다.
59. **Network** 탭에서 301 또는 302 리다이렉트 응답을 확인합니다.

> [!NOTE]
> 이것이 태스크 2에서 설정한 "Redirect HTTP to HTTPS" 정책의 동작입니다. 모든 HTTP 요청은 자동으로 HTTPS로 리다이렉트됩니다.

✅ **태스크 완료**: Amazon CloudFront 캐싱 및 HTTPS 리다이렉트가 정상적으로 동작합니다.

## 태스크 4: QuickTable 콘텐츠 업데이트 및 캐시 무효화

이 태스크에서는 QuickTable 콘텐츠를 업데이트하고 캐시된 콘텐츠를 강제로 갱신하는 방법을 학습합니다.

60. 텍스트 에디터에서 `index.html` 파일을 엽니다.
61. 제목을 "QuickTable v2.0 - 더 빠른 예약 경험"으로 변경합니다.
62. 파일을 저장합니다.
63. Amazon S3 콘솔에서 버킷을 선택합니다.
64. [[Upload]] 버튼을 클릭합니다.
65. 수정한 `index.html` 파일을 선택합니다.

> [!NOTE]
> 동일한 파일명으로 업로드하면 기존 파일을 덮어씁니다. Amazon S3는 자동으로 버전 관리를 하지 않으므로 이전 버전은 삭제됩니다.

66. [[Upload]] 버튼을 클릭합니다.
67. Amazon CloudFront 도메인으로 다시 접속합니다.
68. 여전히 이전 버전이 표시되는 것을 확인합니다 (캐시됨).

> [!NOTE]
> CachingOptimized 정책의 기본 TTL은 24시간입니다. Amazon S3에 새 파일을 업로드해도 TTL이 만료되기 전까지는 CloudFront가 캐시된 이전 버전을 제공합니다. 이것이 캐시 무효화가 필요한 이유입니다.

> [!CONCEPT] 캐시 무효화 (Invalidation)
> 캐시된 콘텐츠를 즉시 갱신하려면 무효화를 생성해야 합니다.
> 무효화는 모든 엣지 로케이션의 캐시를 제거하여 다음 요청 시 오리진에서 새 콘텐츠를 가져오도록 합니다.

69. Amazon CloudFront 콘솔에서 배포를 선택합니다.
70. **Invalidations** 탭을 선택합니다.
71. [[Create invalidation]] 버튼을 클릭합니다.
72. **Object paths**에 `/index.html`을 입력합니다.

> [!NOTE]
> 모든 파일을 무효화하려면 `/*`를 입력합니다. 매월 처음 1,000개 경로는 무료이며, 이후 경로당 $0.005가 부과됩니다.

73. Create invalidation 버튼을 클릭합니다.
74. 무효화 상태가 `Completed`가 될 때까지 기다립니다 (1-2분).
75. 브라우저 개발자 도구(F12)에서 **Network** 탭을 선택합니다.
76. **Disable cache** 체크박스가 활성화되어 있는지 확인합니다.
77. 강력 새로고침을 수행합니다 (Ctrl+Shift+R 또는 Cmd+Shift+R).
78. `index.html` 요청을 선택합니다.
79. `x-cache` 헤더가 `Miss from cloudfront`로 표시되는지 확인합니다.

> [!NOTE]
> 무효화 직후 첫 요청은 반드시 `Miss from cloudfront`여야 합니다. 이는 캐시가 제거되어 오리진에서 새 콘텐츠를 가져오는 것을 의미합니다.

80. 변경된 제목 "QuickTable v2.0 - 더 빠른 예약 경험"이 표시되는 것을 확인합니다.
81. 페이지를 다시 새로고침합니다.
82. `x-cache` 헤더가 `Hit from cloudfront`로 변경되는지 확인합니다.

✅ **태스크 완료**: 캐시 무효화를 통해 QuickTable 콘텐츠를 갱신했습니다.

## 태스크 5: 성능 모니터링

이 태스크에서는 Amazon CloudFront 메트릭을 확인하여 배포 성능을 모니터링합니다.

83. Amazon CloudFront 콘솔에서 배포를 선택합니다.
84. **Monitoring** 탭을 선택합니다.
85. **Requests** 그래프를 확인합니다 (총 요청 수).
86. **Bytes downloaded** 그래프를 확인합니다 (다운로드된 데이터량).

> [!NOTE]
> **성능 모니터링 주의사항**:
>
> **데이터 지연**: 메트릭은 1-5분 후 표시됩니다. 데이터가 없으면 잠시 후 새로고침합니다.
>
> **Cache hit rate 추가 비용**: "Enable additional metrics" 활성화 시 배포당 $0.01/월 추가 비용이 발생합니다. 이 실습에서는 활성화하지 않아도 됩니다.
>
> **소규모 테스트의 한계**: 요청 수가 적어 통계적으로 의미있는 데이터가 없을 수 있습니다. 실제 운영 환경에서는 수천 건 이상의 요청이 필요합니다.

87. **Cache hit rate** 그래프를 확인합니다 (캐시 적중률, 데이터가 없을 수 있음).

> [!CONCEPT] 캐시 적중률 (Cache Hit Rate)
> 엣지 로케이션에서 캐시된 콘텐츠로 응답한 비율입니다.
>
> - **80% 이상**: 좋음 - 대부분의 요청이 엣지에서 처리됨
> - **50-80%**: 보통 - TTL 증가 고려
> - **50% 미만**: 낮음 - 캐시 전략 재검토 필요

88. **Error rate** 그래프를 확인합니다 (4xx, 5xx 에러 비율).
89. 아래로 스크롤하여 **Popular objects** 섹션을 확인합니다.
90. 가장 많이 요청된 파일을 확인합니다.

✅ **태스크 완료**: Amazon CloudFront 성능 메트릭을 확인했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- QuickTable 프론트엔드를 Amazon S3 오리진 버킷에 업로드
- Amazon CloudFront 배포 생성 및 OAC 설정으로 전 세계 배포
- 캐싱 동작 확인 및 응답 헤더 분석
- 캐시 무효화를 통한 QuickTable 콘텐츠 갱신
- Amazon CloudFront 성능 메트릭 모니터링

Week 9-3에서 구축한 QuickTable 정적 웹사이트가 이제 CloudFront를 통해 전 세계 사용자에게 빠르게 제공됩니다. Week 10-2의 ElastiCache와 결합하여 QuickTable은 글로벌 규모의 고성능 레스토랑 예약 시스템으로 발전했습니다.

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
	- **Tag value**: `10-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. Amazon S3 버킷이 표시됩니다.

> [!NOTE]
> CloudFront 배포를 Tag Editor로 찾으려면 **Regions**에서 `us-east-1 (버지니아 북부)`를 선택하거나 `All regions`를 선택합니다. CloudFront는 글로벌 서비스로 us-east-1에 등록됩니다. ap-northeast-2만 선택하면 CloudFront가 표시되지 않습니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### CloudFront 배포 삭제

8. Amazon CloudFront 콘솔에서 배포를 선택합니다.
9. [[Disable]] 버튼을 클릭합니다.
10. 확인 창에서 [[Disable]] 버튼을 클릭합니다.
11. 배포 상태가 `Disabled`가 될 때까지 기다립니다.

> [!TROUBLESHOOTING]
> **문제**: "Distribution must be disabled before deleting" 오류 발생
>
> **원인**: Disabled 상태에서도 즉시 Delete가 안 될 수 있습니다
>
> **해결**: 5-10분 추가 대기 후 재시도합니다. 5. 배포를 다시 선택합니다. 6. [[Delete]] 버튼을 클릭합니다. 7. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

#### Amazon S3 버킷 삭제

12. Amazon S3 콘솔로 이동합니다.
13. 버킷을 선택합니다.
14. [[Empty]] 버튼을 클릭합니다.
15. 확인 창에서 `permanently delete`를 입력합니다.
16. [[Empty]] 버튼을 클릭합니다.
17. 버킷을 다시 선택합니다.
18. [[Delete]] 버튼을 클릭합니다.
19. 확인 창에서 버킷 이름을 입력합니다.
20. [[Delete bucket]] 버튼을 클릭합니다.

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
