---
title: 'Amazon CloudWatch Container Insights로 Amazon EKS 모니터링 및 자동 스케일링'
week: 13
session: 3
awsServices:
  - Amazon CloudWatch
  - Amazon EKS
learningObjectives:
  - Container Insights의 개념과 컨테이너 메트릭 수집 구조를 이해할 수 있습니다.
  - Container Insights를 활성화하고 AWS CloudWatch 에이전트를 배포할 수 있습니다.
  - AWS CloudWatch 대시보드에서 클러스터 메트릭을 확인할 수 있습니다.
  - AWS CloudWatch Logs Insights로 컨테이너 로그를 쿼리하고 분석할 수 있습니다.

prerequisites:
  - Week 7-3 Amazon EKS 클러스터 생성 실습 완료
  - kubectl 기본 명령어 숙지
  - Amazon CloudWatch 기본 개념 이해
---

이 실습에서는 Amazon EKS 클러스터에 Amazon CloudWatch Container Insights를 활성화하고, Amazon CloudWatch를 통해 컨테이너 수준의 성능 메트릭과 로그를 수집 및 분석합니다. Amazon CloudWatch Logs Insights를 사용하여 로그를 쿼리하고, 커스텀 대시보드를 생성하며, 성능 이상을 감지하는 알람을 설정합니다. Horizontal Pod Autoscaler를 통해 자동 스케일링을 구현하여 트래픽 변화에 대응합니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
>
> **예상 비용** (ap-northeast-2 리전 기준):
>
> | 리소스                 | 타입          | 시간당 비용       |
> | ---------------------- | ------------- | ----------------- |
> | Amazon EKS 클러스터    | 컨트롤 플레인 | 약 $0.10          |
> | Amazon EC2 인스턴스    | t3.medium × 2 | 약 $0.104         |
> | NAT Gateway            | -             | 약 $0.045         |
> | Elastic Load Balancing | Classic LB    | 약 $0.025         |
> | Amazon CloudWatch Logs | 스토리지      | GB당 월 $0.50     |
> | **총 예상**            | -             | **약 $0.27/시간** |

실습 소요 시간을 확인합니다.

> [!IMPORTANT]
> 이 실습은 Amazon EKS 클러스터 생성(15-20분), Container Insights 설치, 대시보드 생성, 알람 설정 등 다양한 작업을 포함합니다.
> 전체 소요 시간이 **2시간 이상** 예상되므로, 충분한 시간을 확보한 후 진행합니다.
>
> **클러스터 삭제에도 10-15분이 소요**되므로, 실습 종료 시 반드시 삭제 완료를 확인한 후 퇴실합니다.

> [!DOWNLOAD]
> [week13-3-container-insights-lab.zip](/files/week13/week13-3-container-insights-lab.zip)
>
> - `cloudwatch-agent-config.json` - CloudWatch 에이전트 설정 파일
> - `lambda_function.py` - 모니터링 관련 Lambda 함수 코드
> - `lambda-iam-policy.json` - Lambda 실행 역할 IAM 정책

## 태스크 1: Amazon EKS 클러스터 생성

이 태스크에서는 eksctl을 사용하여 Amazon EKS 클러스터를 생성하고 Amazon CloudWatch Container Insights를 위한 Amazon CloudWatch 로깅을 활성화합니다.

1. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.
2. AWS CloudShell 환경이 로드될 때까지 기다립니다.

CloudShell 초기화를 기다립니다.

> [!NOTE]
> AWS CloudShell 초기 로딩에 30초-1분이 소요될 수 있습니다.

3. eksctl 버전을 확인합니다:

```bash
eksctl version
```

4. 클러스터 설정 파일을 생성합니다:

```bash
cat > cluster-config.yaml << 'EOF'
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: container-insights-cluster
  region: ap-northeast-2
  version: "1.29"
  tags:
    Project: AWS-Lab
    Week: "13-3"
    CreatedBy: Student

managedNodeGroups:
  - name: managed-ng-1
    instanceType: t3.medium
    minSize: 2
    maxSize: 3
    desiredCapacity: 2
    volumeSize: 20
    ssh:
      allow: false
    labels:
      role: worker
    tags:
      nodegroup-role: worker
      Project: AWS-Lab
      Week: "13-3"
      CreatedBy: Student
    iam:
      attachPolicyARNs:
        - arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
        - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
        - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

cloudWatch:
  clusterLogging:
    enableTypes: ["api", "audit", "authenticator", "controllerManager", "scheduler"]
EOF
```

> [!NOTE]
> Amazon EKS 버전 1.29를 사용합니다. 버전 1.28은 2024년 11월에 지원이 종료되었습니다.
> CloudWatchAgentServerPolicy를 노드 그룹에 추가하여 Amazon CloudWatch Container Insights 메트릭 수집 권한을 부여합니다.

5. 파일 내용을 확인합니다:

```bash
cat cluster-config.yaml
```

6. Amazon EKS 클러스터를 생성합니다:

```bash
nohup eksctl create cluster -f cluster-config.yaml > cluster-creation.log 2>&1 &
```

> [!NOTE]
> 클러스터 생성에 15-20분이 소요됩니다. `nohup` 명령어를 사용하여 백그라운드에서 실행하므로 AWS CloudShell 세션 타임아웃을 방지할 수 있습니다.
>
> 다음 명령어로 진행 상황을 확인합니다:
>
> ```bash
> tail -f cluster-creation.log
> ```
>
> Ctrl+C를 눌러 로그 확인을 종료합니다 (클러스터 생성은 계속 진행됩니다).

7. 클러스터 생성 완료를 확인합니다:

```bash
tail -f cluster-creation.log
```

> [!NOTE]
> "Amazon EKS cluster "container-insights-cluster" in "ap-northeast-2" region is ready" 메시지가 표시되면 Ctrl+C를 눌러 로그 확인을 종료합니다.

8. 클러스터 상태를 확인합니다:

```bash
eksctl get cluster --name container-insights-cluster --region ap-northeast-2
```

> [!OUTPUT]
>
> ```text
> NAME                        REGION          EKSCTL CREATED
> container-insights-cluster  ap-northeast-2  True
> ```

9. kubectl 설정을 확인합니다:

