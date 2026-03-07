# Week 3-2: 3-Tier 아키텍처 보안 그룹 구성 실습

## 📋 개요

이 실습에서는 3-Tier 아키텍처를 위한 VPC 환경을 CloudFormation으로 자동 생성하고, 계층별 보안 그룹을 수동으로 구성하여 보안 그룹 체인을 학습합니다.

## 📦 포함 파일

- `week3-2-security-group-lab.yaml` - 3-Tier VPC 환경 CloudFormation 템플릿
- `README.md` - 이 파일 (배포 가이드 및 아키텍처 설명)

## 🏗️ 아키텍처 구성 요소

### 1. VPC 및 네트워크
- **VPC**: 10.0.0.0/16 CIDR 블록
- **가용 영역**: ap-northeast-2a, ap-northeast-2c (2개 AZ)

### 2. 서브넷 구성 (총 8개)

#### Public Tier (2개)
- `Public-Subnet-A`: 10.0.1.0/24 (ap-northeast-2a)
- `Public-Subnet-C`: 10.0.2.0/24 (ap-northeast-2c)
- **용도**: Application Load Balancer (ALB) 배치

#### Web Tier (2개)
- `Web-Subnet-A`: 10.0.11.0/24 (ap-northeast-2a)
- `Web-Subnet-C`: 10.0.12.0/24 (ap-northeast-2c)
- **용도**: 웹 서버 (Nginx, Apache 등)

#### App Tier (2개)
- `App-Subnet-A`: 10.0.21.0/24 (ap-northeast-2a)
- `App-Subnet-C`: 10.0.22.0/24 (ap-northeast-2c)
- **용도**: 애플리케이션 서버 (Node.js, Java 등)

#### DB Tier (2개)
- `DB-Subnet-A`: 10.0.31.0/24 (ap-northeast-2a)
- `DB-Subnet-C`: 10.0.32.0/24 (ap-northeast-2c)
- **용도**: 데이터베이스 (RDS, Aurora 등)

### 3. 네트워크 게이트웨이
- **Internet Gateway**: Public 서브넷의 인터넷 연결
- **NAT Gateway**: Private 서브넷의 아웃바운드 인터넷 연결
  - Public-Subnet-A에 배치
  - Elastic IP 자동 할당

### 4. 라우팅 테이블

#### Public Route Table
- 대상: 0.0.0.0/0 → Internet Gateway
- 연결: Public-Subnet-A, Public-Subnet-C

#### Private Route Table
- 대상: 0.0.0.0/0 → NAT Gateway
- 연결: Web-Subnet-A/C, App-Subnet-A/C, DB-Subnet-A/C

### 5. 보안 그룹 (기본 구성)

템플릿은 다음 보안 그룹을 **기본 규칙만 포함하여** 생성합니다:

#### ALB-SG (Application Load Balancer)
- **Inbound**: 
  - HTTP (80) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0

#### Web-Tier-SG (웹 서버)
- **Inbound**: 
  - HTTP (80) from ALB-SG
  - HTTPS (443) from ALB-SG

#### App-Tier-SG (애플리케이션 서버)
- **Inbound**: 
  - TCP 8080 from Web-Tier-SG

#### DB-Tier-SG (데이터베이스)
- **Inbound**: 
  - MySQL/Aurora (3306) from App-Tier-SG

> **참고**: 실습에서는 SSH 접근 규칙 등 추가 규칙을 수동으로 구성합니다.

## 🚀 CloudFormation 배포 가이드

### 1. AWS Management Console 접속
1. AWS Management Console에 로그인합니다
2. 상단 검색창에서 `CloudFormation`을 검색하고 선택합니다
3. 리전이 **ap-northeast-2 (서울)**인지 확인합니다

### 2. 스택 생성
1. [[Create stack]] > **With new resources (standard)**를 선택합니다
2. **Prepare template**에서 `Template is ready`를 선택합니다
3. **Template source**에서 `Upload a template file`을 선택합니다
4. [[Choose file]] 버튼을 클릭하고 `vpc-3tier-environment.yaml` 파일을 선택합니다
5. [[Next]] 버튼을 클릭합니다

### 3. 스택 세부 정보 지정
1. **Stack name**에 `week3-2-vpc-environment`를 입력합니다
2. **Parameters** 섹션:
   - **EnvironmentName**: `Lab` (기본값 유지)
   - 다른 파라미터는 기본값 유지
3. [[Next]] 버튼을 클릭합니다

