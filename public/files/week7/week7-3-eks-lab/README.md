# Week 7-3: kubectl을 활용한 Amazon EKS 클러스터 운영

## 포함 파일

- `week7-3-eks-lab.yaml` - VPC, IAM 역할 사전 구성 AWS CloudFormation 템플릿
- `nginx-deployment.yaml` - Nginx Deployment 매니페스트 (태스크 6에서 사용)
- `nginx-service.yaml` - Nginx Service 매니페스트 (태스크 8에서 사용)
- `nginx-ingress-alb.yaml` - ALB Ingress 매니페스트 (참고용)

## 관련 태스크

- 태스크 0: 사전 인프라 구축 (week7-3-eks-lab.yaml을 사용하여 VPC, IAM 역할 자동 생성)
- 태스크 1: Amazon EKS 콘솔에서 클러스터 생성
- 태스크 2: 노드 그룹 추가
- 태스크 3: kubectl 구성 및 클러스터 연결
- 태스크 6: YAML 매니페스트로 Deployment 생성 (nginx-deployment.yaml 사용)
- 태스크 8: Service 생성 (nginx-service.yaml 사용)
