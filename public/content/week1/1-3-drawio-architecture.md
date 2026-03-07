---
title: 'draw.io로 고가용성(HA) 아키텍처 다이어그램 작성'
week: 1
session: 3
awsServices: []
learningObjectives:
  - Draw.io를 사용하여 AWS 아키텍처 다이어그램을 작성할 수 있습니다.
  - QuickTable 3-Tier 아키텍처 다이어그램을 작성할 수 있습니다.
  - Multi-AZ 구성으로 고가용성 설계를 적용할 수 있습니다.
  - 아키텍처 다이어그램을 PNG 파일로 내보낼 수 있습니다.
prerequisites:
  - AWS 기본 서비스 이해
  - 네트워킹 기본 개념
---

이 실습에서는 **Draw.io**를 사용하여 **QuickTable 레스토랑 예약 시스템**의 전체 아키텍처 다이어그램을 작성하는 방법을 학습합니다.

먼저 **Draw.io**의 **AWS 아이콘 라이브러리**를 활용하여 **3-Tier 아키텍처**의 기본 구조를 그립니다. **프레젠테이션 계층**(Application Load Balancer), **애플리케이션 계층**(Amazon EC2 인스턴스), **데이터 계층**(Amazon RDS MySQL)을 명확히 구분하고, 각 계층의 역할과 통신 흐름을 시각화합니다.

**Multi-AZ 설계 원칙**을 적용하여 **Amazon EC2 인스턴스**, **Amazon RDS Multi-AZ**, **Amazon EC2 Auto Scaling**의 고가용성(HA, High Availability) 구성을 다이어그램에 표현하고, **보안 그룹** 설정을 통한 계층화된 보안을 구현합니다. 이를 통해 실제 프로덕션 환경에서 사용되는 **AWS Well-Architected Framework**의 **6가지 원칙**을 이해하게 됩니다.

> [!ARCHITECTURE]
> <img src="/images/week1/1-3-quicktable-3tier-architecture-with-sg.png" alt="QuickTable 3-Tier Architecture" class="guide-img-lg" />
>
> _QuickTable 레스토랑 예약 시스템의 3-Tier 고가용성 아키텍처_

> [!DOWNLOAD]
> [week1-3-architecture-lab.zip](/files/week1/week1-3-architecture-lab.zip)
>
> - `template-info.md` - Draw.io 템플릿 사용 안내 및 AWS 아이콘 라이브러리 로드 방법
>
> **관련 태스크:**
>
> - 태스크 1: Draw.io 환경 설정 (`template-info.md` 참고하여 AWS 아이콘 라이브러리 자동 로드)
> - 태스크 2-8: QuickTable 아키텍처 다이어그램 작성 (Multi-AZ 고가용성 설계 원칙 및 3-Tier 아키텍처 구성 요소 학습)

> [!NOTE]
> 이 실습은 Draw.io를 사용한 다이어그램 작성 실습으로, AWS 리소스를 생성하지 않습니다.

## 태스크 1: Draw.io 환경 설정

이 태스크에서는 **Draw.io** 작업 환경을 설정하고 **AWS 아이콘 라이브러리**를 로드합니다.

### 상세 단계

1. 웹 브라우저에서 다음 URL에 접속합니다: `https://app.diagrams.net/?splash=0&libs=aws4&lang=ko`.

> [!NOTE]
> URL 파라미터 `splash=0`은 시작 화면을 건너뛰고, `libs=aws4`는 AWS 아이콘 라이브러리를 자동으로 로드하며, `lang=ko`는 한국어 인터페이스를 설정합니다. 접속하면 자동으로 빈 다이어그램이 열립니다.

### 다이어그램 이름 설정

2. 상단의 **제목 없는 다이어그램**을 클릭합니다.
   <img src="/images/week1/1-3-task1-step1-diagram-name.png" alt="Draw.io 다이어그램 이름 변경 대화상자" class="guide-img-md" />

3. **파일명** 필드에 `quicktable-architecture`를 입력합니다.
4. **유형**은 `XML 파일 (.drawio)`로 유지합니다.
5. [[이름 바꾸기]] 버튼을 클릭합니다.
   <img src="/images/week1/1-3-task1-step1-diagram-name-2.png" alt="Draw.io 다이어그램 이름 변경 완료 화면" class="guide-img-sm" />

### 다이어그램 저장

6. 상단 메뉴에서 **파일** > **저장**을 선택합니다.
   <img src="/images/week1/1-3-task1-step1-save-confirm.png" alt="Draw.io 파일 메뉴에서 저장 선택" class="guide-img-sm" />
   <img src="/images/week1/1-3-task1-step1-save-location.png" alt="Draw.io 저장 위치 선택 대화상자" class="guide-img-sm" />

7. **위치**에서 저장 위치를 선택합니다 (예: `Google 드라이브 - 내 드라이브`, `브라우저`, `기기` 등).
   <img src="/images/week1/1-3-task1-step1-save-button.png" alt="Draw.io 저장 버튼" class="guide-img-sm" />

8. [[저장]] 버튼을 클릭합니다.