```bash
kubectl get nodes
```

> [!OUTPUT]
>
> ```text
> NAME                                               STATUS   ROLES    AGE   VERSION
> ip-192-168-1-10.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.29.0-eks-5e0fdde
> ip-192-168-2-20.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.29.0-eks-5e0fdde
> ```

✅ **태스크 완료**: Amazon EKS 클러스터가 생성되었습니다.

## 태스크 2: Amazon CloudWatch Container Insights 활성화 (Amazon EKS Add-on 방식)

이 태스크에서는 Amazon EKS Add-on 방식으로 Amazon CloudWatch Container Insights를 활성화하고 Amazon CloudWatch 에이전트를 배포합니다.

> [!CONCEPT] Amazon CloudWatch Container Insights 아키텍처
> Amazon CloudWatch Container Insights는 컨테이너화된 애플리케이션의 성능 메트릭과 로그를 자동으로 수집하는 완전 관리형 모니터링 솔루션입니다.
>
> **주요 구성 요소**:
>
> - **Amazon CloudWatch 에이전트**: DaemonSet으로 각 노드에 배포되어 노드 수준 메트릭(CPU, 메모리, 디스크, 네트워크)을 수집합니다
> - **Fluent Bit**: 경량 로그 프로세서로 컨테이너 로그를 수집하고 Amazon CloudWatch Logs로 스트리밍합니다
> - **메트릭 수집 흐름**: Kubernetes API → kubelet → cAdvisor → Amazon CloudWatch 에이전트 → Amazon CloudWatch

Amazon EKS Add-on 방식을 사용합니다.

> [!NOTE]
> 2024년 이후 Amazon EKS Add-on 방식이 권장됩니다. 이 방식은 설치와 업데이트가 간편하며, AWS가 자동으로 관리합니다.

10. CloudShell에서 Amazon EKS Add-on으로 Amazon CloudWatch Container Insights를 활성화합니다:

```bash
aws eks create-addon \
  --cluster-name container-insights-cluster \
  --addon-name amazon-cloudwatch-observability \
  --region ap-northeast-2
```

11. Add-on 설치 상태를 확인합니다:

```bash
aws eks describe-addon \
  --cluster-name container-insights-cluster \
  --addon-name amazon-cloudwatch-observability \
  --region ap-northeast-2 \
  --query 'addon.status' \
  --output text
```

> [!NOTE]
> Add-on 설치에 2-3분이 소요됩니다. 상태가 "ACTIVE"로 변경될 때까지 기다립니다.
>
> 다음 명령어로 상태를 반복 확인합니다:
>
> ```bash
> watch -n 10 'aws eks describe-addon --cluster-name container-insights-cluster --addon-name amazon-cloudwatch-observability --region ap-northeast-2 --query "addon.status" --output text'
> ```
>
> Ctrl+C를 눌러 watch 모드를 종료합니다.

12. 배포된 Pod 상태를 확인합니다:

```bash
kubectl get pods -n amazon-cloudwatch
```

> [!OUTPUT]
>
> ```text
> NAME                                                         READY   STATUS    RESTARTS   AGE
> amazon-cloudwatch-observability-controller-xxxxx-yyyyy      1/1     Running   0          2m
> cloudwatch-agent-xxxxx                                       1/1     Running   0          2m
> cloudwatch-agent-zzzzz                                       1/1     Running   0          2m
> fluent-bit-xxxxx                                             1/1     Running   0          2m
> fluent-bit-zzzzz                                             1/1     Running   0          2m
> ```

13. 모든 Pod가 "Running" 상태가 될 때까지 기다립니다.

> [!NOTE]
> Pod 시작에 1-2분이 소요될 수 있습니다. 다음 명령어로 상태를 확인합니다:
>
> ```bash
> kubectl get pods -n amazon-cloudwatch --watch
> ```
>
> Ctrl+C를 눌러 watch 모드를 종료합니다.

✅ **태스크 완료**: Amazon CloudWatch Container Insights가 활성화되었습니다.

## 태스크 3: 샘플 애플리케이션 배포

이 태스크에서는 모니터링할 샘플 애플리케이션을 배포합니다.

14. 샘플 애플리케이션 Deployment를 생성합니다:

```bash
cat > sample-app.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  namespace: default
  labels:
    app: sample-app
    Project: AWS-Lab
    Week: "13-3"
    CreatedBy: Student
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
        Project: AWS-Lab
        Week: "13-3"
        CreatedBy: Student
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: sample-app-service
  namespace: default
  labels:
    Project: AWS-Lab
    Week: "13-3"
    CreatedBy: Student
spec:
  type: LoadBalancer
  selector:
    app: sample-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
EOF
```

15. 애플리케이션을 배포합니다:

```bash
kubectl apply -f sample-app.yaml
```

16. 배포 상태를 확인합니다:

```bash
kubectl get deployments
```

> [!OUTPUT]
>
> ```
> NAME         READY   UP-TO-DATE   AVAILABLE   AGE
> sample-app   3/3     3            3           30s
> ```

17. Pod 상태를 확인합니다:

```bash
kubectl get pods -l app=sample-app
```

18. Service 정보를 확인합니다:

```bash
kubectl get service sample-app-service
```

19. LoadBalancer의 External IP가 할당될 때까지 기다립니다:

```bash
kubectl get service sample-app-service --watch
```

> [!NOTE]
> LoadBalancer 생성에 2-3분이 소요됩니다. EXTERNAL-IP가 `<pending>`에서 실제 주소로 변경되면 Ctrl+C를 눌러 종료합니다.

비용 정보를 확인합니다.

> [!WARNING]
> Classic Load Balancer는 시간당 약 $0.025가 부과됩니다. 실습 종료 후 반드시 삭제합니다.

20. External IP를 메모장에 복사합니다.

21. 웹 브라우저에서 External IP로 접속하여 nginx 기본 페이지를 확인합니다.

✅ **태스크 완료**: 샘플 애플리케이션이 배포되었습니다.

## 태스크 4: Amazon CloudWatch Container Insights 대시보드 확인

이 태스크에서는 Amazon CloudWatch 콘솔에서 Container Insights 대시보드를 확인하고 메트릭을 분석합니다.

