# Week 3-1: Amazon VPC Endpoint 실습

## 📋 개요

이 실습에서는 Amazon VPC Endpoint의 두 가지 타입인 Interface Endpoint와 Gateway Endpoint를 생성하고 동작 원리를 학습합니다.

## 📦 포함 파일

- `week3-1-vpc-lab.yaml` - VPC 환경 CloudFormation 템플릿
- `week3-vpc-base.yaml` - VPC 기본 환경 템플릿 (참고용)
- `README.md` - 이 파일 (배포 가이드 및 아키텍처 설명)

## 🏗️ 아키텍처 구성 요소

### 1. VPC 및 네트워크
- **VPC**: 10.0.0.0/16 CIDR 블록
- **가용 영역**: ap-northeast-2a, ap-northeast-2c (2개 AZ)

### 2. 서브넷 구성
- **Public Subnet**: 10.0.1.0/24, 10.0.2.0/24
- **Private Subnet**: 10.0.11.0/24, 10.0.12.0/24

### 3. 네트워크 구성 요소
- **Internet Gateway**: 퍼블릭 서브넷 인터넷 연결
- **NAT Gateway**: 프라이빗 서브넷 아웃바운드 인터넷 연결
- **Route Tables**: 퍼블릭/프라이빗 라우팅 테이블

### 4. EC2 인스턴스
- **Private EC2**: 프라이빗 서브넷에 배치
- **용도**: VPC Endpoint 테스트용

## 🚀 배포 방법

### 1. CloudFormation 스택 생성

1. AWS Management Console에서 CloudFormation 서비스로 이동
2. "Create stack" → "With new resources (standard)" 선택
3. "Upload a template file" 선택 후 `week3-1-vpc-lab.yaml` 업로드
4. 스택 이름: `week3-1-vpc-stack`
5. 파라미터 기본값 유지
6. 태그 추가:
   - Project: AWS-Lab
   - Week: 3-1
   - CreatedBy: Student
7. "Submit" 클릭하여 스택 생성

### 2. 스택 생성 완료 대기

- 생성 시간: 약 5-7분
- 상태가 "CREATE_COMPLETE"로 변경될 때까지 대기

### 3. Outputs 확인

스택 생성 완료 후 Outputs 탭에서 다음 정보 확인:
- VPC ID
- Private Subnet IDs
- EC2 Instance ID
- Security Group ID

## 📚 VPC Endpoint 개념

### Interface Endpoint (ENI 기반)
- AWS PrivateLink 기술 사용
- 서브넷에 ENI(Elastic Network Interface) 생성
- 프라이빗 IP 주소 할당
- 시간당 요금 + 데이터 처리 요금
- 대부분의 AWS 서비스 지원

### Gateway Endpoint (라우팅 테이블 기반)
- 라우팅 테이블에 경로 추가
- ENI 생성 없음
- 무료
- S3, DynamoDB만 지원

## 🔍 실습에서 생성할 VPC Endpoint

### 1. Interface Endpoint (3개)
- **ssm**: AWS Systems Manager 서비스
- **ssmmessages**: Session Manager 메시지
- **ec2messages**: EC2 인스턴스 메시지

### 2. Gateway Endpoint (1개)
- **S3**: Amazon S3 서비스

## 🧹 리소스 정리

실습 종료 후 다음 순서로 리소스 삭제:

1. **VPC Endpoint 삭제** (콘솔에서 수동 삭제)
   - Interface Endpoint 3개 삭제
   - Gateway Endpoint 1개 삭제

2. **CloudFormation 스택 삭제**
   - CloudFormation 콘솔에서 `week3-1-vpc-stack` 선택
   - "Delete" 버튼 클릭
   - 삭제 완료까지 약 5-10분 소요

## ⚠️ 주의사항

- NAT Gateway는 시간당 요금이 발생하므로 실습 종료 후 반드시 삭제
- Interface Endpoint도 시간당 요금이 발생하므로 실습 종료 후 반드시 삭제
- Gateway Endpoint는 무료이지만 정리 차원에서 삭제 권장

## 📖 참고 자료

- [AWS VPC Endpoints 공식 문서](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [AWS PrivateLink 가격](https://aws.amazon.com/privatelink/pricing/)
- [Session Manager VPC Endpoint 요구사항](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-privatelink.html)