> [!NOTE]
> 이후 태스크를 진행하면서 주기적으로 **파일** > **저장**을 선택하여 작업 내용을 저장하는 것을 권장합니다.

> [!TIP]
> **새 다이어그램 만들기**
>
> 이미 다른 다이어그램을 작업 중이거나 새로 시작하려면:
>
> 1. 상단 메뉴에서 **파일** > **새로 만들기**를 선택합니다.
> 2. **빈 다이어그램**을 선택합니다.
> 3. [[만들기]] 버튼을 클릭합니다.
>
>    <img src="/images/week1/1-3-task1-step1-new-diagram.png" alt="Draw.io 새 다이어그램 만들기" class="guide-img-sm" />

> [!TIP]
> **영어 인터페이스로 변경하기**
>
> 영어 인터페이스를 선호하는 경우:
>
> 1. 상단 메뉴에서 **추가 도구**를 선택합니다.
> 2. **Language**를 선택합니다.
> 3. **English**를 선택합니다.
> 4. 페이지가 새로고침되면서 영어로 변경됩니다.
>
> 또는 URL에 `lang=en` 파라미터를 사용할 수 있습니다: `https://app.diagrams.net/?splash=0&libs=aws4&lang=en`

✅ **태스크 완료**: Draw.io 작업 환경이 준비되고 AWS 아이콘 라이브러리가 자동으로 로드되었습니다.

## 태스크 2: AWS 리전 및 QuickTable Amazon VPC 구성

이 태스크에서는 **AWS 리전**, **QuickTable Amazon VPC**, **2개의 가용 영역(Availability Zone)**을 다이어그램에 배치합니다. **Multi-AZ** 구조를 통해 **고가용성** 아키텍처의 기반을 마련합니다.

> [!ARCHITECTURE]
> <img src="/images/week1/1-3-quicktable-3tier-architecture-with-arrows.png" alt="QuickTable 3-Tier Architecture with Traffic Flow" class="guide-img-lg" />
>
> _트래픽 흐름이 표시된 QuickTable 아키텍처 (회색 화살표: 데이터 흐름, 점선: 복제/아웃바운드)_

> [!NOTE]
> 왼쪽 패널에 AWS 아이콘 라이브러리가 자동으로 로드되어 있습니다.

### AWS 리전 배치

9. 왼쪽 패널에서 **AWS / Groups** 카테고리를 확장합니다.

> [!TIP]
> **AWS 아이콘 검색 방법**: 왼쪽 패널 상단의 검색창에 `Region` 또는 `VPC`를 입력하면 아이콘을 빠르게 찾을 수 있습니다.  
> 카테고리를 클릭하면 해당 카테고리의 모든 아이콘이 표시됩니다. 이후 태스크에서도 이 방법을 사용하여 필요한 아이콘을 검색합니다.

10. **Region** 아이콘을 캔버스로 드래그합니다.
   <img src="/images/week1/1-3-task2-step2-region-drag.png" alt="Draw.io 캔버스에 Region 아이콘 드래그" class="guide-img-sm" />

11. Region 박스 크기를 조정하여 전체 아키텍처를 포함할 수 있도록 확장합니다.
12. Region 박스를 더블클릭하여 레이블을 `AWS Region: ap-northeast-2 (Seoul)`로 변경합니다.

### Amazon VPC 배치

13. **VPC** 아이콘을 Region 내부로 드래그합니다.
   <img src="/images/week1/1-3-task2-step2-vpc-drag.png" alt="Draw.io 캔버스에 VPC 아이콘 드래그" class="guide-img-sm" />

14. VPC 박스 크기를 조정하여 전체 아키텍처를 포함할 수 있도록 확장합니다.
   <img src="/images/week1/1-3-task2-step2-vpc-size.png" alt="Draw.io에서 VPC 박스 크기 조정" class="guide-img-sm" />

15. VPC 박스를 더블클릭하여 레이블을 `QuickTable Amazon VPC (10.0.0.0/16)`로 변경합니다.

### 가용 영역 배치

16. 왼쪽 패널에서 **Availability Zone** 아이콘을 검색합니다.
   <img src="/images/week1/1-3-task2-step2-az-placement.png" alt="Draw.io에 VPC와 2개 가용 영역" class="guide-img-sm" />

17. **Availability Zone** 아이콘을 VPC 내부에 배치하고 크기를 조정합니다.

> [!TIP]
> **아이콘 복제 방법**:
>
> - 배치한 아이콘을 선택 → **마우스 오른쪽 버튼** → **Duplicate** 선택
> - **단축키**: **⌘ (Cmd) + D** (Mac) / **Ctrl + D** (Windows)
> - **드래그**: **⌘ (Cmd)** (Mac) / **Ctrl** (Windows)을 누른 채로 드래그
>
> **여러 아이콘 선택**:
>
> - **Shift 클릭**: Shift 키를 누른 채로 아이콘을 클릭하면 여러 개를 선택할 수 있습니다.
> - **드래그 선택**: 빈 공간에서 드래그하여 영역을 지정하면 해당 영역의 모든 아이콘이 선택됩니다.
> - 선택한 여러 아이콘을 한 번에 복제하거나 이동할 수 있습니다.