> [!CONCEPT] Amazon CloudWatch Container Insights 메트릭 계층 구조
> Amazon CloudWatch Container Insights는 4가지 수준의 메트릭을 제공하여 클러스터부터 개별 컨테이너까지 세밀한 모니터링을 지원합니다.
>
> **메트릭 수준**:
>
> - **클러스터 수준**: 전체 클러스터의 CPU, 메모리, Pod 수, 노드 상태 등 집계 메트릭
> - **노드 수준**: 개별 워커 노드의 리소스 사용률, 네트워크 트래픽, 파일시스템 사용량
> - **Pod 수준**: 각 Pod의 CPU/메모리 사용률, 네트워크 I/O, 재시작 횟수
> - **컨테이너 수준**: Pod 내 개별 컨테이너의 리소스 사용량 및 상태
>
> 이러한 계층적 구조를 통해 성능 문제를 빠르게 식별하고 원인을 추적할 수 있습니다.

22. AWS Management Console에서 상단 검색창에 `CloudWatch`를 입력한 후 선택합니다.
23. 왼쪽 메뉴에서 **Insights** > **Container Insights**를 선택합니다.
24. **Performance monitoring** 섹션이 표시됩니다.
25. 상단의 드롭다운에서 `Amazon EKS Clusters`를 선택합니다.
26. **container-insights-cluster** 클러스터를 선택합니다.
27. 대시보드에서 다음 메트릭을 확인합니다:
   - **CPU Utilization**: 클러스터 전체 CPU 사용률
   - **Memory Utilization**: 클러스터 전체 메모리 사용률
   - **Network**: 네트워크 송수신 바이트
   - **Pod Count**: 실행 중인 Pod 수

> [!NOTE]
> 메트릭이 표시되기까지 5-10분이 소요될 수 있습니다. 페이지를 새로고침하여 최신 데이터를 확인합니다.

28. 상단의 드롭다운을 `Amazon EKS Nodes`로 변경합니다.
29. 개별 노드의 성능 메트릭을 확인합니다.
30. 노드 이름을 클릭하여 상세 정보를 확인합니다.
31. 상단의 드롭다운을 `Amazon EKS Pods`로 변경합니다.
32. **sample-app** Pod들을 찾습니다.
33. Pod 이름을 클릭하여 상세 메트릭을 확인합니다:
    - CPU 사용률
    - 메모리 사용률
    - 네트워크 트래픽
    - 디스크 I/O

34. 상단의 드롭다운을 `Amazon EKS Namespaces`로 변경합니다.
35. **default** 네임스페이스를 선택합니다.
36. 네임스페이스 수준의 리소스 사용량을 확인합니다.

✅ **태스크 완료**: Amazon CloudWatch Container Insights 대시보드를 확인했습니다.

## 태스크 5: Amazon CloudWatch Logs Insights로 로그 분석

이 태스크에서는 Amazon CloudWatch Logs Insights를 사용하여 컨테이너 로그를 쿼리하고 분석합니다.

> [!CONCEPT] Amazon CloudWatch Logs Insights 쿼리 언어
> Amazon CloudWatch Logs Insights는 SQL과 유사한 쿼리 언어를 제공하여 대량의 로그 데이터를 빠르게 검색하고 분석할 수 있습니다.
>
> **주요 쿼리 패턴**:
>
> - **필터링**: `filter` 명령으로 특정 조건에 맞는 로그만 선택 (예: 에러 로그, 특정 네임스페이스)
> - **파싱**: `parse` 명령으로 로그 메시지에서 구조화된 데이터 추출 (예: HTTP 메서드, 상태 코드)
> - **집계**: `stats` 명령으로 로그 개수, 평균, 최대/최소값 계산
> - **정렬**: `sort` 명령으로 결과를 시간순 또는 값 기준으로 정렬
>
> 쿼리는 초당 수백만 개의 로그 이벤트를 스캔할 수 있으며, 결과는 실시간으로 시각화됩니다.

37. Amazon CloudWatch 콘솔로 이동합니다.
38. 왼쪽 메뉴에서 **Logs** > **Logs Insights**를 선택합니다.
39. **Select log group(s)** 드롭다운을 클릭합니다.
40. 다음 로그 그룹들을 선택합니다:
   - `/aws/containerinsights/container-insights-cluster/application`
   - `/aws/containerinsights/container-insights-cluster/dataplane`
   - `/aws/containerinsights/container-insights-cluster/host`

41. 쿼리 에디터에 다음 쿼리를 입력합니다:

```text
fields @timestamp, @message
| filter kubernetes.namespace_name = "default"
| filter kubernetes.pod_name like /sample-app/
| sort @timestamp desc
| limit 20
```

42. 시간 범위를 `Last 1 hour`로 설정합니다.
43. [[Run query]] 버튼을 클릭합니다.
44. 쿼리 결과에서 sample-app Pod의 로그를 확인합니다.

> [!NOTE]
> 로그가 표시되지 않으면 시간 범위를 `Last 3 hours`로 확장한 후 페이지를 새로고침합니다.

45. 다음 쿼리로 에러 로그만 필터링합니다:

```text
fields @timestamp, @message, kubernetes.pod_name
| filter kubernetes.namespace_name = "default"
| filter @message like /error|Error|ERROR/
| sort @timestamp desc
| limit 50
```

46. [[Run query]] 버튼을 클릭합니다.

47. Pod별 로그 개수를 집계하는 쿼리를 실행합니다:

```text
fields kubernetes.pod_name
| filter kubernetes.namespace_name = "default"
| stats count() by kubernetes.pod_name
| sort count() desc
```

48. [[Run query]] 버튼을 클릭합니다.
49. 결과를 **Visualization** 탭에서 확인합니다.
50. **Bar** 차트를 선택하여 시각화합니다.

51. HTTP 요청 로그를 분석하는 쿼리를 실행합니다:

```text
fields @timestamp, @message
| filter kubernetes.namespace_name = "default"
| filter @message like /GET|POST|PUT|DELETE/
| parse @message /(?<method>\w+)\s+(?<path>\/\S*)\s+HTTP/
| stats count() by method, path
| sort count() desc
```

