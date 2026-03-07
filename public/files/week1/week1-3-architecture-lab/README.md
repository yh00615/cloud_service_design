# QuickTable 아키텍처 다이어그램 실습 가이드

이 가이드는 Draw.io를 사용하여 QuickTable 레스토랑 예약 시스템의 3-Tier 아키텍처를 설계하는 실습을 위한 참고 자료입니다.

## 📦 실습 목표

- Draw.io를 사용하여 AWS 3-Tier 아키텍처 다이어그램 작성
- Multi-AZ 고가용성 설계 원칙 적용
- QuickTable 프로젝트의 3-Tier 구성 요소 이해

## 🚀 Draw.io 빠른 시작

### 1. Draw.io 접속

**URL**: https://app.diagrams.net/?splash=0&libs=aws4

**파라미터 설명**:

- `splash=0` - 시작 화면 건너뛰기
- `libs=aws4` - AWS 아이콘 라이브러리 자동 로드

### 2. 언어 설정

**메뉴**: Extras > Language > English

### 3. 새 다이어그램 생성

1. Create New Diagram
2. Blank Diagram 선택
3. 파일명: `quicktable-architecture`
4. 저장 위치 선택 (Device, Google Drive, OneDrive 등)

## 🏗️ QuickTable 아키텍처 구성 요소

### VPC 및 네트워크

| 구성 요소            | CIDR         | 설명               |
| -------------------- | ------------ | ------------------ |
| QuickTable VPC       | 10.0.0.0/16  | 전체 네트워크 범위 |
| Public Subnet A      | 10.0.1.0/24  | ap-northeast-2a    |
| Public Subnet C      | 10.0.2.0/24  | ap-northeast-2c    |
| Private App Subnet A | 10.0.11.0/24 | ap-northeast-2a    |
| Private App Subnet C | 10.0.12.0/24 | ap-northeast-2c    |
| Private DB Subnet A  | 10.0.21.0/24 | ap-northeast-2a    |
| Private DB Subnet C  | 10.0.22.0/24 | ap-northeast-2c    |

### QuickTable 리소스 명명 규칙

| 리소스 타입        | 명명 규칙               | 예시                 |
| ------------------ | ----------------------- | -------------------- |
| VPC                | `QuickTable VPC`        | `QuickTable VPC`     |
| ALB                | `QuickTable-ALB`        | `QuickTable-ALB`     |
| EC2 (Web)          | `QuickTable-Web-{AZ}`   | `QuickTable-Web-A`   |
| RDS                | `quicktable-db`         | `quicktable-db`      |
| Auto Scaling Group | `QuickTable-{Tier}-ASG` | `QuickTable-Web-ASG` |
| Security Group     | `QuickTable-{Tier}-SG`  | `QuickTable-ALB-SG`  |

### 보안 그룹 규칙

#### QuickTable-ALB-SG

```
Inbound:
- Port 80 (HTTP) from 0.0.0.0/0
- Port 443 (HTTPS) from 0.0.0.0/0

Outbound:
- All traffic to QuickTable-Web-SG
```

#### QuickTable-Web-SG

```
Inbound:
- Port 80 from QuickTable-ALB-SG
- Port 443 from QuickTable-ALB-SG

Outbound:
- All traffic to QuickTable-DB-SG
```

#### QuickTable-DB-SG

```
Inbound:
- Port 3306 (MySQL) from QuickTable-Web-SG

Outbound:
- None (데이터베이스는 아웃바운드 불필요)
```

## 🎨 다이어그램 작성 팁

### 색상 구분

- **초록색**: Public Subnet (인터넷 접근 가능)
- **파란색**: Private App Subnet (애플리케이션 계층)
- **보라색**: Private DB Subnet (데이터베이스 계층)

### 화살표 사용

- **실선 화살표**: 데이터 흐름
- **점선 화살표**: 관리/모니터링 연결
- **양방향 화살표**: 동기화/복제 (RDS Multi-AZ)

### 레이블 작성

- **명확한 이름**: QuickTable 명명 규칙 준수
- **CIDR 표기**: 서브넷에는 CIDR 블록 포함
- **포트 정보**: 보안 그룹에는 허용 포트 명시

