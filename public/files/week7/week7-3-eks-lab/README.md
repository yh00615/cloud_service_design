# Week 7-3: kubectl을 활용한 Amazon EKS 클러스터 운영

## 포함 파일

- `week7-3-eks-lab.yaml` - Amazon EKS 클러스터 및 노드 그룹 AWS CloudFormation 템플릿
- `nginx-deployment.yaml` - Nginx Deployment 매니페스트 (태스크 3에서 사용)
- `nginx-service.yaml` - Nginx Service 매니페스트 (태스크 6에서 사용)
- `nginx-ingress-alb.yaml` - ALB Ingress 매니페스트 (참고용)

## 관련 태스크

- 태스크 0: 실습 환경 구축 (week7-3-eks-lab.yaml을 사용하여 Amazon EKS 클러스터, 워커 노드, AWS IAM 역할 자동 생성)
- 태스크 3: Deployment 생성 (nginx-deployment.yaml을 사용하여 Nginx 애플리케이션 배포)
- 태스크 6: Service 생성 (nginx-service.yaml을 사용하여 LoadBalancer 타입 Service 생성)
