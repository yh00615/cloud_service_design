---
title: 'kubectl을 활용한 Amazon EKS 클러스터 운영'
week: 7
session: 3
awsServices:
  - Amazon EKS
  - Kubernetes
learningObjectives:
  - Kubernetes의 기본 개념(Pod, Deployment, Service)과 Amazon EKS 아키텍처를 이해할 수 있습니다.
  - Amazon EKS 콘솔에서 클러스터를 생성하고 노드 그룹을 추가할 수 있습니다.
  - kubectl을 구성하고 Amazon EKS 클러스터에 연결할 수 있습니다.
  - Pod와 Deployment를 생성하고 롤링 업데이트/롤백을 수행할 수 있습니다.
  - Kubernetes Service를 생성하고 애플리케이션을 외부에 노출할 수 있습니다.
prerequisites:
  - Week 3-1 Amazon VPC 기본 개념 이해
  - 컨테이너 기본 개념 이해
---

이 실습에서는 Amazon EKS(Elastic Kubernetes Service) 콘솔에서 관리형 Kubernetes 클러스터를 직접 생성하고, kubectl 명령어를 사용하여 기본적인 Kubernetes 리소스를 관리하는 방법을 학습합니다.

> [!NOTE]
> **QuickTable 프로젝트 연계**: 이 실습에서 학습하는 Amazon EKS와 Kubernetes 개념은 Week 9-2에서 QuickTable 컨테이너 이미지를 빌드하고 Amazon ECR에 푸시하는 데 활용됩니다.
>
> **학습 흐름**:
>
> - Week 7-3: Amazon EKS 클러스터 생성 및 kubectl 기본 (현재)
> - Week 9-2: AWS CodeBuild로 QuickTable 컨테이너 이미지 빌드 및 Amazon ECR 푸시
> - Week 9-3: AWS CodePipeline으로 QuickTable 웹사이트 Amazon S3 자동 배포

> [!DOWNLOAD]
> [week7-3-eks-lab.zip](/files/week7/week7-3-eks-lab.zip)
>
> - `week7-3-eks-lab.yaml` - VPC, IAM 역할 사전 구성 AWS CloudFormation 템플릿
> - `nginx-deployment.yaml` - Nginx Deployment 매니페스트 (태스크 6에서 사용)
> - `nginx-service.yaml` - Nginx Service 매니페스트 (태스크 8에서 사용)
> - `nginx-ingress-alb.yaml` - ALB Ingress 매니페스트 (참고용)
>
> **관련 태스크:**
>
> - 태스크 0: 사전 인프라 구축 (week7-3-eks-lab.yaml을 사용하여 VPC, IAM 역할 자동 생성)
> - 태스크 1: Amazon EKS 콘솔에서 클러스터 생성
> - 태스크 2: 노드 그룹 추가
> - 태스크 6: YAML 매니페스트로 Deployment 생성 (nginx-deployment.yaml 사용)
> - 태스크 8: Service 생성 (nginx-service.yaml 사용)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 **즉시 삭제**해야 합니다.

> [!COST]
> **Kubernetes Extended Support 비용 안내**: Kubernetes 버전이 Extended Support에 진입하면 클러스터 비용이 크게 증가합니다.
> 추가 비용을 피하려면 클러스터 생성 시 Standard Support 버전을 선택합니다.
> 지원 버전 확인 방법은 📚 참고 섹션의 "Kubernetes 버전 지원 정책"을 참조합니다.

> [!TIP]
> **실습 시간 최적화**: 태스크 0의 AWS CloudFormation 스택 생성에 3-5분, 태스크 1의 EKS 클러스터 생성에 10-15분이 소요됩니다.
> 수업 시작 전 사전 과제로 태스크 0~2를 미리 수행하면 실습 시간을 효율적으로 활용할 수 있습니다.

## 태스크 0: 사전 인프라 구축

이 태스크에서는 AWS CloudFormation을 사용하여 EKS 클러스터에 필요한 VPC와 IAM 역할을 미리 생성합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon VPC 및 네트워크**: Amazon VPC (10.0.0.0/16), 퍼블릭 서브넷 2개, 인터넷 게이트웨이, 라우팅 테이블
- **AWS IAM 역할**: Amazon EKS 클러스터 역할 (AmazonEKSClusterPolicy), 워커 노드 역할 (AmazonEKSWorkerNodePolicy, AmazonEC2ContainerRegistryReadOnly, AmazonEKS_CNI_Policy)

> [!WARNING]
> **보안 주의**: 이 실습에서는 간소화를 위해 퍼블릭 서브넷만 사용합니다.
>
> **프로덕션 환경 필수 사항:**
>
> - 워커 노드는 반드시 프라이빗 서브넷에 배치합니다.
> - 퍼블릭 서브넷의 워커 노드는 퍼블릭 IP가 할당되어 인터넷에서 직접 접근 가능합니다.
> - NAT Gateway를 통해 아웃바운드 트래픽만 허용하고 인바운드는 차단해야 합니다.
> - Week 3-2에서 학습한 최소 권한 원칙을 적용합니다.

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week7-3-eks-lab.zip` 파일의 압축을 해제합니다.
2. `week7-3-eks-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

<img src="/images/week7/7-3-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week7-3-eks-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week7-3-eks-lab-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **ClusterName**: `my-eks-cluster`
    - **CreatedByTag**: `CloudFormation`
    - **ProjectTag**: `AWS-Lab`
    - **WeekTag**: `7-3`

> [!IMPORTANT]
> 모든 파라미터는 기본값을 그대로 사용합니다.
> 값을 변경하면 이후 태스크의 명령어와 일치하지 않을 수 있습니다.

11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week7/7-3-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다.
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다.
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다. (Events 탭에서 원인 확인 필요)
>
> VPC와 IAM 역할만 생성하므로 3-5분 내에 완료됩니다.

18. 스택 상태가 **CREATE_COMPLETE**로 변경되면 **Outputs** 탭을 선택합니다.
19. 출력값들을 확인하고 메모장에 복사합니다:
    - `VpcId`: Amazon VPC ID (예: vpc-0123456789abcdef0)
    - `PublicSubnet1Id`: 퍼블릭 서브넷 1 ID
    - `PublicSubnet2Id`: 퍼블릭 서브넷 2 ID
    - `ClusterRoleName`: EKS 클러스터 IAM 역할 이름 (예: my-eks-cluster-cluster-role)
    - `NodeRoleName`: 워커 노드 IAM 역할 이름 (예: my-eks-cluster-node-role)

> [!IMPORTANT]
> 이 출력값들은 태스크 1, 2에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: VPC와 IAM 역할이 준비되었습니다.

## 태스크 1: Amazon EKS 콘솔에서 클러스터 생성

이 태스크에서는 Amazon EKS 콘솔에서 직접 Kubernetes 클러스터를 생성합니다.

20. AWS Management Console 상단 검색창에 `EKS`를 입력하고 **Elastic Kubernetes Service**를 선택합니다.
21. 왼쪽 메뉴에서 **Clusters**를 선택합니다.
22. [[Create cluster]] 버튼을 클릭합니다.

### Configuration options 선택

23. **Configuration options**에서 `Custom configuration`을 선택합니다.