18. 복제 기능을 사용하여 두 번째 Availability Zone을 추가합니다.

19. 첫 번째 AZ 레이블을 `ap-northeast-2a`로 설정합니다.
20. 두 번째 AZ 레이블을 `ap-northeast-2c`로 설정합니다.
    <img src="/images/week1/1-3-task2-step2-az-labels.png" alt="Draw.io에서 가용 영역 레이블 설정 완료" class="guide-img-sm" />

> [!NOTE]
> Multi-AZ 구성은 하나의 가용 영역에 장애가 발생해도 다른 가용 영역에서 서비스를 계속 제공할 수 있도록 합니다.
> QuickTable은 2개의 AZ를 사용하여 고가용성을 보장합니다.

✅ **태스크 완료**: AWS 리전, QuickTable Amazon VPC, 2개의 가용 영역이 생성되었습니다.

## 태스크 3: 3-Tier 서브넷 구성

이 태스크에서는 **3-Tier 아키텍처**의 핵심인 **퍼블릭 서브넷**, **프라이빗 서브넷(애플리케이션)**, **프라이빗 서브넷(데이터베이스)**을 각 가용 영역에 배치합니다.

> [!NOTE]
> **서브넷 종류**: AWS / Groups 카테고리에는 2가지 서브넷 아이콘이 있습니다.
>
> - **Public Subnet** (초록색): 인터넷 게이트웨이를 통해 외부와 통신
> - **Private Subnet** (파란색): NAT Gateway를 통해 아웃바운드만 허용 또는 완전히 격리

> [!TIP]
> **서브넷 색상 변경**: AWS / Groups 카테고리의 서브넷 아이콘은 예전 버전이며 그룹화되어 있어 색상 변경이 어렵습니다.
>
> **이번 실습에서는**: 제공되는 아이콘을 그대로 사용하여 다이어그램을 작성합니다. 색상 변경은 선택사항입니다.
>
> **정식 아키텍처 다이어그램 작성 시**: [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) 페이지에서 공식 아키텍처 아이콘 PPT를 다운로드하여 최신 아이콘을 가져온 후, 박스를 직접 그려서 서브넷을 표현하는 것을 권장합니다.
>
> **일반적인 색상 구분**:
>
> - **Public Subnet**: 초록색 계열 (인터넷 연결)
> - **Private Subnet**: 파란색 계열 (격리된 환경)

### ap-northeast-2a 서브넷 배치

21. 왼쪽 패널에서 **Public Subnet** 아이콘을 검색합니다.
22. **Public Subnet** 아이콘을 **ap-northeast-2a** AZ 내부에 배치하고 크기를 조정합니다.
23. 레이블을 `Public Subnet A (10.0.1.0/24)`로 설정합니다.

24. 왼쪽 패널에서 **Private Subnet** 아이콘을 검색합니다.
25. **Private Subnet** 아이콘을 **ap-northeast-2a** AZ 내부에 배치하고 크기를 조정합니다.
26. 레이블을 `Private App Subnet A (10.0.11.0/24)`로 설정합니다.
27. 복제 기능을 사용하여 세 번째 서브넷을 추가합니다.
28. 레이블을 `Private DB Subnet A (10.0.21.0/24)`로 설정합니다.

### ap-northeast-2c 서브넷 배치

29. **ap-northeast-2a**의 3개 서브넷을 모두 선택합니다 (Shift 키를 누른 채로 클릭).
30. 복제 기능을 사용하여 **ap-northeast-2c** AZ로 복사합니다.
31. 첫 번째 서브넷 레이블을 `Public Subnet C (10.0.2.0/24)`로 변경합니다.
32. 두 번째 서브넷 레이블을 `Private App Subnet C (10.0.12.0/24)`로 변경합니다.
33. 세 번째 서브넷 레이블을 `Private DB Subnet C (10.0.22.0/24)`로 변경합니다.
    <img src="/images/week1/1-3-task3-step3-subnets-complete.png" alt="Draw.io에 3-Tier 서브넷 구성 완료" class="guide-img-sm" />

> [!NOTE]
> **퍼블릭 서브넷**: 인터넷 게이트웨이를 통해 외부와 통신하며, Application Load Balancer가 배치됩니다.
>
> **프라이빗 서브넷(애플리케이션)**: NAT Gateway를 통해 외부로 나가는 트래픽만 허용하며, Amazon EC2 웹 서버와 앱 서버가 배치됩니다.
>
> **프라이빗 서브넷(데이터베이스)**: 외부 인터넷 접근이 차단되며, Amazon RDS 데이터베이스가 배치됩니다.

✅ **태스크 완료**: 3-Tier 서브넷 구성이 완료되었습니다.

## 태스크 4: 인터넷 게이트웨이 및 NAT Gateway

이 태스크에서는 **인터넷 게이트웨이**와 **NAT Gateway**를 추가하여 네트워크 연결을 구성합니다.