### 4. 스택 옵션 구성
1. **Tags** (선택사항):
   - Key: `Purpose`, Value: `Week3-Lab`
   - Key: `Owner`, Value: `[본인 이름]`
2. 다른 옵션은 기본값 유지
3. [[Next]] 버튼을 클릭합니다

### 5. 검토 및 생성
1. 설정 내용을 검토합니다
2. 페이지 하단으로 스크롤합니다
3. [[Submit]] 버튼을 클릭합니다

### 6. 스택 생성 모니터링
1. 스택 상태가 `CREATE_IN_PROGRESS`로 표시됩니다
2. **Events** 탭을 선택하여 생성 과정을 확인합니다
3. 약 5-7분 후 상태가 `CREATE_COMPLETE`로 변경됩니다

> **참고**: NAT Gateway 생성에 시간이 소요됩니다. 대기하는 동안 실습 가이드를 미리 읽어보세요.

### 7. 출력값 확인
1. **Outputs** 탭을 선택합니다
2. 다음 값들을 메모장에 복사합니다:

| 출력 키 | 설명 | 사용 태스크 |
|---------|------|-------------|
| VpcId | VPC ID | 모든 태스크 |
| PublicSubnetAId | Public 서브넷 A ID | 태스크 1 |
| PublicSubnetCId | Public 서브넷 C ID | 태스크 1 |
| WebSubnetAId | Web 서브넷 A ID | 태스크 2 |
| WebSubnetCId | Web 서브넷 C ID | 태스크 2 |
| AppSubnetAId | App 서브넷 A ID | 태스크 3 |
| AppSubnetCId | App 서브넷 C ID | 태스크 3 |
| DBSubnetAId | DB 서브넷 A ID | 태스크 4 |
| DBSubnetCId | DB 서브넷 C ID | 태스크 4 |
| ALBSecurityGroupId | ALB 보안 그룹 ID | 태스크 1 |
| WebSecurityGroupId | Web 보안 그룹 ID | 태스크 2 |
| AppSecurityGroupId | App 보안 그룹 ID | 태스크 3 |
| DBSecurityGroupId | DB 보안 그룹 ID | 태스크 4 |

> **중요**: 이 출력값들은 실습 가이드의 각 태스크에서 사용됩니다.

## 📐 보안 그룹 설계 원칙

### 1. 최소 권한 원칙 (Principle of Least Privilege)
각 계층은 **필요한 최소한의 권한**만 부여받아야 합니다.

**❌ 잘못된 예시:**
```
DB-Tier-SG Inbound: MySQL (3306) from 0.0.0.0/0
→ 인터넷 전체에서 데이터베이스 접근 가능 (보안 위험!)
```

**✅ 올바른 예시:**
```
DB-Tier-SG Inbound: MySQL (3306) from App-Tier-SG
→ App 계층에서만 데이터베이스 접근 가능 (최소 권한)
```

### 2. 보안 그룹 체인 (Security Group Chaining)
각 계층은 **이전 계층의 보안 그룹만** 참조해야 합니다.

```
Internet → ALB-SG → Web-Tier-SG → App-Tier-SG → DB-Tier-SG
```

**장점:**
- 명확한 트래픽 흐름
- 계층 간 격리
- 쉬운 문제 해결

### 3. Stateful 특성 활용
보안 그룹은 **Stateful**이므로:
- 인바운드 규칙만 설정하면 됩니다
- 응답 트래픽은 자동으로 허용됩니다
- 아웃바운드 규칙은 기본값(모두 허용) 유지

### 4. 보안 그룹 vs NACL

| 항목 | 보안 그룹 | NACL |
|------|-----------|------|
| 적용 레벨 | 인스턴스 | 서브넷 |
| 상태 추적 | Stateful | Stateless |
| 규칙 타입 | Allow만 | Allow + Deny |
| 규칙 평가 | 모든 규칙 | 번호 순서 |
| 응답 트래픽 | 자동 허용 | 명시적 허용 필요 |

## 🔍 실습 후 검증 방법

### 1. VPC 구성 확인
```bash
# VPC 콘솔에서 확인
- VPC: 1개 (10.0.0.0/16)
- 서브넷: 8개 (Public 2, Web 2, App 2, DB 2)
- Internet Gateway: 1개
- NAT Gateway: 1개
- 라우팅 테이블: 2개 (Public, Private)
```

