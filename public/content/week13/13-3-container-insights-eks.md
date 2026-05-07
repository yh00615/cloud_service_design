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

> [!CONCEPT] 주요 명령어 설명
>
> - **`eksctl`**: Amazon EKS 클러스터를 생성·관리하는 CLI 도구. YAML 설정 파일로 클러스터를 선언적으로 구성합니다.
> - **`kubectl`**: Kubernetes 클러스터와 통신하는 CLI 도구. Pod, Service, Deployment 등 리소스를 관리합니다.
> - **`cat > file << 'EOF'`**: Here Document 문법. 여러 줄의 텍스트를 파일로 저장합니다. `EOF`가 나올 때까지 입력된 내용이 파일에 기록됩니다.
> - **`nohup ... &`**: 명령어를 백그라운드에서 실행합니다. 터미널 세션이 종료되어도 프로세스가 계속 실행됩니다.
> - **`tail -f`**: 파일의 마지막 부분을 실시간으로 출력합니다. 로그 모니터링에 사용합니다. **Ctrl+C**로 종료합니다.

1. AWS Management Console 상단의 AWS CloudShell 아이콘을 클릭합니다.

<img src="/images/week13/13-3-task1-step1-cloudshell.png" alt="CloudShell 아이콘 클릭" class="guide-img-sm" />

> [!NOTE]
> AWS CloudShell 초기 로딩에 30초-1분이 소요될 수 있습니다. 환경이 로드될 때까지 기다립니다.

> [!IMPORTANT]
> CloudShell 상단에 표시된 리전이 **ap-northeast-2 (Seoul)**인지 확인합니다. 다른 리전으로 설정되어 있으면 AWS 콘솔 우측 상단에서 리전을 변경한 후 CloudShell을 다시 엽니다.

2. eksctl을 설치합니다:

```bash
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz"
tar -xzf eksctl_Linux_amd64.tar.gz
sudo mv eksctl /usr/local/bin
rm eksctl_Linux_amd64.tar.gz
```

<img src="/images/week13/13-3-task1-step2-eksctl-install.png" alt="eksctl 설치 완료" class="guide-img-md" />

3. eksctl 버전을 확인합니다:

```bash
eksctl version
```

<img src="/images/week13/13-3-task1-step3-eksctl-version.png" alt="eksctl 버전 확인" class="guide-img-sm" />

4. 클러스터 설정 파일을 생성합니다:

> [!TIP]
> **AWS 프리 티어(무료 플랜)를 사용하는 경우**, 아래 설정의 `instanceType: t3.medium`은 프리 티어 대상이 아닙니다. 유료 플랜을 사용하는 경우 변경 없이 그대로 진행합니다.
> 프리 티어 사용자는 아래 코드 블록을 메모장에 복사한 후 다음 부분을 변경하고, 변경된 내용을 CloudShell에 붙여넣어 실행합니다.
>
> ```yaml
> # 변경 전
>     instanceType: t3.medium
>
> # 변경 후
>     instanceType: c7i-flex.large
> ```
>
> 프리 티어 대상 인스턴스: `t3.micro`, `t3.small`, `t4g.micro`, `t4g.small`, `c7i-flex.large`, `m7i-flex.large`
>
> 단, `t3.micro`/`t3.small`은 메모리가 작아 EKS 노드로 사용하기 어려우므로 `c7i-flex.large` (2 vCPU, 4GB 메모리)를 권장합니다.

> [!WARNING]
> Amazon EKS 컨트롤 플레인 및 관련 리소스(NAT Gateway, Load Balancer 등)는 프리 티어에 포함되지 않으며 비용이 발생할 수 있습니다. 실습 종료 후 반드시 모든 리소스를 삭제합니다.

```bash
cat > cluster-config.yaml << 'EOF'
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: container-insights-cluster
  region: ap-northeast-2
  version: "1.32"
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

<img src="/images/week13/13-3-task1-step4-config.png" alt="클러스터 설정 파일 생성" class="guide-img-md" />

> [!NOTE]
> Amazon EKS 버전 1.32를 사용합니다. 사용 가능한 최신 버전은 [Amazon EKS 문서](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)에서 확인할 수 있습니다.
> CloudWatchAgentServerPolicy를 노드 그룹에 추가하여 Amazon CloudWatch Container Insights 메트릭 수집 권한을 부여합니다.

5. 파일 내용을 확인합니다:

```bash
cat cluster-config.yaml
```

<img src="/images/week13/13-3-task1-step5-cat-config.png" alt="cluster-config.yaml 파일 내용 확인" class="guide-img-md" />

6. Amazon EKS 클러스터를 생성합니다:

```bash
nohup eksctl create cluster -f cluster-config.yaml > cluster-creation.log 2>&1 &
```

> [!NOTE]
> 클러스터 생성에 15-20분이 소요됩니다. `nohup` 명령어를 사용하여 백그라운드에서 실행하므로 AWS CloudShell 세션 타임아웃을 방지할 수 있습니다.

7. 다음 명령어로 진행 상황을 확인합니다:

```bash
tail -f cluster-creation.log
```

<img src="/images/week13/13-3-task1-step6-create-cluster.png" alt="클러스터 생성 진행 중 로그" class="guide-img-md" />

<img src="/images/week13/13-3-task1-step7-cluster-ready.png" alt="클러스터 생성 완료 로그" class="guide-img-md" />

> [!NOTE]
> **"Amazon EKS cluster "container-insights-cluster" in "ap-northeast-2" region is ready"** 메시지가 표시되면 클러스터 생성이 완료된 것입니다.  
> **Ctrl+C**를 눌러 로그 확인을 종료합니다.

8. 클러스터 상태를 확인합니다:

```bash
eksctl get cluster --name container-insights-cluster --region ap-northeast-2
```

<img src="/images/week13/13-3-task1-step8-get-cluster.png" alt="eksctl get cluster 결과" class="guide-img-lg" />

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

<img src="/images/week13/13-3-task1-step9-get-nodes.png" alt="kubectl get nodes 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```text
> NAME                                               STATUS   ROLES    AGE   VERSION
> ip-192-168-1-10.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.32.0-eks-5e0fdde
> ip-192-168-2-20.ap-northeast-2.compute.internal   Ready    <none>   5m    v1.32.0-eks-5e0fdde
> ```

✅ **태스크 완료**: Amazon EKS 클러스터가 생성되었습니다.

## 태스크 2: Amazon CloudWatch Container Insights 활성화 (Amazon EKS Add-on 방식)

이 태스크에서는 Amazon EKS Add-on 방식으로 Amazon CloudWatch Container Insights를 활성화하고 Amazon CloudWatch 에이전트를 배포합니다.

> [!CONCEPT] Amazon CloudWatch Container Insights 아키텍처
> Amazon CloudWatch Container Insights는 컨테이너화된 애플리케이션의 성능 메트릭과 로그를 자동으로 수집하는 완전 관리형 모니터링 솔루션입니다.
>
> **주요 구성 요소**:
>
> - **Amazon CloudWatch 에이전트**: DaemonSet으로 각 노드에 배포되어 노드 수준 메트릭(CPU, 메모리, 디스크, 네트워크)을 수집합니다.
> - **Fluent Bit**: 경량 로그 프로세서로 컨테이너 로그를 수집하고 Amazon CloudWatch Logs로 스트리밍합니다.
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

<img src="/images/week13/13-3-task2-step10-addon.png" alt="EKS Add-on Container Insights 활성화" class="guide-img-md" />

11. Add-on 설치 상태를 확인합니다:

```bash
aws eks describe-addon \
  --cluster-name container-insights-cluster \
  --addon-name amazon-cloudwatch-observability \
  --region ap-northeast-2 \
  --query 'addon.status' \
  --output text