34. 왼쪽 패널 검색창에서 **Internet Gateway**를 검색합니다. (또는 **AWS / Networking & Content Delivery** 카테고리에서 찾습니다.)
35. **Internet Gateway** 아이콘을 VPC 상단 중앙에 배치하고 크기를 조정합니다.
36. 레이블을 `QuickTable IGW`로 설정합니다.
   <img src="/images/week1/1-3-task4-step4-igw-placement.png" alt="Draw.io에 Internet Gateway 배치" class="guide-img-sm" />

> [!TIP]
> **텍스트 위치 및 정렬 조정**:
>
> 아이콘에 화살표를 연결하면 텍스트가 가려지거나 레이아웃이 복잡해질 수 있습니다. 오른쪽 패널에서 텍스트 위치를 자유롭게 조정할 수 있습니다.
>
> 1. 아이콘을 선택합니다.
> 2. 오른쪽 패널의 **텍스트** 섹션에서:
>    - **정렬**: 왼쪽/가운데/오른쪽 정렬 선택
>    - **수직 정렬**: 위/가운데/아래 정렬 선택
>    - **간격**: Spacing 값을 조정하여 텍스트와 아이콘 사이 거리 조절
> 3. 텍스트를 아이콘 외부에 배치하려면 **Position** 섹션에서 위치를 조정합니다.
>
> 이 방법을 사용하면 화살표가 많아져도 텍스트가 가려지지 않고 깔끔한 다이어그램을 유지할 수 있습니다.

37. 왼쪽 패널에서 **NAT Gateway** 아이콘을 검색합니다.
38. **NAT Gateway** 아이콘을 **Public Subnet A** 내부에 배치하고 크기를 조정합니다.
39. 레이블을 `NAT Gateway A`로 설정합니다.
40. **NAT Gateway** 아이콘을 **Public Subnet C** 내부에 추가로 배치합니다.
41. 레이블을 `NAT Gateway C`로 설정합니다.
42. 각 NAT Gateway에서 Internet Gateway로 화살표를 연결합니다.
   <img src="/images/week1/1-3-task4-arrow-connected.png" alt="Draw.io에서 NAT Gateway와 Internet Gateway 간 화살표 연결 완료" class="guide-img-sm" />

> [!TIP]
> **화살표 연결 방법**:
>
> 1. 왼쪽 도구 모음에서 **화살표** 도구를 선택합니다.
>
>    <img src="/images/week1/1-3-task4-arrow-tool.png" alt="Draw.io 왼쪽 도구 모음에서 화살표 도구 선택" class="guide-img-sm" />
>
> 2. 시작 아이콘을 클릭한 후 끝 아이콘을 클릭하면 화살표가 연결됩니다.
> 3. 화살표를 선택하고 오른쪽 패널에서 스타일(실선/점선, 색상, 두께)을 변경할 수 있습니다.
>
>    <img src="/images/week1/1-3-task4-arrow-style.png" alt="Draw.io 오른쪽 패널에서 화살표 스타일 변경" class="guide-img-sm" />

> [!NOTE]
> **Internet Gateway**: 퍼블릭 서브넷의 리소스가 인터넷과 양방향 통신을 할 수 있도록 합니다.
>
> **NAT Gateway**: 프라이빗 서브넷의 리소스가 인터넷으로 나가는 트래픽을 처리합니다. NAT Gateway는 퍼블릭 서브넷에 배치되며, Internet Gateway를 통해 인터넷에 연결됩니다. 프라이빗 서브넷의 리소스는 NAT Gateway를 통해 인터넷으로 나가는 트래픽만 허용하며, 외부에서 들어오는 트래픽은 차단합니다. Multi-AZ 구성으로 고가용성을 보장합니다.

✅ **태스크 완료**: 인터넷 게이트웨이 및 NAT Gateway가 추가되었습니다.

## 태스크 5: Application Load Balancer 추가

이 태스크에서는 **Application Load Balancer(ALB)**를 퍼블릭 서브넷에 배치하여 외부 트래픽을 수신하고 Amazon EC2 인스턴스로 분산합니다.

43. 왼쪽 패널에서 **Application Load Balancer** 아이콘을 검색합니다.
44. **Application Load Balancer** 아이콘을 **Public Subnet A**와 **Public Subnet C** 사이에 배치합니다.
45. 레이블을 `QuickTable ALB`로 설정하고, 오른쪽 패널에서 텍스트 정렬을 오른쪽으로 변경합니다.
46. Internet Gateway에서 ALB로 화살표를 연결합니다.
   <img src="/images/week1/1-3-task5-alb-complete.png" alt="Draw.io에 Application Load Balancer 추가 완료" class="guide-img-sm" />

> [!NOTE]
> Application Load Balancer는 Layer 7(애플리케이션 계층)에서 동작하며, HTTP/HTTPS 트래픽을 처리합니다.
> Multi-AZ 구성으로 2개의 퍼블릭 서브넷에 배포되어 고가용성을 보장합니다.

✅ **태스크 완료**: Application Load Balancer가 추가되었습니다.

## 태스크 6: Amazon EC2 인스턴스 및 Amazon EC2 Auto Scaling 그룹

이 태스크에서는 **Web Tier**의 **Amazon EC2 인스턴스**와 **Amazon EC2 Auto Scaling 그룹**을 추가합니다.

