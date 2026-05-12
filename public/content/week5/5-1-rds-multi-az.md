---
title: 'Amazon RDS Multi-AZ 고가용성 구성 및 운영'
week: 5
session: 1
awsServices:
  - Amazon RDS
learningObjectives:
  - Amazon RDS Multi-AZ와 Read Replica의 차이점(고가용성 vs 읽기 확장)을 이해할 수 있습니다.
  - Amazon RDS MySQL 인스턴스를 Multi-AZ로 생성하고 페일오버를 시뮬레이션할 수 있습니다.
  - Amazon RDS Read Replica를 생성하고 읽기 부하를 분산할 수 있습니다.
  - 수동 스냅샷과 자동 백업을 생성하고 관리할 수 있습니다.
prerequisites:
  - 관계형 데이터베이스 기본 개념 이해
  - Amazon VPC 및 서브넷 기본 개념 이해
---

이 실습에서는 Amazon RDS MySQL 인스턴스를 Multi-AZ 배포로 생성하고 고가용성 데이터베이스 아키텍처를 구축합니다. Primary DB와 Standby DB가 서로 다른 가용 영역에 자동으로 배포되어 동기식 복제가 이루어지며, 페일오버 테스트를 통해 자동 전환 과정을 확인합니다. Read Replica를 생성하여 읽기 성능을 확장하고, 자동 백업과 수동 스냅샷을 구성하여 데이터 보호 전략을 학습합니다.

> [!DOWNLOAD]
> [week5-1-rds-lab.zip](/files/week5/week5-1-rds-lab.zip)
>
> - `week5-1-rds-lab.yaml` - Amazon VPC 환경 AWS CloudFormation 템플릿 (태스크 0에서 Amazon VPC, 서브넷, 보안 그룹, DB 서브넷 그룹 자동 생성)
> - `init_database.sql` - 데이터베이스 초기화 스크립트 (선택사항)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation 템플릿 배포)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 시간당 비용이 발생합니다.  
> 실습 종료 후 반드시 모든 리소스를 삭제하여 불필요한 비용이 발생하지 않도록 주의하세요.

> [!TIP]
> **실습 시간 단축 팁**: 태스크 0 (AWS CloudFormation 스택 생성)과 태스크 1 (Amazon RDS 인스턴스 생성)은 대기 시간이 길어 실습 시간의 대부분을 차지합니다 (약 15-20분).  
> 실습 시작 전에 태스크 0과 태스크 1을 미리 완료해두면 실제 실습 시간을 크게 단축할 수 있습니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 Amazon RDS 실습에 필요한 기본 네트워크 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon VPC 및 네트워크**: Amazon VPC (10.0.0.0/16), 퍼블릭 서브넷 2개, 프라이빗 서브넷 2개 (Multi-AZ)
- **인터넷 연결**: 인터넷 게이트웨이, NAT Gateway
- **보안 그룹**: Amazon RDS 보안 그룹 (MySQL 포트 3306)
- **DB 서브넷 그룹**: Amazon RDS 인스턴스 배포를 위한 서브넷 그룹