52. [[Run query]] 버튼을 클릭합니다.
53. HTTP 메서드별 요청 수를 확인합니다.

54. 쿼리를 저장하려면 [[Save]] 버튼을 클릭합니다.
55. **Query name**에 `Sample App HTTP Requests`를 입력합니다.
56. [[Save]] 버튼을 클릭합니다.

✅ **태스크 완료**: Amazon CloudWatch Logs Insights로 로그를 분석했습니다.

## 태스크 6: 커스텀 대시보드 생성

이 태스크에서는 Amazon EKS 클러스터 모니터링을 위한 커스텀 Amazon CloudWatch 대시보드를 생성합니다.

> [!CONCEPT] Amazon CloudWatch 대시보드 위젯 타입
> Amazon CloudWatch 대시보드는 다양한 위젯 타입을 제공하여 메트릭과 로그를 효과적으로 시각화합니다.
>
> **주요 위젯 타입**:
>
> - **Line 위젯**: 시계열 데이터를 선 그래프로 표시하여 시간에 따른 추세 분석 (예: CPU 사용률 변화)
> - **Number 위젯**: 단일 메트릭의 현재 값을 큰 숫자로 표시하여 즉각적인 상태 파악 (예: 실행 중인 Pod 수)
> - **Logs table 위젯**: 로그 쿼리 결과를 테이블 형태로 표시하여 최근 이벤트 확인
> - **Bar/Pie 위젯**: 카테고리별 비교 및 비율 시각화
>
> 대시보드는 자동 새로고침을 지원하며, 여러 리전의 메트릭을 하나의 대시보드에 통합할 수 있습니다.

57. Amazon CloudWatch 콘솔로 이동합니다.
58. 왼쪽 메뉴에서 **Dashboards**를 선택합니다.
59. [[Create dashboard]] 버튼을 클릭합니다.
60. **Dashboard name**에 `Amazon EKS-Container-Insights-Dashboard`를 입력합니다.

> [!NOTE]
> 대시보드 이름에 공백을 사용하지 않는 것이 권장됩니다. URL 인코딩 문제를 방지할 수 있습니다.

61. [[Create dashboard]] 버튼을 클릭합니다.
62. **Add widget** 대화상자가 표시됩니다.
63. **Line** 위젯을 선택합니다.
64. [[Next]] 버튼을 클릭합니다.
65. **Metrics** 탭에서 다음을 선택합니다:
   - **ContainerInsights** 네임스페이스를 선택합니다.
   - **ClusterName** 차원을 선택합니다.
   - `container-insights-cluster`를 선택합니다.
   - `cluster_cpu_utilization` 메트릭을 체크합니다.
   - `cluster_memory_utilization` 메트릭을 체크합니다.

66. **Graphed metrics** 탭을 선택합니다.
67. **Statistic**을 `Average`로 설정합니다.
68. **Period**를 `5 minutes`로 설정합니다.
69. [[Create widget]] 버튼을 클릭합니다.

70. [[Add widget]] 버튼을 클릭하여 두 번째 위젯을 추가합니다.
71. **Number** 위젯을 선택합니다.
72. [[Next]] 버튼을 클릭합니다.
73. **ContainerInsights** > **ClusterName**을 선택합니다.
74. `cluster_number_of_running_pods` 메트릭을 선택합니다.
75. [[Create widget]] 버튼을 클릭합니다.

76. [[Add widget]] 버튼을 클릭하여 세 번째 위젯을 추가합니다.
77. **Line** 위젯을 선택합니다.
78. [[Next]] 버튼을 클릭합니다.
79. **ContainerInsights** > **ClusterName, Namespace**를 선택합니다.
80. `namespace_number_of_running_pods` 메트릭을 선택합니다.
81. **default** 네임스페이스를 선택합니다.
82. [[Create widget]] 버튼을 클릭합니다.

83. [[Add widget]] 버튼을 클릭하여 네 번째 위젯을 추가합니다.
84. **Logs table** 위젯을 선택합니다.
85. [[Next]] 버튼을 클릭합니다.
86. **Log groups**에서 `/aws/containerinsights/container-insights-cluster/application`을 선택합니다.
87. 다음 쿼리를 입력합니다:

```text
fields @timestamp, kubernetes.pod_name, @message
| filter kubernetes.namespace_name = "default"
| sort @timestamp desc
| limit 10
```

88. [[Create widget]] 버튼을 클릭합니다.

89. 위젯들을 드래그하여 원하는 레이아웃으로 배치합니다.
90. [[Save dashboard]] 버튼을 클릭합니다.

✅ **태스크 완료**: 커스텀 대시보드가 생성되었습니다.

## 태스크 7: Amazon CloudWatch 알람 설정

이 태스크에서는 Amazon EKS 클러스터의 이상 상황을 감지하는 Amazon CloudWatch 알람을 설정합니다.

> [!CONCEPT] Amazon CloudWatch 알람 평가 메커니즘
> Amazon CloudWatch 알람은 메트릭을 지속적으로 모니터링하고 임계값 초과 시 자동으로 알림을 전송하는 프로액티브 모니터링 도구입니다.
>
> **알람 평가 프로세스**:
>
> - **평가 기간 (Period)**: 메트릭을 집계하는 시간 단위 (예: 5분 평균)
> - **데이터 포인트**: 임계값 비교를 위한 평가 횟수 (예: 3개 중 2개 초과 시 알람)
> - **통계 방법**: Average, Sum, Maximum, Minimum 중 선택
> - **알람 상태**: OK (정상), ALARM (임계값 초과), INSUFFICIENT_DATA (데이터 부족)
>
> **Amazon SNS 통합**: 알람 상태 변경 시 Amazon SNS 토픽으로 알림을 전송하여 이메일, SMS, AWS Lambda 함수 등 다양한 채널로 통지할 수 있습니다.

91. Amazon CloudWatch 콘솔로 이동합니다.
92. 왼쪽 메뉴에서 **Alarms** > **All alarms**를 선택합니다.
93. [[Create alarm]] 버튼을 클릭합니다.
94. [[Select metric]] 버튼을 클릭합니다.
95. **ContainerInsights** 네임스페이스를 선택합니다.
96. **ClusterName** 차원을 선택합니다.
97. `cluster_cpu_utilization` 메트릭을 찾아 체크합니다.
98. [[Select metric]] 버튼을 클릭합니다.
99. **Metric** 섹션에서 다음을 설정합니다:
   - **Statistic**: `Average`
   - **Period**: `5 minutes`

