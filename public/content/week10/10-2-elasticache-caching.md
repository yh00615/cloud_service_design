---
title: 'Amazon ElastiCache 캐싱'
week: 10
session: 2
awsServices:
  - Amazon ElastiCache
learningObjectives:
  - 캐싱 전략(Cache-Aside, Write-Through)과 Valkey 데이터 구조를 이해할 수 있습니다.
  - Amazon ElastiCache Valkey 캐시를 생성하고 엔드포인트를 확인할 수 있습니다.
  - Amazon EC2 인스턴스에서 Valkey CLI로 기본 명령어를 실습할 수 있습니다.
  - Cache-Aside 패턴을 적용한 애플리케이션을 테스트할 수 있습니다.
prerequisites:
  - Week 4-3 QuickTable 예약 API 실습 완료 (Amazon DynamoDB 기본 지식)
  - Python 기본 문법 이해
---

이 실습에서는 Amazon ElastiCache for Valkey를 사용하여 QuickTable 레스토랑 예약 시스템의 성능을 향상시킵니다.
Valkey는 Redis OSS와 완전 호환되는 오픈소스 인메모리 데이터 저장소로, Linux Foundation에서 관리됩니다. AWS는 Valkey를 ElastiCache의 권장 엔진으로 제공하며, Redis OSS 대비 최대 33% 저렴합니다.
Cache-Aside 패턴을 구현하여 데이터베이스 조회 속도를 10-50배 빠르게 만들고, 캐시 히트율을 측정하여 캐싱 효과를 정량적으로 확인합니다.