> [!NOTE]
> **Quick configuration (with EKS Auto Mode)**는 EKS Auto Mode를 사용하여 노드 프로비저닝을 자동화합니다.
> 이 실습에서는 Kubernetes 구성 요소를 직접 이해하기 위해 Custom configuration을 사용합니다.

24. **EKS Auto Mode** 섹션에서 `Use EKS Auto Mode` 토글을 **비활성화**합니다.

> [!NOTE]
> Custom configuration을 선택해도 EKS Auto Mode가 기본으로 활성화되어 있습니다.
> 이 실습에서는 노드 그룹을 직접 생성하므로 Auto Mode를 반드시 비활성화합니다.
>
> **EKS Auto Mode란?** AWS가 노드 프로비저닝, 스케일링, 업데이트를 자동으로 관리하는 기능입니다. 노드 그룹을 직접 생성할 필요 없이 Pod 요청에 따라 자동으로 노드를 추가/제거합니다. 편리하지만 Kubernetes 노드 관리를 직접 학습하기 위해 이 실습에서는 비활성화합니다.

### Cluster configuration

25. **Name**에 `my-eks-cluster`를 입력합니다.
26. **Cluster IAM role**에서 `my-eks-cluster-cluster-role`을 선택합니다.

> [!NOTE]
> 이 역할은 태스크 0에서 AWS CloudFormation으로 생성한 역할입니다.
> 드롭다운에 표시되지 않으면 태스크 0의 스택 생성이 완료되었는지 확인합니다.

27. **Kubernetes version**에서 최신 버전을 선택합니다.
28. **Upgrade policy**에서 `Standard support`를 선택합니다.

> [!NOTE]
> Standard Support를 선택해야 추가 비용이 발생하지 않습니다.
> Extended Support는 Standard Support 기간 종료 후 추가 비용이 발생합니다.

29. 나머지 설정(**Control plane scaling tier**, **Cluster access**, **Envelope encryption**, **ARC Zonal shift**, **Deletion protection**)은 기본값을 유지합니다.
30. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `7-3`     |
| `CreatedBy` | `Student` |

31. [[Next]] 버튼을 클릭합니다.

32. **VPC**에서 태스크 0에서 생성한 VPC를 선택합니다 (이름: `my-eks-cluster-vpc`).
33. **Subnets**에서 두 개의 퍼블릭 서브넷이 자동으로 선택되었는지 확인합니다:
    - `my-eks-cluster-public-subnet-1`
    - `my-eks-cluster-public-subnet-2`

> [!NOTE]
> VPC를 선택하면 해당 VPC의 서브넷이 자동으로 표시됩니다.
> 두 서브넷 모두 선택되어 있어야 합니다.

34. **Cluster endpoint access**에서 `Public`을 선택합니다.

> [!WARNING]
> **보안 주의**: Public 엔드포인트는 실습 환경에서만 사용합니다.
> 프로덕션 환경에서는 `Public and private` 또는 `Private`을 선택하여 접근을 제한해야 합니다.

35. [[Next]] 버튼을 클릭합니다.
36. **Configure observability** 페이지에서 기본값을 유지하고 [[Next]] 버튼을 클릭합니다.
37. **Select add-ons** 페이지에서 기본값을 유지하고 [[Next]] 버튼을 클릭합니다.
38. **Configure selected add-ons settings** 페이지에서 기본값을 유지하고 [[Next]] 버튼을 클릭합니다.
39. **Review and create** 페이지에서 설정을 확인합니다.
40. [[Create]] 버튼을 클릭합니다.

> [!NOTE]
> 클러스터 생성에 10-15분이 소요됩니다. 상태가 "Creating"에서 "**Active**"로 변경될 때까지 기다립니다.
> 대기하는 동안 📚 참고 섹션의 Kubernetes 아키텍처를 미리 읽어봅니다.

✅ **태스크 완료**: Amazon EKS 클러스터가 생성되었습니다.

## 태스크 2: 노드 그룹 추가

이 태스크에서는 생성한 EKS 클러스터에 워커 노드 그룹을 추가합니다.

41. Amazon EKS 콘솔에서 `my-eks-cluster` 클러스터를 선택합니다.
42. **Compute** 탭을 선택합니다.
43. **Node groups** 섹션에서 [[Add node group]] 버튼을 클릭합니다.

### Node group configuration

44. **Name**에 `my-node-group`을 입력합니다.
45. **Node IAM role**에서 `my-eks-cluster-node-role`을 선택합니다.

> [!NOTE]
> 이 역할은 태스크 0에서 AWS CloudFormation으로 생성한 역할입니다.

46. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `7-3`     |
| `CreatedBy` | `Student` |

47. [[Next]] 버튼을 클릭합니다.

### Compute and scaling configuration

48. **AMI type**에서 `Amazon Linux 2023 (AL2023_x86_64_STANDARD)`를 선택합니다.
49. **Capacity type**은 `On-Demand`를 유지합니다 (기본값).
50. **Instance types**에서 `t3.medium`을 선택합니다.

> [!TIP]
> **AWS 프리 티어(무료 플랜)를 사용하는 경우**, `t3.medium`은 프리 티어 대상이 아닙니다. 유료 플랜을 사용하는 경우 변경 없이 그대로 진행합니다.
> 프리 티어 사용자는 `t3.small` 또는 `c7i-flex.large`로 변경하여 비용을 절감할 수 있습니다.

51. **Disk size**는 `20` GiB를 유지합니다 (기본값).
52. **Node group scaling configuration**에서 다음 값을 설정합니다:
    - **Desired size**: `2`
    - **Minimum size**: `1`
    - **Maximum size**: `3`
53. 나머지 설정(**ASG Warm Pool**, **Node group update configuration**, **Node auto repair**)은 기본값을 유지합니다.

> [!NOTE]
> **Capacity type**: `On-Demand`는 안정적인 인스턴스를 제공합니다. 비용 절감이 필요한 경우 `Spot`을 선택할 수 있지만, Spot 인스턴스는 언제든 중단될 수 있으므로 프로덕션 워크로드에는 주의가 필요합니다.

54. [[Next]] 버튼을 클릭합니다.

### Networking

55. **Subnets**에서 두 개의 퍼블릭 서브넷이 선택되어 있는지 확인합니다.
56. [[Next]] 버튼을 클릭합니다.
57. **Review and create** 페이지에서 설정을 확인합니다.
58. [[Create]] 버튼을 클릭합니다.

> [!NOTE]
> 노드 그룹 생성에 3-5분이 소요됩니다. 상태가 "Creating"에서 "**Active**"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: 워커 노드 그룹이 추가되었습니다.

## 태스크 3: kubectl 구성 및 클러스터 연결

이 태스크에서는 CloudShell에서 kubectl을 사용하여 Amazon EKS 클러스터에 연결합니다.

> [!NOTE]
> AWS CloudShell에는 kubectl이 사전 설치되어 있습니다.
> 별도 설치 없이 바로 사용할 수 있습니다.
>
> **세션 타임아웃 주의**: CloudShell은 약 20분 비활성 시 세션이 자동 종료됩니다. 세션이 끊어지면 다시 CloudShell을 열고 `aws eks update-kubeconfig` 명령을 재실행합니다.
>
> **kubectl 버전 호환성**: 버전이 호환 범위를 벗어나면 📚 참고 섹션의 "kubectl 수동 설치 방법"을 참조합니다.

59. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
60. CloudShell이 시작되면 kubectl 버전을 확인합니다:

```bash
kubectl version --client
```

> [!OUTPUT]
>
> ```
> Client Version: v1.32.x 이상
> Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
> ```

61. AWS CLI를 사용하여 kubeconfig를 업데이트합니다:

```bash
aws eks update-kubeconfig --name my-eks-cluster --region ap-northeast-2
```

> [!OUTPUT]
>
> ```
> Added new context arn:aws:eks:ap-northeast-2:xxxx:cluster/my-eks-cluster to /home/cloudshell-user/.kube/config
> ```

62. 클러스터 연결을 확인합니다:

```bash
kubectl get nodes
```

> [!OUTPUT]
>
> ```
> NAME                                            STATUS   ROLES    AGE   VERSION
> ip-xxx-xxx-xxx-xxx.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.32.x
> ip-xxx-xxx-xxx-xxx.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.32.x
> ```

> [!TROUBLESHOOTING]
> **문제**: `kubectl get nodes` 실행 시 연결 오류가 발생합니다.
>
> **증상 1**: `error: You must be logged in to the server (Unauthorized)`  
> **원인**: AWS CloudShell의 AWS IAM 사용자/역할이 클러스터 생성자와 다릅니다.  
> **해결**: Amazon EKS 클러스터는 생성자에게만 기본 접근 권한을 부여합니다. 동일한 AWS IAM 사용자/역할로 CloudShell을 사용하는지 확인합니다.
>
> **증상 2**: `Unable to connect to the server`  
> **원인**: 클러스터가 아직 생성 중이거나 엔드포인트 접근 문제입니다.  
> **해결**: 클러스터 상태가 ACTIVE인지 확인합니다:
>
> ```bash
> aws eks describe-cluster --name my-eks-cluster --query 'cluster.status' --output text
> ```
>
> 출력이 `ACTIVE`가 아니면 클러스터 생성이 완료될 때까지 기다립니다.

✅ **태스크 완료**: kubectl이 Amazon EKS 클러스터에 연결되었습니다.

## 태스크 4: Kubernetes Pod 생성 및 관리

이 태스크에서는 kubectl을 사용하여 Pod를 생성하고 관리하는 방법을 학습합니다.

> [!NOTE]
> Pod를 직접 생성하는 방식은 학습 및 디버깅 목적으로만 사용합니다.
> 프로덕션 환경에서는 Pod가 삭제되면 자동으로 재생성되지 않으므로, 항상 Deployment를 사용해야 합니다.

63. 다음 명령어를 실행하여 nginx Pod를 생성합니다:

```bash
kubectl run nginx-pod --image=nginx:1.28
```

> [!OUTPUT]
>
> ```
> pod/nginx-pod created
> ```

64. Pod 목록을 확인합니다:

```bash
kubectl get pods
```

> [!OUTPUT]
>
> ```
> NAME        READY   STATUS    RESTARTS   AGE
> nginx-pod   1/1     Running   0          10s
> ```

65. Pod의 상세 정보를 확인합니다:

```bash
kubectl describe pod nginx-pod
```

> [!NOTE]
> 출력에서 다음 항목을 확인합니다:
>
> - **Status**: Running (Pod가 정상 실행 중)
> - **IP**: Pod에 할당된 Amazon VPC IP 주소
> - **Node**: Pod가 실행 중인 워커 노드
> - **Events**: Pod 생성 과정 (Scheduled → Pulling → Pulled → Created → Started)

66. Pod의 로그를 확인합니다:

```bash
kubectl logs nginx-pod
```

> [!NOTE]
> nginx Pod에 아직 HTTP 요청이 없으므로 로그가 비어 있거나 기본 시작 로그만 표시될 수 있습니다.
> 웹 브라우저나 curl로 nginx에 접속하면 액세스 로그가 표시됩니다.

67. Pod 내부에 접속합니다:

```bash
kubectl exec -it nginx-pod -- /bin/bash
```

> [!WARNING]
> `kubectl exec`는 디버깅 목적으로만 사용합니다.
> 프로덕션 환경에서는 Pod 내부 접속을 RBAC으로 제한하고, 감사 로그를 활성화해야 합니다.

68. Pod 내부에서 nginx 버전을 확인합니다:

```bash
nginx -v
```

69. `exit` 명령어를 입력하여 Pod에서 나옵니다.

✅ **태스크 완료**: Kubernetes Pod를 생성하고 관리했습니다.

## 태스크 5: Kubernetes Deployment 생성 (명령형)

이 태스크에서는 명령형 방식으로 Deployment를 생성하고 관리하는 방법을 학습합니다.

70. 다음 명령어를 실행하여 nginx Deployment를 생성합니다:

```bash
kubectl create deployment nginx-deployment --image=nginx:1.28 --replicas=2
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-deployment created
> ```

> [!NOTE]
> 명령형 방식은 빠르게 리소스를 생성할 수 있지만, 버전 관리와 재현성이 떨어집니다.
> 프로덕션 환경에서는 선언형 방식(YAML 매니페스트)을 권장합니다.
>
> replicas를 2로 설정하여 리소스 사용량을 최소화합니다.
> t3.medium 2대에서 총 4 vCPU, 8GB 메모리를 사용할 수 있습니다.

71. Deployment 목록을 확인합니다:

```bash
kubectl get deployments
```

> [!OUTPUT]
>
> ```
> NAME               READY   UP-TO-DATE   AVAILABLE   AGE
> nginx-deployment   2/2     2            2           20s
> ```

72. Pod 목록을 확인합니다:

```bash
kubectl get pods
```

> [!OUTPUT]
>
> ```
> NAME                                READY   STATUS    RESTARTS   AGE
> nginx-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
> nginx-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
> nginx-pod                           1/1     Running   0          5m
> ```

73. Deployment를 스케일링합니다:

```bash
kubectl scale deployment nginx-deployment --replicas=3
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-deployment scaled
> ```

74. Pod 개수가 증가했는지 확인합니다:

```bash
kubectl get pods
```

75. Deployment의 상세 정보를 확인합니다:

```bash
kubectl describe deployment nginx-deployment
```

> [!NOTE]
> **다음 태스크 준비**: 태스크 6에서는 선언형 방식으로 새로운 Deployment를 생성합니다.
> 리소스 사용량을 관리하기 위해 태스크 5에서 생성한 리소스를 먼저 정리합니다.

76. 태스크 5에서 생성한 Deployment를 삭제합니다:

```bash
kubectl delete deployment nginx-deployment
```

> [!OUTPUT]
>
> ```
> deployment.apps "nginx-deployment" deleted
> ```

77. 태스크 4에서 생성한 Pod를 삭제합니다:

```bash
kubectl delete pod nginx-pod
```

> [!OUTPUT]
>
> ```
> pod "nginx-pod" deleted
> ```

78. 삭제가 완료되었는지 확인합니다:

```bash
kubectl get pods
```

> [!OUTPUT]
>
> ```
> No resources found in default namespace.
> ```

> [!NOTE]
> 모든 Pod가 삭제되었습니다. 이제 태스크 6을 진행할 준비가 되었습니다.

✅ **태스크 완료**: 명령형 방식으로 Kubernetes Deployment를 생성하고 스케일링했습니다.