```

<img src="/images/week13/13-3-task2-step11-addon-status.png" alt="Add-on 상태 확인 - ACTIVE" class="guide-img-md" />

> [!NOTE]
> Add-on 설치에 2-3분이 소요됩니다. 상태가 "**ACTIVE**"로 변경될 때까지 기다립니다.
>
> 다음 명령어로 상태를 반복 확인합니다:
>
> ```bash
> watch -n 10 'aws eks describe-addon --cluster-name container-insights-cluster --addon-name amazon-cloudwatch-observability --region ap-northeast-2 --query "addon.status" --output text'
> ```
>
> **Ctrl+C**를 눌러 watch 모드를 종료합니다.

12. 배포된 Pod 상태를 확인합니다:

```bash
kubectl get pods -n amazon-cloudwatch
```

<img src="/images/week13/13-3-task2-step12-pods.png" alt="kubectl get pods - CloudWatch 에이전트 Pod 확인" class="guide-img-md" />

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

> [!NOTE]
> 모든 Pod가 **Running** 상태가 될 때까지 기다립니다. Pod 시작에 1-2분이 소요될 수 있습니다. 다음 명령어로 상태를 확인합니다:
>
> ```bash
> kubectl get pods -n amazon-cloudwatch --watch
> ```
>
> **Ctrl+C**를 눌러 watch 모드를 종료합니다.

✅ **태스크 완료**: Amazon CloudWatch Container Insights가 활성화되었습니다.

## 태스크 3: 샘플 애플리케이션 배포

이 태스크에서는 모니터링할 샘플 애플리케이션을 배포합니다.

13. 샘플 애플리케이션 Deployment를 생성합니다:

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
        image: nginx:1.28
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

14. 애플리케이션을 배포합니다:

```bash
kubectl apply -f sample-app.yaml
```

<img src="/images/week13/13-3-task3-step14-deploy.png" alt="kubectl apply 배포 결과" class="guide-img-md" />

15. 배포 상태를 확인합니다:

```bash
kubectl get deployments
```

<img src="/images/week13/13-3-task3-step15-service.png" alt="kubectl get deployments 결과" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> NAME         READY   UP-TO-DATE   AVAILABLE   AGE
> sample-app   3/3     3            3           21s
> ```

16. Pod 상태를 확인합니다:

```bash
kubectl get pods -l app=sample-app
```

<img src="/images/week13/13-3-task3-step16-service-lb.png" alt="Pod 상태 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> NAME                          READY   STATUS    RESTARTS   AGE
> sample-app-6b58d5fddf-4982m   1/1     Running   0          32s
> sample-app-6b58d5fddf-7jvtv   1/1     Running   0          32s
> sample-app-6b58d5fddf-b41dq   1/1     Running   0          32s
> ```

17. Service 정보를 확인합니다:

```bash
kubectl get service sample-app-service
```

<img src="/images/week13/13-3-task3-step17-service-info.png" alt="kubectl get service - LoadBalancer External IP 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> NAME                 TYPE           CLUSTER-IP      EXTERNAL-IP                                                                   PORT(S)        AGE
> sample-app-service   LoadBalancer   10.100.61.112   af9b560215ff6485daeb3c021c07a9d0-4758011.ap-northeast-2.elb.amazonaws.com   80:31757/TCP   43s
> ```

> [!NOTE]
> EXTERNAL-IP가 `<pending>`으로 표시되는 경우, LoadBalancer 생성에 2-3분이 소요됩니다. 다음 명령어로 할당을 대기합니다:
>
> ```bash
> kubectl get service sample-app-service --watch
> ```
>
> EXTERNAL-IP가 실제 주소로 변경되면 **Ctrl+C**를 눌러 종료합니다.

> [!WARNING]
> Load Balancer는 시간 단위로 비용이 발생합니다. 실습 종료 후 반드시 삭제합니다.

18. External IP를 메모장에 복사합니다.

19. 웹 브라우저에서 External IP로 접속하여 nginx 기본 페이지를 확인합니다.

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