> [!DOWNLOAD]
> [week10-2-elasticache-lab.zip](/files/week10/week10-2-elasticache-lab.zip)
>
> - `week10-2-elasticache-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 실습 환경 자동 생성)
> - `app.py` - FastAPI 애플리케이션 (Cache-Aside 패턴 구현, DynamoDB + Valkey)
> - `requirements.txt` - Python 의존성 패키지
> - `.env.example` - 환경 변수 설정 예제
> - `init_dynamodb.py` - DynamoDB 테이블 초기화 스크립트
> - `benchmark.py` - 성능 벤치마크 스크립트
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation으로 Amazon VPC, Amazon ElastiCache 서브넷 그룹, Amazon DynamoDB 테이블, Amazon S3 버킷 자동 생성)
> - 태스크 5: 실전 애플리케이션으로 Cache-Aside 패턴 테스트 (app.py를 Amazon EC2에서 실행하여 캐시 성능 측정)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **반드시 삭제해야 합니다**.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon VPC 및 네트워크**: Amazon VPC, 퍼블릭/프라이빗 서브넷, 인터넷 게이트웨이, NAT Gateway
- **보안 그룹**: Amazon ElastiCache 보안 그룹, Amazon EC2 보안 그룹
- **Amazon ElastiCache Subnet Group**: Valkey 캐시 배치를 위한 서브넷 그룹
- **SSM 인스턴스 프로파일**: Amazon EC2에서 Session Manager 접속을 위한 AWS IAM 역할 및 인스턴스 프로파일
- **Amazon DynamoDB 테이블**: QuickTable 예약 데이터 저장용 테이블
- **Amazon S3 버킷**: 실습 파일 업로드 및 EC2 다운로드용 버킷

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
2. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

<img src="/images/week10/10-2-task0-step4-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

3. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
4. **Specify template**에서 `Upload a template file`을 선택합니다.
5. [[Choose file]] 버튼을 클릭한 후 다운로드한 `week10-2-elasticache-lab.yaml` 파일을 선택합니다.
6. [[Next]] 버튼을 클릭합니다.

<img src="/images/week10/10-2-task0-step6-upload.png" alt="CloudFormation 템플릿 업로드" class="guide-img-md" />

7. **Stack name**에 `week10-2-quicktable-cache-stack`을 입력합니다.
8. **Parameters** 섹션에서 기본값을 확인합니다:
   - **CacheNodeType**: `cache.t3.micro`
   - **CreatedByTag**: `CloudFormation`
   - **EnvironmentName**: `week10-2-elasticache-lab`
   - **ProjectTag**: `AWS-Lab`
   - **WeekTag**: `10-2`
9. [[Next]] 버튼을 클릭합니다.

<img src="/images/week10/10-2-task0-step9-parameters.png" alt="CloudFormation Parameters 설정" class="guide-img-md" />

10. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

11. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
12. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week10/10-2-task0-step14-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

13. [[Next]] 버튼을 클릭합니다.
14. **Review and create** 페이지에서 설정을 확인합니다.
15. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다.
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다.
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다. (Events 탭에서 원인 확인 필요)
>
> 스택 생성에 5-7분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

16. **Outputs** 탭을 선택합니다.

    <img src="/images/week10/10-2-task0-step16-create-progress.png" alt="CloudFormation 스택 생성 완료" class="guide-img-md" />

17. 출력값들을 확인하고 메모장에 복사합니다:
    - `VpcId`: Amazon VPC ID (예: vpc-0123456789abcdef0)
    - `PrivateSubnetAId`: 프라이빗 서브넷 A ID (예: subnet-0a1b2c3d4e5f6g7h8)
    - `PrivateSubnetCId`: 프라이빗 서브넷 C ID (예: subnet-9i8h7g6f5e4d3c2b1)
    - `ElastiCacheSecurityGroupId`: Amazon ElastiCache 보안 그룹 ID (예: sg-0123456789abcdef0)
    - `EC2SecurityGroupId`: Amazon EC2 보안 그룹 ID (예: sg-9876543210fedcba0)
    - `SSMInstanceProfileName`: SSM 인스턴스 프로파일 이름
    - `ElastiCacheSubnetGroupName`: Amazon ElastiCache 서브넷 그룹 이름
    - `APIDataTableName`: Amazon DynamoDB 테이블 이름
    - `LabFilesBucketName`: 실습 파일 업로드용 Amazon S3 버킷 이름

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon ElastiCache Valkey 캐시 생성

### 태스크 설명

이 태스크에서는 Amazon ElastiCache for Valkey 캐시를 생성합니다.
Valkey는 Redis OSS 호환 오픈소스 인메모리 데이터 저장소로, 데이터베이스 조회 결과를 캐싱하여 애플리케이션 성능을 크게 향상시킬 수 있습니다.

> [!CONCEPT] Valkey란?
> Valkey는 2024년 Redis OSS의 라이선스 변경(SSPL/RSALv2) 이후 Linux Foundation에서 시작된 오픈소스 프로젝트입니다.
>
> - Redis OSS v7.0과 완전 호환 (명령어, 데이터 구조, 클라이언트 라이브러리 동일)
> - AWS가 ElastiCache의 권장 엔진으로 제공
> - Redis OSS 대비 최대 33% 저렴 (Serverless 기준)
> - 기존 Redis 클라이언트(redis-cli, redis-py 등)를 그대로 사용 가능

### 상세 단계

18. AWS Management Console에 로그인한 후 상단 검색창에 `ElastiCache`를 입력하고 선택합니다.
19. 왼쪽 메뉴에서 **Valkey caches**를 선택합니다.
20. [[Create cache]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task1-step20-elasticache-console.png" alt="ElastiCache Valkey caches - Create cache" class="guide-img-md" />

> [!NOTE]
> 왼쪽 메뉴에 Redis OSS caches도 있지만, AWS는 Valkey를 권장 엔진으로 제공합니다. Valkey는 Redis OSS와 완전 호환되므로 기존 Redis 명령어와 클라이언트를 그대로 사용할 수 있습니다.

21. **Engine**에서 `Valkey - recommended`가 선택되어 있는지 확인합니다.
22. **Deployment option**에서 `Node-based cluster`를 선택합니다.

> [!NOTE]
> **Serverless**는 자동 스케일링을 제공하지만, 이 실습에서는 캐시 구성을 직접 설정하는 학습 목적으로 **Node-based cluster**를 선택합니다.

23. **Creation method**에서 `Cluster cache`를 선택합니다.

    <img src="/images/week10/10-2-task1-step23-cache-settings.png" alt="Create cache - Creation method 선택" class="guide-img-md" />

> [!NOTE]
> `Easy create`는 권장 설정으로 빠르게 생성하지만, 이 실습에서는 캐시 구성을 직접 설정하는 학습 목적으로 `Cluster cache`를 선택합니다.

24. **Cluster mode**에서 `Disabled`를 선택합니다.

> [!NOTE]
> Cluster mode Disabled는 단일 샤드(노드 그룹)로 구성됩니다. 이 실습에서는 단순한 캐싱 용도이므로 Disabled로 충분합니다.

25. **Cluster info** 섹션에서 **Name**에 `quicktable-cache`, **Description**에 `QuickTable reservation cache`를 입력합니다.

    <img src="/images/week10/10-2-task1-step25-cluster-info.png" alt="Cluster info - Name, Description 입력" class="guide-img-md" />

26. **Location**에서 `AWS Cloud`를 선택합니다 (기본값).
27. **Multi-AZ**의 `Enable` 체크를 해제합니다.
28. **Auto-failover**의 `Enable` 체크를 해제합니다.

    <img src="/images/week10/10-2-task1-step28-node-type.png" alt="Node type 및 설정" class="guide-img-md" />

> [!NOTE]
> Multi-AZ와 Auto-failover는 고가용성을 위한 설정입니다. 이 실습에서는 레플리카를 0으로 설정하므로 비활성화합니다.

29. **Engine version**에서 최신 버전을 선택합니다 (예: `8.2`).

> [!NOTE]
> ElastiCache 콘솔에서 Valkey 엔진 버전 `8.0`, `8.1`, `8.2` 등이 표시될 수 있습니다. 최신 버전을 선택해도 실습 진행에는 문제 없습니다.

30. **Port**는 `6379` (기본값)을 유지합니다.
31. **Parameter groups**는 기본값을 유지합니다.
32. **Node type**에서 `cache.t3.micro`를 선택합니다.

> [!NOTE]
> 기본값은 `cache.r7g.large`로 설정되어 있습니다. 실습 비용을 줄이기 위해 반드시 `cache.t3.micro`로 변경합니다.

33. **Number of replicas**에서 `0`을 입력합니다.

    <img src="/images/week10/10-2-task1-step33-subnet-group.png" alt="Connectivity - Subnet group 설정" class="guide-img-md" />

34. **Connectivity** 섹션에서 **Network type**은 `IPv4`를 유지합니다.
35. **Subnet groups**에서 `Choose existing subnet group`을 선택하고, 태스크 0에서 생성한 서브넷 그룹을 선택합니다.

> [!NOTE]
> 서브넷 그룹을 선택하면 **Associated subnets**에 프라이빗 서브넷 2개 (ap-northeast-2a, ap-northeast-2c)가 자동으로 표시됩니다.

36. **Availability Zone placements**에서 `No preference`를 선택합니다.
37. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task1-step37-security.png" alt="Security 설정" class="guide-img-md" />

38. **Security** 섹션에서 **Encryption at rest**의 `Enable` 체크를 해제합니다.

39. **Encryption in transit**의 `Enable` 체크를 해제합니다.
40. **Selected security groups**에서 [[Manage]] 버튼을 클릭하고, 태스크 0에서 생성한 `week10-2-elasticache-lab-ElastiCache-SG` 보안 그룹을 선택합니다.

> [!NOTE]
> 기본 보안 그룹이 선택되어 있으면 해제하고, ElastiCache 전용 보안 그룹만 선택합니다.

41. **Backup** 섹션에서 `Enable automatic backups`의 체크를 해제합니다.

    <img src="/images/week10/10-2-task1-step41-tags.png" alt="Tags 설정" class="guide-img-md" />

42. **Maintenance** 섹션은 기본값을 유지합니다.
    - **Maintenance window**: `No preference`
    - **Auto upgrade minor versions**: `Enable`
    - **Topic for Amazon SNS notification**: `Disable notifications`
43. **Logs** 섹션은 기본값 (모두 체크 해제)을 유지합니다.

    <img src="/images/week10/10-2-task1-step43-logs.png" alt="Logs 섹션 기본값 유지" class="guide-img-md" />

44. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-2`    |
| `CreatedBy` | `Student` |

45. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task1-step45-next.png" alt="Tags 설정 후 Next" class="guide-img-md" />

46. **Review and create** 페이지에서 설정을 확인합니다.

    <img src="/images/week10/10-2-task1-step46-review.png" alt="Review and create 페이지" class="guide-img-md" />

47. [[Create]] 버튼을 클릭합니다.

> [!NOTE]
> 캐시 생성에 5-10분이 소요됩니다. 상태가 "Available"로 변경될 때까지 기다립니다. 페이지를 새로고침하여 상태를 확인합니다.

> [!TIP]
> 프로덕션 환경에서는 다음을 권장합니다:
>
> - **Number of replicas**: 1개 이상 (고가용성)
> - **Encryption at rest**: 활성화 (데이터 보안)
> - **Encryption in-transit**: 활성화 (전송 보안)
> - **Automatic backups**: 활성화 (데이터 복구)
> - **Multi-AZ**: 활성화 (장애 대응)

✅ **태스크 완료**: Amazon ElastiCache Valkey 캐시가 생성되었습니다.

<img src="/images/week10/10-2-task1-complete.png" alt="ElastiCache Valkey 캐시 생성 완료" class="guide-img-md" />

## 태스크 2: Valkey 엔드포인트 확인

### 태스크 설명

이 태스크에서는 생성된 Valkey 캐시의 Primary endpoint를 확인하고 복사합니다.
이 엔드포인트는 애플리케이션에서 Valkey에 연결할 때 사용됩니다.

### 상세 단계

48. Amazon ElastiCache 콘솔에서 `quicktable-cache` 캐시를 선택합니다.
49. **Cluster details** 섹션에서 **Primary endpoint**를 확인합니다.

    <img src="/images/week10/10-2-task2-step49-endpoint.png" alt="ElastiCache Primary endpoint 확인" class="guide-img-md" />

50. Primary endpoint 값을 복사하여 메모장에 저장합니다.

> [!NOTE]
> Primary endpoint 형식은 `quicktable-cache.xxxxx.ng.0001.apne2.cache.amazonaws.com:6379`입니다.
> 포트 번호(`:6379`)를 제외한 호스트명만 복사합니다.

> [!IMPORTANT]
> 이 엔드포인트는 태스크 5에서 FastAPI 애플리케이션 환경 변수로 사용됩니다.

✅ **태스크 완료**: Valkey 엔드포인트를 확인했습니다.

## 태스크 3: Amazon EC2 인스턴스 생성 및 Valkey CLI 설치

### 태스크 설명

이 태스크에서는 Valkey CLI를 설치할 Amazon EC2 인스턴스를 생성하고, Session Manager를 통해 접속합니다.
Valkey CLI를 사용하여 기본 명령어를 실습하고 캐싱 동작을 이해합니다.

> [!NOTE]
> Valkey는 Redis OSS와 완전 호환되므로 redis-cli를 그대로 사용할 수 있습니다. 이 실습에서는 valkey-cli를 설치하여 사용합니다.

### 상세 단계