### 2. 보안 그룹 체인 확인
```bash
# 각 보안 그룹의 인바운드 규칙 확인
ALB-SG:
  - HTTP (80) from 0.0.0.0/0 ✓
  - HTTPS (443) from 0.0.0.0/0 ✓

Web-Tier-SG:
  - HTTP (80) from ALB-SG ✓
  - HTTPS (443) from ALB-SG ✓
  - SSH (22) from My IP ✓

App-Tier-SG:
  - TCP 8080 from Web-Tier-SG ✓
  - SSH (22) from Web-Tier-SG ✓

DB-Tier-SG:
  - MySQL (3306) from App-Tier-SG ✓
```

### 3. 네트워크 연결 확인
```bash
# Public 서브넷 → Internet Gateway
Public Route Table:
  - 0.0.0.0/0 → igw-xxxxx ✓

# Private 서브넷 → NAT Gateway
Private Route Table:
  - 0.0.0.0/0 → nat-xxxxx ✓
```

## 💰 비용 정보

### 예상 비용 (ap-northeast-2 리전 기준)
- **NAT Gateway**: 시간당 약 $0.045
- **Elastic IP**: NAT Gateway 연결 시 무료
- **VPC, 서브넷, 보안 그룹**: 무료

### 실습 시간별 예상 비용
- 1시간: 약 $0.045
- 2시간: 약 $0.090
- 4시간: 약 $0.180

> **중요**: 실습 종료 후 반드시 CloudFormation 스택을 삭제하여 비용을 절감하세요.

## 🗑️ 리소스 정리

### CloudFormation 스택 삭제
1. CloudFormation 콘솔로 이동합니다
2. `week3-2-vpc-environment` 스택을 선택합니다
3. [[Delete]] 버튼을 클릭합니다
4. 확인 창에서 [[Delete]] 버튼을 클릭합니다
5. 스택 삭제가 완료될 때까지 기다립니다 (약 3-5분)

> **참고**: CloudFormation 스택을 삭제하면 다음 리소스가 자동으로 삭제됩니다:
> - VPC 및 모든 서브넷
> - Internet Gateway
> - NAT Gateway 및 Elastic IP
> - 라우팅 테이블
> - 보안 그룹

### 수동 삭제가 필요한 경우
스택 삭제가 실패하면 다음 순서로 수동 삭제합니다:

1. **NAT Gateway 삭제** (가장 먼저)
2. **Elastic IP 해제**
3. **Internet Gateway Detach 및 삭제**
4. **서브넷 삭제** (8개)
5. **보안 그룹 삭제** (4개)
6. **라우팅 테이블 삭제** (2개)
7. **VPC 삭제** (가장 마지막)

## 📚 추가 학습 리소스

### AWS 공식 문서
- [Amazon VPC 사용 설명서](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/)
- [보안 그룹](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/VPC_SecurityGroups.html)
- [네트워크 ACL](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/vpc-network-acls.html)
- [NAT Gateway](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/vpc-nat-gateway.html)

### 베스트 프랙티스
- [VPC 보안 모범 사례](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/vpc-security-best-practices.html)
- [3-Tier 아키텍처 설계](https://aws.amazon.com/architecture/reference-architecture-diagrams/)

## 🆘 문제 해결

### 스택 생성 실패
**문제**: `CREATE_FAILED` 상태

**해결**:
1. **Events** 탭에서 오류 메시지 확인
2. 일반적인 원인:
   - 리전에 NAT Gateway 할당량 초과
   - Elastic IP 할당량 초과
   - VPC 할당량 초과
3. 할당량 증가 요청 또는 기존 리소스 정리 후 재시도

### NAT Gateway 생성 시간 초과
**문제**: NAT Gateway 생성에 10분 이상 소요

**해결**:
1. 정상적인 현상입니다 (최대 15분 소요 가능)
2. **Events** 탭에서 `CREATE_IN_PROGRESS` 상태 확인
3. 오류가 없으면 계속 대기

### 보안 그룹 규칙 추가 실패
**문제**: "규칙을 추가할 수 없습니다" 오류

**해결**:
1. 참조하는 보안 그룹이 존재하는지 확인
2. 동일한 규칙이 이미 존재하는지 확인
3. 보안 그룹 규칙 할당량 확인 (기본 60개)

## 📞 지원

문제가 지속되면 다음을 확인하세요:
- AWS 서비스 상태: https://status.aws.amazon.com/
- AWS Support Center (계정 로그인 필요)
- 실습 가이드의 문제 해결 섹션

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-02-07  
**작성자**: AWS 실습 가이드 팀