100. **Conditions** 섹션에서 다음을 설정합니다:
    - **Threshold type**: `Static`
    - **Whenever cluster_cpu_utilization is...**: `Greater`
    - **than...**: `70`

101. [[Next]] 버튼을 클릭합니다.

102. **Notification** 섹션에서 다음을 설정합니다:
    - **Alarm state trigger**: `In alarm`
    - **Select an Amazon SNS topic**: `Create new topic`
    - **Create a new topic...**: `Amazon EKS-High-CPU-Alert`
    - **Email endpoints that will receive the notification**: 본인의 이메일 주소 입력

> [!NOTE]
> Amazon SNS 토픽 이름에 공백을 사용하지 않는 것이 권장됩니다. ARN 참조 시 문제를 방지할 수 있습니다.

103. [[Create topic]] 버튼을 클릭합니다.

> [!NOTE]
> 입력한 이메일 주소로 확인 메일이 발송됩니다. 이메일을 열고 **Confirm subscription** 링크를 클릭하여 구독을 확인합니다.

104. [[Next]] 버튼을 클릭합니다.
105. **Alarm name**에 `Amazon EKS-Cluster-High-CPU`를 입력합니다.
106. **Alarm description**에 `Alert when Amazon EKS cluster CPU utilization exceeds 70%`를 입력합니다.
107. [[Next]] 버튼을 클릭합니다.
108. 설정을 검토합니다.
109. [[Create alarm]] 버튼을 클릭합니다.

110. 두 번째 알람을 생성하기 위해 [[Create alarm]] 버튼을 다시 클릭합니다.
111. [[Select metric]] 버튼을 클릭합니다.
112. **ContainerInsights** > **ClusterName**을 선택합니다.
113. `cluster_memory_utilization` 메트릭을 선택합니다.
114. [[Select metric]] 버튼을 클릭합니다.
115. **Conditions** 섹션에서 다음을 설정합니다:
    - **Threshold type**: `Static`
    - **Whenever cluster_memory_utilization is...**: `Greater`
    - **than...**: `80`

116. [[Next]] 버튼을 클릭합니다.
117. **Select an Amazon SNS topic**에서 `Amazon EKS-High-CPU-Alert`를 선택합니다.
118. [[Next]] 버튼을 클릭합니다.
119. **Alarm name**에 `Amazon EKS-Cluster-High-Memory`를 입력합니다.
120. **Alarm description**에 `Alert when Amazon EKS cluster memory utilization exceeds 80%`를 입력합니다.
121. [[Next]] 버튼을 클릭합니다.
122. [[Create alarm]] 버튼을 클릭합니다.

123. 세 번째 알람을 생성하기 위해 [[Create alarm]] 버튼을 다시 클릭합니다.
124. [[Select metric]] 버튼을 클릭합니다.
125. **ContainerInsights** > **ClusterName**을 선택합니다.
126. `cluster_failed_node_count` 메트릭을 선택합니다.
127. [[Select metric]] 버튼을 클릭합니다.
128. **Conditions** 섹션에서 다음을 설정합니다:
    - **Threshold type**: `Static`
    - **Whenever cluster_failed_node_count is...**: `Greater`
    - **than...**: `0`

129. [[Next]] 버튼을 클릭합니다.
130. **Select an Amazon SNS topic**에서 `Amazon EKS-High-CPU-Alert`를 선택합니다.
131. [[Next]] 버튼을 클릭합니다.
132. **Alarm name**에 `Amazon EKS-Cluster-Failed-Nodes`를 입력합니다.
133. **Alarm description**에 `Alert when any node in the cluster fails`를 입력합니다.
134. [[Next]] 버튼을 클릭합니다.
135. [[Create alarm]] 버튼을 클릭합니다.

136. **All alarms** 페이지에서 생성된 3개의 알람을 확인합니다.

✅ **태스크 완료**: Amazon CloudWatch 알람이 설정되었습니다.

## 태스크 8: 성능 메트릭 분석 및 최적화

이 태스크에서는 수집된 메트릭을 분석하고 클러스터 성능을 최적화합니다.

> [!CONCEPT] Kubernetes 리소스 관리 및 오토스케일링
> Kubernetes는 리소스 requests/limits와 오토스케일링을 통해 애플리케이션 성능과 비용을 최적화합니다.
>
> **리소스 관리**:
>
> - **Requests**: 스케줄러가 Pod 배치 시 보장하는 최소 리소스 (노드 선택 기준)
> - **Limits**: Pod가 사용할 수 있는 최대 리소스 (초과 시 스로틀링 또는 종료)
> - **CPU Limit 초과**: 스로틀링 (Throttling) - 프로세스 속도 제한
> - **Memory Limit 초과**: OOMKilled (Out of Memory) - Pod 강제 종료
>
> **오토스케일링 전략**:
>
> - **HPA (Horizontal Pod Autoscaler)**: CPU/메모리 사용률 기반으로 Pod 수를 자동 증감 (2-10개)
> - **VPA (Vertical Pod Autoscaler)**: 과거 사용 패턴 분석하여 requests/limits 자동 조정
> - **Cluster Autoscaler**: 노드 부족 시 워커 노드 자동 추가/제거
>
> HPA는 트래픽 변화에 빠르게 대응하고, VPA는 리소스 낭비를 최소화하며, 두 가지를 함께 사용하면 최적의 성능과 비용 효율을 달성할 수 있습니다.

137. Amazon CloudWatch 콘솔에서 **Insights** > **Container Insights**를 선택합니다.
138. 드롭다운에서 `Amazon EKS Pods`를 선택합니다.
139. **sample-app** Pod들을 확인합니다.
140. CPU 사용률이 가장 높은 Pod를 찾습니다.
141. Pod 이름을 클릭하여 상세 메트릭을 확인합니다.
142. **Performance** 탭에서 다음을 분석합니다:
   - CPU 사용 패턴
   - 메모리 사용 패턴
   - 네트워크 트래픽 패턴

