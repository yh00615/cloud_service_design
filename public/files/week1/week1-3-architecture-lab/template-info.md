# Draw.io 환경 설정 가이드

이 가이드는 Draw.io에서 AWS 아키텍처 다이어그램을 작성하기 위한 환경 설정 방법을 설명합니다.

## 빠른 시작

### Draw.io 접속 (AWS 아이콘 자동 로드)

**URL**: https://app.diagrams.net/?splash=0&libs=aws4&lang=ko

**파라미터 설명**:

- `splash=0` - 시작 화면 건너뛰기
- `libs=aws4` - AWS 아이콘 라이브러리 자동 로드
- `lang=ko` - 한국어 인터페이스 (영어 선호 시 `lang=en`)

### 새 다이어그램 생성

1. 위 URL로 접속하면 자동으로 빈 다이어그램이 열립니다
2. 상단의 **제목 없는 다이어그램**을 클릭하여 이름 변경
3. 파일명: `quicktable-architecture` 입력
4. 저장 위치 선택 (Google 드라이브, 브라우저, 기기 등)

## QuickTable 아키텍처 구성 요소

### 필수 구성 요소

- VPC (10.0.0.0/16)
- 2개의 가용 영역 (ap-northeast-2a, ap-northeast-2c)
- 6개의 서브넷 (Public x2, Private App x2, Private DB x2)
- Internet Gateway
- NAT Gateway x2 (각 AZ에 1개씩)
- Application Load Balancer
- EC2 인스턴스 (Web Tier, App Tier) + Auto Scaling
- RDS Multi-AZ (Primary + Standby)
- 4개의 Security Group (ALB, Web, App, DB)

## 다이어그램 작성 팁

### 색상 구분

- **초록색**: Public Subnet
- **파란색**: Private App Subnet
- **보라색**: Private DB Subnet

### 화살표 사용

- **실선**: 데이터 흐름
- **점선**: 관리/모니터링
- **양방향**: 동기화/복제 (RDS Multi-AZ)

## 추가 정보

상세한 아키텍처 설계 가이드, 보안 그룹 규칙, Auto Scaling 전략, AWS Well-Architected Framework 원칙은 `README.md` 파일을 참고하세요.