> [!WARNING]
> 이 실습에서는 NAT Gateway를 직접 사용하지 않지만, 실무 환경과 유사한 IaC 구성을 학습하기 위해 포함되었습니다.  
> NAT Gateway는 시간당 비용이 발생하므로 실습 종료 후 반드시 리소스를 정리해야 합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week5-1-rds-lab.zip` 파일의 압축을 해제합니다.
2. `week5-1-rds-lab.yaml` 파일을 확인합니다.
3. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
4. 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
5. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
   <img src="/images/week5/5-1-task0-step5-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

6. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
7. **Specify template**에서 `Upload a template file`을 선택합니다.
8. [[Choose file]] 버튼을 클릭한 후 `week5-1-rds-lab.yaml` 파일을 선택합니다.
9. [[Next]] 버튼을 클릭합니다.
   <img src="/images/week5/5-1-task0-step9-next.png" alt="CloudFormation Next 버튼 클릭" class="guide-img-md" />

10. **Stack name**에 `week5-1-rds-stack`을 입력합니다.
11. **Parameters** 섹션에서 기본값을 확인합니다:
    - **EnvironmentName**: `week5-1-rds`
    - **ProjectTag**: `AWS-Lab`
    - **WeekTag**: `5-1`
    - **CreatedByTag**: `CloudFormation`

> [!TIP]
> CloudFormation 파라미터로 태그를 설정하면 스택이 생성하는 모든 리소스(VPC, 서브넷, 보안 그룹 등)에 자동으로 태그가 적용됩니다.

12. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task0-step12-next.png" alt="Parameters 설정 후 Next" class="guide-img-md" />

13. **Configure stack options** 페이지에서 아래로 스크롤합니다.
14. [[Next]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task0-step14-next.png" alt="Configure stack options Next" class="guide-img-md" />

15. **Review** 페이지에서 설정을 확인합니다.
16. [[Submit]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task0-step16-submit.png" alt="Submit 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> 스택 생성이 시작되면 상태가 "**CREATE_IN_PROGRESS**"로 표시됩니다.
> 스택 생성에 5-7분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.
> 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.

17. **Outputs** 탭을 선택합니다.
    <img src="/images/week5/5-1-task0-step17-outputs.png" alt="스택 생성 완료 및 Outputs 탭" class="guide-img-md" />
18. 출력값들을 확인하고 메모장에 복사합니다:
    - `VpcId`: Amazon VPC ID (예: vpc-0123456789abcdef0)
    - `PrivateSubnetAId`: 프라이빗 서브넷 A ID (ap-northeast-2a)
    - `PrivateSubnetCId`: 프라이빗 서브넷 C ID (ap-northeast-2c)
    - `DBSubnetGroupName`: DB 서브넷 그룹 이름 (예: week5-1-rds-db-subnet-group)
    - `RDSSecurityGroupId`: Amazon RDS 보안 그룹 ID (예: sg-0123456789abcdef0)

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 Amazon RDS 인스턴스를 생성할 때 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: Amazon RDS MySQL 인스턴스를 Multi-AZ로 생성

이 태스크에서는 Amazon RDS MySQL 인스턴스를 Multi-AZ 배포로 생성합니다. Multi-AZ는 Primary DB와 Standby DB를 서로 다른 가용 영역에 자동으로 배포하여 고가용성을 제공합니다.

### 엔진 및 템플릿 선택

19. AWS Management Console 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**인지 확인합니다.
20. 상단 검색창에 `RDS`을 입력하고 선택합니다.
21. 왼쪽 메뉴에서 **Databases**를 선택합니다.
22. [[Create database]] 드롭다운을 클릭한 후 **Full configuration**을 선택합니다.
    <img src="/images/week5/5-1-task1-step22-create-database.png" alt="Create database 드롭다운에서 Full configuration 선택" class="guide-img-md" />

> [!NOTE]
> Create database 버튼이 드롭다운으로 변경되었습니다.  
> **Full configuration**을 선택하면 모든 설정을 직접 구성할 수 있습니다.  
> Express configuration은 간소화된 설정으로 Multi-AZ 등 세부 옵션을 제어할 수 없습니다.

23. **Engine type**에서 `MySQL`을 선택합니다.
24. **Choose a database creation method** 섹션에서 `Full configuration`을 선택합니다.
    <img src="/images/week5/5-1-task1-step24-full-config.png" alt="Full configuration 선택" class="guide-img-md" />

25. **Templates**에서 `Dev/Test`를 선택합니다.

> [!IMPORTANT]
> **무료 플랜(Free tier)은 Multi-AZ 배포를 지원하지 않습니다.**  
> 무료 플랜 사용자는 이번 실습의 핵심 목적인 Multi-AZ 고가용성 구성을 실습할 수 없습니다.  
> Multi-AZ 실습을 위해서는 반드시 유료 플랜(Dev/Test 또는 Production 템플릿)을 선택해야 합니다.

### 가용성 및 내구성 설정

26. **Availability and durability** 섹션에서 `Multi-AZ DB instance deployment (2 instances)`를 선택합니다.
    <img src="/images/week5/5-1-task1-step26-availability.png" alt="Multi-AZ DB instance deployment 선택" class="guide-img-md" />

> [!NOTE]
> Multi-AZ DB instance deployment는 Primary 인스턴스와 읽기 불가능한 Standby 인스턴스를 서로 다른 가용 영역에 생성합니다.  
> 이 구성은 99.95% 가동 시간과 자동 페일오버를 제공합니다.

### Settings

27. **Engine version**에서 콘솔에서 기본 선택되는 MySQL 버전을 사용합니다 (예: MySQL 8.4.8).
28. **DB instance identifier**에 `mysql-lab-instance`를 입력합니다.
29. **Credentials Settings** 섹션에서 **Master username**에 `admin`을 확인합니다 (기본값).
30. **Credentials management**에서 `Self managed`를 선택합니다.

> [!NOTE]
> 기본값이 `Managed in AWS Secrets Manager`로 선택되어 있습니다.  
> 이 실습에서는 학습 목적으로 `Self managed`를 선택하여 비밀번호를 직접 관리합니다.

31. **Master password**에 `MyPassword123!`을 입력합니다.
32. **Confirm password**에 `MyPassword123!`을 입력합니다.
    <img src="/images/week5/5-1-task1-step32-credentials.png" alt="Credentials Settings 입력" class="guide-img-md" />

> [!WARNING]
> 이 실습에서는 학습 목적으로 간단한 비밀번호를 사용합니다.  
> 프로덕션 환경에서는 강력한 비밀번호 정책을 적용하고, AWS Secrets Manager를 사용하여 데이터베이스 자격 증명을 안전하게 관리합니다.

### 인스턴스 구성 및 스토리지 설정

33. **DB instance class**에서 `Burstable classes` - `db.t3.small`을 선택합니다.
    <img src="/images/week5/5-1-task1-step33-instance-class.png" alt="DB instance class 선택" class="guide-img-md" />

> [!IMPORTANT]
> **db.t3.micro는 대부분의 리전에서 Multi-AZ를 지원하지 않습니다.**  
> Multi-AZ 배포를 위해서는 `db.t3.small` 이상의 인스턴스 클래스를 선택해야 합니다.
>
> 콘솔에서 기본 선택되는 인스턴스 클래스(예: db.m5d.large)는 비용이 높으므로, **Burstable classes (includes t classes)**를 선택한 후 `db.t3.small`을 선택합니다.

34. **Storage type**에서 `General Purpose SSD (gp3)`를 선택합니다.
35. **Allocated storage**에 `20` GiB를 입력합니다.

> [!TIP]
> 콘솔에서 기본 Storage type이 `Provisioned IOPS SSD (io2)`로 선택될 수 있습니다.
> 실습 비용 절감을 위해 다음과 같이 변경합니다:
>
> - **Storage type**: `General Purpose SSD (gp3)`
> - **Allocated storage**: `20` GiB
> - **Provisioned IOPS**: 기본값 유지 (3000)
> - **Storage throughput**: 기본값 유지 (125 MiBps)

36. **Additional storage configuration** 섹션을 확장합니다.
37. ▢ **Enable storage autoscaling**을 체크 해제합니다.
    <img src="/images/week5/5-1-task1-step37-storage.png" alt="Storage 설정" class="guide-img-md" />

### 네트워크 설정

38. **Compute resource** 섹션에서 `Don't connect to an EC2 compute resource`를 선택합니다.