143. CloudShell로 이동합니다.
144. Pod의 리소스 사용량을 실시간으로 확인합니다:

```bash
kubectl top pods -l app=sample-app
```

> [!OUTPUT]
>
> ```
> NAME                          CPU(cores)   MEMORY(bytes)
> sample-app-xxxxx-yyyyy        50m          32Mi
> sample-app-xxxxx-zzzzz        48m          30Mi
> sample-app-xxxxx-wwwww        52m          34Mi
> ```

145. 노드의 리소스 사용량을 확인합니다:

```bash
kubectl top nodes
```

146. Pod의 리소스 제한을 확인합니다:

```bash
kubectl describe pod -l app=sample-app | grep -A 5 "Limits:"
```

147. 리소스 사용량이 제한에 가까운 경우 Deployment를 업데이트합니다:

```bash
kubectl set resources deployment sample-app \
  --limits=cpu=1000m,memory=256Mi \
  --requests=cpu=500m,memory=128Mi
```

148. 업데이트된 Pod를 확인합니다:

```bash
kubectl get pods -l app=sample-app --watch
```

> [!NOTE]
> 새로운 리소스 제한으로 Pod가 재시작됩니다. 모든 Pod가 "Running" 상태가 되면 Ctrl+C를 눌러 watch에서 나옵니다.

> [!CONCEPT] 리소스 최적화의 의미
> 이 실습에서는 리소스 제한을 증가시켰지만, 실제 프로덕션 환경에서는 애플리케이션의 실제 사용 패턴을 분석하여 적절한 값을 설정해야 합니다.
>
> nginx는 정적 콘텐츠를 제공하는 경량 웹 서버로 CPU 사용량이 매우 낮습니다. 따라서 리소스 제한을 증가시켜도 실제 사용량은 크게 변하지 않을 수 있습니다.
>
> 실제 애플리케이션에서는 다음을 고려해야 합니다:
>
> - **부하 테스트**: 실제 트래픽 패턴을 시뮬레이션하여 리소스 사용량 측정
> - **모니터링 기간**: 최소 1주일 이상의 데이터를 수집하여 패턴 분석
> - **여유 공간**: 피크 시간대를 고려하여 20-30% 여유 확보

149. Horizontal Pod Autoscaler를 생성합니다:

```bash
kubectl autoscale deployment sample-app \
  --cpu-percent=50 \
  --min=2 \
  --max=10
```

150. HPA 상태를 확인합니다:

```bash
kubectl get hpa
```

> [!OUTPUT]
>
> ```
> NAME         REFERENCE               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
> sample-app   Deployment/sample-app   25%/50%   2         10        3          30s
> ```

151. Amazon CloudWatch Container Insights로 이동합니다.
152. 5-10분 후 메트릭 변화를 확인합니다.

> [!NOTE]
> HPA는 CPU 사용률이 목표값(50%)을 초과할 때 Pod 수를 자동으로 증가시킵니다.
> nginx는 정적 콘텐츠 제공으로 CPU 사용량이 낮아 자동 스케일링이 트리거되지 않을 수 있습니다.
>
> 실제 프로덕션 환경에서는 부하 테스트 도구(Apache Bench, JMeter 등)를 사용하여 트래픽을 생성하고 HPA 동작을 확인합니다.

✅ **태스크 완료**: 성능 메트릭을 분석하고 최적화했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon EKS 클러스터를 생성하고 Container Insights를 활성화했습니다
- Amazon EKS Add-on 방식으로 Amazon CloudWatch 에이전트와 Fluent Bit을 배포했습니다
- 샘플 애플리케이션을 배포하고 LoadBalancer 서비스를 생성했습니다
- Container Insights 대시보드에서 클러스터, 노드, Pod 수준의 메트릭을 확인했습니다
- Amazon CloudWatch Logs Insights로 컨테이너 로그를 쿼리하고 분석했습니다
- 커스텀 대시보드를 생성하여 주요 메트릭을 시각화했습니다
- Amazon CloudWatch 알람을 설정하여 이상 상황을 자동으로 감지했습니다
- 리소스 제한을 조정하고 Horizontal Pod Autoscaler를 설정하여 자동 스케일링을 구현했습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 반드시 수행하여 불필요한 비용을 방지합니다.
>
> **Amazon EKS 클러스터 삭제에 10-15분이 소요**되므로, 삭제 명령어 실행 후 반드시 완료를 확인한 후 퇴실합니다.

### 방법 1: Tag Editor로 리소스 찾기 (참고)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `13-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. Amazon EKS 클러스터는 eksctl로 삭제하는 것이 권장됩니다.

### 방법 2: eksctl로 클러스터 삭제 (권장)

8. CloudShell에서 샘플 애플리케이션을 삭제합니다:

```bash
kubectl delete -f sample-app.yaml
```

> [!NOTE]
> LoadBalancer 서비스가 삭제되면서 Classic Load Balancer도 자동으로 삭제됩니다. 2-3분이 소요될 수 있습니다.

9. HPA를 삭제합니다:

```bash
kubectl delete hpa sample-app
```

10. Amazon EKS 클러스터를 삭제합니다:

```bash
eksctl delete cluster --name container-insights-cluster --region ap-northeast-2
```

> [!IMPORTANT]
> 클러스터 삭제에 10-15분이 소요됩니다. 다음 메시지가 표시될 때까지 기다립니다:
>
> ```
> [✓]  all cluster resources were deleted
> ```
>
> **eksctl delete cluster 명령어는 다음을 자동으로 삭제합니다**:
>
> - Amazon EKS 클러스터 (컨트롤 플레인)
> - 관리형 노드 그룹 (Amazon EC2 인스턴스)
> - Amazon VPC 및 네트워크 리소스 (서브넷, 라우팅 테이블, 인터넷 게이트웨이, NAT Gateway)
> - 보안 그룹
> - AWS CloudFormation 스택
>
> 삭제가 완료되지 않은 상태에서 CloudShell을 종료하면 리소스가 남아 비용이 계속 발생할 수 있습니다.

11. 삭제 완료를 확인합니다:

```bash
eksctl get cluster --name container-insights-cluster --region ap-northeast-2
```