51. AWS Management Console에 로그인한 후 상단 검색창에 `EC2`을 입력하고 선택합니다.
52. 왼쪽 메뉴에서 **Instances**를 선택합니다.
53. [[Launch instances]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task3-step53-ec2-console.png" alt="EC2 Launch instances" class="guide-img-md" />

54. **Name**에 `quicktable-cache-client`를 입력합니다.

    <img src="/images/week10/10-2-task3-step54-name-tags.png" alt="EC2 Name 및 Tags 설정" class="guide-img-md" />

55. **Add additional tags** 링크를 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `10-2`    |
| `CreatedBy` | `Student` |

<img src="/images/week10/10-2-task3-step55-tags.png" alt="Additional tags 추가" class="guide-img-md" />

56. **Application and OS Images**에서 `Amazon Linux 2023 AMI`를 선택합니다.

    <img src="/images/week10/10-2-task3-step56-ami.png" alt="AMI 선택" class="guide-img-md" />

57. **Instance type**에서 `t3.micro`를 선택합니다.
58. **Key pair**에서 `Proceed without a key pair`를 선택합니다.

    <img src="/images/week10/10-2-task3-step58-keypair.png" alt="Key pair - Proceed without a key pair" class="guide-img-md" />

59. **Network settings**에서 [[Edit]] 버튼을 클릭한 후 **Amazon VPC**는 태스크 0에서 생성한 VPC, **Subnet**은 프라이빗 서브넷 중 하나, **Auto-assign public IP**는 `Disable`을 선택합니다.
60. **Firewall (security groups)**에서 `Select existing security group`을 선택하고, 태스크 0에서 생성한 `week10-2-elasticache-lab-EC2-SG` 보안 그룹을 선택합니다.

    <img src="/images/week10/10-2-task3-step60-security-group.png" alt="Security group 선택" class="guide-img-md" />

61. **Advanced details** 섹션을 확장합니다.
62. **IAM instance profile**에서 태스크 0에서 생성한 `week10-2-elasticache-lab-SSMInstanceProfile`을 선택합니다.

    <img src="/images/week10/10-2-task3-step63-launch.png" alt="IAM instance profile 및 Launch instance" class="guide-img-md" />

63. [[Launch instance]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task3-step63-launch-success.png" alt="Launch instance 완료" class="guide-img-md" />

> [!NOTE]
> 인스턴스 생성이 완료될 때까지 기다립니다. 상태가 "Running"으로 변경되면 다음 단계를 진행합니다.

64. 인스턴스를 선택합니다.
65. [[Connect]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task3-step65-ssm-connect.png" alt="EC2 Connect 버튼" class="guide-img-md" />

66. **SSM Session Manager** 탭을 선택합니다.
67. [[Connect]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-task3-step67-ssm-session.png" alt="Session Manager Connect" class="guide-img-md" />

> [!NOTE]
> Session Manager는 SSH 키 없이 안전하게 Amazon EC2 인스턴스에 접속할 수 있는 AWS Systems Manager 기능입니다.
> AWS IAM 역할을 통해 인증되므로 별도의 키 관리가 필요 없습니다.

68. Session Manager 터미널이 열리면 다음 명령어로 Valkey CLI를 설치합니다:

```bash
sudo yum install -y gcc make
cd /tmp
wget https://github.com/valkey-io/valkey/archive/refs/tags/8.0.7.tar.gz
tar xvzf 8.0.7.tar.gz
cd valkey-8.0.7
make
sudo cp src/valkey-cli /usr/local/bin/
```

<img src="/images/week10/10-2-task4-step68-valkey-install1.png" alt="Valkey CLI 설치 진행" class="guide-img-md" />

<img src="/images/week10/10-2-task4-step68-valkey-install2.png" alt="Valkey CLI 설치 완료" class="guide-img-sm" />

> [!NOTE]
> Valkey 8.0.7은 8.0.x 시리즈의 최신 안정 버전입니다 (2026년 2월 릴리스). Valkey 9.0.x 시리즈도 출시되었으나, ElastiCache에서 사용하는 엔진 버전과 맞추기 위해 8.0.x를 사용합니다.
> 최신 버전은 [Valkey Releases](https://github.com/valkey-io/valkey/releases) 페이지에서 확인할 수 있으며, 위 명령어의 버전 번호(`8.0.7`)를 변경하여 사용합니다.

69. Valkey CLI 설치를 확인합니다:

```bash
valkey-cli --version
```

<img src="/images/week10/10-2-task4-step69-valkey-version.png" alt="valkey-cli 버전 확인" class="guide-img-sm" />

> [!OUTPUT]
>
> ```
> valkey-cli 8.0.7
> ```

70. Valkey 캐시에 연결합니다:

```bash
valkey-cli -h <Primary-Endpoint> -p 6379
```

> [!NOTE]
> `<Primary-Endpoint>`를 태스크 2에서 복사한 엔드포인트로 대체합니다.
> 예: `valkey-cli -h quicktable-cache.xxxxx.ng.0001.apne2.cache.amazonaws.com -p 6379`

71. 연결이 성공하면 Valkey CLI 프롬프트가 표시됩니다:

> [!OUTPUT]
>
> ```
> quicktable-cache.xxxxx.ng.0001.apne2.cache.amazonaws.com:6379>
> ```

72. PING 명령어로 연결을 테스트합니다:

```bash
PING
```

<img src="/images/week10/10-2-task4-step72-valkey-connect.png" alt="PING PONG 연결 테스트" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> PONG
> ```

✅ **태스크 완료**: Amazon EC2 인스턴스를 생성하고 Valkey CLI를 설치했습니다.

## 태스크 4: 기본 Valkey 명령어 실습

### 태스크 설명

이 태스크에서는 Valkey CLI를 사용하여 기본 명령어를 실습합니다.
String, Hash, List 데이터 타입과 TTL 설정 방법을 학습합니다.

> [!NOTE]
> Valkey는 Redis OSS와 동일한 명령어를 사용합니다. SET, GET, HSET, LPUSH 등 모든 Redis 명령어가 그대로 동작합니다.

### 상세 단계

73. Valkey CLI 프롬프트에서 다음 명령어들을 실행합니다.

#### String 타입 (SET/GET)

74. 키-값 쌍을 저장합니다:

```bash
SET user:1:name "John Doe"
```

```bash
SET user:1:email "john@example.com"
```

<img src="/images/week10/10-2-task4-step74-string-ops.png" alt="String SET 명령어 실행" class="guide-img-md" />

75. 저장된 값을 조회합니다:

```bash
GET user:1:name
```

```bash
GET user:1:email
```

<img src="/images/week10/10-2-task4-step75-hash-ops.png" alt="String GET 명령어 실행" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> "John Doe"
> "john@example.com"
> ```

#### TTL 설정 (SETEX)

76. TTL(Time To Live)을 설정하여 30분 후 자동 삭제되는 데이터를 저장합니다:

```bash
SETEX session:abc123 1800 "user_session_data"
```

77. 남은 TTL을 확인합니다:

```bash
TTL session:abc123
```

<img src="/images/week10/10-2-task4-step77-ttl.png" alt="TTL 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> (integer) 1795
> ```

> [!NOTE]
> TTL 값은 초 단위로 표시됩니다. 1800초 = 30분입니다.
> 시간이 지나면 값이 감소하며, -1은 TTL이 설정되지 않음, -2는 키가 존재하지 않음을 의미합니다.
>
> <img src="/images/week10/10-2-task4-step77-ttl-note.png" alt="TTL 만료 후 확인" class="guide-img-md" />

#### Hash 타입 (HSET/HGETALL)

78. Hash 데이터 구조로 사용자 정보를 저장합니다:

```bash
HSET user:2 name "Jane Smith" email "jane@example.com" age "28"
```

79. Hash의 모든 필드를 조회합니다:

```bash
HGETALL user:2
```

<img src="/images/week10/10-2-task4-step79-hash.png" alt="Hash HGETALL 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> 1) "name"
> 2) "Jane Smith"
> 3) "email"
> 4) "jane@example.com"
> 5) "age"
> 6) "28"
> ```

#### List 타입 (LPUSH/LRANGE)

80. List에 예약 ID를 추가합니다:

```bash
LPUSH reservations:recent "res001" "res002" "res003"
```

81. List의 모든 요소를 조회합니다:

```bash
LRANGE reservations:recent 0 -1
```

<img src="/images/week10/10-2-task4-step81-list.png" alt="List LRANGE 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> 1) "res003"
> 2) "res002"
> 3) "res001"
> ```

> [!NOTE]
> LPUSH는 리스트의 왼쪽(앞)에 요소를 추가하므로 역순으로 저장됩니다.

#### 키 삭제 및 존재 확인 (DEL/EXISTS)

82. 키를 삭제합니다:

```bash
DEL user:1:name
```

83. 키가 존재하는지 확인합니다:

```bash
EXISTS user:1:name
```

```bash
EXISTS user:1:email
```

<img src="/images/week10/10-2-task4-step83-del.png" alt="DEL 및 EXISTS 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> (integer) 0
> (integer) 1
> ```

EXISTS는 키가 존재하면 1, 존재하지 않으면 0을 반환합니다.

84. Valkey CLI를 종료합니다:

```bash
exit
```

<img src="/images/week10/10-2-task4-step84-exit.png" alt="Valkey CLI 종료" class="guide-img-md" />

✅ **태스크 완료**: Valkey 기본 명령어를 실습했습니다.

## 태스크 5: 실전 애플리케이션으로 Cache-Aside 패턴 테스트

### 태스크 설명

이 태스크에서는 FastAPI 애플리케이션을 실행하여 Cache-Aside 패턴을 실전에서 테스트합니다.
데이터베이스를 초기화하고, API를 호출하여 캐시 성능을 측정합니다.

### 상세 단계

#### 실습 파일을 Amazon S3에 업로드 (CloudShell)

85. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
86. CloudShell 우측 상단의 **Actions** 드롭다운을 클릭한 후 `Upload file`을 선택합니다.

    <img src="/images/week10/10-2-task5-step86-cloudshell.png" alt="CloudShell Actions > Upload file" class="guide-img-md" />

87. 다운로드한 `week10-2-elasticache-lab.zip` 파일을 선택하고 업로드합니다.
88. 업로드한 파일을 S3 버킷에 복사합니다:

```bash
aws s3 cp ~/week10-2-elasticache-lab.zip s3://<LabFilesBucketName>/
```

<img src="/images/week10/10-2-task5-step88-s3-upload.png" alt="S3 버킷에 파일 복사" class="guide-img-md" />

> [!NOTE]
> `<LabFilesBucketName>`은 태스크 0의 Outputs에서 확인한 값으로 대체합니다.

#### Amazon EC2에서 실습 파일 다운로드 및 실행 (Session Manager)

89. Amazon EC2 콘솔로 이동하여 `quicktable-cache-client` 인스턴스를 선택합니다.
90. [[Connect]] > **Session Manager** > [[Connect]]를 클릭합니다.
91. `ec2-user`로 전환합니다:

```bash
sudo su - ec2-user
```

<img src="/images/week10/10-2-task5-step91-ssm-connect.png" alt="ec2-user 전환" class="guide-img-sm" />

> [!NOTE]
> Session Manager는 `ssm-user`로 접속됩니다. `ec2-user`로 전환해야 홈 디렉토리(`/home/ec2-user`)를 사용할 수 있고, 파일 다운로드 및 패키지 설치가 정상적으로 동작합니다.

92. S3에서 실습 파일을 다운로드하고 압축을 해제합니다:

```bash
aws s3 cp s3://<LabFilesBucketName>/week10-2-elasticache-lab.zip .
unzip week10-2-elasticache-lab.zip
```

<img src="/images/week10/10-2-task5-step92-s3-download.png" alt="S3 다운로드 및 압축 해제" class="guide-img-md" />

> [!NOTE]
> 파일이 홈 디렉토리(`~`)에 직접 압축 해제됩니다. `ls` 명령어로 `app.py`, `requirements.txt` 등이 있는지 확인합니다.

93. Python 3와 pip를 설치합니다:

```bash
sudo yum install -y python3 python3-pip
```

<img src="/images/week10/10-2-task5-step93-s3-download.png" alt="Python 3 설치" class="guide-img-md" />

94. 필요한 Python 패키지를 설치합니다:

```bash
pip3 install -r requirements.txt
```

<img src="/images/week10/10-2-task5-step94-pip-install.png" alt="pip install 완료" class="guide-img-md" />

95. 환경 변수를 설정합니다:

```bash
export REDIS_HOST=<Primary-Endpoint>
export REDIS_PORT=6379
export DYNAMODB_TABLE=week10-2-elasticache-lab-APIData
export AWS_DEFAULT_REGION=ap-northeast-2
```

<img src="/images/week10/10-2-task5-step95-env-vars.png" alt="환경 변수 설정" class="guide-img-md" />

> [!NOTE]
> `<Primary-Endpoint>`를 태스크 2에서 복사한 엔드포인트로 대체합니다.
> **주의**: 복사한 엔드포인트에 포트 번호(`:6379`)가 포함되어 있을 수 있습니다. `REDIS_HOST`에는 호스트명만 입력해야 하므로 `:6379` 부분은 제거합니다.
> (예: `xxx.cache.amazonaws.com:6379` → `xxx.cache.amazonaws.com`)
>
> 환경 변수명이 `REDIS_HOST`인 이유는 Valkey가 Redis OSS와 호환되어 기존 Redis 클라이언트 라이브러리를 그대로 사용하기 때문입니다.
>
> 설정한 환경 변수를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> echo $REDIS_HOST
> echo $REDIS_PORT
> echo $DYNAMODB_TABLE
> ```

96. DynamoDB 테이블을 초기화합니다:

```bash
python3 init_dynamodb.py
```

<img src="/images/week10/10-2-task5-step96-env-verify.png" alt="DynamoDB 테이블 초기화" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> DynamoDB 테이블 초기화 중...
> 10개의 사용자 데이터가 추가되었습니다.
> ```

97. FastAPI 애플리케이션을 백그라운드로 실행합니다:

```bash
nohup uvicorn app:app --host 0.0.0.0 --port 5000 > app.log 2>&1 &
```

<img src="/images/week10/10-2-task5-step97-init-dynamodb.png" alt="FastAPI 앱 백그라운드 실행" class="guide-img-md" />

> [!NOTE]
> FastAPI는 자동으로 API 문서를 생성합니다:
>
> - Swagger UI: `http://<Amazon EC2-IP>:5000/docs`
> - ReDoc: `http://<Amazon EC2-IP>:5000/redoc`

98. 애플리케이션이 정상적으로 실행되는지 확인합니다:

```bash
curl -s http://localhost:5000/health | python3 -m json.tool
```

<img src="/images/week10/10-2-task5-step98-app-start.png" alt="앱 실행 및 health check" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "redis": "connected",
>   "database": "connected"
> }
> ```

99. 캐시 없이 사용자 정보를 조회합니다 (첫 번째 요청):

```bash
curl -s http://localhost:5000/user/1/nocache | python3 -m json.tool
```

<img src="/images/week10/10-2-task5-step99-benchmark.png" alt="캐시 없이 조회 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "source": "database",
>   "data": {
>     "id": 1,
>     "name": "김철수",
>     "email": "kim@example.com",
>     "age": 28,
>     "city": "Seoul"
>   },
>   "responseTimeMs": 45.23
> }
> ```

100. 캐시를 사용하여 동일한 사용자 정보를 조회합니다 (첫 번째 요청 - 캐시 미스):

```bash
curl -s http://localhost:5000/user/1 | python3 -m json.tool
```

> [!OUTPUT]
>
> ```json
> {
>   "source": "database",
>   "data": {
>     "id": 1,
>     "name": "김철수",
>     "email": "kim@example.com",
>     "age": 28,
>     "city": "Seoul"
>   },
>   "responseTimeMs": 43.87
> }
> ```

101. 동일한 요청을 다시 실행합니다 (두 번째 요청 - 캐시 히트):

```bash
curl -s http://localhost:5000/user/1 | python3 -m json.tool
```

<img src="/images/week10/10-2-task5-step101-cache-hit.png" alt="캐시 히트 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "source": "cache",
>   "data": {
>     "id": 1,
>     "name": "김철수",
>     "email": "kim@example.com",
>     "age": 28,
>     "city": "Seoul"
>   },
>   "responseTimeMs": 2.15
> }
> ```

> [!TIP]
> 캐시를 사용하면 응답 시간이 약 20배 빨라집니다 (43.87ms → 2.15ms).
> 실제 프로덕션 환경에서는 10-50배의 성능 향상을 기대할 수 있습니다.

102. 캐시 통계를 확인합니다:

```bash
curl -s http://localhost:5000/cache/stats | python3 -m json.tool
```

<img src="/images/week10/10-2-task5-step102-cache-stats.png" alt="캐시 통계 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```json
> {
>   "totalConnections": 15,
>   "totalCommands": 42,
>   "keyspaceHits": 8,
>   "keyspaceMisses": 3,
>   "hitRate": 72.73
> }
> ```

103. 성능 벤치마크를 실행합니다:

```bash
python3 benchmark.py
```

<img src="/images/week10/10-2-task5-step103-benchmark.png" alt="벤치마크 실행 결과" class="guide-img-sm" />

> [!OUTPUT]
>
> ```
> 성능 벤치마크 실행 중...
>
> 캐시 없이 100회 요청:
> - 평균 응답 시간: 6.0ms
> - 총 소요 시간: 0.60초
>
> 캐시 사용 100회 요청:
> - 평균 응답 시간: 2.6ms
> - 총 소요 시간: 0.26초
> - 캐시 히트율: 95.8%
>
> 성능 향상: 2.3배
> ```

> [!NOTE]
> 성능 향상 배율은 네트워크 환경에 따라 달라집니다. 같은 VPC 내에서는 DynamoDB 접근도 빠르기 때문에 차이가 작을 수 있습니다.
> 실제 프로덕션 환경에서 외부 데이터베이스를 사용하는 경우 10-50배의 성능 향상을 기대할 수 있습니다.
>
> <img src="/images/week10/10-2-task5-step103-benchmark-note.png" alt="벤치마크 결과 상세" class="guide-img-sm" />

✅ **태스크 완료**: FastAPI 애플리케이션으로 Cache-Aside 패턴을 테스트했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon ElastiCache for Valkey 캐시를 생성하고 엔드포인트를 확인했습니다.
- Amazon EC2 인스턴스에서 Valkey CLI로 기본 명령어를 실습했습니다.
- Cache-Aside 패턴을 적용한 FastAPI 애플리케이션으로 캐시 성능을 측정했습니다.
- 캐시를 사용하면 데이터베이스 조회 대비 성능 향상을 확인했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> Amazon ElastiCache 캐시와 Amazon EC2 인스턴스는 AWS CloudFormation 스택에 포함되지 않으므로 **반드시 수동으로 먼저 삭제**해야 합니다.
> Amazon S3 버킷에 객체가 있으면 AWS CloudFormation 스택 삭제 시 버킷 삭제가 실패합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `10-2`
6. [[Search resources]] 버튼을 클릭합니다.

<img src="/images/week10/10-2-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Amazon EC2, Amazon ElastiCache, Amazon S3 리소스 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. CloudShell에서 Amazon EC2 인스턴스를 종료합니다:

```bash
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=quicktable-cache-client" "Name=instance-state-name,Values=running" --query "Reservations[0].Instances[0].InstanceId" --output text --region ap-northeast-2)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region ap-northeast-2
```

<img src="/images/week10/10-2-cleanup-step7-ec2-terminate.png" alt="EC2 인스턴스 종료" class="guide-img-md" />

> [!NOTE]
> 인스턴스 상태를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws ec2 describe-instances --instance-ids $INSTANCE_ID --query "Reservations[0].Instances[0].State.Name" --output text --region ap-northeast-2
> ```
>
> `terminated`가 출력되면 삭제 완료입니다.
>
> <img src="/images/week10/10-2-cleanup-step7-ec2-note.png" alt="EC2 인스턴스 종료 확인" class="guide-img-md" />

8. Amazon ElastiCache 캐시를 삭제합니다:

```bash
aws elasticache delete-replication-group --replication-group-id quicktable-cache --region ap-northeast-2
```

<img src="/images/week10/10-2-cleanup-step8-elasticache-delete.png" alt="ElastiCache 캐시 삭제" class="guide-img-md" />

> [!NOTE]
> Amazon ElastiCache 캐시 삭제에 5-10분이 소요됩니다. 삭제 상태를 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws elasticache describe-replication-groups --replication-group-id quicktable-cache --query "ReplicationGroups[0].Status" --output text --region ap-northeast-2
> ```
>
> `available`은 아직 삭제되지 않은 상태, `deleting`이 출력되면 대기하고, `ReplicationGroupNotFoundFault` 오류가 나오면 삭제 완료입니다.
>
> <img src="/images/week10/10-2-cleanup-step8-elasticache-note.png" alt="ElastiCache 삭제 상태 확인" class="guide-img-md" />

9. Amazon S3 버킷을 비웁니다:

```bash
aws s3 rm s3://<LabFilesBucketName> --recursive --region ap-northeast-2
```

<img src="/images/week10/10-2-cleanup-step9-s3-empty.png" alt="S3 버킷 비우기" class="guide-img-md" />

> [!NOTE]
> `<LabFilesBucketName>`은 태스크 0의 Outputs에서 확인한 값으로 대체합니다.
> 버킷이 비워졌는지 확인하려면 다음 명령어를 실행합니다:
>
> ```bash
> aws s3 ls s3://<LabFilesBucketName>/ --region ap-northeast-2
> ```
>
> 출력이 없으면 비우기 완료입니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

10. Amazon EC2 콘솔로 이동합니다.
11. 왼쪽 메뉴에서 **Instances**를 선택합니다.
12. `quicktable-cache-client` 인스턴스를 선택합니다.
13. **Instance state** > `Terminate instance`를 선택합니다.

    <img src="/images/week10/10-2-cleanup-step13-stack-delete.png" alt="EC2 Terminate instance" class="guide-img-md" />

14. 확인 창에서 [[Terminate]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-cleanup-step14-stack-confirm.png" alt="Terminate 확인" class="guide-img-sm" />

15. Amazon ElastiCache 콘솔로 이동합니다.
16. 왼쪽 메뉴에서 **Valkey caches**를 선택합니다.
17. `quicktable-cache` 캐시를 선택합니다.
18. **Actions** > `Delete`를 선택합니다.

    <img src="/images/week10/10-2-cleanup-step18-elasticache-delete.png" alt="ElastiCache Actions > Delete" class="guide-img-md" />

19. **Create backup**에서 `No`를 선택합니다.
20. 확인 창에서 `quicktable-cache`를 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-cleanup-step20-elasticache-confirm.png" alt="ElastiCache 삭제 확인 - 이름 입력" class="guide-img-sm" />

> [!NOTE]
> Amazon ElastiCache 캐시 삭제에 5-10분이 소요됩니다. 삭제가 완료될 때까지 기다립니다.

21. Amazon S3 콘솔로 이동합니다.
22. 태스크 0에서 생성한 `LabFilesBucketName` 값의 버킷을 선택합니다.
23. [[Empty]] 버튼을 클릭합니다.
24. 확인 창에서 `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-cleanup-step24-s3-empty.png" alt="S3 버킷 Empty 확인" class="guide-img-sm" />

### 단계 3: AWS CloudFormation 스택 삭제

25. AWS CloudFormation 콘솔로 이동합니다.
26. `week10-2-quicktable-cache-stack` 스택을 선택합니다.
27. [[Delete stack]] 버튼을 클릭합니다.
28. 확인 창에서 스택 이름 `week10-2-quicktable-cache-stack`을 입력합니다.

    <img src="/images/week10/10-2-cleanup-step28-stack-delete.png" alt="CloudFormation 스택 삭제 확인" class="guide-img-sm" />

29. [[Delete stack]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 Amazon VPC, 서브넷, 보안 그룹, NAT Gateway, Amazon DynamoDB 테이블, Amazon S3 버킷, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

### 단계 4: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

30. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
31. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
32. **Regions**에서 `ap-northeast-2`를 선택합니다.
33. **Resource types**에서 `All supported resource types`를 선택합니다.
34. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `10-2`
35. [[Search resources]] 버튼을 클릭합니다.

    <img src="/images/week10/10-2-cleanup-step35-tageditor-final.png" alt="Tag Editor 최종 삭제 확인" class="guide-img-md" />

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

36. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
37. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
38. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
39. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
40. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [Amazon ElastiCache 사용 설명서](https://docs.aws.amazon.com/ko_kr/AmazonElastiCache/latest/dg/WhatIs.html)
- [Valkey 공식 문서](https://valkey.io/docs/)
- [Valkey 명령어 참조](https://valkey.io/commands/)
- [캐싱 전략 및 패턴](https://docs.aws.amazon.com/ko_kr/AmazonElastiCache/latest/dg/Strategies.html)

## 📚 참고: Amazon ElastiCache 및 캐싱 전략

### Amazon ElastiCache 개요

Amazon ElastiCache는 완전 관리형 인메모리 데이터 저장소 서비스입니다. Valkey, Redis OSS, Memcached 엔진을 지원하며, 데이터베이스 조회 결과를 캐싱하여 애플리케이션 성능을 크게 향상시킬 수 있습니다.

**주요 특징:**

- 완전 관리형 서비스 (패치, 백업, 모니터링 자동화).
- 고가용성 (Multi-AZ, 자동 장애 조치).
- 확장성 (클러스터 모드, 샤딩).
- 보안 (암호화, Amazon VPC, AWS IAM).

**지원 엔진 비교:**

| 항목        | Valkey                                 | Redis OSS   | Memcached |
| ----------- | -------------------------------------- | ----------- | --------- |
| 라이선스    | BSD (오픈소스)                         | SSPL/RSALv2 | BSD       |
| 데이터 구조 | String, Hash, List, Set, Sorted Set 등 | 동일        | String만  |
| 영속성      | 지원 (RDB, AOF)                        | 지원        | 미지원    |
| 복제        | 지원                                   | 지원        | 미지원    |
| 비용        | 최대 33% 저렴                          | 기준        | 기준      |
| AWS 권장    | ✅ 권장                                | -           | -         |

### 캐싱 전략

**Cache-Aside (Lazy Loading):**

- 애플리케이션이 캐시를 먼저 확인하고, 없으면 데이터베이스에서 조회.
- 장점: 필요한 데이터만 캐싱, 캐시 장애 시에도 애플리케이션 동작.
- 단점: 첫 번째 요청은 느림, 캐시 만료 관리 필요.

**Write-Through:**

- 데이터 쓰기 시 캐시와 데이터베이스에 동시 저장.
- 장점: 캐시 데이터 항상 최신 상태.
- 단점: 쓰기 지연 시간 증가, 사용하지 않는 데이터도 캐싱.

**Write-Behind (Write-Back):**

- 캐시에 먼저 쓰고, 비동기로 데이터베이스에 저장.
- 장점: 쓰기 성능 향상.
- 단점: 캐시 장애 시 데이터 손실 위험.

### Valkey 데이터 타입

Valkey는 Redis OSS와 동일한 데이터 타입을 지원합니다:

- **String**: 단순 키-값 저장 (예: 세션, 카운터).
- **Hash**: 객체 저장 (예: 사용자 프로필).
- **List**: 순서가 있는 문자열 목록 (예: 최근 활동).
- **Set**: 중복 없는 문자열 집합 (예: 태그).
- **Sorted Set**: 점수로 정렬된 집합 (예: 리더보드).
