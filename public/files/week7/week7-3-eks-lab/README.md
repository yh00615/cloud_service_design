# Week 7-3 EKS Lab - CloudFormation 템플릿 가이드

## 개요

이 CloudFormation 템플릿은 Amazon EKS 클러스터와 워커 노드 그룹을 자동으로 생성합니다.

## 생성되는 리소스

### 네트워크 인프라
- **VPC**: 10.0.0.0/16 CIDR 블록
- **퍼블릭 서브넷 2개**: 10.0.1.0/24, 10.0.2.0/24 (서로 다른 가용 영역)
- **인터넷 게이트웨이**: 외부 인터넷 연결
- **라우팅 테이블**: 퍼블릭 서브넷용

### IAM 역할
- **EKS 클러스터 역할**: AmazonEKSClusterPolicy 포함
- **워커 노드 역할**: AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly, AmazonEKS_CNI_Policy 포함

### Amazon EKS 리소스
- **EKS 클러스터**: Kubernetes 버전 1.32
- **노드 그룹**: t3.medium 인스턴스 2개 (기본값)

## 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| ClusterName | my-eks-cluster | EKS 클러스터 이름 |
| NodeGroupName | my-node-group | 노드 그룹 이름 |
| NodeInstanceType | t3.medium | 워커 노드 인스턴스 타입 |
| DesiredCapacity | 2 | 노드 그룹 원하는 용량 |
| MinSize | 1 | 노드 그룹 최소 크기 |
| MaxSize | 3 | 노드 그룹 최대 크기 |

## 출력값

| 출력 키 | 설명 |
|---------|------|
| ClusterName | EKS 클러스터 이름 |
| ClusterEndpoint | EKS 클러스터 API 엔드포인트 |
| ClusterArn | EKS 클러스터 ARN |
| NodeGroupName | 노드 그룹 이름 |
| VpcId | VPC ID |
| ClusterRoleArn | EKS 클러스터 IAM 역할 ARN |
| NodeRoleArn | 워커 노드 IAM 역할 ARN |

## 배포 방법

1. AWS CloudFormation 콘솔로 이동합니다.
2. [[Create stack]] 버튼을 클릭합니다.
3. `week7-3-eks-lab.yaml` 파일을 업로드합니다.
4. 스택 이름을 `week7-3-eks-lab-stack`으로 입력합니다.
5. 파라미터는 기본값을 사용합니다.
6. 태그를 추가합니다:
   - Project: AWS-Lab
   - Week: 7-3
   - CreatedBy: Student
7. IAM 리소스 생성 권한을 승인합니다.
8. 스택 생성을 시작합니다.

## 예상 소요 시간

- 스택 생성: 20-30분
  - EKS 클러스터: 10-15분
  - 노드 그룹: 5-10분

## 주의사항

### Kubernetes 버전

템플릿은 Kubernetes 버전 1.32를 사용합니다. 지원되지 않는 경우 다음과 같이 수정합니다:

```yaml
EKSCluster:
  Type: AWS::EKS::Cluster
  Properties:
    Version: '1.33'  # 또는 지원되는 최신 버전
```

### 보안

- 이 템플릿은 학습 목적으로 퍼블릭 서브넷에 워커 노드를 배치합니다.
- 프로덕션 환경에서는 프라이빗 서브넷 사용을 권장합니다.

### 비용

- EKS 클러스터: 시간당 약 $0.10
- 워커 노드 (t3.medium x 2): 시간당 약 $0.0832
- 총 예상 비용: 시간당 약 $0.18

## 삭제 방법

1. CloudFormation 콘솔로 이동합니다.
2. `week7-3-eks-lab-stack` 스택을 선택합니다.
3. [[Delete]] 버튼을 클릭합니다.
4. 스택 삭제가 완료될 때까지 기다립니다 (10-15분).

## 문제 해결

### 스택 생성 실패

**증상**: CREATE_FAILED 상태

**원인 및 해결**:
- IAM 권한 부족: IAM 리소스 생성 권한 확인
- 리전 제한: 다른 리전에서 시도
- Kubernetes 버전 미지원: 템플릿의 Version 값 수정

### 노드 그룹 생성 실패

**증상**: 노드 그룹이 CREATE_FAILED 상태

**원인 및 해결**:
- 인스턴스 타입 제한: 다른 인스턴스 타입 시도 (t3.small, t3.large)
- 가용 영역 용량 부족: 다른 리전 시도

## 참고 자료

- [Amazon EKS 사용 설명서](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/)
- [CloudFormation EKS 리소스](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/AWS_EKS.html)