> [!NOTE]
> 이 실습에서는 EC2 인스턴스와의 자동 연결 설정을 사용하지 않고, VPC와 보안 그룹을 수동으로 구성합니다.  
> EC2 자동 연결을 선택하면 AWS가 네트워크 설정을 자동으로 구성하지만, 학습 목적으로 각 설정을 직접 구성합니다.

39. **Virtual private cloud (Amazon VPC)**에서 태스크 0에서 생성한 Amazon VPC를 선택합니다 (`week5-1-rds-VPC`).
40. **DB subnet group**에서 태스크 0에서 생성한 서브넷 그룹을 선택합니다 (`week5-1-rds-db-subnet-group`).
41. **Public access**에서 `No`를 선택합니다.
42. **VPC security group**에서 `Choose existing`을 선택합니다.
43. 기본(default) 보안 그룹의 [[X]] 버튼을 클릭하여 제거합니다.

> [!NOTE]
> VPC를 선택하면 기본(default) 보안 그룹이 자동으로 선택됩니다.  
> RDS 인스턴스가 올바르게 작동하려면 default 보안 그룹을 제거하고 태스크 0에서 생성한 RDS 전용 보안 그룹을 선택해야 합니다.

44. 태스크 0에서 생성한 Amazon RDS 보안 그룹을 선택합니다 (`week5-1-rds-RDS-SG`).
    <img src="/images/week5/5-1-task1-step44-security-group.png" alt="VPC security group 선택" class="guide-img-md" />

> [!NOTE]
> Single-AZ 배포에서는 Availability Zone을 직접 선택할 수 있지만, Multi-AZ deployment를 선택하면 AWS가 Primary와 Standby를 자동으로 서로 다른 AZ에 배치하므로 해당 선택 옵션이 표시되지 않습니다.

### 태그 및 모니터링 설정

45. 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
46. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `5-1`     |
| `CreatedBy` | `Student` |

47. 아래로 스크롤하여 **Monitoring** 섹션을 확인합니다.
48. **Monitoring** 섹션에서 `Database Insights - Standard`를 선택하고 **Enhanced Monitoring**을 체크 해제합니다 (비용 절감).
    <img src="/images/week5/5-1-task1-step48-monitoring.png" alt="Monitoring 설정" class="guide-img-md" />

### 추가 설정 및 생성

49. **Additional configuration** 섹션을 확장합니다 (페이지 맨 하단).
50. **Initial database name**에 `labdb`를 입력합니다.
    <img src="/images/week5/5-1-task1-step50-additional-config.png" alt="Additional configuration 설정" class="guide-img-md" />

> [!NOTE]
> Multi-AZ DB cluster deployment (3 instances)를 선택한 경우  
> Initial database name이 "Not supported for Multi-AZ DB cluster"로 비활성화됩니다.  
> 이 경우 이 단계를 건너뜁니다.  
> Multi-AZ DB instance deployment (2 instances)를 선택한 경우에만 입력 가능합니다.

51. ☑️ **Enable automated backups**가 체크되어 있는지 확인합니다 (기본값).

> [!IMPORTANT]
> **자동 백업은 Read Replica 생성의 필수 조건입니다.**  
> Read Replica는 자동 백업이 활성화된 경우에만 생성할 수 있습니다.  
> 이 설정을 체크하지 않으면 태스크 4에서 Read Replica를 생성할 수 없습니다.

52. **Backup retention period**에서 `7` days를 선택합니다.

> [!WARNING]
> 백업 보존 기간이 7일로 설정되면 최대 7개의 자동 백업이 보관되어 스토리지 비용이 발생합니다.  
> **실습 종료 후 반드시 모든 RDS 리소스를 삭제하여 백업 스토리지 비용이 누적되지 않도록 합니다.**

53. ▢ **Enable deletion protection**을 체크 해제합니다.
    <img src="/images/week5/5-1-task1-step53-deletion-protection.png" alt="Enable deletion protection 체크 해제" class="guide-img-md" />