47. 왼쪽 패널에서 **instance** 아이콘을 검색합니다. (필요하다면 **그 외 결과** 버튼을 누릅니다.)
48. **Amazon EC2 Instance** 아이콘을 **Private App Subnet A** 내부에 배치합니다.
49. 레이블을 `Web Server A1`로 설정합니다.
50. **Web Server A1**을 복사하여 옆에 배치합니다.
51. 레이블을 `Web Server A2`로 설정합니다.
52. **Amazon EC2 Instance** 아이콘을 **Private App Subnet C** 내부에 배치합니다.
53. 레이블을 `Web Server C1`로 설정합니다.
54. **Web Server C1**을 복사하여 옆에 배치합니다.
55. 레이블을 `Web Server C2`로 설정합니다.
56. 왼쪽 패널에서 **Auto Scaling** 또는 **Amazon EC2 Auto Scaling** 아이콘을 검색합니다.
57. **Amazon EC2 Auto Scaling** 아이콘을 Web Server 영역 주변에 배치합니다.
58. 레이블을 `QuickTable Web ASG`로 설정합니다.
59. ALB에서 각 AZ의 모든 Web Server로 화살표를 연결합니다. (ALB → Web Server A1, ALB → Web Server A2, ALB → Web Server C1, ALB → Web Server C2)
    <img src="/images/week1/1-3-task6-web-servers-complete.png" alt="Draw.io에 Web Server 및 Auto Scaling 그룹 추가 완료" class="guide-img-sm" />

60. 각 AZ의 Web Server 1개에서 NAT Gateway로 점선 화살표를 연결합니다. (Web Server A1 → NAT Gateway A, Web Server C2 → NAT Gateway C)
    <img src="/images/week1/1-3-task6-nat-connection.png" alt="Draw.io에 Web Server와 NAT Gateway 점선 연결 완료" class="guide-img-sm" />

> [!TIP]
> **점선 화살표 만들기**:
>
> 1. 화살표를 선택합니다.
> 2. 오른쪽 패널의 **스타일** 섹션에서 **점선(Dashed)** 옵션을 선택합니다.
> 3. 점선은 아웃바운드 트래픽(인터넷으로 나가는 트래픽)을 나타냅니다.

> [!NOTE]
> **Web Tier**: Nginx 또는 Apache를 실행하며, 정적 콘텐츠를 제공하고 요청을 처리합니다. 각 가용 영역에 2개씩 총 4개의 Web Server를 배치하여 고가용성과 확장성을 보장합니다.
>
> **Amazon EC2 Auto Scaling**: 트래픽에 따라 Amazon EC2 인스턴스 수를 자동으로 조정하여 비용을 최적화하고 가용성을 보장합니다.

✅ **태스크 완료**: Amazon EC2 인스턴스 및 Amazon EC2 Auto Scaling 그룹이 추가되었습니다.

## 태스크 7: Amazon RDS Multi-AZ 데이터베이스

이 태스크에서는 **Amazon RDS MySQL Multi-AZ** 데이터베이스를 프라이빗 데이터베이스 서브넷에 추가합니다.

61. 왼쪽 패널에서 **RDS** 아이콘을 검색합니다.
62. **Amazon RDS DB Instance** 아이콘을 **Private DB Subnet A** 내부에 배치합니다.
63. 레이블을 `RDS Primary`로 설정합니다.
64. **Amazon RDS DB Instance** 아이콘을 **Private DB Subnet C** 내부에 배치합니다.
65. 레이블을 `RDS Standby`로 설정합니다.
66. Primary에서 Standby로 점선 화살표를 연결하고, 화살표에 `Replication` 레이블을 추가합니다.

> [!TIP]
> **화살표에 레이블 추가**:
>
> 1. 화살표를 더블클릭합니다.
> 2. 텍스트를 입력합니다 (예: `Replication`).
> 3. 오른쪽 패널에서 폰트 크기와 위치를 조정할 수 있습니다.
>
> RDS Multi-AZ는 Primary에서 Standby로 단방향 동기식 복제가 이루어집니다. 점선 화살표를 사용하여 복제 흐름을 표현합니다.

67. 각 가용 영역의 Web Server 1개씩 RDS로 화살표를 연결합니다. (Web Server A1 → RDS Primary, Web Server C2 → RDS Standby)
   <img src="/images/week1/1-3-task7-rds-complete.png" alt="Draw.io에 RDS Multi-AZ 추가 완료" class="guide-img-sm" />

> [!NOTE]
> **Amazon RDS Multi-AZ**: Primary DB 인스턴스와 Standby DB 인스턴스가 서로 다른 가용 영역에 배포됩니다.
>
> **동기식 복제**: Primary에 쓰기가 발생하면 즉시 Standby로 복제됩니다.
>
> **자동 페일오버**: Primary에 장애가 발생하면 1-2분 내에 Standby가 자동으로 Primary로 승격됩니다.
>
> **엔드포인트**: 애플리케이션은 단일 엔드포인트를 사용하며, 페일오버 시 DNS가 자동으로 업데이트됩니다.

