# QuickTable 3-Tier 아키텍처 개요

## 시스템 개요

QuickTable은 레스토랑 예약 시스템으로, 고객이 온라인으로 레스토랑을 검색하고 예약할 수 있는 웹 애플리케이션입니다.

## 아키텍처 구성

### 1. 프레젠테이션 계층 (Presentation Tier)

**구성 요소:**
- Application Load Balancer (ALB)
- 퍼블릭 서브넷 (2개 가용 영역)

**역할:**
- 인터넷에서 들어오는 HTTPS 트래픽 수신
- 트래픽을 애플리케이션 계층으로 분산
- SSL/TLS 종료 처리

### 2. 애플리케이션 계층 (Application Tier)

**구성 요소:**
- Amazon EC2 인스턴스 (Web Server)
- Amazon EC2 Auto Scaling 그룹
- 프라이빗 애플리케이션 서브넷 (2개 가용 영역)

**역할:**
- 비즈니스 로직 처리
- 사용자 요청 처리 및 응답 생성
- 데이터베이스와 통신

### 3. 데이터 계층 (Data Tier)

**구성 요소:**
- Amazon RDS MySQL (Multi-AZ)
- 프라이빗 데이터베이스 서브넷 (2개 가용 영역)

**역할:**
- 예약 데이터 저장 및 관리
- 트랜잭션 처리
- 데이터 백업 및 복구

## 네트워킹

### VPC 구성
- **CIDR**: 10.0.0.0/16
- **가용 영역**: ap-northeast-2a, ap-northeast-2c

### 서브넷 구성
각 가용 영역당:
- Public Subnet: 10.0.1.0/24, 10.0.2.0/24
- Private App Subnet: 10.0.11.0/24, 10.0.12.0/24
- Private DB Subnet: 10.0.21.0/24, 10.0.22.0/24

### 인터넷 연결
- **Internet Gateway**: 인터넷 트래픽 수신
- **NAT Gateway**: 프라이빗 서브넷의 아웃바운드 트래픽 처리 (각 AZ)

## 보안

### 보안 그룹
- **ALB-SG**: 0.0.0.0/0에서 HTTPS(443) 허용
- **Web-SG**: ALB-SG에서 HTTP(80) 허용
- **DB-SG**: Web-SG에서 MySQL(3306) 허용

### 네트워크 ACL
- 기본 NACL 사용
- 서브넷 레벨 트래픽 제어

## 고가용성 (High Availability)

### Multi-AZ 구성
- 2개 가용 영역에 리소스 분산
- 단일 장애 지점 제거

### Auto Scaling
- 트래픽에 따라 EC2 인스턴스 자동 확장/축소
- 최소 2개, 최대 6개 인스턴스

### RDS Multi-AZ
- Primary와 Standby 인스턴스
- 자동 장애 조치 (Failover)

## 확장성 (Scalability)

### 수평 확장
- Auto Scaling을 통한 EC2 인스턴스 추가
- ALB를 통한 트래픽 분산

### 수직 확장
- EC2 인스턴스 타입 변경
- RDS 인스턴스 타입 변경

## 성능 최적화

### 캐싱
- Amazon ElastiCache Redis (선택사항)
- 자주 조회되는 데이터 캐싱

### CDN
- Amazon CloudFront (선택사항)
- 정적 콘텐츠 배포

## 모니터링 및 로깅

### Amazon CloudWatch
- 메트릭 수집 및 모니터링
- 알람 설정

### AWS CloudTrail
- API 호출 로깅
- 감사 추적

## 비용 최적화

### 리소스 최적화
- Auto Scaling을 통한 리소스 효율화
- Reserved Instances 활용

### 스토리지 최적화
- S3 Lifecycle 정책
- RDS 스토리지 자동 확장

## 재해 복구 (Disaster Recovery)

### 백업
- RDS 자동 백업 (7일 보관)
- 스냅샷 생성

### 복구 전략
- Multi-AZ를 통한 자동 장애 조치
- 백업에서 복원