## 태스크 6: YAML 매니페스트로 Deployment 생성 (선언형)

이 태스크에서는 선언형 방식으로 YAML 매니페스트 파일을 사용하여 Deployment를 생성하는 방법을 학습합니다.

> [!CONCEPT] 명령형 vs 선언형
> **명령형 (Imperative)**: `kubectl create`, `kubectl scale` 등 명령어로 직접 리소스 생성 및 수정
>
> - 장점: 빠르고 간단함
> - 단점: 버전 관리 어려움, 재현성 낮음, 변경 이력 추적 불가
>
> **선언형 (Declarative)**: YAML 파일로 원하는 상태를 정의하고 `kubectl apply` 실행
>
> - 장점: Git으로 버전 관리, 재현 가능, 변경 이력 추적, 프로덕션 권장
> - 단점: 초기 학습 곡선

79. 다운로드한 실습 파일에서 `nginx-deployment.yaml` 파일을 확인합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-app
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.28
          ports:
            - containerPort: 80
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

80. CloudShell에 파일을 업로드합니다:
    - CloudShell 우측 상단의 **Actions** > **Upload file**을 클릭합니다.
    - `nginx-deployment.yaml` 파일을 선택합니다.

81. 업로드된 파일을 확인합니다:

```bash
cat nginx-deployment.yaml
```

82. YAML 파일을 사용하여 Deployment를 생성합니다:

```bash
kubectl apply -f nginx-deployment.yaml
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-app created
> ```

83. Deployment 목록을 확인합니다:

```bash
kubectl get deployments
```

> [!OUTPUT]
>
> ```
> NAME        READY   UP-TO-DATE   AVAILABLE   AGE
> nginx-app   3/3     3            3           10s
> ```

84. Pod 목록을 확인합니다:

```bash
kubectl get pods -l app=nginx
```

> [!OUTPUT]
>
> ```
> NAME                         READY   STATUS    RESTARTS   AGE
> nginx-app-xxxxxxxxxx-xxxxx   1/1     Running   0          20s
> nginx-app-xxxxxxxxxx-xxxxx   1/1     Running   0          20s
> nginx-app-xxxxxxxxxx-xxxxx   1/1     Running   0          20s
> ```

> [!NOTE]
> 태스크 5에서 이전 리소스를 모두 정리했으므로, nginx-app 3개만 실행됩니다.
> 각 Pod는 cpu: 100m request를 사용하므로, 총 300m(0.3 vCPU)가 필요합니다.
> t3.medium 2대는 총 4 vCPU, 8GB 메모리를 제공하므로 충분히 수용 가능합니다.

85. Deployment의 상세 정보를 확인합니다:

```bash
kubectl describe deployment nginx-app
```

86. 롤링 업데이트 전략을 확인합니다:

```bash
kubectl get deployment nginx-app -o yaml | grep -A 3 "strategy:"
```

> [!OUTPUT]
>
> ```
>   strategy:
>     rollingUpdate:
>       maxSurge: 1
>       maxUnavailable: 0
> ```

> [!TIP]
> YAML 매니페스트 파일은 Git 저장소에 저장하여 버전 관리하고, CI/CD 파이프라인에서 자동 배포할 수 있습니다.
> 이를 GitOps라고 하며, 프로덕션 환경에서 권장되는 방식입니다.

✅ **태스크 완료**: YAML 매니페스트를 사용하여 선언형 방식으로 Deployment를 생성했습니다.

## 태스크 7: 롤링 업데이트 및 롤백

이 태스크에서는 Deployment의 롤링 업데이트와 롤백 기능을 학습합니다.

> [!CONCEPT] 롤링 업데이트 (Rolling Update)
> 롤링 업데이트는 애플리케이션의 다운타임 없이 새 버전으로 점진적으로 업데이트하는 방식입니다.
> Kubernetes는 기본적으로 롤링 업데이트 전략을 사용하며, 다음과 같이 동작합니다:
>
> 1. 새 버전의 Pod를 하나씩 생성합니다
> 2. 새 Pod가 Ready 상태가 되면 기존 Pod를 하나씩 종료합니다
> 3. 모든 Pod가 새 버전으로 교체될 때까지 반복합니다

87. 현재 nginx-app Deployment의 이미지 버전을 확인합니다:

```bash
kubectl describe deployment nginx-app | grep Image
```

> [!OUTPUT]
>
> ```
>     Image:        nginx:1.28
> ```

88. 다음 명령어를 실행하여 이미지를 업데이트합니다:

```bash
kubectl set image deployment/nginx-app nginx=nginx:1.29
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-app image updated
> ```

> [!NOTE]
> `kubectl set image`는 실무에서 가장 많이 사용하는 롤링 업데이트 방법입니다.
> 빠르고 간단하지만, 변경 이력이 Git에 남지 않습니다.
>
> **대안 방법 (선언형)**: YAML 파일을 수정하여 업데이트할 수도 있습니다:
>
> ```bash
> sed -i 's/nginx:1.28/nginx:1.29/' nginx-deployment.yaml
> kubectl apply -f nginx-deployment.yaml
> ```
>
> 선언형 방식은 YAML 파일을 Git으로 버전 관리할 수 있어 프로덕션 환경에서 권장됩니다.

89. 롤링 업데이트 진행 상황을 실시간으로 확인합니다:

```bash
kubectl rollout status deployment/nginx-app
```

> [!OUTPUT]
>
> ```
> Waiting for deployment "nginx-app" rollout to finish: 1 out of 3 new replicas have been updated...
> Waiting for deployment "nginx-app" rollout to finish: 2 out of 3 new replicas have been updated...
> Waiting for deployment "nginx-app" rollout to finish: 2 of 3 updated replicas are available...
> deployment "nginx-app" successfully rolled out
> ```

90. 업데이트된 이미지 버전을 확인합니다:

```bash
kubectl describe deployment nginx-app | grep Image
```

> [!OUTPUT]
>
> ```
>     Image:        nginx:1.29
> ```

91. 롤아웃 히스토리를 확인합니다:

```bash
kubectl rollout history deployment/nginx-app
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-app
> REVISION  CHANGE-CAUSE
> 1         <none>
> 2         <none>
> ```

> [!NOTE]
> REVISION 1: nginx:1.28 (최초 생성)
> REVISION 2: nginx:1.29 (이미지 업데이트)

92. 특정 리비전의 상세 정보를 확인합니다:

```bash
kubectl rollout history deployment/nginx-app --revision=2
```

93. 이전 버전으로 롤백합니다:

```bash
kubectl rollout undo deployment/nginx-app
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-app rolled back
> ```

> [!NOTE]
> 롤백을 실행하면 이전 버전(nginx:1.28)으로 되돌아갑니다.
>
> **REVISION 번호 변화:**
>
> - 최초: REVISION 1 (nginx:1.28)
> - 업데이트: REVISION 2 (nginx:1.29)
> - 롤백: REVISION 3 (nginx:1.28) ← 새로운 리비전 생성
>
> 롤백 자체도 하나의 배포로 기록되므로 REVISION 1은 사라지고 REVISION 2, 3이 남습니다.

94. 롤백 진행 상황을 확인합니다:

```bash
kubectl rollout status deployment/nginx-app
```

95. 이미지 버전이 1.28로 롤백되었는지 확인합니다:

```bash
kubectl describe deployment nginx-app | grep Image
```

> [!OUTPUT]
>
> ```
>     Image:        nginx:1.28
> ```

96. 롤아웃 히스토리를 다시 확인합니다:

```bash
kubectl rollout history deployment/nginx-app
```

> [!OUTPUT]
>
> ```
> deployment.apps/nginx-app
> REVISION  CHANGE-CAUSE
> 2         <none>
> 3         <none>
> ```

> [!NOTE]
> **REVISION 번호 변화 확인:**
>
> - REVISION 1은 사라지고, REVISION 2(nginx:1.29)와 REVISION 3(nginx:1.28, 롤백)이 남습니다.
> - 롤백 자체도 하나의 새로운 배포로 기록되므로 REVISION 번호가 증가합니다.
> - 가장 오래된 REVISION(1)은 히스토리에서 제거됩니다.
>
> **특정 리비전으로 롤백:**
> 다시 nginx:1.29으로 돌아가려면 다음 명령어를 실행합니다:
>
> ```bash
> kubectl rollout undo deployment/nginx-app --to-revision=2
> ```
>
> 이 경우 REVISION 4가 생성되며 이미지는 nginx:1.29이 됩니다.
>
> 이 명령어는 선택사항입니다. 실행하지 않아도 다음 태스크에 영향이 없습니다.

> [!TIP]
> 롤링 업데이트 전략을 세밀하게 제어하려면 YAML 파일에 다음 설정을 추가할 수 있습니다:
>
> ```yaml
> spec:
>   strategy:
>     type: RollingUpdate
>     rollingUpdate:
>       maxSurge: 1 # 동시에 생성할 수 있는 추가 Pod 수
>       maxUnavailable: 0 # 동시에 사용 불가능한 Pod 수
> ```

✅ **태스크 완료**: 롤링 업데이트를 수행하고 이전 버전으로 롤백했습니다.

## 태스크 8: Kubernetes Service 생성

이 태스크에서는 Service를 사용하여 Pod에 네트워크 접근을 제공하는 방법을 학습합니다.

### 방법 1: 명령형 방식 (빠른 테스트)

97. 다음 명령어를 실행하여 LoadBalancer 타입의 Service를 생성합니다:

```bash
kubectl expose deployment nginx-app --type=LoadBalancer --port=80
```

> [!OUTPUT]
>
> ```
> service/nginx-app exposed
> ```

### 방법 2: 선언형 방식 (프로덕션 권장)

98. 다운로드한 실습 파일에서 `nginx-service.yaml` 파일을 확인합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-app
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

99. CloudShell에 파일을 업로드합니다:
    - CloudShell 우측 상단의 **Actions** > **Upload file**을 클릭합니다.
    - `nginx-service.yaml` 파일을 선택합니다.

100. YAML 파일을 사용하여 Service를 생성합니다:

```bash
kubectl apply -f nginx-service.yaml
```

> [!OUTPUT]
>
> ```
> service/nginx-app created
> ```

> [!NOTE]
> 방법 1 또는 방법 2 중 하나만 선택하여 실행합니다. 두 방법 모두 동일한 Service를 생성합니다.

### Service 확인

101. Service 목록을 확인합니다:

```bash
kubectl get services
```

> [!OUTPUT]
>
> ```
> NAME               TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
> kubernetes         ClusterIP      10.100.0.1      <none>        443/TCP        30m
> nginx-app          LoadBalancer   10.100.xxx.xxx  <pending>     80:xxxxx/TCP   10s
> ```

> [!NOTE]
> EXTERNAL-IP가 처음에는 `<pending>`으로 표시됩니다. AWS Load Balancer가 생성되면 실제 DNS 주소로 변경되며, 1-2분이 소요될 수 있습니다.

102. EXTERNAL-IP가 할당될 때까지 실시간으로 확인합니다:

```bash
kubectl get service nginx-app -w
```

> [!NOTE]
> `-w` (watch) 옵션을 사용하면 상태 변경을 실시간으로 확인할 수 있습니다.
> EXTERNAL-IP가 `<pending>`에서 실제 주소로 변경되면 Ctrl+C를 눌러 종료합니다.

103. Service의 상세 정보를 확인합니다:

```bash
kubectl describe service nginx-app
```

104. kubectl로 Load Balancer DNS 이름을 확인합니다:

```bash
kubectl get service nginx-app \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}{"\n"}'
```

> [!OUTPUT]
>
> ```
> xxxxx-xxxxxxxx.ap-northeast-2.elb.amazonaws.com
> ```

105. AWS Management Console 상단 검색창에 `EC2`를 입력하고 선택합니다.
106. 왼쪽 메뉴에서 **Instances**를 선택합니다.
107. 인스턴스 목록에서 이름에 `my-node-group`이 포함된 워커 노드 인스턴스를 하나 선택합니다.
108. 하단의 **Security** 탭을 선택합니다.
109. **Security groups** 섹션에서 보안 그룹 링크 (예: `eks-cluster-sg-my-eks-cluster-xxxxx`)를 클릭합니다.

> [!NOTE]
> Amazon EKS 워커 노드에 연결된 보안 그룹을 수정해야 LoadBalancer Service가 NodePort를 통해 Pod에 접근할 수 있습니다.

110. 하단의 **Inbound rules** 탭을 선택합니다.
111. [[Edit inbound rules]] 버튼을 클릭합니다.
112. [[Add rule]] 버튼을 클릭합니다.
113. **Type**에서 `Custom TCP`를 선택합니다.
114. **Port range**에 `30000-32767`을 입력합니다.
115. **Source**에서 `Anywhere-IPv4` (0.0.0.0/0)를 선택합니다.
116. [[Save rules]] 버튼을 클릭합니다.

> [!NOTE]
> **학습 목적**: 이 단계는 Kubernetes Service와 AWS 보안 그룹의 관계를 이해하기 위한 학습 목적입니다.
>
> LoadBalancer 타입의 Service는 AWS Classic Load Balancer를 생성하고, NodePort 범위(30000-32767)를 통해 워커 노드와 통신합니다.
> 보안 그룹에 이 포트 범위를 허용해야 Load Balancer가 워커 노드의 Pod에 트래픽을 전달할 수 있습니다.
>
> **프로덕션 환경**: AWS CloudFormation 템플릿에서 미리 이 포트 범위를 설정하면 수동 수정이 불필요합니다.
> 실무에서는 인프라 코드(IaC)로 모든 보안 그룹 규칙을 사전 정의하는 것이 권장됩니다.

> [!WARNING]
> **보안 주의**: 0.0.0.0/0으로 포트를 여는 것은 실습 환경에서만 사용합니다.
> 프로덕션 환경에서는 Load Balancer의 보안 그룹만 허용하거나, 특정 IP 범위로 제한해야 합니다.
> Week 3-2에서 학습한 최소 권한 원칙을 적용합니다.

> [!NOTE]
> **Load Balancer 준비 시간**: Classic Load Balancer의 DNS가 전파되고 Health Check가 통과하기까지 3-5분이 소요될 수 있습니다.
> 보안 그룹 수정 직후 바로 접속하면 타임아웃이 발생할 수 있으므로 잠시 기다린 후 접속합니다.
>
> **연결 테스트 명령어**:
>
> ```bash
> curl -v http://$(kubectl get service nginx-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
> ```
>
> 이 명령어로 Load Balancer 연결 상태를 확인할 수 있습니다.