✅ **태스크 완료**: Amazon RDS Multi-AZ 데이터베이스가 추가되었습니다.

## 태스크 8: 보안 그룹 표시

이 태스크에서는 각 계층의 **보안 그룹**을 다이어그램에 표시하여 계층화된 보안 구조를 시각화합니다.

### ALB 보안 그룹

68. 왼쪽 패널에서 **Security Group** 또는 **보안 그룹**을 검색합니다.
69. **Security Group** 아이콘을 ALB 주변에 배치합니다.
70. 레이블을 `ALB-SG`로 설정합니다.

### Web Server 보안 그룹

71. **Security Group** 아이콘을 Web Server 주변에 배치합니다. (같은 보안 그룹에 여러 개를 한 번에 포함 가능)
72. 레이블을 `Web-SG`로 설정합니다.

### RDS 보안 그룹

73. **Security Group** 아이콘을 Amazon RDS 주변에 배치합니다.
74. 레이블을 `DB-SG`로 설정합니다.
   <img src="/images/week1/1-3-task8-security-groups-complete.png" alt="Draw.io에 보안 그룹 추가 완료" class="guide-img-sm" />

> [!NOTE]
> 보안 그룹은 계층화된 보안을 구현합니다. 각 계층은 이전 계층의 보안 그룹만 허용하여 최소 권한 원칙을 적용합니다.

✅ **태스크 완료**: 보안 그룹이 표시되었습니다.

## 태스크 9: 다이어그램 내보내기

이 태스크에서는 완성된 **QuickTable 3-Tier 아키텍처 다이어그램**을 **고해상도 PNG 이미지**로 내보냅니다.

75. 모든 요소가 정렬되어 있는지 확인합니다.
76. 화살표가 명확하게 연결되어 있는지 확인합니다.
77. 레이블이 읽기 쉬운지 확인합니다.
78. 보안 그룹이 각 계층을 명확히 구분하는지 확인합니다.
79. 상단 메뉴에서 **파일** > **다음에서 가져오기** > **PNG...**를 선택합니다.
   <img src="/images/week1/1-3-task9-export-menu.png" alt="Draw.io 파일 메뉴에서 PNG 내보내기 선택" class="guide-img-sm" />

80. **이미지** 대화상자에서 필요한 설정을 확인한 후 [[내보내기]] 버튼을 클릭합니다.
   <img src="/images/week1/1-3-task9-export-dialog.png" alt="Draw.io PNG 내보내기 대화상자" class="guide-img-sm" />

> [!NOTE]
> **배율** 설정은 이미지 해상도를 결정합니다. 100%는 기본 해상도이며, 더 높은 해상도가 필요한 경우 200% 또는 300%로 설정할 수 있습니다.

81. 파일명을 `quicktable-architecture`로 입력하고 저장 위치를 선택합니다.
82. [[저장]] 버튼을 클릭합니다.
   <img src="/images/week1/1-3-task9-save-complete.png" alt="Draw.io PNG 파일 저장 완료" class="guide-img-sm" />

> [!TIP]
> 다이어그램을 팀원과 공유하려면 **파일** > **다음에서 가져오기** > **SVG...**를 선택하여 벡터 형식으로도 저장합니다. SVG 파일은 확대해도 선명하며, 웹 문서에 삽입하기 적합합니다.

> [!TIP]
> **다이어그램 추가 개선 (선택사항)**:
>
> 기본 아키텍처가 완성되었다면, 다음 요소를 추가하여 더욱 완성도 높은 다이어그램을 만들 수 있습니다:
>
> - **사용자 아이콘**: Internet Gateway 외부에 사용자 아이콘을 배치하여 트래픽 시작점을 명확히 표현
> - **CloudWatch**: 모니터링 아이콘 추가
> - **Route 53**: DNS 라우팅 표현
> - **CloudFront**: CDN 계층 추가
> - **ElastiCache**: 캐싱 계층 추가
>
> 이러한 추가 요소는 실습 범위를 벗어나지만, 실제 프로덕션 아키텍처를 표현할 때 유용합니다.

✅ **태스크 완료**: QuickTable 3-Tier 아키텍처 다이어그램이 PNG 이미지로 내보내기되었습니다.

<img src="/images/week1/1-3-task9-complete.png" alt="Draw.io 다이어그램 내보내기 완료 화면" class="guide-img-sm" />

## 마무리

다음을 성공적으로 수행했습니다:

- Draw.io를 사용하여 QuickTable 3-Tier 아키텍처 다이어그램을 작성했습니다.
- Multi-AZ 고가용성 아키텍처를 설계했습니다.
- Amazon VPC, 서브넷, 인터넷 게이트웨이, NAT Gateway를 구성했습니다.
- Application Load Balancer, Amazon EC2 인스턴스, Amazon EC2 Auto Scaling 그룹을 배치했습니다.
- Amazon RDS Multi-AZ 데이터베이스를 추가했습니다.
- 계층화된 보안 그룹 구조를 시각화했습니다.
- 다이어그램을 PNG 이미지로 내보냈습니다.
- Week 5-1에서 구축할 전체 시스템의 청사진을 완성했습니다.