## 📋 체크리스트

### 필수 구성 요소

- [ ] QuickTable VPC (10.0.0.0/16)
- [ ] 2개의 가용 영역 (ap-northeast-2a, ap-northeast-2c)
- [ ] 6개의 서브넷 (Public x2, Private App x2, Private DB x2)
- [ ] Internet Gateway
- [ ] NAT Gateway x2 (각 AZ에 1개씩)
- [ ] QuickTable-ALB (Application Load Balancer)
- [ ] QuickTable-Web Tier EC2 x2 + Auto Scaling
- [ ] quicktable-db (RDS Multi-AZ: Primary + Standby)
- [ ] 3개의 Security Group (ALB, Web, DB)

### 연결 확인

- [ ] Internet Gateway → Public Subnet
- [ ] NAT Gateway → Private Subnet
- [ ] QuickTable-ALB → Web Tier
- [ ] Web Tier → RDS Primary
- [ ] RDS Primary ↔ RDS Standby (Synchronous Replication)

## 🔍 AWS Well-Architected Framework 원칙

### 1. 안정성 (Reliability)

**Multi-AZ 고가용성**

- Application Load Balancer는 2개의 퍼블릭 서브넷에 배포됩니다
- EC2 인스턴스는 Auto Scaling으로 각 AZ에 최소 1개씩 배포됩니다
- RDS Multi-AZ는 Primary와 Standby를 서로 다른 AZ에 배포합니다
- 단일 장애점(SPOF) 없이 고가용성을 보장합니다

**자동 복구**

- Auto Scaling이 비정상 인스턴스를 자동으로 교체합니다
- RDS Multi-AZ는 장애 시 1-2분 내에 자동 페일오버합니다
- ALB Health Check로 정상 인스턴스로만 트래픽을 전달합니다

### 2. 보안 (Security)

**계층화된 보안**

- 각 계층은 독립적인 보안 그룹으로 보호됩니다
- ALB-SG: 인터넷에서 HTTPS(443)만 허용
- Web-SG: ALB에서 HTTP(80)만 허용
- DB-SG: Web Tier에서 MySQL(3306)만 허용

**최소 권한 원칙**

- 각 EC2 인스턴스는 필요한 최소한의 IAM 역할만 가집니다
- RDS는 프라이빗 서브넷에 배치되어 외부 접근이 차단됩니다
- 보안 그룹은 이전 계층의 보안 그룹만 허용합니다

### 3. 성능 효율성 (Performance Efficiency)

**Auto Scaling 전략**

- Web Tier: CPU 70% 이상 시 스케일 아웃
- 트래픽 증가 시 자동으로 인스턴스를 추가합니다
- 트래픽 감소 시 자동으로 인스턴스를 제거합니다

**로드 밸런싱**

- ALB가 트래픽을 여러 EC2 인스턴스로 분산합니다
- Cross-Zone Load Balancing으로 AZ 간 트래픽을 균등하게 분산합니다
- Health Check로 정상 인스턴스로만 트래픽을 전달합니다

### 4. 비용 최적화 (Cost Optimization)

**인스턴스 타입 최적화**

- Web Tier: t3.small (가벼운 웹 서버)
- Reserved Instance 또는 Savings Plans로 최대 60% 비용 절감

**Auto Scaling 비용 절감**

- 트래픽이 적을 때 최소 인스턴스 수로 운영합니다
- 트래픽이 많을 때만 인스턴스를 추가합니다
- 유휴 리소스를 최소화하여 비용을 절감합니다

## 💡 QuickTable 아키텍처 고급 기능

### RDS Multi-AZ 고가용성

**동기식 복제**

- Primary DB에 쓰기가 발생하면 즉시 Standby로 복제됩니다
- 데이터 일관성을 보장합니다 (RPO = 0)
- 자동 페일오버로 1-2분 내에 복구됩니다 (RTO = 1-2분)

**자동 백업**

- 매일 자동 백업이 수행됩니다
- 백업 보존 기간: 7일
- Point-in-Time Recovery로 특정 시점으로 복구 가능합니다

### Auto Scaling 전략

**Web Tier Auto Scaling**