117. 웹 브라우저에서 EXTERNAL-IP 주소로 접속하여 nginx 기본 페이지를 확인합니다.

✅ **태스크 완료**: Kubernetes Service를 생성하고 외부에서 접근했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 VPC와 IAM 역할을 사전 구성했습니다.
- Amazon EKS 콘솔에서 클러스터를 생성하고 노드 그룹을 추가했습니다.
- kubectl을 구성하고 Amazon EKS 클러스터에 연결했습니다.
- 명령형 방식으로 Kubernetes Pod와 Deployment를 생성했습니다.
- 선언형 방식으로 YAML 매니페스트를 사용하여 Deployment를 관리했습니다.
- 롤링 업데이트를 수행하고 이전 버전으로 롤백했습니다.
- LoadBalancer Service를 통해 애플리케이션을 외부에 노출했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.
> Amazon EKS 클러스터와 워커 노드는 실행 중인 동안 지속적으로 비용이 발생합니다.

> [!IMPORTANT]
> 삭제 순서를 반드시 지켜야 합니다. 순서가 잘못되면 리소스 간 의존성으로 인해 삭제가 실패할 수 있습니다.
>
> **삭제 순서**: Kubernetes 리소스 (Service, Deployment) → Load Balancer 확인 → 노드 그룹 → 클러스터 → AWS CloudFormation 스택

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `7-3`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Kubernetes 리소스 삭제

7. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
8. Service를 삭제합니다:

```bash
kubectl delete service nginx-app
```

> [!IMPORTANT]
> Service 삭제 후 AWS Load Balancer가 완전히 삭제될 때까지 1-2분 대기합니다.
> Load Balancer가 남아있으면 이후 Amazon VPC 삭제가 실패합니다.

9. Deployment를 삭제합니다:

```bash
kubectl delete deployment nginx-app
kubectl delete deployment nginx-deployment 2>/dev/null
```

> [!NOTE]
> `nginx-deployment`는 태스크 5에서 이미 삭제했을 수 있습니다. "not found" 오류가 나오면 정상입니다.

10. 모든 리소스가 삭제되었는지 확인합니다:

```bash
kubectl get all
```

> [!NOTE]
> `kubernetes` ClusterIP Service만 남아있으면 정상입니다. Pod, Deployment, ReplicaSet이 남아있으면 해당 리소스를 추가로 삭제합니다.

### 단계 3: Load Balancer 삭제 확인

11. AWS Management Console 상단 검색창에 `EC2`를 입력하고 선택합니다.
12. 왼쪽 메뉴에서 **Load Balancers**를 선택합니다.
13. `nginx-app`와 관련된 Load Balancer가 목록에서 사라졌는지 확인합니다.

> [!NOTE]
> Load Balancer가 아직 남아있으면 선택 후 **Actions** > `Delete load balancer`를 선택하여 수동 삭제합니다.
> Load Balancer가 완전히 삭제되어야 다음 단계를 진행할 수 있습니다.

### 단계 4: Amazon EKS 노드 그룹 및 클러스터 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

14. CloudShell에서 노드 그룹을 삭제합니다:

```bash
aws eks delete-nodegroup \
  --cluster-name my-eks-cluster \
  --nodegroup-name my-node-group \
  --region ap-northeast-2
```

> [!NOTE]
> 노드 그룹 삭제에 3-5분이 소요됩니다. 다음 명령어로 삭제 완료를 확인합니다:
>
> ```bash
> aws eks describe-nodegroup --cluster-name my-eks-cluster --nodegroup-name my-node-group --region ap-northeast-2 --query 'nodegroup.status' --output text
> ```
>
> "DELETING"이 출력되면 대기하고, "ResourceNotFoundException" 오류가 나오면 삭제 완료입니다.

15. 노드 그룹 삭제가 완료되면 클러스터를 삭제합니다:

```bash
aws eks delete-cluster \
  --name my-eks-cluster \
  --region ap-northeast-2
```

> [!NOTE]
> 클러스터 삭제에 5-10분이 소요됩니다. 노드 그룹이 완전히 삭제되지 않은 상태에서 클러스터 삭제를 시도하면 오류가 발생합니다.
> 다음 명령어로 삭제 완료를 확인합니다:
>
> ```bash
> aws eks describe-cluster --name my-eks-cluster --region ap-northeast-2 --query 'cluster.status' --output text
> ```
>
> "DELETING"이 출력되면 대기하고, "ResourceNotFoundException" 오류가 나오면 삭제 완료입니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

16. AWS Management Console 상단 검색창에 `EKS`를 입력하고 **Elastic Kubernetes Service**를 선택합니다.
17. **Clusters**에서 `my-eks-cluster`를 선택합니다.
18. **Compute** 탭을 선택합니다.
19. **Node groups** 섹션에서 `my-node-group`을 선택합니다.
20. [[Delete]] 버튼을 클릭합니다.
21. 확인 창에서 `my-node-group`을 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 노드 그룹 삭제에 3-5분이 소요됩니다. 노드 그룹이 완전히 삭제되어야 클러스터를 삭제할 수 있습니다.

22. 노드 그룹이 삭제되면 클러스터 목록으로 돌아갑니다.
23. `my-eks-cluster`를 선택합니다.
24. [[Delete cluster]] 버튼을 클릭합니다.
25. 확인 창에서 `my-eks-cluster`를 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 클러스터 삭제에 5-10분이 소요됩니다. 상태가 "Deleting"에서 완전히 사라질 때까지 기다립니다.

### 단계 5: AWS CloudFormation 스택 삭제