---

# 🗑️ 리소스 정리

> [!NOTE]
> 이 실습은 Draw.io를 사용한 다이어그램 작성 실습으로, AWS 리소스를 생성하지 않았습니다.

## 파일 정리 (선택사항)

실습에서 생성한 파일을 정리합니다.

- **다이어그램 파일 보관**: `quicktable-architecture.drawio` 파일은 향후 아키텍처 변경 시 수정할 수 있으므로 보관을 권장합니다.
- **파일 삭제**: 저장된 파일을 삭제하려면 다운로드 폴더 또는 저장 위치에서 직접 삭제합니다.

> [!TIP]
> 생성한 다이어그램은 Week 5-1 실습에서 참고 자료로 사용할 수 있습니다.

---

## 완료 확인

다음 구성 요소가 모두 포함되어 있는지 확인합니다:

- Amazon VPC 및 2개의 가용 영역
- 3-Tier 서브넷 구성 (퍼블릭, 프라이빗 앱, 프라이빗 DB)
- 인터넷 게이트웨이 및 NAT Gateway
- Application Load Balancer
- Amazon EC2 인스턴스 및 Amazon EC2 Auto Scaling 그룹
- Amazon RDS Multi-AZ 데이터베이스
- 보안 그룹 표시

> [!SUCCESS]
> 모든 구성 요소가 포함되어 있으면 다이어그램 작성이 완료되었습니다.

✅ **실습 종료**: QuickTable 3-Tier 아키텍처 다이어그램이 완성되었습니다.

## 추가 학습 리소스

