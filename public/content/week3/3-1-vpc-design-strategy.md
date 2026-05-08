---
title: 'Amazon VPC Endpoint 생성 및 연결 확인'
week: 3
session: 1
awsServices:
  - Amazon VPC
learningObjectives:
  - Amazon VPC Endpoint의 개념과 프라이빗 연결의 이점을 이해할 수 있습니다.
  - AWS Systems Manager Interface Endpoint를 생성하고 구성할 수 있습니다.
  - Amazon S3 Gateway Endpoint를 생성하고 라우팅 테이블을 확인할 수 있습니다.
  - Amazon VPC Endpoint를 통한 프라이빗 연결을 검증하고 동작을 확인할 수 있습니다.
prerequisites:
  - Amazon VPC 기본 개념 이해
  - 네트워킹 기본 개념 (IP 주소, 서브넷, 라우팅)
---

이 실습에서는 Amazon VPC Endpoint의 두 가지 타입인 Interface Endpoint와 Gateway Endpoint를 직접 생성하고 동작 원리를 학습합니다.

먼저 AWS Systems Manager용 Interface Endpoint 3개(ssm, ssmmessages, ec2messages)를 생성하여 프라이빗 서브넷에서 Session Manager로 Amazon EC2 인스턴스에 접속합니다. 그 다음 Amazon S3 Gateway Endpoint를 생성하여 인터넷 게이트웨이를 거치지 않고 Amazon S3에 안전하게 접근하는 방법을 확인합니다.

Amazon VPC Endpoint는 Amazon VPC와 AWS 서비스 간의 프라이빗 연결을 제공하여 인터넷을 통하지 않고도 AWS 서비스에 접근할 수 있게 합니다. Interface Endpoint(ENI 기반)와 Gateway Endpoint(라우팅 테이블 기반)의 차이를 AWS 콘솔에서 직접 확인하고, 각각의 동작 방식을 실제로 검증합니다.

> [!CONCEPT] Amazon VPC Endpoint 타입 비교
> Amazon VPC Endpoint는 두 가지 타입이 있으며, 동작 방식이 다릅니다.
>
> **Interface Endpoint (ENI 기반)**:
>
> - 서브넷에 ENI(Elastic Network Interface)를 생성하여 프라이빗 IP를 할당합니다.
> - AWS PrivateLink 기술을 사용합니다.
> - 대부분의 AWS 서비스를 지원합니다. (AWS Systems Manager, Amazon CloudWatch, AWS KMS 등)
> - 시간당 요금 + 데이터 처리 요금이 발생합니다.
>
> **Gateway Endpoint (라우팅 테이블 기반)**:
>
> - 라우팅 테이블에 경로를 추가하여 트래픽을 전달합니다.
> - Amazon S3와 Amazon DynamoDB만 지원합니다.
> - 추가 비용이 발생하지 않습니다. (무료)

> [!DOWNLOAD]
> [week3-1-vpc-lab.zip](/files/week3/week3-1-vpc-lab.zip)
>
> - `week3-1-vpc-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 VPC, 서브넷, IGW, NAT Gateway, EC2 자동 생성)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (week3-1-vpc-lab.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon VPC 1개**: 퍼블릭/프라이빗 서브넷이 포함된 VPC (week3-1-vpc)
- **서브넷 4개**: 퍼블릭 서브넷 2개, 프라이빗 서브넷 2개
- **NAT Gateway 1개**: 프라이빗 서브넷의 인터넷 접근용
- **Amazon EC2 인스턴스 1개**: 프라이빗 서브넷에 배치된 테스트 인스턴스
- **AWS IAM 역할 1개**: Amazon EC2 인스턴스용 SSM 역할

Amazon VPC Endpoint(Interface Endpoint, Gateway Endpoint)는 태스크 1-2에서 직접 생성합니다.

> [!WARNING]
> NAT Gateway는 시간 단위로 비용이 발생합니다. 실습 종료 후 반드시 리소스를 삭제합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week3-1-vpc-lab.zip` 파일의 압축을 해제합니다.
2. `week3-1-vpc-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

<img src="/images/week3/3-1-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week3-1-vpc-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week3-1-vpc-stack`을 입력합니다.
10. **Parameters** 섹션에서 태그 관련 파라미터(`ProjectTag`, `WeekTag`, `CreatedByTag`)의 기본값을 확인합니다. 변경이 필요하면 수정합니다.
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week3/3-1-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> AWS CloudFormation 스택 목록 페이지로 자동 이동합니다. 페이지 중앙에 스택 목록 테이블이 표시됩니다.

18. 테이블에서 `week3-1-vpc-stack` 스택을 찾습니다.
19. 스택 행의 **Status** 열을 확인합니다.

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다. 스택 생성이 시작되면 다음과 같은 상태 변화가 나타납니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다.
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다.
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다. (Events 탭에서 원인 확인 필요)

20. `week3-1-vpc-stack` 스택을 클릭하여 상세 페이지로 이동합니다.
21. **Events** 탭을 선택합니다.