20. AWS Management Console에서 상단 검색창에 `CloudWatch`를 입력한 후 선택합니다.
21. 왼쪽 메뉴에서 **Infrastructure Monitoring** > **Container Insights**를 선택합니다.
22. 우측 상단의 [[View performance dashboards]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task4-step22-container-insights.png" alt="Container Insights - View performance dashboards" class="guide-img-md" />

23. 상단의 드롭다운에서 `Service: EKS`를 선택합니다.

24. 왼쪽 **Performance dashboard views**에서 `Clusters`가 선택되어 있는지 확인합니다.
25. 아래 **Filters** 섹션의 **Cluster** 드롭다운에서 `container-insights-cluster`를 선택합니다.

    <img src="/images/week13/13-3-task4-step25-cluster-filter.png" alt="Cluster 필터 선택" class="guide-img-md" />

26. 대시보드를 스크롤하며 다음 섹션들을 확인합니다:
    - **Cluster summary**: Nodes status, Container restarts, Node CPU utilization, Node memory utilization 등
    - **Pods performance and status**: Pod CPU/Memory utilization over pod/node limit 등
    - **Nodes performance**: Node CPU/Memory utilization, Filesystem utilization, Node network total bytes 등
    - **Nodes status and capacity**: Number of ready nodes, Nodes error condition 등
    - **Control plane**: API server requests, REST client requests, ETCD request duration 등
    - **Resources**: 클러스터 내 리소스 목록 (Name, Type, Alarm state, Max CPU%, Max Memory%)

    <img src="/images/week13/13-3-task4-step26-dashboard1.png" alt="Clusters 대시보드 - Cluster summary, Pods performance" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step26-dashboard2.png" alt="Clusters 대시보드 - Nodes performance, Nodes status" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step26-dashboard3.png" alt="Clusters 대시보드 - Control plane, Resources" class="guide-img-md" />

> [!NOTE]
> 메트릭이 표시되기까지 5-10분이 소요될 수 있습니다. 페이지를 새로고침하여 최신 데이터를 확인합니다.

27. **Performance dashboard views**에서 `Nodes`를 선택합니다.
28. 대시보드에서 다음 섹션들을 확인합니다:
    - **Nodes summary**: Node status, Pods per node, CPU utilization, Memory utilization 등
    - **Performance metrics**: CPU utilization, Memory utilization, Disk utilization, Network utilization (노드별 비교) 등
    - **Node status metrics**: Number of running pods, Number of containers, Node status condition (disk pressure, memory pressure, ready, Pid pressure) 등
    - **Pods capacity / Allocatable pods**
    - **Resources Performance** 탭: Pod performance 목록 (Pod Name, Namespace, Max CPU%, Max Memory%)

    <img src="/images/week13/13-3-task4-step28-nodes1.png" alt="Nodes 대시보드 - Summary, Performance metrics" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step28-nodes2.png" alt="Nodes 대시보드 - Node status metrics" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step28-nodes3.png" alt="Nodes 대시보드 - Pods capacity, Resources Performance" class="guide-img-md" />

29. **Filters** 섹션의 **Node** 드롭다운에서 개별 노드를 선택하여 특정 노드의 메트릭을 필터링할 수 있습니다.
30. **Performance dashboard views**에서 `Pods`를 선택합니다.
31. **Filters** 섹션에서 **Pod** 드롭다운을 클릭하고 `sample-app`으로 시작하는 Pod 하나를 선택합니다.

> [!TIP]
> Namespace → Workload → Pod 순서로 필터링할 수도 있고, Pod 드롭다운에서 직접 선택해도 됩니다.

32. Pod 수준의 상세 메트릭을 확인합니다:
    - **Pods summary**: Number of containers, Number of running containers, Pod CPU utilization, Pod memory utilization 등
    - **Performance metrics**: Pod CPU utilization, Pod CPU utilization over pod limit, Pod memory utilization, Pod memory utilization over pod limit 등
    - **Pod status metrics**: Number of running containers, Number of container restarts, Pod container status (running, terminated, waiting) 등
    - **Resources Performance** 탭: Container performance (Container Name, Pod Name, Namespace, Node, Max CPU%, Max Memory%)

    <img src="/images/week13/13-3-task4-step32-pods1.png" alt="Pods 대시보드 - Summary, Performance metrics" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step32-pods2.png" alt="Pods 대시보드 - Pod status metrics" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step32-pods3.png" alt="Pods 대시보드 - Resources Performance 탭" class="guide-img-md" />

33. **Performance dashboard views**에서 `Namespaces`를 선택합니다.
34. **Filters** 섹션의 **Namespace** 드롭다운에서 `default`를 선택합니다.
35. 네임스페이스 수준의 리소스 사용량을 확인합니다:
    - **Namespaces summary**: Number of running pods, Pod CPU utilization, Pod memory utilization, Pod network bytes 등
    - **Performance metrics**: Pod CPU utilization, Pod memory utilization, Number of pods, Pod CPU/Memory utilization over pod limit, Network 등
    - **Resources Performance** 탭: Pod performance (Pod Name, Namespace, Max CPU%, Max Memory%)

    <img src="/images/week13/13-3-task4-step35-namespaces1.png" alt="Namespaces 대시보드 - Summary, Performance metrics" class="guide-img-md" />

    <img src="/images/week13/13-3-task4-step35-namespaces2.png" alt="Namespaces 대시보드 - Resources Performance 탭" class="guide-img-md" />

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

36. Amazon CloudWatch 콘솔로 이동합니다.
37. 왼쪽 메뉴에서 **Logs** > **Logs Insights**를 선택합니다.
38. **Select log group(s)** 드롭다운을 클릭합니다.
39. 다음 로그 그룹들을 선택합니다:
    - `/aws/containerinsights/container-insights-cluster/application`
    - `/aws/containerinsights/container-insights-cluster/dataplane`
    - `/aws/containerinsights/container-insights-cluster/host`
    - `/aws/containerinsights/container-insights-cluster/performance`
    - `/aws/eks/container-insights-cluster/cluster`

    <img src="/images/week13/13-3-task5-step39-log-groups.png" alt="Logs Insights - 로그 그룹 선택" class="guide-img-md" />

> [!NOTE]
> 로그 그룹이 모두 표시되지 않을 수 있습니다. 실습에서는 `application` 로그 그룹만 선택해도 충분합니다.

40. 쿼리 에디터에 다음 쿼리를 입력합니다:

```text
fields @timestamp, @message
| filter kubernetes.namespace_name = "default"
| filter kubernetes.pod_name like /sample-app/
| sort @timestamp desc
| limit 20
```

> [!NOTE]
> **쿼리 설명**: `default` 네임스페이스에서 `sample-app` Pod의 로그를 최신순으로 20건 조회합니다.
> `fields`는 표시할 컬럼, `filter`는 조건, `sort`는 정렬, `limit`는 결과 수를 제한합니다.

41. 시간 범위를 `Last 1 hour`로 설정합니다.
42. [[Run query]] 버튼을 클릭합니다.
43. 쿼리 결과에서 sample-app Pod의 로그를 확인합니다.

    <img src="/images/week13/13-3-task5-step43-query-result.png" alt="Logs Insights 쿼리 결과" class="guide-img-md" />

    <img src="/images/week13/13-3-task5-step43-query-result2.png" alt="Logs Insights 쿼리 결과 상세" class="guide-img-md" />

> [!NOTE]
> 로그가 표시되지 않으면 시간 범위를 `Last 3 hours`로 확장한 후 페이지를 새로고침합니다.

44. 다음 쿼리로 에러 로그만 필터링합니다:

```text
fields @timestamp, @message, kubernetes.pod_name
| filter kubernetes.namespace_name = "default"
| filter @message like /error|Error|ERROR/
| sort @timestamp desc
| limit 50
```

> [!NOTE]
> **쿼리 설명**: 로그 메시지에 `error`, `Error`, `ERROR` 중 하나라도 포함된 로그만 필터링합니다. 정규식(`/.../ `)으로 대소문자 변형을 모두 검색합니다.

45. [[Run query]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task5-step45-error-query.png" alt="에러 로그 필터링 쿼리 결과" class="guide-img-md" />

46. Pod별 로그 개수를 집계하는 쿼리를 실행합니다:

```text
fields kubernetes.pod_name
| filter kubernetes.namespace_name = "default"
| stats count() as log_count by kubernetes.pod_name
| sort log_count desc
```

> [!NOTE]
> **쿼리 설명**: `stats count() ... by`로 Pod별 로그 발생 건수를 집계합니다. 로그가 많은 Pod를 빠르게 식별할 수 있습니다.

47. [[Run query]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task5-step47-stats-query.png" alt="Pod별 로그 집계 쿼리 결과" class="guide-img-md" />

48. 결과를 **Visualization** 탭에서 확인합니다.
49. **Bar** 차트를 선택하여 시각화합니다.

    <img src="/images/week13/13-3-task5-step49-bar-chart.png" alt="Bar 차트 시각화" class="guide-img-md" />

    <img src="/images/week13/13-3-task5-step49-bar-chart2.png" alt="Bar 차트 시각화 상세" class="guide-img-md" />

50. HTTP 요청 로그를 분석하는 쿼리를 실행합니다:

```text
fields @timestamp, @message
| filter kubernetes.namespace_name = "default"
| filter @message like /GET|POST|PUT|DELETE/
| parse @message /(?<method>\w+)\s+(?<path>\/\S*)\s+HTTP/
| stats count() as req_count by method, path
| sort req_count desc
```

51. [[Run query]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task5-step51-http-query.png" alt="HTTP 요청 로그 분석 쿼리 결과" class="guide-img-md" />

52. HTTP 메서드별 요청 수를 확인합니다.

53. 쿼리를 저장하려면 [[Save]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task5-step53-save-query.png" alt="쿼리 저장" class="guide-img-sm" />

54. **Query name**에 `Sample App HTTP Requests`를 입력합니다.
55. [[Save]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task5-step55-save1.png" alt="쿼리 저장 설정" class="guide-img-md" />

    <img src="/images/week13/13-3-task5-step55-save2.png" alt="쿼리 저장 완료" class="guide-img-md" />

> [!NOTE]
> 저장된 쿼리는 Logs Insights 쿼리 에디터 하단의 **Saved and sample queries** 탭에서 찾을 수 있습니다.
> 저장된 쿼리를 클릭하면 쿼리 텍스트와 로그 그룹이 자동으로 로드되어 바로 실행할 수 있습니다.
> **Update saved query** 버튼으로 수정하거나, **Schedule query**로 정기 실행을 설정할 수도 있습니다.

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

56. Amazon CloudWatch 콘솔로 이동합니다.
57. 왼쪽 메뉴에서 **Dashboards**를 선택합니다.
58. [[Create dashboard]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step58-dashboards.png" alt="CloudWatch Dashboards 페이지" class="guide-img-md" />

59. **Create new dashboard** 모달 창에서 **Dashboard name**에 `EKS_Container_Insights_Dashboard`를 입력합니다.
60. [[Create dashboard]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step59-create-dashboard.png" alt="Create new dashboard 모달 - 이름 입력" class="guide-img-sm" />

61. 대시보드 우측 상단의 [[+]] 버튼을 클릭합니다. Add widget 다이얼로그가 표시됩니다.

### 위젯 1: 클러스터 CPU/메모리 사용률 (Line)

62. Add widget 다이얼로그에서 **Data sources types**는 `Cloudwatch`를 선택합니다.
63. **Data type**에서 `Metrics`를 선택합니다.
64. **Widget type**에서 `Line`을 선택합니다.
65. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step64-add-widget.png" alt="Add widget - Data type, Widget type 선택" class="guide-img-md" />

66. **Browse** 탭에서 **ContainerInsights** > **ClusterName**을 선택합니다.

    <img src="/images/week13/13-3-task6-step66-browse-metrics.png" alt="Browse - ContainerInsights > ClusterName 선택" class="guide-img-md" />

67. 검색창에 `cpu`를 입력하고 `node_cpu_utilization` 메트릭을 체크합니다.

    <img src="/images/week13/13-3-task6-step67-cpu-metric.png" alt="node_cpu_utilization 메트릭 선택" class="guide-img-md" />

68. 검색창을 지우고 `memory`를 입력하여 `node_memory_utilization` 메트릭을 체크합니다.

    <img src="/images/week13/13-3-task6-step68-memory-metric.png" alt="node_memory_utilization 메트릭 선택" class="guide-img-md" />

69. **Graphed metrics** 탭을 선택합니다.
70. 우측 상단의 **Statistic** 드롭다운이 `Average`, **Period** 드롭다운이 `5 minutes`로 설정되어 있는지 확인합니다. 다른 값이면 변경합니다.

    <img src="/images/week13/13-3-task6-step70-graphed-metrics.png" alt="Graphed metrics - Statistic, Period 설정" class="guide-img-md" />

71. 불필요한 메트릭은 체크 해제하고 원하는 메트릭만 남깁니다.
72. [[Create widget]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step72-widget1-create.png" alt="위젯 1 - Create widget 완료" class="guide-img-md" />

### 위젯 2: 실행 중인 Pod 수 (Number)

73. 대시보드 상단의 [[+]] 버튼을 클릭하여 위젯을 추가합니다.
74. **Data type**에서 `Metrics`를 선택합니다.
75. **Widget type**에서 `Number`를 선택합니다.
76. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step76-widget2-next.png" alt="위젯 2 - Number 타입 선택 후 Next" class="guide-img-md" />

77. **ContainerInsights** > **ClusterName**을 선택합니다.

78. `cluster_number_of_running_pods` 메트릭을 선택합니다.
79. [[Create widget]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step79-widget2-create.png" alt="위젯 2 - Create widget 완료" class="guide-img-md" />

### 위젯 3: 네임스페이스별 Pod 수 (Line)

80. [[+]] 버튼을 클릭하여 위젯을 추가합니다.

    <img src="/images/week13/13-3-task6-step80-widget3-add.png" alt="위젯 3 - Add widget" class="guide-img-md" />

81. **Data type**에서 `Metrics`, **Widget type**에서 `Line`을 선택합니다.
82. [[Next]] 버튼을 클릭합니다.

83. **ContainerInsights** > **ClusterName, Namespace**를 선택합니다.
84. `namespace_number_of_running_pods` 메트릭에서 **default** 네임스페이스를 선택합니다.
85. [[Create widget]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step85-widget3-create.png" alt="위젯 3 - Create widget 완료" class="guide-img-md" />

### 위젯 4: 컨테이너 로그 (Logs table)

86. [[+]] 버튼을 클릭하여 위젯을 추가합니다.
87. **Data type**에서 `Logs`를 선택합니다.
88. **Widget type**에서 `Logs table`을 선택합니다.
89. [[Next]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step82-widget3-next.png" alt="위젯 4 - Logs table 선택 후 Next" class="guide-img-md" />

90. **Log groups**에서 `/aws/containerinsights/container-insights-cluster/application`을 선택합니다.

91. 다음 쿼리를 입력합니다:

```text
fields @timestamp, kubernetes.pod_name, @message
| filter kubernetes.namespace_name = "default"
| sort @timestamp desc
| limit 10
```

92. [[Create widget]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step92-widget4-create.png" alt="위젯 4 - Create widget 완료" class="guide-img-md" />

### 대시보드 저장

93. 위젯들을 드래그하여 원하는 레이아웃으로 배치합니다.
94. [[Save]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task6-step94-save-dashboard.png" alt="대시보드 저장 완료" class="guide-img-md" />

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

95. Amazon CloudWatch 콘솔로 이동합니다.
96. 왼쪽 메뉴에서 **Alarms**를 선택합니다.
97. [[Create alarm]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task7-step97-create-alarm.png" alt="Create alarm 버튼" class="guide-img-md" />

98. [[Select metric]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-task7-step98-select-metric.png" alt="Select metric 버튼" class="guide-img-md" />

99. **ContainerInsights** 네임스페이스를 선택합니다.
100. **ClusterName** 차원을 선택합니다.
101. 검색창에 `cpu`를 입력하고 `node_cpu_utilization` 메트릭을 찾아 체크합니다.
102. [[Select metric]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step102-metric-selected.png" alt="메트릭 선택 완료" class="guide-img-md" />

103. **Metric** 섹션에서 다음을 설정합니다:
     - **Statistic**: `Average`
     - **Period**: `5 minutes`
104. **Conditions** 섹션에서 **Threshold type**을 `Static`, **Whenever...**를 `Greater`, **than...**을 `70`으로 설정합니다.
105. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step105-conditions.png" alt="Conditions 설정 및 Next" class="guide-img-md" />

106. **Notification** 섹션에서 다음을 설정합니다:
     - **Alarm state trigger**: `In alarm`
     - **Select an Amazon SNS topic**: `Create new topic`
     - **Create a new topic...**: `EKS_High_CPU_Alert`
     - **Email endpoints that will receive the notification**: 본인의 이메일 주소 입력

> [!NOTE]
> Amazon SNS 토픽 이름에 공백을 사용하지 않는 것이 권장됩니다. ARN 참조 시 문제를 방지할 수 있습니다.

107. [[Create topic]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step107-create-topic.png" alt="Create topic 버튼 클릭" class="guide-img-md" />

> [!NOTE]
> 입력한 이메일 주소로 확인 메일이 발송됩니다. 이메일을 열고 **Confirm subscription** 링크를 클릭하여 구독을 확인합니다.

108. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step108-next.png" alt="Notification 설정 후 Next" class="guide-img-md" />

109. **Alarm name**에 `EKS_Cluster_High_CPU`를 입력합니다.
110. **Alarm description**에 `Alert when Amazon EKS cluster CPU utilization exceeds 70%`를 입력합니다.
111. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `13-3`    |
| `CreatedBy` | `Student` |

112. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step112-alarm-name.png" alt="Alarm name, Tags 설정 후 Next" class="guide-img-md" />

113. 설정을 검토합니다.

114. [[Create alarm]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step114-create-alarm-done.png" alt="첫 번째 알람 생성 완료" class="guide-img-md" />

     <img src="/images/week13/13-3-task7-step114-create-alarm-done2.png" alt="첫 번째 알람 생성 확인" class="guide-img-md" />

115. 두 번째 알람을 생성하기 위해 [[Create alarm]] 버튼을 다시 클릭합니다.

116. [[Select metric]] 버튼을 클릭합니다.
117. **ContainerInsights** > **ClusterName**을 선택합니다.
118. 검색창에 `memory`를 입력하고 `node_memory_utilization` 메트릭을 선택합니다.
119. [[Select metric]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step119-memory-metric.png" alt="Memory 메트릭 선택" class="guide-img-md" />

120. **Conditions** 섹션에서 **Threshold type**을 `Static`, **Whenever...**를 `Greater`, **than...**을 `80`으로 설정합니다.

121. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step121-conditions2.png" alt="두 번째 알람 Conditions 설정" class="guide-img-md" />

122. **Select an Amazon SNS topic**에서 `EKS_High_CPU_Alert`를 선택합니다.
123. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step123-notification2.png" alt="두 번째 알람 Notification 설정" class="guide-img-md" />

124. **Alarm name**에 `EKS_Cluster_High_Memory`를 입력합니다.

125. **Alarm description**에 `Alert when Amazon EKS cluster memory utilization exceeds 80%`를 입력합니다.
126. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `13-3`    |
| `CreatedBy` | `Student` |

127. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step127-alarm2-name.png" alt="두 번째 알람 이름 및 태그 설정" class="guide-img-md" />

128. [[Create alarm]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step128-alarm2-create.png" alt="두 번째 알람 생성 완료" class="guide-img-md" />

129. 세 번째 알람을 생성하기 위해 [[Create alarm]] 버튼을 다시 클릭합니다.
130. [[Select metric]] 버튼을 클릭합니다.
131. **ContainerInsights** > **ClusterName**을 선택합니다.
132. `cluster_failed_node_count` 메트릭을 선택합니다.
133. [[Select metric]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step133-failed-node.png" alt="세 번째 알람 - failed_node_count 메트릭 선택" class="guide-img-md" />

134. **Conditions** 섹션에서 **Threshold type**을 `Static`, **Whenever...**를 `Greater`, **than...**을 `0`으로 설정합니다.
135. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step135-conditions3.png" alt="세 번째 알람 Conditions 설정" class="guide-img-md" />

136. **Select an Amazon SNS topic**에서 `EKS_High_CPU_Alert`를 선택합니다.
137. [[Next]] 버튼을 클릭합니다.
138. **Alarm name**에 `EKS_Cluster_Failed_Nodes`를 입력합니다.
139. **Alarm description**에 `Alert when any node in the cluster fails`를 입력합니다.
140. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `13-3`    |
| `CreatedBy` | `Student` |

141. [[Next]] 버튼을 클릭합니다.

     <img src="/images/week13/13-3-task7-step141-alarm3-name.png" alt="세 번째 알람 이름 및 태그 설정" class="guide-img-md" />

142. [[Create alarm]] 버튼을 클릭합니다.

143. **Alarms** 페이지에서 생성된 3개의 알람을 확인합니다.

     <img src="/images/week13/13-3-task7-step143-alarms-list.png" alt="3개 알람 생성 확인" class="guide-img-md" />

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

### metrics-server 설치 및 리소스 확인

144. CloudShell에서 metrics-server를 설치합니다:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

<img src="/images/week13/13-3-task8-step144-metrics-install.png" alt="metrics-server 설치" class="guide-img-md" />

> [!NOTE]
> `kubectl top` 명령어는 metrics-server가 필요합니다. EKS에는 기본 설치되어 있지 않으므로 직접 설치해야 합니다.
> 설치 후 1-2분 대기하면 메트릭 수집이 시작됩니다.

145. metrics-server가 정상 동작하는지 확인합니다:

```bash
kubectl get deployment metrics-server -n kube-system
```

<img src="/images/week13/13-3-task8-step145-metrics-server.png" alt="metrics-server 정상 동작 확인" class="guide-img-md" />

146. Pod의 리소스 사용량을 확인합니다:

```bash
kubectl top pods -l app=sample-app
```

<img src="/images/week13/13-3-task8-step146-top-pods.png" alt="kubectl top pods 결과" class="guide-img-md" />

147. 노드의 리소스 사용량을 확인합니다:

```bash
kubectl top nodes
```

<img src="/images/week13/13-3-task8-step147-top-nodes.png" alt="kubectl top nodes 결과" class="guide-img-md" />

### 리소스 제한 설정

148. Pod의 현재 리소스 제한을 확인합니다:

```bash
kubectl describe pod -l app=sample-app | grep -A 5 "Limits:"
```

<img src="/images/week13/13-3-task8-step148-describe-limits.png" alt="Pod 리소스 제한 확인" class="guide-img-md" />

149. Deployment에 리소스 제한을 설정합니다:

> [!NOTE]
> 아래 명령어로 CPU requests를 500m(0.5 코어), limits를 1000m(1 코어), 메모리 requests를 128Mi, limits를 256Mi로 설정합니다.

```bash
kubectl set resources deployment sample-app \
  --limits=cpu=1000m,memory=256Mi \
  --requests=cpu=500m,memory=128Mi
```

150. 업데이트된 Pod를 확인합니다:

```bash
kubectl get pods -l app=sample-app --watch
```

<img src="/images/week13/13-3-task8-step150-watch1.png" alt="Pod 재시작 진행 중" class="guide-img-md" />

<img src="/images/week13/13-3-task8-step150-watch2.png" alt="Pod 재시작 완료" class="guide-img-md" />

> [!NOTE]
> 새로운 리소스 제한으로 Pod가 재시작됩니다. 모든 Pod가 **Running** 상태가 되면 **Ctrl+C**를 눌러 watch에서 나옵니다.

### HPA (Horizontal Pod Autoscaler) 설정

151. Horizontal Pod Autoscaler를 생성합니다:

> [!NOTE]
> **HPA 파라미터 설명**:
>
> - `--cpu-percent=50`: 전체 Pod의 평균 CPU 사용률이 50%를 초과하면 스케일 아웃
> - `--min=2`: 최소 Pod 수 (트래픽이 적어도 2개 유지)
> - `--max=10`: 최대 Pod 수 (과도한 스케일 아웃 방지)

```bash
kubectl autoscale deployment sample-app \
  --cpu-percent=50 \
  --min=2 \
  --max=10
```

<img src="/images/week13/13-3-task8-step151-hpa-create.png" alt="HPA 생성" class="guide-img-md" />

152. HPA 상태를 확인합니다:

```bash
kubectl get hpa
```

<img src="/images/week13/13-3-task8-step152-hpa-status1.png" alt="HPA 상태 - unknown" class="guide-img-md" />

<img src="/images/week13/13-3-task8-step152-hpa-status2.png" alt="HPA 상태 - 0%/50%" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> NAME         REFERENCE               TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
> sample-app   Deployment/sample-app   0%/50%    2         10        3          30s
> ```

### 부하 테스트로 HPA 동작 확인

153. 부하 생성 Pod를 실행합니다:

```bash
kubectl run load-generator --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://sample-app-service > /dev/null; done"
```

<img src="/images/week13/13-3-task8-step153-load-generator.png" alt="부하 생성 Pod 실행" class="guide-img-md" />

154. HPA 상태를 실시간으로 모니터링합니다:

```bash
kubectl get hpa --watch
```

<img src="/images/week13/13-3-task8-step154-hpa-watch.png" alt="HPA watch - CPU 변화 모니터링" class="guide-img-md" />

> [!NOTE]
> 1-2분 후 CPU 사용률이 소폭 상승하는 것을 확인할 수 있습니다.
> nginx 특성상 50% 임계값까지 도달하지 않아 스케일 아웃은 트리거되지 않을 수 있지만, CPU 변화를 관찰하는 것이 목적입니다.
> **Ctrl+C**로 watch를 종료합니다.

155. 부하 생성 Pod를 삭제합니다:

```bash
kubectl delete pod load-generator
```

<img src="/images/week13/13-3-task8-step155-delete-load.png" alt="부하 생성 Pod 삭제" class="guide-img-md" />

### Container Insights에서 변화 확인

156. Amazon CloudWatch 콘솔에서 **Infrastructure Monitoring** > **Container Insights**를 선택합니다.
157. 우측 상단의 [[View performance dashboards]] 버튼을 클릭합니다.
158. **Performance dashboard views**에서 `Pods`를 선택합니다.
159. **Filters** 섹션의 **Pod** 드롭다운에서 `sample-app`으로 시작하는 Pod 하나를 선택합니다.

     <img src="/images/week13/13-3-task8-step159-pod-filter.png" alt="Pod 필터 선택" class="guide-img-md" />

160. Pod CPU utilization 그래프에서 부하 생성 시점의 스파이크와 정상 복귀를 확인합니다.

     <img src="/images/week13/13-3-task8-step160-cpu-before.png" alt="부하 생성 중 CPU 스파이크" class="guide-img-md" />

     <img src="/images/week13/13-3-task8-step160-cpu-after.png" alt="부하 제거 후 CPU 정상 복귀" class="guide-img-md" />

> [!NOTE]
> 실제 CPU 집약적 애플리케이션(API 서버, 데이터 처리 등)에서는 부하 증가 시 HPA가 자동으로 Pod를 증가시킵니다.
> 이 실습에서는 nginx의 경량 특성으로 인해 스케일 아웃이 트리거되지 않지만, HPA 설정과 모니터링 방법을 학습하는 것이 핵심입니다.

> [!CONCEPT] 리소스 최적화의 의미
> 이 실습에서는 리소스 제한을 설정하고 HPA를 구성했지만, 실제 프로덕션 환경에서는 애플리케이션의 실제 사용 패턴을 분석하여 적절한 값을 설정해야 합니다.
>
> 실제 애플리케이션에서는 다음을 고려해야 합니다:
>
> - **부하 테스트**: 실제 트래픽 패턴을 시뮬레이션하여 리소스 사용량 측정
> - **모니터링 기간**: 최소 1주일 이상의 데이터를 수집하여 패턴 분석
> - **여유 공간**: 피크 시간대를 고려하여 20-30% 여유 확보

✅ **태스크 완료**: 성능 메트릭을 분석하고 최적화했습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon EKS 클러스터를 생성하고 Container Insights를 활성화했습니다.
- Amazon EKS Add-on 방식으로 Amazon CloudWatch 에이전트와 Fluent Bit을 배포했습니다.
- 샘플 애플리케이션을 배포하고 LoadBalancer 서비스를 생성했습니다.
- Container Insights 대시보드에서 클러스터, 노드, Pod 수준의 메트릭을 확인했습니다.
- Amazon CloudWatch Logs Insights로 컨테이너 로그를 쿼리하고 분석했습니다.
- 커스텀 대시보드를 생성하여 주요 메트릭을 시각화했습니다.
- Amazon CloudWatch 알람을 설정하여 이상 상황을 자동으로 감지했습니다.
- 리소스 제한을 조정하고 Horizontal Pod Autoscaler를 설정하여 자동 스케일링을 구현했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 반드시 수행하여 불필요한 비용을 방지합니다.
>
> **Amazon EKS 클러스터 삭제에 10-15분이 소요**되므로, 삭제 명령어 실행 후 반드시 완료를 확인한 후 퇴실합니다.

### Tag Editor로 리소스 찾기 (참고)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `13-3`
6. [[Search resources]] 버튼을 클릭합니다.

<img src="/images/week13/13-3-cleanup-step6-tageditor.png" alt="Tag Editor 검색 결과" class="guide-img-md" />

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. Amazon EKS 클러스터는 eksctl로 삭제하는 것이 권장됩니다.

### 단계 1: Amazon EKS 클러스터 및 리소스 삭제

#### 옵션 1: eksctl로 클러스터 삭제 (권장)

> [!TIP]
> eksctl CLI에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. CloudShell에서 샘플 애플리케이션을 삭제합니다:

```bash
kubectl delete -f sample-app.yaml
```

<img src="/images/week13/13-3-cleanup-step7-delete-app.png" alt="샘플 앱 삭제" class="guide-img-md" />

> [!NOTE]
> LoadBalancer 서비스가 삭제되면서 Classic Load Balancer도 자동으로 삭제됩니다. 2-3분이 소요될 수 있습니다.

8. HPA를 삭제합니다:

```bash
kubectl delete hpa sample-app
```

<img src="/images/week13/13-3-cleanup-step8-delete-cluster.png" alt="HPA 삭제" class="guide-img-md" />

9. Amazon EKS 클러스터를 삭제합니다:

> [!TIP]
> CloudShell 세션이 만료되어 eksctl 명령어가 없는 경우, 다음 명령어로 다시 설치합니다:
>
> ```bash
> curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz"
> tar -xzf eksctl_Linux_amd64.tar.gz
> sudo mv eksctl /usr/local/bin
> rm eksctl_Linux_amd64.tar.gz
> ```
>
> <img src="/images/week13/13-3-cleanup-step9-tip-eksctl.png" alt="eksctl 재설치" class="guide-img-md" />

```bash
eksctl delete cluster --name container-insights-cluster --region ap-northeast-2
```

<img src="/images/week13/13-3-cleanup-step9-delete-cluster.png" alt="eksctl delete cluster 실행" class="guide-img-md" />

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

10. 삭제 완료를 확인합니다:

```bash
eksctl get cluster --name container-insights-cluster --region ap-northeast-2
```

<img src="/images/week13/13-3-cleanup-step10-cluster-deleted.png" alt="클러스터 삭제 완료 확인" class="guide-img-md" />

> [!OUTPUT]
>
> ```
> No clusters found
> ```

#### 옵션 2: 수동 삭제 (또는 옵션 1 삭제 확인 참고용)

> [!TIP]
> AWS 콘솔 방식을 선호하거나 eksctl 삭제가 실패한 경우 이 방법을 사용합니다.
> eksctl로 정상 삭제된 경우에도 리소스가 남아있지 않은지 확인하는 용도로 검토하는 것을 권장합니다.
>
> eksctl CLI에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

11. Amazon EC2 콘솔로 이동합니다.
12. 왼쪽 메뉴에서 **Load Balancers**를 선택합니다.
13. `sample-app-service`와 연결된 Load Balancer를 선택합니다.
14. **Actions** > `Delete load balancer`를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step14-actions-delete-lb.png" alt="Load Balancer Actions > Delete" class="guide-img-md" />

15. 확인 창에서 `confirm`을 입력하고 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-cleanup-step15-confirm-delete-lb.png" alt="Load Balancer 삭제 확인 - confirm 입력" class="guide-img-sm" />

16. Amazon EKS 콘솔로 이동합니다.
17. `container-insights-cluster` 클러스터를 선택합니다.
18. [[Delete cluster]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-cleanup-step18-delete-cluster.png" alt="EKS Delete cluster 버튼" class="guide-img-md" />

19. 확인 창에서 클러스터 이름을 입력하고 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 클러스터 삭제에 10-15분이 소요됩니다. 삭제가 완료될 때까지 기다립니다.

20. Amazon VPC 콘솔로 이동합니다.
21. 왼쪽 메뉴에서 **NAT Gateways**를 선택합니다.
22. `eksctl-container-insights-cluster`로 시작하는 NAT Gateway를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step27-nat-gateway.png" alt="NAT Gateway 선택" class="guide-img-md" />

23. **Actions** > `Delete NAT gateway`를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step23-nat-delete.png" alt="NAT Gateway 삭제" class="guide-img-md" />

24. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

25. 왼쪽 메뉴에서 **Elastic IPs**를 선택합니다.
26. NAT Gateway와 연결되었던 Elastic IP를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step26-elastic-ip.png" alt="Elastic IP 선택" class="guide-img-md" />

27. **Actions** > `Release Elastic IP addresses`를 선택합니다.
28. 확인 창에서 [[Release]] 버튼을 클릭합니다.

29. AWS CloudFormation 콘솔로 이동합니다.
30. `eksctl-container-insights-cluster-cluster` 스택을 선택합니다.
31. [[Delete]] 버튼을 클릭합니다.
32. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

### Amazon CloudWatch 리소스 정리 (필수)

> [!WARNING]
> 아래 리소스는 eksctl 클러스터 삭제로 자동 삭제되지 않으므로 반드시 수동으로 삭제해야 합니다.

33. Amazon CloudWatch 콘솔로 이동합니다.
34. 왼쪽 메뉴에서 **Alarms**를 선택합니다.
35. 생성한 3개의 알람을 선택합니다:
    - `EKS_Cluster_High_CPU`
    - `EKS_Cluster_High_Memory`
    - `EKS_Cluster_Failed_Nodes`

    <img src="/images/week13/13-3-cleanup-step35-alarms-select.png" alt="3개 알람 선택" class="guide-img-md" />

36. **Actions** > `Delete`를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step36-alarms-delete.png" alt="알람 삭제" class="guide-img-md" />

37. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

38. 왼쪽 메뉴에서 **Dashboards**를 선택합니다.
39. `EKS_Container_Insights_Dashboard`를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step39-dashboard-select.png" alt="대시보드 선택" class="guide-img-md" />

40. [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-cleanup-step40-dashboard-delete.png" alt="대시보드 삭제" class="guide-img-sm" />

41. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

42. 왼쪽 메뉴에서 **Logs** > **Log Management**를 선택합니다.
43. 다음 로그 그룹들을 선택합니다:
    - `/aws/containerinsights/container-insights-cluster/application`
    - `/aws/containerinsights/container-insights-cluster/dataplane`
    - `/aws/containerinsights/container-insights-cluster/host`
    - `/aws/containerinsights/container-insights-cluster/performance`
    - `/aws/eks/container-insights-cluster/cluster`

> [!NOTE]
> 로그 그룹이 표시되지 않으면 이미 클러스터 삭제 시 자동으로 삭제된 것입니다.

44. **Actions** > `Delete log group(s)`를 선택합니다.

    <img src="/images/week13/13-3-cleanup-step44-log-select.png" alt="로그 그룹 선택 및 Actions" class="guide-img-md" />

45. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

    <img src="/images/week13/13-3-cleanup-step45-log-delete.png" alt="로그 그룹 삭제 확인" class="guide-img-sm" />

> [!WARNING]
> 로그 그룹을 삭제하지 않으면 스토리지 비용이 계속 발생합니다.

> [!TIP]
> AWS CLI로 삭제하려면 CloudShell에서 다음 명령어를 실행합니다:
>
> ```bash
> for lg in $(aws logs describe-log-groups --log-group-name-prefix /aws/containerinsights/container-insights-cluster --query "logGroups[*].logGroupName" --output text --region ap-northeast-2); do aws logs delete-log-group --log-group-name "$lg" --region ap-northeast-2; echo "삭제: $lg"; done
> aws logs delete-log-group --log-group-name /aws/eks/container-insights-cluster/cluster --region ap-northeast-2
> ```
>
> <img src="/images/week13/13-3-cleanup-step45-tip-cli-log.png" alt="CLI 로그 그룹 삭제" class="guide-img-md" />

### Amazon SNS 토픽 삭제 (필수)

46. AWS Management Console 상단 검색창에 `SNS`을 입력하고 선택합니다.
47. 왼쪽 메뉴에서 **Topics**를 선택합니다.
48. `EKS_High_CPU_Alert` 토픽을 선택합니다.

    <img src="/images/week13/13-3-cleanup-step48-sns-select.png" alt="SNS 토픽 선택" class="guide-img-md" />

49. [[Delete]] 버튼을 클릭합니다.
50. 확인 창에서 `delete me`를 입력합니다.

    <img src="/images/week13/13-3-cleanup-step50-sns-confirm.png" alt="SNS 토픽 삭제 확인 - delete me 입력" class="guide-img-sm" />

51. [[Delete]] 버튼을 클릭합니다.

### 최종 삭제 확인 (Tag Editor 활용)

52. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
53. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
54. **Regions**에서 `ap-northeast-2`를 선택합니다.
55. **Resource types**에서 `All supported resource types`를 선택합니다.
56. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `13-3`
57. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> Amazon EC2 인스턴스, NAT Gateway, VPC 등은 eksctl 클러스터 삭제 시 자동으로 삭제되지만, Tag Editor에 완전히 반영되기까지 5-10분이 소요될 수 있습니다.
> 이러한 리소스가 잠시 남아있더라도 시간이 지나면 자동으로 사라집니다.

<img src="/images/week13/13-3-cleanup-step56-final-check.png" alt="Tag Editor 최종 삭제 확인" class="guide-img-md" />

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
1. Kubernetes API → 클러스터 메타데이터.
2. kubelet → Pod 및 컨테이너 메트릭.
3. cAdvisor → 컨테이너 리소스 사용량.
4. Amazon CloudWatch 에이전트 → 메트릭 집계 및 전송.
5. Amazon CloudWatch → 메트릭 저장 및 시각화.
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
| stats count() as req_count by method, status
| sort req_count desc
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

- Metrics Server가 Pod CPU/메모리 사용률 수집.
- HPA가 목표 사용률과 현재 사용률 비교.
- 필요 시 Pod 수를 자동으로 증가/감소.
- 스케일링 쿨다운 기간 적용 (기본 5분).

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

- **로그 필터링**: 불필요한 로그 수집 제외.
- **보관 기간 설정**: 오래된 로그 자동 삭제.
- **로그 샘플링**: 모든 로그 대신 샘플만 수집.
- **메트릭 해상도**: 1분 대신 5분 간격 사용.

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

- Amazon CloudWatch 에이전트 Pod 상태 확인.
- AWS IAM 역할 권한 확인.
- 로그 그룹 생성 확인.
- 5-10분 대기 후 재확인.

**로그가 수집되지 않는 경우**:

- Fluent Bit Pod 상태 확인.
- ConfigMap 설정 확인.
- 로그 그룹 권한 확인.

**높은 CPU/메모리 사용률**:

- 리소스 제한 증가.
- HPA로 자동 스케일링.
- 애플리케이션 최적화.
- 노드 타입 업그레이드.

**Pod OOMKilled**:

- 메모리 제한 증가.
- 메모리 누수 확인.
- 애플리케이션 프로파일링.