- [AWS 아키텍처 센터](https://aws.amazon.com/ko/architecture/)
- [AWS Well-Architected Framework](https://aws.amazon.com/ko/architecture/well-architected/)
- [웹 호스팅을 위한 AWS 클라우드 아키텍처](https://docs.aws.amazon.com/ko_kr/whitepapers/latest/web-application-hosting-best-practices/an-aws-cloud-architecture-for-web-hosting.html)
- [AWS 아키텍처 다이어그램 및 모범 사례](https://builder.aws.com/)
- [Amazon RDS Multi-AZ 배포](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Amazon EC2 Auto Scaling 모범 사례](https://docs.aws.amazon.com/ko_kr/autoscaling/ec2/userguide/as-best-practices.html)

## 📚 참고: QuickTable 3-Tier 아키텍처 설계 원칙

### 3-Tier 아키텍처 개요

**계층 분리의 이점**

- 각 계층은 독립적으로 확장 가능합니다.
- 보안 그룹으로 계층 간 트래픽을 제어합니다.
- 장애 격리가 용이하여 한 계층의 문제가 다른 계층에 영향을 주지 않습니다.
- 유지보수와 업데이트가 쉽습니다.

**QuickTable 3-Tier 구성**

- **프레젠테이션 계층**: Application Load Balancer (퍼블릭 서브넷)
- **애플리케이션 계층**: Amazon EC2 Web Server + App Server (프라이빗 애플리케이션 서브넷)
- **데이터 계층**: Amazon RDS MySQL Multi-AZ (프라이빗 데이터베이스 서브넷)

### Multi-AZ 고가용성 설계

**가용 영역 분산**

- 2개의 가용 영역(ap-northeast-2a, ap-northeast-2c)을 사용합니다.
- 각 AZ에 동일한 구성의 서브넷을 배치합니다.
- 하나의 AZ에 장애가 발생해도 다른 AZ에서 서비스를 계속 제공합니다.

**Application Load Balancer**

- 2개의 퍼블릭 서브넷에 배포되어 고가용성을 보장합니다.
- Health Check를 통해 정상 인스턴스로만 트래픽을 전달합니다.
- Cross-Zone Load Balancing으로 AZ 간 트래픽을 균등하게 분산합니다.

**Amazon RDS Multi-AZ**

- Primary DB 인스턴스와 Standby DB 인스턴스가 서로 다른 AZ에 배포됩니다.
- 동기식 복제로 데이터 일관성을 보장합니다.
- 자동 페일오버로 1-2분 내에 Standby가 Primary로 승격됩니다.

### 네트워크 구성

**Amazon VPC 설계**

- CIDR 블록: 10.0.0.0/16 (65,536개 IP 주소)
- 퍼블릭 서브넷: 10.0.1.0/24, 10.0.2.0/24 (각 256개 IP)
- 프라이빗 애플리케이션 서브넷: 10.0.11.0/24, 10.0.12.0/24
- 프라이빗 데이터베이스 서브넷: 10.0.21.0/24, 10.0.22.0/24

**인터넷 연결**

- 인터넷 게이트웨이: 퍼블릭 서브넷의 리소스가 인터넷과 양방향 통신
- NAT Gateway: 프라이빗 서브넷의 리소스가 인터넷으로 나가는 트래픽만 허용
- Multi-AZ NAT Gateway: 각 AZ에 NAT Gateway를 배치하여 고가용성 보장

### 보안 그룹 설계

**계층화된 보안**

- **QuickTable-ALB-SG**: 인터넷(0.0.0.0/0)에서 HTTPS(443) 트래픽만 허용
- **QuickTable-Web-SG**: ALB 보안 그룹에서 HTTP(80) 트래픽만 허용
- **QuickTable-App-SG**: Web 보안 그룹에서 8080 포트 트래픽만 허용
- **QuickTable-DB-SG**: App 보안 그룹에서 MySQL(3306) 트래픽만 허용

**최소 권한 원칙**

- 각 계층은 이전 계층의 보안 그룹만 허용합니다.
- 불필요한 포트는 모두 차단합니다.
- 데이터베이스는 외부 인터넷 접근이 완전히 차단됩니다.

### Amazon EC2 Auto Scaling 전략

**Web Tier Amazon EC2 Auto Scaling**

- 최소 인스턴스: 2개 (각 AZ에 1개씩)
- 최대 인스턴스: 10개
- 스케일링 정책: CPU 사용률 70% 이상 시 스케일 아웃

**App Tier Amazon EC2 Auto Scaling**

- 최소 인스턴스: 2개 (각 AZ에 1개씩)
- 최대 인스턴스: 20개
- 스케일링 정책: CPU 사용률 60% 이상 시 스케일 아웃

**스케일링 쿨다운**

- 스케일 아웃 후 5분 대기 (인스턴스 초기화 시간 고려)
- 스케일 인 후 10분 대기 (트래픽 변동 고려)

### Amazon RDS 데이터베이스 설계

**Multi-AZ 배포**

- Primary DB: ap-northeast-2a
- Standby DB: ap-northeast-2c
- 동기식 복제로 RPO(Recovery Point Objective) = 0

**자동 백업**

- 백업 보존 기간: 7일
- 백업 시간: 새벽 3-4시 (트래픽이 적은 시간)
- Point-in-Time Recovery 지원

**읽기 성능 최적화**

- Read Replica를 추가하여 읽기 트래픽 분산 가능
- 애플리케이션에서 읽기/쓰기 엔드포인트 분리

### 비용 최적화

**Amazon EC2 인스턴스 타입 선택**

- Web Tier: t3.small (2 vCPU, 2GB RAM) - 가벼운 웹 서버
- App Tier: t3.medium (2 vCPU, 4GB RAM) - 비즈니스 로직 처리
- Reserved Instance 또는 Savings Plans로 비용 절감

**NAT Gateway 비용 절감**

- Amazon VPC Endpoint를 사용하여 Amazon S3, Amazon DynamoDB 접근 시 NAT Gateway 우회
- 트래픽이 적은 환경에서는 NAT Instance 고려

**Amazon RDS 비용 최적화**

- db.t3.micro 또는 db.t3.small로 시작
- 트래픽 증가 시 수직 확장 (인스턴스 타입 변경)
- Reserved Instance로 최대 60% 비용 절감

### 모니터링 및 로깅

**Amazon CloudWatch 메트릭**

- ALB: 요청 수, 응답 시간, 오류율
- Amazon EC2: CPU 사용률, 네트워크 트래픽, 디스크 I/O
- Amazon RDS: CPU 사용률, 연결 수, 읽기/쓰기 IOPS

**Amazon CloudWatch Logs**

- ALB 액세스 로그: Amazon S3에 저장
- Amazon EC2 애플리케이션 로그: Amazon CloudWatch Logs Agent로 수집
- Amazon RDS 슬로우 쿼리 로그: 성능 최적화에 활용

**Amazon CloudWatch Alarms**

- CPU 사용률 80% 이상: Amazon SNS 알림
- Amazon RDS 연결 수 90% 이상: 경고
- ALB 5xx 오류율 5% 이상: 긴급 알림

### 재해 복구 전략

**백업 전략**

- Amazon RDS 자동 백업: 매일 새벽 3시
- Amazon EC2 AMI 스냅샷: 주 1회
- 백업 데이터를 다른 리전에 복제 (선택사항)

**복구 시나리오**

- **AZ 장애**: Multi-AZ 구성으로 자동 페일오버 (1-2분)
- **리전 장애**: 다른 리전에 백업에서 복구 (RTO: 1-2시간)
- **데이터 손상**: Point-in-Time Recovery로 특정 시점 복구

### 확장 가능성

**수평 확장**

- Amazon EC2 Auto Scaling으로 Amazon EC2 인스턴스 수 자동 조정
- Read Replica 추가로 읽기 성능 향상
- ALB가 자동으로 트래픽 분산

**수직 확장**

- Amazon EC2 인스턴스 타입 변경 (t3.small → t3.medium → t3.large)
- Amazon RDS 인스턴스 타입 변경 (db.t3.micro → db.t3.small → db.t3.medium)
- 다운타임 최소화 (Amazon RDS는 Multi-AZ 페일오버 활용)

**서버리스 전환 경로**

- Week 4-3: AWS Lambda + Amazon API Gateway로 애플리케이션 계층 전환
- Week 5-3: Amazon DynamoDB로 데이터 계층 전환
- Week 10-2: Amazon ElastiCache로 캐싱 계층 추가
- Week 14-2: Amazon Bedrock Knowledge Bases 기반 RAG 구현