- 최소 인스턴스: 2개 (각 AZ에 1개씩)
- 최대 인스턴스: 10개
- 스케일링 정책: CPU 사용률 70% 이상 시 스케일 아웃
- 스케일링 쿨다운: 5분 (인스턴스 초기화 시간 고려)

### 모니터링 및 로깅

**CloudWatch 메트릭**

- ALB: 요청 수, 응답 시간, 오류율
- EC2: CPU 사용률, 네트워크 트래픽, 디스크 I/O
- RDS: CPU 사용률, 연결 수, 읽기/쓰기 IOPS

**CloudWatch Logs**

- ALB 액세스 로그: S3에 저장
- EC2 애플리케이션 로그: CloudWatch Logs Agent로 수집
- RDS 슬로우 쿼리 로그: 성능 최적화에 활용

**CloudWatch Alarms**

- CPU 사용률 80% 이상: SNS 알림
- RDS 연결 수 90% 이상: 경고
- ALB 5xx 오류율 5% 이상: 긴급 알림

## 📤 다이어그램 내보내기

### PNG 내보내기

1. File > Export as > PNG
2. Zoom: 300% (고해상도)
3. 배경: 투명 또는 흰색
4. 파일명: `quicktable-architecture.png`

### PDF 내보내기

1. File > Export as > PDF
2. 페이지 크기: A4 또는 Letter
3. 파일명: `quicktable-architecture.pdf`

### 원본 저장

1. File > Save
2. 형식: .drawio 또는 .xml
3. 저장 위치: Device, Google Drive, OneDrive 등

## 🔗 추가 리소스

### AWS 공식 문서

- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [3-Tier 아키텍처 모범 사례](https://docs.aws.amazon.com/ko_kr/whitepapers/latest/web-application-hosting-best-practices/an-aws-cloud-architecture-for-web-hosting.html)
- [RDS Multi-AZ 배포](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Auto Scaling 모범 사례](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-best-practices.html)
- [Application Load Balancer](https://docs.aws.amazon.com/ko_kr/elasticloadbalancing/latest/application/introduction.html)

### Draw.io 리소스

- [Draw.io 공식 사이트](https://www.diagrams.net/)
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)
- [Draw.io AWS 라이브러리](https://github.com/aws/aws-icons-for-plantuml)

### 3-Tier 아키텍처 예시

- [Web Application Hosting](https://aws.amazon.com/getting-started/hands-on/host-static-website/)
- [High Availability Architecture](https://docs.aws.amazon.com/ko_kr/whitepapers/latest/real-time-communication-on-aws/high-availability-and-scalability-on-aws.html)
- [Database Best Practices](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

## 📝 실습 후 확인 사항

### 아키텍처 검증

- [ ] VPC와 2개의 가용 영역이 올바르게 배치되었는가?
- [ ] 6개의 서브넷(Public x2, Private App x2, Private DB x2)이 모두 표시되었는가?
- [ ] QuickTable 명명 규칙을 준수했는가?
- [ ] ALB, EC2 인스턴스, RDS가 올바른 서브넷에 배치되었는가?
- [ ] 4개의 보안 그룹이 명확히 표현되었는가?
- [ ] 데이터 흐름이 명확히 표현되었는가?

### 다이어그램 품질

- [ ] 레이블이 명확하고 읽기 쉬운가?
- [ ] 화살표가 데이터 흐름을 정확히 표현하는가?
- [ ] 계층 구분이 명확한가?
- [ ] 다이어그램이 깔끔하고 정돈되어 있는가?
- [ ] 고해상도로 내보내기가 완료되었는가?

## 🎓 학습 목표 달성 확인

- [ ] Draw.io를 사용하여 AWS 3-Tier 아키텍처 다이어그램을 작성할 수 있습니다.
- [ ] Multi-AZ 고가용성 설계 원칙을 적용할 수 있습니다.
- [ ] QuickTable 프로젝트의 3-Tier 구성 요소를 이해합니다.
- [ ] 계층화된 보안 그룹 구조를 이해합니다.
- [ ] RDS Multi-AZ의 동작 원리를 이해합니다.
- [ ] Auto Scaling 전략을 이해합니다.
- [ ] Week 5-1에서 구축할 전체 시스템의 청사진을 완성했습니다.