> [!NOTE]
> **Events** 탭에는 리소스 생성 과정이 실시간으로 표시됩니다. 각 리소스의 상태가 "CREATE_IN_PROGRESS" → "CREATE_COMPLETE" 순서로 변경됩니다. Amazon VPC, 서브넷, NAT Gateway, Amazon EC2 인스턴스 등이 순차적으로 생성됩니다. 스택 생성에 5-7분이 소요됩니다. 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다.

22. 페이지를 새로고침하여 최신 상태를 확인합니다.
23. 페이지 상단의 **Status** 필드를 확인합니다.
24. **Status**가 "**CREATE_COMPLETE**"로 변경될 때까지 22-23단계를 반복합니다.

> [!NOTE]
> 페이지 상단의 **Status** 필드는 전체 스택의 상태를 보여줍니다. "CREATE_IN_PROGRESS"에서 "CREATE_COMPLETE"로 변경되면 모든 리소스가 성공적으로 생성된 것입니다. 만약 "CREATE_FAILED"가 표시되면 **Events** 탭에서 오류 원인을 확인합니다.

25. **Outputs** 탭을 선택합니다.
26. 다음 5개의 출력값을 복사하여 메모장에 저장합니다:
    - `EC2InstanceId`: 테스트용 Amazon EC2 인스턴스 ID (예: i-059b2cacf31051563) — Session Manager 접속 및 Endpoint 동작 검증에 사용
    - `NatGatewayId`: NAT Gateway ID (예: nat-00c641f27402301d) — NAT Gateway 경유 확인 및 비교 테스트에 사용
    - `PrivateRouteTableAId`: 프라이빗 라우팅 테이블 A ID (예: rtb-0f0cf6518862c43a5) — Gateway Endpoint 라우팅 테이블 연결에 사용
    - `PrivateSubnetAId`: 프라이빗 서브넷 A ID (예: subnet-0a9c618bfe47719c1) — Interface Endpoint 서브넷 지정에 사용
    - `VpcId`: Amazon VPC ID (예: vpc-005596f39eb843d61) — Interface/Gateway Endpoint 생성 시 VPC 선택에 사용

> [!TIP]
> 이 출력값들은 이후 태스크에서 반복적으로 사용됩니다. 메모장에 복사해두면 실습을 원활하게 진행할 수 있습니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: AWS Systems Manager Interface Endpoint 생성

이 태스크에서는 AWS Systems Manager용 Interface Endpoint를 생성하여 프라이빗 서브넷에서 Session Manager로 Amazon EC2 인스턴스에 접속할 수 있도록 설정합니다.

> [!NOTE]
> Interface Endpoint는 ENI(Elastic Network Interface) 기반으로 동작하며, 시간당 요금이 부과됩니다. Session Manager를 사용하려면 3개의 Interface Endpoint(ssm, ssmmessages, ec2messages)가 필요합니다.

### 태스크 1.1: SSM Interface Endpoint 생성

27. AWS Management Console에 로그인한 후 상단 검색창에 `VPC`을 입력하고 선택합니다.
28. 왼쪽 메뉴에서 **Endpoints**를 선택합니다.
29. [[Create endpoint]] 버튼을 클릭합니다.
30. **Name tag**에 `week3-1-ssm-endpoint`를 입력합니다.
31. **Type** 섹션에서 **Select a category** 아래의 `AWS services`를 선택합니다.
32. **Services** 검색창에 `ssm`을 입력합니다.
33. 검색 결과에서 **Service Name**이 `com.amazonaws.ap-northeast-2.ssm`이고 **Type**이 `Interface`인 항목을 선택합니다.

> [!NOTE]
> SSM Interface Endpoint는 AWS Systems Manager 서비스에 접근하기 위한 엔드포인트입니다. Session Manager를 사용하려면 이 엔드포인트가 필수입니다.

34. **Amazon VPC**에서 메모장에 저장한 VpcId를 선택합니다.
35. **Subnets** 섹션으로 스크롤합니다.
36. **Availability Zone**에서 `ap-northeast-2a`를 선택합니다.
37. **Subnet ID**에서 메모장에 저장한 `PrivateSubnetAId`를 선택합니다.

> [!NOTE]
> Interface Endpoint는 선택한 서브넷에 ENI(Elastic Network Interface)를 생성합니다. 프라이빗 서브넷에 생성하여 인터넷을 거치지 않고 AWS 서비스에 접근합니다.

38. **Security groups** 섹션으로 스크롤합니다.
39. 기본 보안 그룹을 제거합니다.
40. 보안 그룹 검색창에 `week3-1`을 입력합니다.
41. `week3-1-endpoint-sg`를 선택합니다.

> [!NOTE]
> AWS CloudFormation이 생성한 보안 그룹은 HTTPS(443 포트) 인바운드 트래픽을 허용합니다. Interface Endpoint는 HTTPS를 통해 통신합니다.