> [!OUTPUT]
>
> ```
> No clusters found
> ```

### 방법 2: 수동 삭제

eksctl 삭제가 실패한 경우 다음 순서로 수동 삭제합니다:

12. Amazon EC2 콘솔로 이동합니다.
13. 왼쪽 메뉴에서 **Load Balancers**를 선택합니다.
14. `sample-app-service`와 연결된 Load Balancer를 선택합니다.
15. **Actions** > `Delete load balancer`를 선택합니다.
16. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

17. Amazon EKS 콘솔로 이동합니다.
18. `container-insights-cluster` 클러스터를 선택합니다.
19. [[Delete cluster]] 버튼을 클릭합니다.
20. 확인 창에서 클러스터 이름을 입력하고 [[Delete]] 버튼을 클릭합니다.
21. 클러스터 삭제가 완료될 때까지 기다립니다 (10-15분 소요).

22. Amazon VPC 콘솔로 이동합니다.
23. 왼쪽 메뉴에서 **NAT Gateways**를 선택합니다.
24. `eksctl-container-insights-cluster`로 시작하는 NAT Gateway를 선택합니다.
25. **Actions** > `Delete NAT gateway`를 선택합니다.
26. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

27. 왼쪽 메뉴에서 **Elastic IPs**를 선택합니다.
28. NAT Gateway와 연결되었던 Elastic IP를 선택합니다.
29. **Actions** > `Release Elastic IP addresses`를 선택합니다.
30. 확인 창에서 [[Release]] 버튼을 클릭합니다.

31. Amazon AWS CloudFormation 콘솔로 이동합니다.
32. `eksctl-container-insights-cluster-cluster` 스택을 선택합니다.
33. [[Delete]] 버튼을 클릭합니다.
34. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

### Amazon CloudWatch 리소스 정리

35. Amazon CloudWatch 콘솔로 이동합니다.
36. 왼쪽 메뉴에서 **Alarms** > **All alarms**를 선택합니다.
37. 생성한 3개의 알람을 선택합니다:
   - `Amazon EKS-Cluster-High-CPU`
   - `Amazon EKS-Cluster-High-Memory`
   - `Amazon EKS-Cluster-Failed-Nodes`
38. **Actions** > `Delete`를 선택합니다.
39. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

40. 왼쪽 메뉴에서 **Dashboards**를 선택합니다.
41. `Amazon EKS-Container-Insights-Dashboard`를 선택합니다.
42. [[Delete]] 버튼을 클릭합니다.
43. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

44. AWS Management Console 상단 검색창에 `SNS`을 입력하고 선택합니다.
45. 왼쪽 메뉴에서 **Topics**를 선택합니다.
46. `Amazon EKS-High-CPU-Alert` 토픽을 선택합니다.
47. [[Delete]] 버튼을 클릭합니다.
48. 확인 창에서 `delete me`를 입력합니다.
49. [[Delete]] 버튼을 클릭합니다.

50. Amazon CloudWatch 콘솔로 이동합니다.
51. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
52. 다음 로그 그룹들을 선택합니다:
    - `/aws/containerinsights/container-insights-cluster/application`
    - `/aws/containerinsights/container-insights-cluster/dataplane`
    - `/aws/containerinsights/container-insights-cluster/host`
    - `/aws/containerinsights/container-insights-cluster/performance`
    - `/aws/eks/container-insights-cluster/cluster`

> [!NOTE]
> 로그 그룹이 표시되지 않으면 이미 클러스터 삭제 시 자동으로 삭제된 것입니다.