54. [[Create database]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task1-step54-create.png" alt="Create database 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> Amazon RDS 인스턴스 생성에 약 10-15분이 소요됩니다. 상태가 "Available"로 변경될 때까지 기다립니다.
> 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다.
>
> <img src="/images/week5/5-1-task1-step54-creating.png" alt="RDS 인스턴스 생성 진행 중" class="guide-img-md" />

✅ **태스크 완료**: Amazon RDS MySQL Multi-AZ 인스턴스가 생성되었습니다.

## 태스크 2: Amazon RDS 인스턴스 정보 확인

이 태스크에서는 생성된 Amazon RDS 인스턴스의 연결 정보와 Multi-AZ 구성을 확인합니다.

55. Amazon RDS 콘솔에서 생성된 `mysql-lab-instance`를 선택합니다.
56. **Connectivity & security** 탭을 선택합니다.
57. **Endpoints** 버튼을 클릭하여 연결 정보를 확인합니다.
    <img src="/images/week5/5-1-task2-step57-connectivity.png" alt="Connectivity & security 탭 확인" class="guide-img-md" />

58. 다음 정보를 확인하고 메모장에 복사합니다:
    - **Endpoint**: 데이터베이스 연결 주소
    - **Port**: `3306`

59. **Configuration** 탭을 선택합니다.
    <img src="/images/week5/5-1-task2-step59-configuration.png" alt="Configuration 탭 확인" class="guide-img-md" />

60. 다음 정보를 확인합니다:
    - **Multi-AZ**: `Yes`
    - **Secondary Zone**: Standby AZ (예: ap-northeast-2c)

> [!NOTE]
> 인스턴스 생성 중에는 Multi-AZ가 "No"로 표시될 수 있습니다. Standby 인스턴스가 완전히 생성되면 "Yes"로 변경됩니다.
> **Secondary Zone**이 표시되지 않는 경우 Standby 배치가 아직 완료되지 않은 것이므로 몇 분 후 페이지를 새로고침합니다.
> 상태가 "Available"이 된 후에도 Multi-AZ가 "No"로 표시된다면 페이지를 새로고침합니다.

✅ **태스크 완료**: Amazon RDS 인스턴스 정보가 확인되었습니다.

## 태스크 3: Multi-AZ 페일오버 시뮬레이션

이 태스크에서는 수동 페일오버를 수행하여 Multi-AZ의 고가용성 메커니즘을 확인합니다. 페일오버는 Primary 인스턴스에 장애가 발생했을 때 Standby 인스턴스가 자동으로 Primary로 승격되는 과정입니다. 이 실습에서는 재부팅을 통해 페일오버를 시뮬레이션합니다.

> [!CONCEPT] Multi-AZ 페일오버의 핵심 가치
>
> Single-AZ 배포에서는 Primary 인스턴스 장애 시 수동 복구에 수십 분이 소요되지만, Multi-AZ는 1-2분 내에 자동으로 Standby를 Primary로 승격합니다.
>
> **핵심 특징:**
>
> - **엔드포인트 불변**: DNS 엔드포인트가 동일하게 유지되어 애플리케이션 코드 변경 불필요
> - **자동 전환**: Amazon RDS가 장애를 감지하고 자동으로 페일오버 수행
> - **데이터 무손실**: 동기식 복제로 데이터 손실 없이 전환

61. Amazon RDS 콘솔에서 `mysql-lab-instance`를 선택합니다.
62. **Actions** > `Reboot`를 선택합니다.
    <img src="/images/week5/5-1-task3-step62-reboot.png" alt="Actions Reboot 선택" class="guide-img-md" />

63. ☑️ **Reboot With Failover?**를 체크합니다.
64. [[Confirm]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task3-step64-failover.png" alt="Reboot With Failover 확인" class="guide-img-sm" />
65. 상태가 "Rebooting"으로 변경됩니다.
    <img src="/images/week5/5-1-task3-step65-rebooting.png" alt="Rebooting 상태 확인" class="guide-img-md" />
    <img src="/images/week5/5-1-task3-step65-rebooting-2.png" alt="페일오버 진행 중" class="guide-img-md" />

> [!NOTE]
> 상태가 "Available"로 변경될 때까지 기다립니다. 페일오버는 1-2분 내에 완료되지만, 콘솔에서 상태가 "Available"로 표시되기까지 추가 시간이 소요될 수 있습니다. 30초 간격으로 페이지를 새로고침하여 상태 변경을 확인합니다.

### 페일오버 결과 확인

66. 페이지를 새로고침합니다.
67. **Connectivity & security** 탭을 선택합니다.
    <img src="/images/week5/5-1-task3-step67-failover-result.png" alt="페일오버 후 Connectivity 확인" class="guide-img-md" />

68. **Endpoints** 버튼을 클릭합니다.
69. **Endpoint**를 확인합니다.

> [!TIP]
> Endpoint가 동일하게 유지됩니다. 이는 Multi-AZ의 핵심 가치로, 페일오버가 발생해도 애플리케이션 코드를 변경할 필요가 없습니다.

70. **Logs & events** 탭을 선택합니다.
    <img src="/images/week5/5-1-task3-step70-events.png" alt="Logs & events 탭 선택" class="guide-img-md" />

71. **Recent events** 섹션에서 다음 페일오버 관련 이벤트들을 확인합니다 (최신순으로 표시):

```
The user requested a failover of the DB instance.
Multi-AZ instance failover completed
DB instance restarted
Multi-AZ instance failover started.
```

> [!NOTE]
> 페일오버는 Standby 인스턴스를 Primary로 승격시키는 고가용성 메커니즘입니다.  
> 이벤트 로그에서 "Multi-AZ instance failover completed"가 표시되면 페일오버가 성공적으로 완료된 것입니다.  
> DNS 엔드포인트는 자동으로 새로운 Primary를 가리키므로 애플리케이션은 중단 없이 계속 작동합니다.  
> 재부팅과 페일오버 처리 과정에서 Availability Zone이 변경될 수도 있고 변경되지 않을 수도 있습니다.

✅ **태스크 완료**: Multi-AZ 페일오버가 성공적으로 수행되었습니다.

## 태스크 4: Read Replica 생성

이 태스크에서는 읽기 성능 확장을 위한 Read Replica를 생성합니다. Read Replica는 Primary DB의 데이터를 비동기식으로 복제하여 읽기 전용 쿼리를 처리합니다.

> [!CONCEPT] Multi-AZ Standby vs Read Replica
>
> - **Multi-AZ Standby**는 읽기/쓰기가 불가능한 대기 전용 인스턴스입니다. 오직 페일오버를 위해 존재하며, 평상시에는 사용할 수 없습니다.
> - **Read Replica**는 읽기 전용 쿼리를 처리할 수 있어 읽기 부하를 분산할 수 있습니다. 따라서 읽기 성능 확장을 위해서는 Read Replica를 별도로 생성해야 합니다.

72. `mysql-lab-instance`를 선택합니다.
73. **Actions** > `Create read replica`를 선택합니다.
    <img src="/images/week5/5-1-task4-step73-create-replica.png" alt="Create read replica 선택" class="guide-img-md" />

74. **DB instance identifier**에 `mysql-lab-replica`를 입력합니다.
75. **DB instance class**에서 `db.t3.small`을 선택합니다.
    <img src="/images/week5/5-1-task4-step75-instance-class.png" alt="Read Replica instance class 선택" class="guide-img-md" />

76. **Storage** 섹션에서 Storage type이 `General Purpose SSD (gp3)`, Allocated storage가 `20` GiB인지 확인합니다.
77. **Additional storage configuration**을 확장하여 ▢ **Enable storage autoscaling**을 체크 해제합니다.
    <img src="/images/week5/5-1-task4-step77-autoscaling.png" alt="Enable storage autoscaling 체크 해제" class="guide-img-md" />

78. **Availability** 섹션에서 기본값을 확인합니다.
    <img src="/images/week5/5-1-task4-step78-availability.png" alt="Availability 섹션 확인" class="guide-img-md" />

> [!NOTE]
> Primary 인스턴스가 Multi-AZ이므로 Read Replica도 Multi-AZ로 기본 선택됩니다.
> 실습에서는 기본값을 유지합니다.

79. **Connectivity** 섹션에서 다음이 선택되어 있는지 확인합니다:
    - **DB subnet group**: `week5-1-rds-db-subnet-group`
    - **VPC security groups**: `week5-1-rds-RDS-SG`
      <img src="/images/week5/5-1-task4-step79-connectivity.png" alt="Connectivity 섹션 확인" class="guide-img-md" />

80. 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
81. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다.

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `5-1`     |
| `CreatedBy` | `Student` |

<img src="/images/week5/5-1-task4-step81-tags.png" alt="Tags 추가" class="guide-img-md" />

82. **Monitoring** 섹션에서 `Database Insights - Standard`를 선택하고 **Enhanced Monitoring**을 체크 해제합니다.
    <img src="/images/week5/5-1-task4-step82-monitoring.png" alt="Monitoring 설정" class="guide-img-md" />

83. **Additional configuration** 섹션을 확장하여 ▢ **Enable deletion protection**이 체크 해제되어 있는지 확인합니다.
    <img src="/images/week5/5-1-task4-step83-additional.png" alt="Additional configuration 확인" class="guide-img-md" />
84. [[Create read replica]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task4-step84-create-replica.png" alt="Create read replica 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> `mysql-lab-replica`의 상태가 "Available"로 변경될 때까지 기다립니다.  
> Read Replica 생성에 약 5-10분이 소요됩니다. 상태가 "Available"로 변경될 때까지 기다린 후 다음 태스크를 진행합니다.

✅ **태스크 완료**: Read Replica가 생성되었습니다.

## 태스크 5: 수동 스냅샷 생성

이 태스크에서는 데이터베이스의 수동 스냅샷을 생성합니다. 수동 스냅샷은 명시적으로 삭제하기 전까지 보관되며, 특정 시점의 데이터를 복구할 때 사용합니다.

85. `mysql-lab-instance`를 선택합니다.
86. **Actions** > `Take snapshot`을 선택합니다.
    <img src="/images/week5/5-1-task5-step86-snapshot.png" alt="Take snapshot 선택" class="guide-img-md" />

87. **Snapshot name**에 `mysql-lab-snapshot-manual`을 입력합니다.
88. [[Take snapshot]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-task5-step88-take-snapshot.png" alt="Take snapshot 버튼 클릭" class="guide-img-md" />

89. 왼쪽 메뉴에서 **Snapshots**를 선택하여 스냅샷 생성 진행 상황을 확인합니다.
    <img src="/images/week5/5-1-task5-step89-snapshots-1.png" alt="Snapshots 목록 확인" class="guide-img-md" />
    <img src="/images/week5/5-1-task5-step89-snapshots-2.png" alt="스냅샷 생성 완료" class="guide-img-md" />

✅ **태스크 완료**: 수동 스냅샷이 생성되었습니다.

## 태스크 6: 자동 백업 확인

이 태스크에서는 Amazon RDS의 자동 백업 설정을 확인합니다. 자동 백업은 지정된 보관 기간 동안 매일 자동으로 생성되며, 특정 시점으로 복구(Point-in-Time Recovery)를 지원합니다.

90. `mysql-lab-instance`를 선택합니다.
91. **Maintenance & backups** 탭을 선택합니다.
    <img src="/images/week5/5-1-task6-step91-maintenance-backups.png" alt="Maintenance & backups 탭" class="guide-img-md" />

92. **Backup** 섹션에서 다음을 확인합니다:
    - **Automated backups**: `Enabled (7 Days)`
    - **Latest restore time**: 복구 가능한 최신 시점 (예: May 12, 2026, 13:50 (UTC+09:00))
    - **Backup window**: 자동 백업 실행 시간 (예: 14:19-14:49 UTC (GMT))
    - **Backup target**: `AWS Cloud (Asia Pacific (Seoul))`
93. **Snapshots** 섹션에서 다음을 확인합니다:
    - `mysql-lab-snapshot-manual` (Manual) — 태스크 5에서 생성한 수동 스냅샷
    - `rds:mysql-lab-instance-YYYY-MM-DD-HH-MM` (Automated) — 자동 생성된 스냅샷

> [!NOTE]
> 자동 스냅샷은 Backup window에 설정된 시간에 매일 생성됩니다.
> 인스턴스 생성 직후에는 자동 스냅샷이 아직 생성되지 않았을 수 있습니다.

✅ **태스크 완료**: 자동 백업이 확인되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon RDS MySQL 인스턴스를 Multi-AZ로 생성했습니다.
- Multi-AZ 페일오버를 시뮬레이션하여 고가용성 메커니즘을 확인했습니다.
- Read Replica를 생성하여 읽기 성능을 향상시켰습니다.
- 자동 백업과 수동 스냅샷을 구성했습니다.
- Multi-AZ와 Read Replica의 차이를 이해했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 반드시 수행하여 불필요한 비용을 방지합니다.

---

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `5-1`
6. [[Search resources]] 버튼을 클릭합니다.
   <img src="/images/week5/5-1-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

7. 이 실습에서 생성한 리소스들이 표시됩니다:
   - Amazon RDS 인스턴스 (`mysql-lab-instance`, `mysql-lab-replica`)
   - AWS CloudFormation 스택으로 생성된 네트워크 리소스 (Amazon VPC, 서브넷, 보안 그룹, NAT Gateway, Elastic IP 등)

> [!NOTE]
> Tag Editor 검색 결과에는 수동으로 생성한 Amazon RDS 인스턴스뿐만 아니라, 태스크 0에서 AWS CloudFormation으로 생성한 네트워크 리소스들도 함께 표시됩니다. 이는 CloudFormation 템플릿에서 모든 리소스에 동일한 태그(`Week: 5-1`)를 적용했기 때문입니다.

> [!TIP]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

---

### 단계 2: Amazon RDS 인스턴스 삭제

다음 두 가지 방법 중 하나를 선택하여 리소스를 삭제할 수 있습니다.

> [!IMPORTANT]
> **삭제 순서 중요**: Read Replica를 먼저 삭제한 후 Primary 인스턴스를 삭제해야 합니다. Read Replica가 존재하는 상태에서 Primary를 삭제하면 Read Replica가 독립 실행형 인스턴스로 자동 승격되어 비용이 계속 발생할 수 있습니다.

### 옵션 1: AWS 콘솔에서 수동 삭제 (권장)

> [!TIP]
> AWS 관리 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 권장합니다.
>
> AWS CLI 명령어에 익숙한 경우 아래 [옵션 2](#option-2)를 사용하면 더 빠르게 삭제할 수 있습니다.

**Read Replica 삭제**

8. Amazon RDS 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Databases**를 선택합니다.
10. `mysql-lab-replica`를 선택합니다.
11. **Actions** > `Delete`를 선택합니다.
    <img src="/images/week5/5-1-cleanup-step11-delete-replica.png" alt="mysql-lab-replica 선택" class="guide-img-md" />

12. 확인 창에서 `delete me`를 입력합니다.
13. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-cleanup-step13-delete-replica-confirm.png" alt="Delete 확인 창" class="guide-img-sm" />

> [!NOTE]
> Read Replica는 최종 스냅샷을 생성할 수 없으므로 체크박스 옵션이 표시되지 않습니다. "Final Snapshots are not available for Read Replica DB Instances" 경고 메시지만 표시됩니다.

> [!OUTPUT]
> 상단에 "Successfully deleted DB instance mysql-lab-replica" 메시지가 표시됩니다.

14. 페이지를 새로고침하여 `mysql-lab-replica`가 목록에서 완전히 사라졌는지 확인합니다.

> [!IMPORTANT]
> Read Replica가 완전히 삭제된 후에 다음 단계로 진행합니다.
> 삭제 직후에는 목록에 남아있을 수 있으므로 페이지를 새로고침하여 `mysql-lab-replica`가 완전히 사라진 것을 확인합니다.

**Primary 인스턴스 삭제**

15. `mysql-lab-instance`를 선택합니다.
16. **Actions** > `Delete`를 선택합니다.
    <img src="/images/week5/5-1-cleanup-step16-delete-primary.png" alt="Primary 인스턴스 Delete 선택" class="guide-img-md" />

17. ▢ **Create final snapshot** 체크박스가 체크 해제되어 있는지 확인합니다.
18. ▢ **Retain automated backups** 체크박스가 체크 해제되어 있는지 확인합니다.
19. ☑️ **I acknowledge that upon instance deletion, automated backups, including system snapshots and point-in-time recovery, will no longer be available.** 체크박스를 체크합니다.
20. 확인 창에서 `delete me`를 입력합니다.
21. [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-cleanup-step21-delete-primary-confirm.png" alt="Primary 삭제 확인 창" class="guide-img-sm" />

> [!OUTPUT]
> 상단에 "Successfully deleted DB instance mysql-lab-instance" 메시지가 표시됩니다.

22. 페이지를 새로고침하여 `mysql-lab-instance`가 목록에서 완전히 사라졌는지 확인합니다.

> [!IMPORTANT]
> Primary 인스턴스가 완전히 삭제된 후에 다음 단계로 진행합니다.
> 삭제 직후에는 목록에 남아있을 수 있으므로 페이지를 새로고침하여 `mysql-lab-instance`가 완전히 사라진 것을 확인합니다.

**수동 스냅샷 삭제**

23. 왼쪽 메뉴에서 **Snapshots**를 선택합니다.
24. **Manual** 탭에서 `mysql-lab-snapshot-manual`을 선택합니다.
25. **Actions** > `Delete snapshot`을 선택합니다.
    <img src="/images/week5/5-1-cleanup-step25-delete-snapshot.png" alt="스냅샷 삭제 선택" class="guide-img-md" />

26. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-cleanup-step26-delete-snapshot-confirm.png" alt="스냅샷 삭제 확인" class="guide-img-sm" />

> [!NOTE]
> 자동 스냅샷은 **System** 탭에 표시됩니다. System 스냅샷은 직접 삭제할 수 없습니다.
>
> - **인스턴스가 존재하는 경우**: 인스턴스의 백업 보존 기간을 줄이면 자동으로 제거됩니다.
> - **인스턴스를 삭제한 경우**: 왼쪽 메뉴의 **Automated backups** > **Retained** 탭에서 retained automated backup을 삭제하면 System 스냅샷도 함께 제거됩니다.
>
> 이 실습에서는 인스턴스 삭제 시 **Retain automated backups**를 체크 해제하므로 자동 백업이 함께 삭제됩니다.
>
> **System 스냅샷이 남아있는 경우**:
>
> 1. 왼쪽 메뉴의 **Automated backups**를 선택합니다.
> 2. **Retained** 탭을 선택합니다.
> 3. `mysql-lab-instance`를 선택합니다.
> 4. **Actions** > `Delete`를 선택합니다.
> 5. 확인 창에서 `delete me`를 입력하고 [[Delete]] 버튼을 클릭합니다.

### 옵션 2: AWS CloudShell 스크립트로 일괄 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 위 [옵션 1](#option-1)을 참고합니다.

27. AWS Management Console 상단의 CloudShell 아이콘을 클릭합니다.
28. Read Replica를 삭제합니다:

```bash
aws rds delete-db-instance \
  --region ap-northeast-2 \
  --db-instance-identifier mysql-lab-replica \
  --skip-final-snapshot \
```

<img src="/images/week5/5-1-cleanup-step28-delete-replica.png" alt="CloudShell 열기" class="guide-img-md" />

29. Read Replica 삭제가 완료될 때까지 대기합니다 (약 5-10분 소요):

```bash
aws rds wait db-instance-deleted \
  --region ap-northeast-2 \
  --db-instance-identifier mysql-lab-replica
```

<img src="/images/week5/5-1-cleanup-step29-wait.png" alt="Read Replica CLI 삭제 실행" class="guide-img-md" />

> [!TIP] CLI로 확인
>
> ```bash
> aws rds describe-db-instances --region ap-northeast-2 --db-instance-identifier mysql-lab-replica 2>&1 | grep -q "DBInstanceNotFound" && echo "삭제 완료" || echo "Available 또는 삭제 진행 중"
> ```
>
> <img src="/images/week5/5-1-cleanup-step29-cli-verify.png" alt="CLI 삭제 확인 결과" class="guide-img-md" />

30. Primary 인스턴스를 삭제합니다:

```bash
aws rds delete-db-instance \
  --region ap-northeast-2 \
  --db-instance-identifier mysql-lab-instance \
  --skip-final-snapshot \
```

<img src="/images/week5/5-1-cleanup-step30-delete-primary.png" alt="Primary CLI 삭제 실행" class="guide-img-md" />

31. Primary 인스턴스 삭제가 완료될 때까지 대기합니다 (약 5-10분 소요):

```bash
aws rds wait db-instance-deleted \
  --region ap-northeast-2 \
  --db-instance-identifier mysql-lab-instance
```

<img src="/images/week5/5-1-cleanup-step31-wait.png" alt="Primary wait 완료" class="guide-img-md" />

> [!TIP] CLI로 확인
>
> ```bash
> aws rds describe-db-instances --region ap-northeast-2 --db-instance-identifier mysql-lab-instance 2>&1 | grep -q "DBInstanceNotFound" && echo "삭제 완료" || echo "Available 또는 삭제 진행 중"
> ```

32. 수동 스냅샷을 삭제합니다:

```bash
aws rds delete-db-snapshot \
  --region ap-northeast-2 \
  --db-snapshot-identifier mysql-lab-snapshot-manual
```

<img src="/images/week5/5-1-cleanup-step32-delete-snapshot-cli.png" alt="수동 스냅샷 CLI 삭제" class="guide-img-md" />

> [!TIP] CLI로 삭제 확인
> 다음 명령어로 모든 인스턴스가 삭제되었는지 확인할 수 있습니다:
>
> ```bash
> # RDS 인스턴스 목록 확인
> aws rds describe-db-instances \
>   --region ap-northeast-2 \
>   --query "DBInstances[?contains(DBInstanceIdentifier, 'mysql-lab')].{ID:DBInstanceIdentifier,Status:DBInstanceStatus}" \
>   --output table
>
> # 수동 스냅샷 확인
> aws rds describe-db-snapshots \
>   --region ap-northeast-2 \
>   --query "DBSnapshots[?contains(DBSnapshotIdentifier, 'mysql-lab')].{ID:DBSnapshotIdentifier,Status:Status}" \
>   --output table
> ```
>
> 결과가 비어있으면 삭제 완료입니다.
>
> <img src="/images/week5/5-1-cleanup-step32-cli-verify.png" alt="CLI 삭제 확인 결과" class="guide-img-md" />

---

### 단계 3: AWS CloudFormation 스택 삭제

> [!IMPORTANT]
> Amazon RDS 인스턴스(Primary, Read Replica)가 모두 삭제 완료된 후에 AWS CloudFormation 스택을 삭제합니다.
> Amazon RDS 인스턴스가 남아있으면 Amazon VPC 관련 리소스 삭제가 실패합니다.

33. AWS CloudFormation 콘솔로 이동합니다.
34. `week5-1-rds-stack` 스택을 선택합니다.
35. [[Delete stack]] 버튼을 클릭합니다.
36. 확인 창에서 스택 이름 `week5-1-rds-stack`을 입력합니다.
37. [[Delete stack]] 버튼을 클릭합니다.
    <img src="/images/week5/5-1-cleanup-step37-delete-stack.png" alt="Delete stack 확인" class="guide-img-sm" />

38. 스택 상태가 "DELETE_IN_PROGRESS"로 변경됩니다.

> [!NOTE]
> 스택 삭제가 완료될 때까지 기다립니다. 스택 삭제에 3-5분이 소요됩니다. 삭제가 완료되면 스택 목록에서 사라집니다.

💡 **참고**: AWS CloudFormation 스택을 삭제하면 Amazon VPC, 서브넷, 보안 그룹, DB 서브넷 그룹 등 모든 네트워크 리소스가 자동으로 삭제됩니다.

---

### 단계 4: Tag Editor로 모든 리소스 삭제 확인

39. AWS Management Console 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
40. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
41. **Regions**에서 `ap-northeast-2`를 선택합니다.
42. **Resource types**에서 `All supported resource types`를 선택합니다.
43. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `5-1`
44. [[Search resources]] 버튼을 클릭합니다.
45. 검색 결과에 리소스가 표시되지 않는지 확인합니다.
    <img src="/images/week5/5-1-cleanup-step45-tageditor-final.png" alt="Tag Editor 최종 확인" class="guide-img-md" />

> [!NOTE]
> 모든 리소스가 정상적으로 삭제되었다면 검색 결과에 아무것도 표시되지 않습니다.
> 만약 리소스가 남아있다면 해당 리소스를 수동으로 삭제합니다.

> [!TIP]
> NAT Gateway가 검색 결과에 표시될 수 있습니다. NAT Gateway는 삭제 후에도 "Deleted" 상태로 일정 시간 Tag Editor에 남아있으며, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

46. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
47. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
48. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
49. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
50. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [Amazon RDS Multi-AZ 배포](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Amazon RDS Read Replicas](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Amazon RDS 백업 및 복원](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)

## 📚 참고: Amazon RDS Multi-AZ 및 Read Replica 개념

### Multi-AZ 페일오버 메커니즘

Multi-AZ 페일오버는 다음 상황에서 자동으로 발생합니다:

**자동 페일오버 트리거**

- Primary AZ 장애: 가용 영역 전체 장애
- Primary DB 인스턴스 장애: 하드웨어 또는 소프트웨어 장애
- 네트워크 연결 끊김: Primary와 Standby 간 연결 문제
- 수동 페일오버: 유지 관리 목적

**페일오버 프로세스**

- Amazon RDS가 Primary 인스턴스의 장애를 감지합니다.
- DNS 레코드가 Standby 인스턴스를 가리키도록 자동 업데이트됩니다.
- Standby 인스턴스가 새로운 Primary가 됩니다.
- 애플리케이션은 동일한 Endpoint를 사용하여 자동으로 재연결됩니다.

### Read Replica 사용 사례

Read Replica는 다음 상황에서 유용합니다:

**읽기 성능 향상**

- 읽기 트래픽을 여러 Replica로 분산
- Primary 인스턴스의 부하 감소
- 지리적으로 분산된 사용자에게 낮은 지연 시간 제공

**보고 및 분석**

- 프로덕션 데이터베이스에 영향을 주지 않고 복잡한 쿼리 실행
- 별도의 Replica에서 분석 워크로드 실행

**재해 복구**

- Read Replica를 독립 실행형 인스턴스로 승격
- 리전 간 Read Replica로 재해 복구 전략 구현

### Multi-AZ vs Read Replica

**Multi-AZ**

- 목적: 고가용성 및 자동 페일오버
- 복제 방식: 동기식 복제
- 접근: Standby는 읽기/쓰기 불가 (대기 전용)
- 페일오버: 자동 (1-2분)
- 비용: Primary와 동일한 인스턴스 비용

**Read Replica**

- 목적: 읽기 성능 확장 및 분석
- 복제 방식: 비동기식 복제
- 접근: 읽기 전용 쿼리 가능
- 페일오버: 수동 승격 필요
- 비용: 각 Replica마다 인스턴스 비용

### 백업 vs 스냅샷

**자동 백업**

- 매일 자동으로 생성
- 보존 기간: 0-35일 (설정 가능)
- Point-in-Time Recovery 지원
- 인스턴스 삭제 시 함께 삭제

**수동 스냅샷**

- 사용자가 수동으로 생성
- 보존 기간: 무제한 (명시적 삭제 필요)
- 특정 시점의 전체 백업
- 인스턴스 삭제 후에도 유지