42. **Policy** 섹션으로 스크롤합니다.
43. **Full access**를 선택한 상태로 유지합니다.
44. **Tags** 섹션으로 스크롤합니다.
45. [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `3-1`     |
| `CreatedBy` | `Student` |

46. [[Create endpoint]] 버튼을 클릭합니다.
47. Endpoint 목록 페이지로 이동합니다.
48. 생성한 `week3-1-ssm-endpoint`의 **Status**가 "Available"로 변경될 때까지 기다립니다.

> [!NOTE]
> Interface Endpoint 생성은 일반적으로 2-3분이 소요됩니다. 페이지를 새로고침하여 상태를 확인합니다.

✅ **하위 태스크 완료**: SSM Interface Endpoint가 생성되었습니다.

### 태스크 1.2: SSM Messages Interface Endpoint 생성

태스크 1.1과 동일한 방법으로 두 번째 Interface Endpoint를 생성합니다.

**달라지는 부분만 확인합니다:**

- **Name tag**: `week3-1-ssmmessages-endpoint`
- **Services** 검색: `ssmmessages`
- **Service Name**: `com.amazonaws.ap-northeast-2.ssmmessages` (Type: Interface)

> [!NOTE]
> SSM Messages Interface Endpoint는 Session Manager의 메시지 전송을 위한 엔드포인트입니다.

나머지 설정(Amazon VPC, 서브넷, 보안 그룹, 태그)은 태스크 1.1과 동일합니다.

✅ **하위 태스크 완료**: SSM Messages Interface Endpoint가 생성되었습니다.

### 태스크 1.3: Amazon EC2 Messages Interface Endpoint 생성

태스크 1.1과 동일한 방법으로 세 번째 Interface Endpoint를 생성합니다.

**달라지는 부분만 확인합니다:**

- **Name tag**: `week3-1-ec2messages-endpoint`
- **Services** 검색: `ec2messages`
- **Service Name**: `com.amazonaws.ap-northeast-2.ec2messages` (Type: Interface)

> [!NOTE]
> Amazon EC2 Messages Interface Endpoint는 Amazon EC2 인스턴스와 AWS Systems Manager 간의 통신을 위한 엔드포인트입니다. 3개의 Interface Endpoint가 모두 "Available" 상태가 되면 Session Manager를 사용할 수 있습니다.

나머지 설정(Amazon VPC, 서브넷, 보안 그룹, 태그)은 태스크 1.1과 동일합니다.

✅ **하위 태스크 완료**: Amazon EC2 Messages Interface Endpoint가 생성되었습니다.

✅ **태스크 완료**: AWS Systems Manager용 Interface Endpoint 3개가 생성되었습니다.

## 태스크 2: Amazon S3 Gateway Endpoint 생성

이 태스크에서는 Amazon S3 Gateway Endpoint를 생성하여 프라이빗 서브넷에서 Amazon S3에 안전하게 접근할 수 있도록 설정합니다.

> [!NOTE]
> Gateway Endpoint는 무료이며, 라우팅 테이블을 통해 트래픽을 라우팅합니다. Interface Endpoint와 달리 시간당 요금이 부과되지 않습니다.

49. AWS Management Console에 로그인한 후 상단 검색창에 `VPC`을 입력하고 선택합니다.
50. 왼쪽 메뉴에서 **Endpoints**를 선택합니다.
51. [[Create endpoint]] 버튼을 클릭합니다.
52. **Name tag**에 `week3-1-s3-endpoint`를 입력합니다.
53. **Type** 섹션에서 **Select a category** 아래의 `AWS services`를 선택합니다.
54. **Services** 검색창에 `s3`를 입력합니다.
55. 검색 결과에서 **Service Name**이 `com.amazonaws.ap-northeast-2.s3`이고 **Type**이 `Gateway`인 항목을 선택합니다.

> [!NOTE]
> Amazon S3는 Gateway Endpoint와 Interface Endpoint를 모두 지원합니다. Gateway Endpoint는 무료이므로 비용 효율적입니다.

56. **Amazon VPC**에서 메모장에 저장한 VpcId를 선택합니다.

> [!NOTE]
> Amazon VPC 드롭다운에서 Amazon VPC ID로 검색하면 쉽게 찾을 수 있습니다.

57. **Route tables** 섹션으로 스크롤합니다.
58. 메모장에 저장한 `PrivateRouteTableAId`에 해당하는 라우팅 테이블을 체크합니다.

> [!NOTE]
> 라우팅 테이블 이름에 "Private"가 포함되어 있는지 확인합니다. Gateway Endpoint는 선택한 라우팅 테이블에 자동으로 라우팅 규칙을 추가합니다.

59. **Policy** 섹션으로 스크롤합니다.
60. **Full access**를 선택한 상태로 유지합니다.

> [!NOTE]
> Full access 정책은 모든 Amazon S3 작업을 허용합니다. 프로덕션 환경에서는 특정 버킷만 접근하도록 제한하는 것이 좋습니다.

61. **Tags** 섹션으로 스크롤합니다.
62. [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `3-1`     |
| `CreatedBy` | `Student` |

63. [[Create endpoint]] 버튼을 클릭합니다.
64. Endpoint 목록 페이지로 이동합니다.
65. 생성한 `week3-1-s3-endpoint`의 **Status**가 "Available"로 변경될 때까지 기다립니다.

> [!NOTE]
> Gateway Endpoint 생성은 일반적으로 1-2분 내에 완료됩니다. 페이지를 새로고침하여 상태를 확인합니다.

✅ **태스크 완료**: Amazon S3 Gateway Endpoint가 생성되었습니다.

## 태스크 3: Interface Endpoint와 Gateway Endpoint 비교

이 태스크에서는 AWS 콘솔에서 Interface Endpoint와 Gateway Endpoint의 차이점을 직접 확인합니다.

66. Amazon VPC 콘솔에서 왼쪽 메뉴에서 **Endpoints**를 선택합니다.
67. Endpoint 목록에서 `week3-1-ssm-endpoint` (Interface Endpoint)를 클릭합니다.
68. **Details** 탭에서 다음 정보를 확인합니다:
    - **Status**: Available
    - **Endpoint type**: Interface
    - **VPC ID**: week3-1-vpc-VPC
    - **Service name**: com.amazonaws.ap-northeast-2.ssm
    - **Private DNS names enabled**: Yes
    - **DNS names**: 프라이빗 DNS 이름 여러 개 표시

> [!NOTE]
> Interface Endpoint는 ENI(Elastic Network Interface)를 생성하여 프라이빗 IP 주소를 할당받습니다. 이 IP 주소를 통해 AWS 서비스에 접근합니다.

69. 왼쪽 메뉴에서 **Endpoints**를 선택하여 목록으로 이동합니다.
70. `week3-1-s3-endpoint` (Gateway Endpoint)를 클릭합니다.
71. **Details** 탭에서 다음 정보를 확인합니다:
    - **Status**: Available
    - **Endpoint type**: Gateway
    - **VPC ID**: week3-1-vpc-VPC
    - **Service name**: com.amazonaws.ap-northeast-2.s3
    - **Private DNS names enabled**: No
72. 하단의 **Route tables** 탭에서 연결된 라우팅 테이블(`week3-1-vpc-Private-RT-A`)을 확인합니다.

> [!NOTE]
> Gateway Endpoint는 ENI를 생성하지 않고 라우팅 테이블에 경로를 추가하는 방식으로 동작합니다. 따라서 Network interfaces와 DNS names 정보가 없습니다.

73. 두 Endpoint의 **Details** 탭을 비교하여 다음 차이점을 확인합니다:

| 항목                                    | Interface Endpoint           | Gateway Endpoint      |
| --------------------------------------- | ---------------------------- | --------------------- |
| **Endpoint type** (Details)             | Interface                    | Gateway               |
| **Private DNS names enabled** (Details) | Yes                          | No                    |
| **Private DNS names** (Details)         | ✅ 2개 이상 표시             | ❌ – (없음)           |
| **DNS names** (Details)                 | ✅ 프라이빗 DNS 여러 개 제공 | ❌ 없음               |
| **Subnets** (하단 탭)                   | ✅ 서브넷/IP 주소 확인 가능  | ❌ 탭 없음            |
| **Security Groups** (하단 탭)           | ✅ 보안 그룹 적용 가능       | ❌ 탭 없음            |
| **Route tables** (하단 탭)              | ❌ 탭 없음                   | ✅ 라우팅 테이블 연결 |

> [!NOTE]
> **Interface Endpoint**는 ENI 기반으로 동작하여 프라이빗 IP 주소와 DNS 이름을 제공합니다. 보안 그룹으로 트래픽을 제어할 수 있습니다.
>
> **Gateway Endpoint**는 라우팅 테이블 기반으로 동작하여 Prefix List를 통해 트래픽을 라우팅합니다. 보안 그룹 대신 Endpoint 정책으로 접근을 제어합니다.

✅ **태스크 완료**: Interface Endpoint와 Gateway Endpoint의 차이점을 AWS 콘솔에서 확인했습니다.

## 태스크 4: 라우팅 테이블 확인

이 태스크에서는 Amazon VPC Endpoint가 라우팅 테이블에 자동으로 추가되었는지 확인합니다.

74. Amazon VPC 콘솔에서 왼쪽 메뉴에서 **Route tables**를 선택합니다.
75. 검색창에 메모장에 저장한 `PrivateRouteTableAId`를 입력하여 프라이빗 서브넷 라우팅 테이블을 찾습니다.
76. 해당 라우팅 테이블을 클릭합니다.
77. 하단의 **Routes** 탭을 선택합니다.
78. 라우팅 규칙 목록에서 Amazon S3 Gateway Endpoint가 자동으로 추가한 규칙을 찾습니다.
79. **Destination** 열에서 `pl-`로 시작하는 항목을 찾습니다.
80. 해당 항목의 **Target** 열에서 `vpce-`로 시작하는 항목을 확인합니다.

> [!NOTE]
> Gateway Endpoint는 라우팅 테이블에 자동으로 라우팅 규칙을 추가합니다. **Destination**의 Prefix List (pl-로 시작)는 Amazon S3 서비스의 IP 주소 범위를 나타냅니다. 이 Prefix List로 향하는 트래픽은 Amazon VPC Endpoint를 통해 라우팅됩니다.

81. 다른 라우팅 규칙들도 확인합니다.
82. **Destination**이 `10.0.0.0/16`인 항목의 **Target**이 `local`인지 확인합니다.
83. **Destination**이 `0.0.0.0/0`인 항목의 **Target**이 NAT Gateway(`nat-`로 시작)인지 확인합니다.

> [!NOTE]
> 라우팅 규칙의 의미:
>
> - `10.0.0.0/16` → `local`: Amazon VPC 내부 트래픽은 로컬로 라우팅
> - `0.0.0.0/0` → `nat-xxxxx`: 인터넷 트래픽은 NAT Gateway를 통해 라우팅
> - `pl-xxxxxxxx` → `vpce-xxxxx`: Amazon S3 트래픽은 Amazon VPC Endpoint를 통해 라우팅

✅ **태스크 완료**: 라우팅 테이블이 확인되었습니다.

## 태스크 5: Amazon VPC Endpoint 동작 검증

이 태스크에서는 Amazon VPC Endpoint만으로 Amazon S3에 접근할 수 있는지 실제로 검증합니다. NAT Gateway 경로를 일시적으로 제거하여 Amazon VPC Endpoint를 통한 Amazon S3 접근을 증명합니다.

### 태스크 5.1: 현재 상태 확인 (NAT Gateway + Amazon VPC Endpoint)

먼저 NAT Gateway와 Amazon VPC Endpoint가 모두 있는 현재 상태에서 Amazon S3 접근과 인터넷 접근을 확인합니다.

84. AWS Management Console에 로그인한 후 상단 검색창에 `EC2`을 입력하고 선택합니다.
85. 왼쪽 메뉴에서 **Instances**를 선택합니다.
86. 메모장에 저장한 EC2InstanceId를 확인합니다.
87. 검색창에 EC2InstanceId를 입력하여 인스턴스를 찾습니다.
88. 해당 인스턴스의 체크박스를 선택합니다.

> [!NOTE]
> 인스턴스 이름에 "week3-1"이 포함되어 있고, **Instance state**가 "Running"으로 표시되어야 합니다.

89. **Instance state**가 "Running"이고 **Status check**가 "2/2 checks passed"인지 확인합니다.

> [!NOTE]
> **Status check**는 인스턴스의 시스템 상태와 인스턴스 상태를 확인합니다. AWS CloudFormation 스택이 "CREATE_COMPLETE"로 완료되어도 인스턴스의 Status check가 아직 진행 중일 수 있습니다. "2/2 checks passed"가 표시될 때까지 기다립니다. 일반적으로 1-2분이 소요됩니다.

90. [[Connect]] 버튼을 클릭합니다.
91. **Session Manager** 탭을 선택합니다.

> [!NOTE]
> Session Manager를 사용하면 SSH 키 없이도 Amazon EC2 인스턴스에 안전하게 접속할 수 있습니다. AWS IAM 역할을 통해 인증되며, 모든 세션이 CloudTrail에 기록됩니다.

92. [[Connect]] 버튼을 클릭합니다.

> [!NOTE]
> 새 브라우저 탭이 열리고 터미널 화면이 표시됩니다. 터미널 연결에 10-20초가 소요될 수 있습니다. `bash-5.2$` 또는 `ssm-user@ip-10-0-x-x:~$` 형식의 프롬프트가 표시되면 준비된 것입니다.

93. 다음 명령어를 실행하여 Amazon S3 버킷 목록을 확인합니다:

```bash
aws s3 ls
```

94. Amazon S3 버킷 목록이 정상적으로 표시되는지 확인합니다.

> [!OUTPUT]
>
> ```
> # 계정에 Amazon S3 버킷이 있는 경우 버킷 목록이 표시됩니다.
> 2026-xx-xx xx:xx:xx your-bucket-name-1
> 2026-xx-xx xx:xx:xx your-bucket-name-2
>
> # 버킷이 없는 경우 빈 출력이 나타나며, 이는 정상입니다.
> # 명령어가 오류 없이 실행되면 Amazon S3 접근이 가능한 것입니다.
> ```

95. 다음 명령어를 실행하여 인터넷 연결을 확인합니다:

```bash
curl -I https://www.google.com
```

96. HTTP 응답 헤더가 정상적으로 수신되는지 확인합니다.

> [!OUTPUT]
>
> ```
> HTTP/2 200
> content-type: text/html; charset=ISO-8859-1
> ...
> ```

> [!NOTE]
> 현재 상태에서는 NAT Gateway를 통해 인터넷에 접근할 수 있고, Amazon S3에도 접근할 수 있습니다. 하지만 Amazon S3 접근이 Amazon VPC Endpoint를 통하는지 NAT Gateway를 통하는지 명확하지 않습니다.

97. Session Manager 창은 닫지 말고 그대로 유지합니다.

✅ **하위 태스크 완료**: 현재 상태에서 Amazon S3와 인터넷 접근이 모두 가능함을 확인했습니다.

### 태스크 5.2: NAT Gateway 경로 제거 후 Amazon VPC Endpoint 검증

NAT Gateway 경로를 제거하여 Amazon VPC Endpoint만으로 Amazon S3에 접근할 수 있는지 검증합니다.

> [!NOTE]
> **Session Manager 세션 유지**: SSM Interface Endpoints가 미리 생성되어 있으므로 NAT Gateway 경로를 제거해도 Session Manager 세션은 유지됩니다. 만약 세션이 끊긴 경우, Amazon EC2 콘솔에서 다시 Connect > Session Manager로 접속합니다. SSM Interface Endpoints가 있으므로 NAT Gateway 없이도 새 세션을 시작할 수 있습니다.

98. Amazon VPC 콘솔로 이동합니다.
99. 왼쪽 메뉴에서 **Route tables**를 선택합니다.
100.  검색창에 메모장에 저장한 `PrivateRouteTableAId`를 입력하여 프라이빗 라우팅 테이블을 찾습니다.
101.  해당 라우팅 테이블을 선택합니다.
102.  하단의 **Routes** 탭을 선택합니다.
103.  **Destination**이 `0.0.0.0/0`이고 **Target**이 NAT Gateway(`nat-`로 시작)인 라우팅 규칙을 찾습니다.
104.  [[Edit routes]] 버튼을 클릭합니다.
105.  **Destination**이 `0.0.0.0/0`인 라우팅 규칙 오른쪽의 [[Remove]] 버튼을 클릭합니다.

> [!IMPORTANT]
> NAT Gateway 경로를 제거하면 인터넷 접근이 차단됩니다. 하지만 Amazon VPC Endpoint 경로(pl-xxx → vpce-xxx)는 그대로 유지되므로 Amazon S3 접근은 가능해야 합니다.

106. [[Save changes]] 버튼을 클릭합니다.
107. Session Manager 창으로 이동합니다.
108. 다음 명령어를 실행하여 인터넷 연결이 차단되었는지 확인합니다:

```bash
curl -I --max-time 5 https://www.google.com
```

109. 연결 타임아웃 오류가 발생하는지 확인합니다.

> [!OUTPUT]
>
> ```
> curl: (28) Connection timed out after 5001 milliseconds
> ```

> [!NOTE]
> NAT Gateway 경로가 제거되었으므로 인터넷 접근이 차단되었습니다. 이제 Amazon VPC Endpoint만으로 Amazon S3에 접근할 수 있는지 확인합니다.

110. 다음 명령어를 실행하여 Amazon S3 버킷 목록을 확인합니다:

```bash
aws s3 ls
```

111. Amazon S3 버킷 목록이 정상적으로 표시되는지 확인합니다.

> [!OUTPUT]
>
> ```
> # 계정에 Amazon S3 버킷이 있는 경우 버킷 목록이 표시됩니다
> 2026-xx-xx xx:xx:xx your-bucket-name-1
> 2026-xx-xx xx:xx:xx your-bucket-name-2
>
> # 버킷이 없는 경우 빈 출력이 나타나며, 이는 정상입니다
> # 명령어가 오류 없이 실행되면 Amazon S3 접근이 가능한 것입니다
> ```

> [!SUCCESS]
> **Amazon VPC Endpoint 검증 성공**: 인터넷 접근이 차단된 상태에서도 Amazon S3에 접근할 수 있습니다. 이는 Amazon VPC Endpoint를 통해 Amazon S3에 접근하고 있음을 증명합니다.

✅ **하위 태스크 완료**: Amazon VPC Endpoint만으로 Amazon S3 접근이 가능함을 검증했습니다.

### 태스크 5.3: NAT Gateway 경로 복원

실습 환경을 원래 상태로 복원합니다.

112. Amazon VPC 콘솔로 이동합니다.
113. 왼쪽 메뉴에서 **Route tables**를 선택합니다.
114. 프라이빗 라우팅 테이블을 선택합니다.
115. 하단의 **Routes** 탭을 선택합니다.
116. [[Edit routes]] 버튼을 클릭합니다.
117. [[Add route]] 버튼을 클릭합니다.
118. **Destination**에 `0.0.0.0/0`을 입력합니다.
119. **Target**에서 `NAT Gateway`를 선택합니다.
120. 드롭다운에서 메모장에 저장한 NatGatewayId를 선택합니다.

> [!NOTE]
> NAT Gateway ID는 `nat-`로 시작합니다. 메모장에 저장한 값을 참고하여 선택합니다.

121. [[Save changes]] 버튼을 클릭합니다.
122. Session Manager 창으로 이동합니다.
123. 다음 명령어를 실행하여 인터넷 연결이 복원되었는지 확인합니다:

```bash
curl -I https://www.google.com
```

124. HTTP 응답 헤더가 정상적으로 수신되는지 확인합니다.

> [!OUTPUT]
>
> ```
> HTTP/2 200
> content-type: text/html; charset=ISO-8859-1
> ...
> ```

125. Session Manager 창을 닫습니다.

✅ **하위 태스크 완료**: 실습 환경이 원래 상태로 복원되었습니다.

✅ **태스크 완료**: Amazon VPC Endpoint의 동작을 실제로 검증하고 이해했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 Amazon VPC 환경을 자동으로 구축했습니다.
- AWS Systems Manager용 Interface Endpoint 3개를 생성하여 Session Manager 접속을 구성했습니다.
- Amazon S3 Gateway Endpoint를 생성하여 프라이빗 서브넷에서 Amazon S3에 안전하게 접근했습니다.
- Interface Endpoint와 Gateway Endpoint의 차이점을 이해했습니다.
- 라우팅 테이블을 통한 트래픽 제어 방식을 확인했습니다.
- Amazon VPC Endpoint의 동작 원리를 실제로 검증했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

---

### 단계 1: Tag Editor로 생성된 리소스 확인

실습에서 생성한 모든 리소스를 Tag Editor로 확인합니다.

#### 수동으로 생성한 리소스 확인 (Week 태그)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `3-1`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> Tag Editor에서 `Week=3-1` 태그로 검색하면 AWS CloudFormation으로 생성된 리소스(VPC, 서브넷, NAT Gateway, EC2 등)가 표시됩니다.
> 단, Amazon VPC Endpoint는 Tag Editor에서 지원하지 않아 검색 결과에 표시되지 않습니다. Endpoint는 VPC 콘솔에서 직접 확인하고 삭제해야 합니다.

#### AWS CloudFormation으로 생성한 리소스 확인 (Name 태그)

7. **Tags** 섹션을 초기화하고 다음을 입력합니다:
   - **Tag key**: `Name`
   - **Optional tag value**에 `week3-1`을 입력합니다.
8. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> AWS CloudFormation 스택으로 생성된 Amazon VPC, 서브넷, NAT Gateway, Amazon EC2 인스턴스 등 모든 리소스가 표시됩니다. 리소스 이름이 `week3-1-`로 시작하는 것들이 이 실습에서 생성된 리소스입니다.

> [!TIP]
> Tag Editor는 리소스 확인 용도로만 사용하며, 실제 삭제는 다음 단계에서 수행합니다. 두 가지 태그 검색을 통해 수동 생성 리소스와 AWS CloudFormation 생성 리소스를 모두 파악할 수 있습니다.

---

### 단계 2: 리소스 삭제

다음 두 가지 방법 중 하나를 선택하여 리소스를 삭제할 수 있습니다.

### 옵션 1: AWS 콘솔에서 수동 삭제 (권장)

> [!TIP]
> AWS 관리 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 권장합니다.
>
> AWS CLI 명령어에 익숙한 경우 아래 [옵션 2](#option-2)를 사용하면 더 빠르게 삭제할 수 있습니다.

**Amazon VPC Endpoint 삭제**

9. Amazon VPC 콘솔로 이동합니다.
10. 왼쪽 메뉴에서 **Endpoints**를 선택합니다.
11. 다음 4개의 엔드포인트를 모두 선택합니다:
    - `week3-1-ssm-endpoint`
    - `week3-1-ssmmessages-endpoint`
    - `week3-1-ec2messages-endpoint`
    - `week3-1-s3-endpoint`

> [!NOTE]
> 4개의 엔드포인트를 모두 선택하려면 각 엔드포인트의 체크박스를 클릭합니다. 모두 선택되면 상단의 **Actions** 버튼이 활성화됩니다.

12. **Actions** > `Delete Amazon VPC endpoints`를 선택합니다.
13. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon VPC Endpoint 삭제는 즉시 완료됩니다. Interface Endpoint 3개와 Gateway Endpoint 1개가 모두 삭제됩니다.

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 위 [옵션 1](#option-1)을 참고합니다.

14. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
15. CloudShell이 열리면 다음 명령어를 실행합니다:

```bash
# Week 3-1 태그가 있는 Amazon VPC Endpoint 찾기
ENDPOINT_IDS=$(aws ec2 describe-vpc-endpoints \
  --region ap-northeast-2 \
  --filters "Name=tag:Week,Values=3-1" \
  --query 'VpcEndpoints[*].VpcEndpointId' \
  --output text)

# 삭제 대상 확인
echo $ENDPOINT_IDS
```

16. 출력된 Endpoint ID 목록(vpce-로 시작하는 4개)을 확인합니다.
17. 다음 명령어를 실행하여 Amazon VPC Endpoint를 삭제합니다:

```bash
# Amazon VPC Endpoint 삭제
if [ -n "$ENDPOINT_IDS" ]; then
  echo "삭제할 Amazon VPC Endpoints: $ENDPOINT_IDS"
  aws ec2 delete-vpc-endpoints \
    --region ap-northeast-2 \
    --vpc-endpoint-ids $ENDPOINT_IDS
  echo "Amazon VPC Endpoints 삭제 완료"
else
  echo "삭제할 Amazon VPC Endpoint가 없습니다"
fi
```

> [!NOTE]
> 스크립트는 `Week=3-1` 태그가 있는 모든 Amazon VPC Endpoint를 자동으로 찾아 삭제합니다. `Unsuccessful` 배열이 비어있으면 모든 Endpoint가 정상 삭제된 것입니다.

**삭제 확인**

18. Amazon VPC 콘솔로 이동합니다.
19. 왼쪽 메뉴에서 **Endpoints**를 선택합니다.
20. 검색창에 `week3-1`을 입력하여 Endpoint가 남아있지 않은지 확인합니다.

> [!NOTE]
> 4개의 Endpoint가 모두 목록에서 사라졌으면 삭제가 완료된 것입니다. 삭제 직후 잠시 "Deleting" 상태로 표시될 수 있으나, 새로고침하면 사라집니다.

---

### 단계 3: AWS CloudFormation 스택 삭제

마지막으로 AWS CloudFormation 스택을 삭제하여 나머지 모든 리소스를 정리합니다.

21. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
22. 스택 목록에서 `week3-1-vpc-stack` 스택을 검색합니다.
23. `week3-1-vpc-stack` 스택의 체크박스를 선택합니다.

> [!NOTE]
> 스택이 선택되면 체크박스에 체크 표시가 나타나고, 상단의 [[Delete stack]] 버튼이 활성화됩니다.

24. [[Delete stack]] 버튼을 클릭합니다.
25. 확인 창에서 스택 이름 `week3-1-vpc-stack`을 입력합니다.
26. [[Delete stack]] 버튼을 클릭하여 삭제를 확인합니다.

> [!NOTE]
> 확인 후 스택 목록 페이지로 이동합니다.

27. `week3-1-vpc-stack` 스택의 **Status** 열을 확인합니다.

> [!NOTE]
> 스택 삭제가 시작되면 **Status**가 "DELETE_IN_PROGRESS"로 표시됩니다. AWS CloudFormation이 생성한 모든 리소스를 역순으로 삭제합니다.

28. 스택을 클릭하여 상세 페이지로 이동합니다.
29. **Events** 탭을 선택합니다.

> [!NOTE]
> **Events** 탭에는 리소스 삭제 과정이 실시간으로 표시됩니다. Amazon EC2 인스턴스, NAT Gateway, 서브넷, Amazon VPC 등이 순차적으로 삭제됩니다. 삭제에 5-7분이 소요됩니다.

30. 스택 삭제가 완료될 때까지 기다립니다.

> [!NOTE]
> 스택이 완전히 삭제되면 스택 목록에서 사라집니다. 만약 "DELETE_FAILED"가 표시되면 **Events** 탭에서 오류 원인을 확인하고, 수동으로 리소스를 삭제한 후 스택 삭제를 다시 시도합니다.

31. 스택 목록 페이지로 돌아가서 `week3-1-vpc-stack` 스택이 목록에서 사라졌는지 확인합니다.

> [!NOTE]
> 스택이 목록에 표시되지 않으면 성공적으로 삭제된 것입니다. 삭제 완료까지 5-7분이 소요됩니다.

---

### 단계 4: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

32. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
33. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
34. **Regions**에서 `ap-northeast-2`를 선택합니다.
35. **Resource types**에서 `All supported resource types`를 선택합니다.
36. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `3-1`
37. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 스택 삭제 직후에는 일부 리소스(Amazon EC2 인스턴스, NAT Gateway 등)가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다. 실제 서비스 콘솔에서 확인하면 이미 삭제 처리되어 있습니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

38. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
39. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
40. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
41. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
42. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [Amazon VPC Endpoints 개요](https://docs.aws.amazon.com/ko_kr/vpc/latest/privatelink/vpc-endpoints.html)
- [Gateway Endpoint vs Interface Endpoint](https://docs.aws.amazon.com/ko_kr/vpc/latest/privatelink/vpce-gateway.html)
- [Amazon VPC Endpoint 정책](https://docs.aws.amazon.com/ko_kr/vpc/latest/privatelink/vpc-endpoints-access.html)

## 📚 참고: Amazon VPC Endpoint 핵심 개념

### Gateway Endpoint vs Interface Endpoint

| 구분            | Gateway Endpoint           | Interface Endpoint              |
| :-------------- | :------------------------- | :------------------------------ |
| **지원 서비스** | Amazon S3, Amazon DynamoDB | 대부분의 AWS 서비스             |
| **구현 방식**   | 라우팅 테이블              | ENI (Elastic Network Interface) |
| **비용**        | 무료                       | 시간당 요금 + 데이터 전송 요금  |
| **가용 영역**   | 리전 전체                  | AZ별로 생성 필요                |
| **보안 그룹**   | 지원 안 함                 | 지원                            |

### Amazon VPC Endpoint 사용 이점

**보안 강화**

- 인터넷을 거치지 않고 AWS 서비스에 접근
- 퍼블릭 IP 주소 불필요
- 데이터가 AWS 네트워크 내부에서만 이동

**성능 향상**

- 낮은 지연 시간
- 높은 처리량
- NAT Gateway 부하 감소

**비용 절감**

- NAT Gateway 데이터 전송 비용 절감
- Gateway Endpoint는 무료

### Amazon VPC Endpoint 정책

Amazon VPC Endpoint 정책을 사용하여 접근을 제어할 수 있습니다:

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

💡 **권장**: 프로덕션 환경에서는 Amazon VPC Endpoint 정책으로 특정 버킷만 접근하도록 제한합니다.