53. **Actions** > `Delete log group(s)`를 선택합니다.
54. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!WARNING]
> Amazon CloudWatch Logs는 스토리지 비용(GB당 월 $0.50)이 부과됩니다. 로그 그룹을 삭제하지 않으면 계속 비용이 발생합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Container Insights 사용 설명서](https://docs.aws.amazon.com/ko_kr/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)
- [Amazon EKS에서 Container Insights 설정](https://docs.aws.amazon.com/ko_kr/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-EKS-quickstart.html)
- [Amazon CloudWatch Logs Insights 쿼리 문법](https://docs.aws.amazon.com/ko_kr/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- [Kubernetes 메트릭 서버](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- [Amazon EKS Add-ons](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/eks-add-ons.html)

## 📚 참고: Amazon CloudWatch Container Insights 및 Amazon EKS 모니터링

### Amazon CloudWatch Container Insights 아키텍처

Amazon CloudWatch Container Insights는 컨테이너화된 애플리케이션과 마이크로서비스의 성능 메트릭과 로그를 수집, 집계, 요약하는 완전 관리형 모니터링 솔루션입니다.

**주요 구성 요소**:

**Amazon CloudWatch 에이전트**:

- DaemonSet으로 각 노드에 배포됩니다
- 노드 수준의 메트릭을 수집합니다 (CPU, 메모리, 디스크, 네트워크)
- StatsD 및 collectd 프로토콜을 지원합니다
- 성능 로그 이벤트를 Amazon CloudWatch Logs로 전송합니다

**Fluent Bit**:

- 경량 로그 프로세서 및 포워더입니다
- 컨테이너 로그를 수집하고 파싱합니다
- 로그를 Amazon CloudWatch Logs로 스트리밍합니다
- 메모리 사용량이 적고 성능이 우수합니다

**메트릭 수집 흐름**:

```
55. Kubernetes API → 클러스터 메타데이터.
56. kubelet → Pod 및 컨테이너 메트릭.
57. cAdvisor → 컨테이너 리소스 사용량.
58. Amazon CloudWatch 에이전트 → 메트릭 집계 및 전송.
59. Amazon CloudWatch → 메트릭 저장 및 시각화.
```

### 수집되는 메트릭 유형

**클러스터 수준 메트릭**:

- `cluster_cpu_utilization`: 클러스터 전체 CPU 사용률
- `cluster_memory_utilization`: 클러스터 전체 메모리 사용률
- `cluster_number_of_running_pods`: 실행 중인 Pod 수
- `cluster_failed_node_count`: 실패한 노드 수

**노드 수준 메트릭**:

- `node_cpu_utilization`: 노드 CPU 사용률
- `node_memory_utilization`: 노드 메모리 사용률
- `node_network_total_bytes`: 네트워크 총 바이트
- `node_filesystem_utilization`: 파일시스템 사용률

**Pod 수준 메트릭**:

- `pod_cpu_utilization`: Pod CPU 사용률
- `pod_memory_utilization`: Pod 메모리 사용률
- `pod_network_rx_bytes`: 수신 네트워크 바이트
- `pod_network_tx_bytes`: 송신 네트워크 바이트

**컨테이너 수준 메트릭**:

- `container_cpu_utilization`: 컨테이너 CPU 사용률
- `container_memory_utilization`: 컨테이너 메모리 사용률
- `container_restart_count`: 컨테이너 재시작 횟수

### Amazon CloudWatch Logs Insights 쿼리 패턴

**기본 필터링**:

```
fields @timestamp, @message
| filter kubernetes.namespace_name = "default"
| sort @timestamp desc
| limit 100
```

**에러 로그 검색**:

```
fields @timestamp, kubernetes.pod_name, @message
| filter @message like /error|Error|ERROR|exception|Exception/
| sort @timestamp desc
```

**특정 시간대 로그**:

```
fields @timestamp, @message
| filter @timestamp >= "2024-02-07T10:00:00"
    and @timestamp <= "2024-02-07T11:00:00"
| sort @timestamp desc
```

**로그 집계 및 통계**:

```
fields kubernetes.pod_name
| stats count() as log_count by kubernetes.pod_name
| sort log_count desc
```

**HTTP 요청 분석**:

```
fields @timestamp, @message
| parse @message /(?<method>\w+)\s+(?<path>\/\S*)\s+HTTP\/(?<version>[\d\.]+)\s+(?<status>\d+)/
| stats count() by method, status
| sort count() desc
```

**응답 시간 분석**:

```
fields @timestamp, @message
| parse @message /duration=(?<duration>\d+)ms/
| stats avg(duration), max(duration), min(duration)
```

### 성능 최적화 전략

**리소스 제한 설정**:

```yaml
resources:
  requests:
    memory: '64Mi'
    cpu: '250m'
  limits:
    memory: '128Mi'
    cpu: '500m'
```

**Requests vs Limits**:

- **Requests**: 스케줄러가 Pod를 배치할 때 보장하는 최소 리소스
- **Limits**: Pod가 사용할 수 있는 최대 리소스
- CPU Limit 초과 시: 스로틀링 (Throttling)
- Memory Limit 초과 시: OOMKilled (Out of Memory)

**Horizontal Pod Autoscaler (HPA)**:

```bash
kubectl autoscale deployment my-app \
  --cpu-percent=50 \
  --min=2 \
  --max=10
```

**HPA 동작 원리**:

60. Metrics Server가 Pod CPU/메모리 사용률 수집.
61. HPA가 목표 사용률과 현재 사용률 비교.
62. 필요 시 Pod 수를 자동으로 증가/감소.
63. 스케일링 쿨다운 기간 적용 (기본 5분).

**Vertical Pod Autoscaler (VPA)**:

- Pod의 리소스 requests/limits를 자동으로 조정
- 과거 사용 패턴을 분석하여 최적값 제안
- HPA와 함께 사용 시 주의 필요

### 알람 설정 베스트 프랙티스

**CPU 사용률 알람**:

- **임계값**: 70-80%
- **평가 기간**: 5분 평균
- **데이터 포인트**: 2/3 (3개 중 2개 초과 시 알람)

**메모리 사용률 알람**:

- **임계값**: 80-90%
- **평가 기간**: 5분 평균
- **주의**: 메모리는 CPU보다 회복이 어려움

**Pod 재시작 알람**:

- **임계값**: 5회/시간
- **원인**: OOMKilled, CrashLoopBackOff, Liveness Probe 실패

**노드 상태 알람**:

- **임계값**: 실패한 노드 > 0
- **즉각 대응**: 노드 교체 또는 복구 필요

### 비용 최적화

**Amazon CloudWatch Logs 비용**:

- 수집: GB당 $0.50
- 저장: GB당 월 $0.03
- 쿼리: 스캔한 데이터 GB당 $0.005

**비용 절감 방법**:

64. **로그 필터링**: 불필요한 로그 수집 제외.
65. **보관 기간 설정**: 오래된 로그 자동 삭제.
66. **로그 샘플링**: 모든 로그 대신 샘플만 수집.
67. **메트릭 해상도**: 1분 대신 5분 간격 사용.

**Container Insights 비용**:

- 메트릭: 커스텀 메트릭 요금 적용
- 로그: Amazon CloudWatch Logs 요금 적용
- 대시보드: 무료 (3개까지)

### 프로덕션 환경 권장사항

**고가용성**:

- 최소 3개 노드 (다중 AZ 배포)
- Pod Disruption Budget 설정
- 노드 자동 복구 활성화

**보안**:

- IRSA (AWS IAM Roles for Service Accounts) 사용
- 네트워크 정책으로 Pod 간 통신 제한
- AWS Secrets Manager로 민감 정보 관리

**모니터링**:

- 모든 네임스페이스에 Container Insights 활성화
- 중요 메트릭에 알람 설정
- 정기적인 대시보드 검토

**로깅**:

- 구조화된 로그 형식 사용 (JSON)
- 로그 레벨 적절히 설정 (DEBUG는 개발 환경만)
- 민감 정보 로그 제외

### 문제 해결

**메트릭이 표시되지 않는 경우**:

68. Amazon CloudWatch 에이전트 Pod 상태 확인.
69. AWS IAM 역할 권한 확인.
70. 로그 그룹 생성 확인.
71. 5-10분 대기 후 재확인.

**로그가 수집되지 않는 경우**:

72. Fluent Bit Pod 상태 확인.
73. ConfigMap 설정 확인.
74. 로그 그룹 권한 확인.

**높은 CPU/메모리 사용률**:

75. 리소스 제한 증가.
76. HPA로 자동 스케일링.
77. 애플리케이션 최적화.
78. 노드 타입 업그레이드.

**Pod OOMKilled**:

79. 메모리 제한 증가.
80. 메모리 누수 확인.
81. 애플리케이션 프로파일링.