26. AWS Management Console 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
27. `week7-3-eks-lab-stack` 스택을 선택합니다.
28. [[Delete stack]] 버튼을 클릭합니다.
29. 확인 창에서 스택 이름 `week7-3-eks-lab-stack`을 입력합니다.
30. [[Delete stack]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 VPC, 서브넷, IAM 역할 등 모든 사전 인프라가 자동으로 삭제됩니다.

> [!TIP] AWS CloudFormation 스택 삭제 실패 시
>
> "DELETE_FAILED" 상태가 되면 Load Balancer 또는 네트워크 인터페이스(ENI)가 남아있을 수 있습니다.
>
> 1. Amazon EC2 콘솔 > **Load Balancers**에서 관련 Load Balancer를 수동 삭제합니다.
> 2. Amazon EC2 콘솔 > **Network Interfaces**에서 해당 VPC의 "available" 상태 ENI를 삭제합니다.
> 3. Amazon EC2 콘솔 > **Security Groups**에서 해당 VPC의 보안 그룹을 삭제합니다 (default 제외).
> 4. AWS CloudFormation 콘솔에서 스택을 다시 삭제합니다.

### 단계 6: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

31. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
32. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
33. **Regions**에서 `ap-northeast-2`를 선택합니다.
34. **Resource types**에서 `All supported resource types`를 선택합니다.
35. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `7-3`
36. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 7: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

37. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
38. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
39. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
40. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
41. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [Amazon EKS 사용 설명서](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/home/)
- [kubectl 치트 시트](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Amazon EKS 모범 사례 가이드](https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html)

## 📚 참고: Amazon EKS 및 Kubernetes 핵심 개념

### Amazon EKS (Elastic Kubernetes Service)

Amazon EKS는 AWS에서 제공하는 관리형 Kubernetes 서비스입니다. Kubernetes 컨트롤 플레인의 설치, 운영, 유지 관리를 자동화하여 사용자는 애플리케이션 배포에만 집중할 수 있습니다.

**주요 특징:**

- 고가용성: 여러 가용 영역에 걸쳐 컨트롤 플레인 자동 배포
- 자동 업그레이드: Kubernetes 버전 업그레이드 자동화
- AWS 통합: AWS IAM, Amazon VPC, ELB 등 AWS 서비스와 네이티브 통합
- 보안: AWS 보안 모범 사례 자동 적용

### Kubernetes 버전 지원 정책

Amazon EKS는 Kubernetes 버전을 Standard Support와 Extended Support로 구분하여 지원합니다.

**지원 버전 확인 방법:**

CloudShell을 열고 다음 명령어를 실행하여 현재 지원되는 Kubernetes 버전을 확인합니다:

```bash
aws eks describe-addon-versions --query 'addons[0].addonVersions[0].compatibilities[*].clusterVersion' --output text | tr '\t' '\n' | sort -V | uniq
```

또는 더 간단하게:

```bash
aws eks describe-cluster-versions --query 'clusterVersions[?status==`STANDARD_SUPPORT`].clusterVersion' --output text
```

### kubectl 수동 설치 방법

CloudShell의 kubectl 버전이 클러스터와 호환되지 않으면 다음 명령어로 수동 설치합니다:

```bash
# 클러스터 버전 확인
CLUSTER_VERSION=$(aws eks describe-cluster --name my-eks-cluster --query 'cluster.version' --output text)
echo "클러스터 버전: $CLUSTER_VERSION"

# 해당 버전의 최신 안정 릴리스 다운로드 및 설치
curl -LO "https://dl.k8s.io/release/stable-${CLUSTER_VERSION}/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

> [!NOTE]
> `stable-${CLUSTER_VERSION}` URL은 해당 마이너 버전의 최신 패치 버전을 자동으로 다운로드합니다.
> 예: 클러스터가 1.32이면 1.32.x의 최신 안정 버전(예: 1.32.3)을 다운로드합니다.

### Kubernetes 아키텍처

**컨트롤 플레인 (Control Plane):**

- API Server: 모든 요청의 진입점
- etcd: 클러스터 상태 저장소
- Scheduler: Pod를 노드에 할당
- Controller Manager: 클러스터 상태 관리

**워커 노드 (Worker Node):**

- kubelet: 노드에서 Pod 실행 관리
- kube-proxy: 네트워크 규칙 관리
- Container Runtime: 컨테이너 실행 (Docker, containerd 등)

### Kubernetes 리소스

**Pod:**

- Kubernetes의 가장 작은 배포 단위
- 하나 이상의 컨테이너를 포함
- 동일한 네트워크 네임스페이스 공유
- 일시적(ephemeral)이며 재시작 시 IP 변경

**Deployment:**

- Pod의 선언적 업데이트 제공
- 원하는 상태(desired state) 유지
- 롤링 업데이트 및 롤백 지원
- ReplicaSet을 통한 Pod 복제 관리

**Service:**

- Pod에 대한 안정적인 네트워크 엔드포인트 제공
- 로드 밸런싱 기능 내장
- 타입: ClusterIP, NodePort, LoadBalancer, ExternalName

### 명령형 vs 선언형 방식

**명령형 (Imperative):**

- 명령어로 직접 리소스 생성 및 수정
- 예: `kubectl create`, `kubectl scale`, `kubectl expose`
- 장점: 빠르고 간단, 학습 및 테스트에 적합
- 단점: 버전 관리 어려움, 재현성 낮음, 변경 이력 추적 불가

**선언형 (Declarative):**

- YAML 파일로 원하는 상태 정의 후 `kubectl apply` 실행
- 예: `kubectl apply -f deployment.yaml`
- 장점: Git으로 버전 관리, 재현 가능, 변경 이력 추적, 프로덕션 권장
- 단점: 초기 학습 곡선, YAML 문법 이해 필요

**프로덕션 권장사항:**

- 개발/테스트: 명령형 방식으로 빠르게 실험
- 프로덕션: 선언형 방식으로 YAML 파일 관리
- GitOps: Git 저장소에 YAML 파일 저장, CI/CD 파이프라인 자동 배포

### 롤링 업데이트 (Rolling Update)

**개념:**

- 애플리케이션의 다운타임 없이 새 버전으로 점진적 업데이트
- Kubernetes의 기본 배포 전략
- 무중단 배포(Zero-downtime deployment) 구현

**동작 방식:**

- 새 버전의 Pod를 하나씩 생성합니다.
- 새 Pod가 Ready 상태가 되면 기존 Pod를 하나씩 종료합니다.
- 모든 Pod가 새 버전으로 교체될 때까지 반복합니다.

**롤링 업데이트 전략 설정:**

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1 # 동시에 생성할 수 있는 추가 Pod 수
      maxUnavailable: 0 # 동시에 사용 불가능한 Pod 수
```

**maxSurge:**

- 원하는 Pod 수를 초과하여 생성할 수 있는 최대 Pod 수
- 예: replicas=3, maxSurge=1 → 업데이트 중 최대 4개 Pod 실행
- 값: 숫자 또는 백분율 (예: 1, 25%)

**maxUnavailable:**

- 업데이트 중 사용 불가능한 최대 Pod 수
- 예: replicas=3, maxUnavailable=1 → 최소 2개 Pod는 항상 실행
- 값: 숫자 또는 백분율 (예: 1, 25%)

**롤백 (Rollback):**

- 이전 버전으로 빠르게 복구
- 명령어: `kubectl rollout undo deployment/<name>`
- 특정 리비전으로 롤백: `kubectl rollout undo deployment/<name> --to-revision=<n>`
- 롤아웃 히스토리: `kubectl rollout history deployment/<name>`

**모범 사례:**

- 프로덕션에서는 maxUnavailable=0 설정 (무중단 보장)
- Health Check (Readiness Probe) 설정 필수
- 롤아웃 히스토리 보존: `revisionHistoryLimit: 10`
- 점진적 롤아웃: Canary 배포, Blue-Green 배포 고려

### kubectl 주요 명령어

**리소스 조회:**

```bash
kubectl get pods                    # Pod 목록
kubectl get deployments             # Deployment 목록
kubectl get services                # Service 목록
kubectl get nodes                   # 노드 목록
kubectl get all                     # 모든 리소스
```

**리소스 상세 정보:**

```bash
kubectl describe pod <pod-name>     # Pod 상세 정보
kubectl logs <pod-name>             # Pod 로그
kubectl exec -it <pod-name> -- bash # Pod 내부 접속
```

**리소스 생성 및 수정:**

```bash
kubectl create deployment <name> --image=<image>  # Deployment 생성
kubectl scale deployment <name> --replicas=<n>    # 스케일링
kubectl expose deployment <name> --port=<port>    # Service 생성
kubectl delete pod <pod-name>                     # Pod 삭제
```

### Amazon EKS 노드 그룹

**관리형 노드 그룹:**

- AWS가 Amazon EC2 인스턴스 수명 주기 관리
- 자동 업데이트 및 패치 적용
- Amazon EC2 Auto Scaling 그룹 자동 생성
- 권장 방식

**자체 관리형 노드:**

- 사용자가 직접 Amazon EC2 인스턴스 관리
- 더 많은 제어권 제공
- 특수한 요구사항이 있을 때 사용

### AWS IAM 역할 및 권한

**클러스터 역할 (eks-cluster-role):**

- Amazon EKS가 AWS 리소스를 관리하기 위한 권한
- AmazonEKSClusterPolicy 필요
- Amazon VPC, 로드 밸런서, 보안 그룹 관리

**노드 역할 (eks-node-role):**

- 워커 노드가 AWS 리소스에 접근하기 위한 권한
- AmazonEKSWorkerNodePolicy: 노드 기본 권한
- AmazonEC2ContainerRegistryReadOnly: Amazon ECR 이미지 pull
- AmazonEKS_CNI_Policy: 네트워크 플러그인 권한

### 네트워킹

**Amazon VPC CNI (Container Network Interface):**

- 각 Pod에 Amazon VPC IP 주소 할당
- AWS 네트워크와 네이티브 통합
- 보안 그룹을 Pod에 직접 적용 가능

**Service 타입별 네트워킹:**

- ClusterIP: 클러스터 내부에서만 접근 가능
- NodePort: 각 노드의 특정 포트로 접근
- LoadBalancer: AWS ELB를 자동 생성하여 외부 노출

### LoadBalancer Service와 AWS Load Balancer

**기본 동작 (Classic Load Balancer):**

- `kubectl expose --type=LoadBalancer` 명령은 기본적으로 Classic Load Balancer를 생성합니다.
- NodePort 범위(30000-32767)를 통해 워커 노드와 통신합니다.
- 학습 및 테스트 환경에서는 충분히 사용 가능합니다.

**프로덕션 환경 권장사항 (ALB/NLB):**

AWS에서는 Classic Load Balancer를 레거시로 분류하고, Application Load Balancer(ALB) 또는 Network Load Balancer(NLB) 사용을 권장합니다.

**AWS Load Balancer Controller 사용:**

- AWS Load Balancer Controller를 클러스터에 설치합니다.
- Ingress 리소스(ALB) 또는 Service 어노테이션(NLB)을 사용합니다.

**ALB 사용 예시 (Ingress):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-app
                port:
                  number: 80
```

**NLB 사용 예시 (Service 어노테이션):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-app
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: 'nlb'
    service.beta.kubernetes.io/aws-load-balancer-scheme: 'internet-facing'
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

**Classic LB vs ALB/NLB 비교:**

| 특징                   | Classic LB       | ALB               | NLB           |
| ---------------------- | ---------------- | ----------------- | ------------- |
| **OSI 계층**           | Layer 4/7        | Layer 7           | Layer 4       |
| **프로토콜**           | HTTP, HTTPS, TCP | HTTP, HTTPS, gRPC | TCP, UDP, TLS |
| **경로 기반 라우팅**   | ❌               | ✅                | ❌            |
| **호스트 기반 라우팅** | ❌               | ✅                | ❌            |
| **WebSocket**          | ✅               | ✅                | ✅            |
| **고정 IP**            | ❌               | ❌                | ✅            |
| **성능**               | 보통             | 높음              | 매우 높음     |
| **비용**               | 낮음             | 중간              | 중간          |
| **AWS 권장**           | ❌ (레거시)      | ✅                | ✅            |

**프로덕션 환경 선택 가이드:**

- **HTTP/HTTPS 애플리케이션**: ALB 사용 (경로 기반 라우팅, SSL 종료, AWS WAF 통합)
- **고성능 TCP/UDP**: NLB 사용 (낮은 지연 시간, 고정 IP, 초당 수백만 요청)
- **레거시 마이그레이션**: Classic LB에서 ALB/NLB로 마이그레이션 계획 수립

**참고 자료:**

- [AWS Load Balancer Controller 설치 가이드](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/aws-load-balancer-controller.html)
- [ALB Ingress 어노테이션](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/ingress/annotations/)
- [NLB Service 어노테이션](https://kubernetes-sigs.github.io/aws-load-balancer-controller/latest/guide/service/annotations/)

### 모범 사례

**보안:**

- AWS IAM 역할을 사용한 Pod 권한 관리 (IRSA)
- 네트워크 정책으로 Pod 간 통신 제어
- Secrets를 사용한 민감 정보 관리
- 최소 권한 원칙 적용

**성능:**

- 적절한 리소스 요청(requests) 및 제한(limits) 설정
- Horizontal Pod Autoscaler 활용
- Cluster Autoscaler로 노드 자동 확장
- 여러 가용 영역에 노드 분산

**비용 최적화:**

- Spot 인스턴스 활용
- 적절한 인스턴스 타입 선택
- 사용하지 않는 리소스 정리
- 리소스 요청 최적화

### 문제 해결

**Pod가 Pending 상태:**

- 노드 리소스 부족 확인
- PersistentVolume 바인딩 확인
- 노드 셀렉터 및 어피니티 규칙 확인

**Pod가 CrashLoopBackOff:**

- 로그 확인: `kubectl logs <pod-name>`
- 이벤트 확인: `kubectl describe pod <pod-name>`
- 컨테이너 이미지 및 설정 검증

**Service 접근 불가:**

- Service 엔드포인트 확인: `kubectl get endpoints`
- 보안 그룹 규칙 확인
- 네트워크 정책 확인

### QuickTable 프로젝트 적용 예시

**Week 9-2에서 활용할 컨테이너 빌드 프로세스:**

이 실습에서 학습한 Amazon EKS와 kubectl 개념은 Week 9-2에서 다음과 같이 활용됩니다:

**1. Docker 이미지 빌드 (buildspec.yml)**:

```yaml
version: 0.2
phases:
  build:
    commands:
      - docker build -t quicktable-api:latest .
      - docker tag quicktable-api:latest $ECR_REPO:latest
      - docker push $ECR_REPO:latest
```

**2. Amazon ECR에 이미지 푸시**:

- AWS CodeBuild가 자동으로 Docker 이미지 빌드
- Amazon ECR(Elastic Container Registry)에 이미지 저장
- 버전 태그 관리 (latest, v1.0.0 등)

**3. Week 9-3에서 Amazon S3 정적 웹사이트 배포**:

- QuickTable 프론트엔드를 Amazon S3에 배포
- CodePipeline으로 자동 배포 파이프라인 구성
- Amazon CloudFront CDN 연동 (Week 10-3)

**학습 연계**:

- **Week 7-3**: Kubernetes 기본 개념 (Pod, Deployment, Service)
- **Week 9-2**: 컨테이너 이미지 빌드 및 Amazon ECR 푸시 (CI/CD)
- **Week 9-3**: Amazon S3 정적 웹사이트 자동 배포 (CI/CD)
- **Week 10-3**: Amazon CloudFront로 글로벌 배포 (성능 최적화)

**실전 프로젝트 흐름**:

- Amazon EKS 클러스터 이해 (Week 7-3).
- 컨테이너 이미지 빌드 자동화 (Week 9-2).
- 웹사이트 배포 자동화 (Week 9-3).
- CDN으로 성능 최적화 (Week 10-3).
