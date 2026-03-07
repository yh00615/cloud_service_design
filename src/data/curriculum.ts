// 실습 계획서 기반 커리큘럼 데이터

export type SessionType = 'theory' | 'lab' | 'demo' | 'none';

export interface Session {
  session: number; // 차시 번호 (1, 2, 3)
  type: SessionType;
  title: string;
  hasContent: boolean; // 실습/데모 가이드가 있는지
  markdownPath?: string; // 마크다운 파일 경로
  description?: string; // 차시 설명
  awsServices?: string[]; // 사용하는 AWS 서비스
  learningObjectives?: string[]; // 차시별 학습 목표
}

export interface WeekCurriculum {
  week: number;
  title: string;
  description: string; // 주차 설명
  sessions: Session[];
  prerequisites?: string[]; // 사전 요구사항
  estimatedTime?: string; // 예상 소요 시간
  difficulty?: 'beginner' | 'intermediate' | 'advanced'; // 난이도
}

// 15주차 커리큘럼 데이터 (실제 실습 계획서 기반)
export const curriculum: WeekCurriculum[] = [
  {
    week: 1,
    title: '클라우드 서비스 디자인 개요',
    description:
      'AWS 글로벌 인프라의 구성 요소와 아키텍처 설계에서의 역할을 이해하고, AWS Well-Architected Framework의 6가지 원칙을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'demo',
        title: 'AWS Resource Groups & Tag Editor를 활용한 리소스 관리',
        hasContent: true,
        markdownPath: '/content/week1/1-1-tag-editor-lab.md',
        description:
          'AWS 글로벌 인프라 구조, AWS 핵심 서비스 개요, AWS 관리형 서비스와 책임 공유 모델',
        awsServices: ['AWS Resource Groups & Tag Editor'],
        learningObjectives: [
          'AWS 글로벌 인프라의 구성 요소와 아키텍처 설계에서의 역할을 설명할 수 있습니다.',
          'AWS 서비스를 계층별로 분류하고 서비스 간 연동 관계를 이해할 수 있습니다.',
          'AWS 관리형 서비스의 책임 공유 모델을 서비스 유형별로 구분하여 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS Well-Architected Tool 워크로드 평가',
        hasContent: true,
        markdownPath: '/content/week1/1-2-well-architected-tool-lab.md',
        description:
          'AWS Well-Architected Framework 개요, 6가지 핵심 원칙과 트레이드오프, AWS Well-Architected Tool 활용',
        awsServices: ['AWS Well-Architected Tool'],
        learningObjectives: [
          'AWS Well-Architected Framework의 정의와 목적을 이해하고, 클라우드 아키텍처 설계에서 왜 필요한지 설명할 수 있습니다.',
          '6가지 핵심 원칙의 개념과 각 원칙 간 트레이드오프 관계를 이해하고, 비즈니스 상황에 따라 적절한 균형을 판단할 수 있습니다.',
          'AWS Well-Architected Tool의 활용 프로세스를 이해하고, 실제 워크로드에 적용하여 아키텍처를 검토하고 개선 방향을 도출할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'draw.io로 HA 아키텍처 다이어그램 작성',
        hasContent: true,
        markdownPath: '/content/week1/1-3-drawio-architecture.md',
        description:
          '클라우드 서비스 디자인 개요, 컴퓨팅 서비스 디자인 패턴, 서비스 통합 디자인 패턴',
        awsServices: [],
        learningObjectives: [
          '클라우드 서비스 디자인의 핵심 요소를 이해하고, 모놀리식과 마이크로서비스 아키텍처의 차이를 설명할 수 있습니다.',
          '인스턴스 기반, 컨테이너 기반, 서버리스 컴퓨팅 패턴의 특징을 비교하고, 워크로드에 적합한 패턴을 판단할 수 있습니다.',
          'API 기반 통합과 이벤트 기반 통합의 차이를 이해하고, 각각의 활용 시나리오를 설명할 수 있습니다.',
        ],
      },
    ],
    prerequisites: ['AWS 기본 개념 이해', '클라우드 컴퓨팅 기초 지식'],
    estimatedTime: '180분',
    difficulty: 'beginner',
  },
  {
    week: 2,
    title: 'AWS IAM 및 조직 관리 고급 전략',
    description:
      'AWS IAM 정책 설계, IAM 역할과 임시 자격증명, AWS Organizations 정책 관리를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'lab',
        title: 'AWS IAM 정책 Condition 요소 활용',
        hasContent: true,
        markdownPath: '/content/week2/2-1-iam-policy-condition.md',
        description:
          'AWS 인증과 권한, AWS IAM 정책 구조 및 평가 로직, 고급 권한 제어 기법',
        awsServices: ['AWS IAM'],
        learningObjectives: [
          'AWS 인증과 권한의 차이를 이해하고, AWS IAM을 통한 사용자 접근 관리 방법을 설명할 수 있습니다.',
          'AWS IAM 정책 구조와 평가 로직을 설명할 수 있습니다.',
          'AWS IAM 정책의 Condition 요소와 권한 경계(Permission Boundary)를 활용한 고급 권한 제어 기법을 이해할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS STS AssumeRole을 활용한 역할 전환',
        hasContent: true,
        markdownPath: '/content/week2/2-2-iam-role-assumerole.md',
        description:
          'AWS IAM 역할 개념 및 임시 자격증명, 신뢰 정책과 권한 정책 구성, AWS STS와 AssumeRole 활용',
        awsServices: ['AWS IAM', 'AWS STS'],
        learningObjectives: [
          'AWS IAM 역할과 임시 자격 증명이 장기 자격 증명 대비 갖는 보안 이점을 설명할 수 있습니다.',
          'AWS IAM 역할의 신뢰 정책(Trust Policy)과 권한 정책(Permission Policy)의 차이를 이해하고 구성할 수 있습니다.',
          'AWS STS(Security Token Service)의 AssumeRole API를 활용하여 다른 역할로 안전하게 전환할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'theory',
        title: 'AWS Organizations 정책 관리',
        hasContent: false,
        description:
          'AWS Organizations 구조 및 OU 설계, 서비스 제어 정책(SCP) 구성, 태그 정책 및 거버넌스 자동화',
        awsServices: ['AWS Organizations'],
        learningObjectives: [
          'AWS Organizations를 활용한 멀티 계정 구조의 관리 전략과 이점을 이해할 수 있습니다.',
          'OU(Organizational Unit)로 계정을 그룹화하고, SCP(Service Control Policy)와 RCP(Resource Control Policy)를 통해 조직 단위별 권한 범위를 제어할 수 있습니다.',
          '태그 정책을 통해 조직 전체의 리소스 태깅을 표준화하고 일관성 있게 관리할 수 있습니다.',
        ],
      },
    ],
    prerequisites: ['Week 1 완료', 'IAM 기본 개념 이해'],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 3,
    title: 'Amazon VPC 고급 네트워킹',
    description:
      'Amazon VPC 설계 전략과 서브넷 구성, 보안 설계, 네트워크 확장을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'lab',
        title: 'Amazon VPC Endpoint 생성 및 연결 확인',
        hasContent: true,
        markdownPath: '/content/week3/3-1-vpc-design-strategy.md',
        description:
          'Amazon VPC 핵심 구성 요소, 서브넷 설계 및 CIDR 계획, Amazon VPC Endpoint',
        awsServices: ['Amazon VPC'],
        learningObjectives: [
          'Amazon VPC의 핵심 구성 요소와 각 구성 요소의 역할을 설명할 수 있습니다.',
          'CIDR(Classless Inter-Domain Routing) 블록 설계 원칙을 이해하고 서브넷 구성에 적용할 수 있습니다.',
          'Amazon VPC Endpoint의 유형을 이해하고 적절한 프라이빗 연결을 선택할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: '3-tier 아키텍처 보안 그룹 및 NACL 구성',
        hasContent: true,
        markdownPath: '/content/week3/3-2-security-group-nacl.md',
        description:
          '다층 방어 네트워크 보안 전략, 보안 그룹과 NACL 비교 및 활용, AWS Network Firewall 구성',
        awsServices: ['Amazon VPC'],
        learningObjectives: [
          '보안 그룹과 NACL(Network Access Control List)을 조합한 다층 방어 전략의 개념과 필요성을 이해할 수 있습니다.',
          '보안 그룹(상태 저장)과 NACL(상태 비저장)의 차이를 이해하고 적절히 활용할 수 있습니다.',
          'AWS Network Firewall의 역할과 도메인 필터링, IDS/IPS 등 주요 사용 사례를 설명할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'theory',
        title: 'Amazon VPC 네트워크 확장',
        hasContent: false,
        description:
          'Amazon VPC Peering을 활용한 네트워크 확장, 하이브리드 네트워크 연결, AWS Transit Gateway 아키텍처',
        awsServices: ['Amazon VPC'],
        learningObjectives: [
          'Amazon VPC Peering을 활용하여 VPC 간 프라이빗 연결을 구성할 수 있습니다.',
          'AWS Site-to-Site VPN과 AWS Direct Connect의 특징을 비교하고 요구사항에 적합한 하이브리드 연결 방식을 선택할 수 있습니다.',
          'AWS Transit Gateway를 활용하여 허브-스포크 방식의 중앙 집중형 네트워크를 설계할 수 있습니다.',
        ],
      },
    ],
    prerequisites: ['Week 1-2 완료', '네트워킹 기본 개념 이해'],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 4,
    title: '서버리스 및 이벤트 기반 아키텍처',
    description:
      '서버리스 아키텍처 설계, API 기반 아키텍처, 이벤트 기반 아키텍처를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: '서버리스 아키텍처 설계',
        hasContent: false,
        description:
          '서버리스 컴퓨팅 개념 및 특징, AWS Lambda 동작 원리, AWS Lambda 성능 최적화',
        awsServices: ['AWS Lambda'],
        learningObjectives: [
          '서버리스 컴퓨팅의 특징과 제약사항을 설명할 수 있습니다.',
          'AWS Lambda의 이벤트 기반 실행 모델과 핸들러 함수 구조를 이해할 수 있습니다.',
          'AWS Lambda의 메모리, 동시성, 콜드 스타트 등 성능에 영향을 미치는 요소를 이해하고 최적화 기법을 적용할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'Amazon API Gateway 인증 구성',
        hasContent: true,
        markdownPath: '/content/week4/4-2-lambda-api-gateway-demo.md',
        description:
          'RESTful API 설계 원칙, Amazon API Gateway 개요, Amazon API Gateway 보안 및 인증',
        awsServices: ['AWS Lambda', 'Amazon API Gateway', 'Amazon Cognito'],
        learningObjectives: [
          'RESTful API의 핵심 설계 원칙을 이해하고 리소스 기반 URI와 HTTP 메소드를 활용하여 API를 설계하고 적용할 수 있습니다.',
          'Amazon API Gateway의 주요 특징과 전체 아키텍처를 이해하고, Lambda 프록시 및 비프록시 통합 방식을 비교할 수 있습니다.',
          'Amazon API Gateway에서 제공하는 Amazon Cognito User Pool, AWS Lambda Authorizer, AWS IAM 역할 등 다양한 인증 방식을 비교하고 요구사항에 적합한 방식을 선택할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'Amazon EventBridge 기반 예약 처리 시스템',
        hasContent: true,
        markdownPath: '/content/week4/4-3-eventbridge-reservation.md',
        description:
          '이벤트 기반 아키텍처 개념, Amazon EventBridge 소개, Amazon EventBridge 동작 방식',
        awsServices: ['Amazon EventBridge', 'AWS Lambda', 'Amazon DynamoDB'],
        learningObjectives: [
          '이벤트 기반 아키텍처의 개념과 핵심 구성 요소를 이해할 수 있습니다.',
          'Amazon EventBridge의 주요 구성 요소와 역할을 이해할 수 있습니다.',
          'Amazon EventBridge의 이벤트 수신, 규칙 매칭, 대상 전달로 이어지는 전체 동작 흐름을 이해할 수 있습니다.',
        ],
      },
    ],
    prerequisites: ['Week 1-3 완료', 'REST API 기본 개념 이해'],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 5,
    title: '고성능 데이터베이스 설계',
    description:
      'Amazon RDS 고급 운영, Amazon Aurora 아키텍처, Amazon DynamoDB 고급 설계를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'demo',
        title: 'Amazon RDS Multi-AZ 장애 조치 시뮬레이션',
        hasContent: true,
        markdownPath: '/content/week5/5-1-rds-multi-az.md',
        description:
          'Amazon RDS 고가용성 구성, Amazon RDS 운영 관리, Amazon RDS Proxy 활용',
        awsServices: ['Amazon RDS'],
        learningObjectives: [
          'Amazon RDS Multi-AZ 배포와 Amazon RDS Read Replica를 비교하고 선택할 수 있습니다.',
          'Amazon RDS의 백업 방식과 스냅샷 활용 방법을 이해할 수 있습니다.',
          'Amazon RDS Proxy로 데이터베이스 연결을 최적화할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'theory',
        title: 'Amazon Aurora 아키텍처',
        hasContent: false,
        description:
          'Amazon Aurora 클러스터 아키텍처, Amazon Aurora 고가용성, Amazon Aurora Serverless v2 및 혼합 구성',
        awsServices: ['Amazon Aurora'],
        learningObjectives: [
          'Amazon Aurora의 클러스터 아키텍처 구조와 Amazon RDS와의 차이를 설명할 수 있습니다.',
          'Amazon Aurora의 고가용성 구조와 장애 조치 방식을 설명할 수 있습니다.',
          'Amazon Aurora Serverless v2의 자동 스케일링과 혼합 구성의 Aurora DB 클러스터 활용 방식을 설명할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'Amazon DynamoDB 테이블 생성 및 보조인덱스 활용',
        hasContent: true,
        markdownPath: '/content/week5/5-3-dynamodb-design.md',
        description:
          'Amazon DynamoDB 설계 원칙, Amazon DynamoDB 데이터 조회, Amazon DynamoDB 인덱스 전략',
        awsServices: ['Amazon DynamoDB'],
        learningObjectives: [
          '파티션 키와 정렬 키의 역할을 이해하고, 액세스 패턴에 맞는 키 설계 원칙을 설명할 수 있습니다.',
          'GetItem, Query, Scan의 차이를 이해하고, 상황에 따라 적절한 데이터 조회 방식을 선택할 수 있습니다.',
          'GSI(Global Secondary Index)와 LSI(Local Secondary Index)의 차이를 비교하고, 쿼리 요구사항에 맞게 인덱스를 설계하여 활용할 수 있습니다.',
        ],
      },
    ],
    prerequisites: ['Week 1-4 완료', '데이터베이스 기본 개념 이해'],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 6,
    title: 'IaC 기반 인프라 자동화',
    description:
      'Infrastructure as Code 개념과 AWS CloudFormation을 활용한 인프라 자동화를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'demo',
        title: 'AWS CloudFormation 스택 생명주기 관리',
        hasContent: true,
        markdownPath: '/content/week6/6-1-cloudformation-overview.md',
        description:
          'IaC 개념과 AWS IaC 도구, AWS CloudFormation 템플릿 및 스택, 변경 세트와 드리프트 감지',
        awsServices: ['AWS CloudFormation'],
        learningObjectives: [
          'IaC(Infrastructure as Code)의 개념과 이점을 이해하고, AWS IaC 도구의 역할과 관계를 설명할 수 있습니다.',
          'AWS CloudFormation의 동작 원리와 템플릿·스택의 관계를 이해할 수 있습니다.',
          '변경 세트와 드리프트 감지를 활용한 스택 변경 관리를 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS CloudFormation 템플릿 분석 및 스택 배포',
        hasContent: true,
        markdownPath: '/content/week6/6-2-cloudformation-template.md',
        description:
          'AWS CloudFormation 템플릿 구조, 내장 함수 및 의사 파라미터, AWS CloudFormation StackSets',
        awsServices: ['AWS CloudFormation', 'Amazon VPC'],
        learningObjectives: [
          'Resources, Parameters, Outputs 섹션의 역할을 이해하고, 재사용 가능한 AWS CloudFormation 템플릿을 작성할 수 있습니다.',
          '내장 함수와 의사 파라미터를 사용하여 동적 값을 참조할 수 있습니다.',
          'AWS CloudFormation StackSets를 활용한 멀티 계정·리전 배포 방식을 설명할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'AWS Infrastructure Composer를 활용한 템플릿 설계',
        hasContent: true,
        markdownPath: '/content/week6/6-3-infrastructure-composer.md',
        description:
          'AWS CDK 개요, AWS SAM 개요, AWS Infrastructure Composer 개요',
        awsServices: ['AWS CloudFormation', 'AWS Infrastructure Composer'],
        learningObjectives: [
          'AWS CDK(Cloud Development Kits)의 특징을 이해하고 프로그래밍 언어 기반의 인프라 정의 방식을 설명할 수 있습니다.',
          'AWS SAM(Serverless Application Model)의 특징을 이해하고 서버리스 애플리케이션에 특화된 활용 방식을 설명할 수 있습니다.',
          'AWS Infrastructure Composer를 활용한 시각적 템플릿 설계 방식을 이해할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-5 완료',
      'VPC 및 네트워킹 기본 개념 이해',
      'YAML 기본 문법 이해',
    ],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 7,
    title: '컨테이너 기반 서비스 설계',
    description:
      'Kubernetes 아키텍처, Amazon EKS 개요 및 운영을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: 'Kubernetes 아키텍처와 핵심 리소스',
        hasContent: false,
        description:
          'Kubernetes 개요 및 아키텍처, Kubernetes 기본 객체, Kubernetes 워크로드',
        awsServices: ['Amazon EKS', 'Kubernetes'],
        learningObjectives: [
          'Kubernetes의 개념과 아키텍처에서 컨트롤 플레인과 데이터 플레인의 구성 요소와 역할을 설명할 수 있습니다.',
          'Pod, Service, Namespace 등 Kubernetes 기본 객체의 개념과 동작 방식을 설명할 수 있습니다.',
          'Deployment, ReplicaSet, StatefulSet, DaemonSet 등 Kubernetes 워크로드의 특징과 차이를 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'theory',
        title: 'Amazon EKS 개요',
        hasContent: false,
        description:
          'AWS 컨테이너 서비스, Amazon EKS 클러스터, Amazon EKS 인증과 권한 관리',
        awsServices: ['Amazon EKS', 'Kubernetes'],
        learningObjectives: [
          'AWS 컨테이너 서비스의 종류와 Amazon ECS, Amazon EKS의 차이를 설명할 수 있습니다.',
          'Amazon EKS 관리형 컨트롤 플레인 구조와 데이터 플레인 유형을 설명할 수 있습니다.',
          'AWS IAM 인증, RBAC(Role-Based Access Control) 권한 관리, IRSA(IAM Roles for Service Accounts)의 개념을 설명할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'kubectl을 활용한 Amazon EKS 클러스터 운영',
        hasContent: true,
        markdownPath: '/content/week7/7-3-eks-cluster-kubectl.md',
        description:
          'Amazon EKS 네트워킹, Amazon EKS 서비스 네트워킹, Amazon EKS 스케일링',
        awsServices: ['Amazon EKS', 'Kubernetes'],
        learningObjectives: [
          'Amazon VPC CNI(Container Network Interface) 플러그인의 동작 방식과 네트워크 정책(Network Policy)의 역할을 설명할 수 있습니다.',
          'Kubernetes Service 타입과 Ingress, AWS Load Balancer Controller의 역할을 설명할 수 있습니다.',
          'HPA(Horizontal Pod Autoscaler), CAS(Cluster Autoscaler), Karpenter의 차이를 비교하여 설명할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-6 완료',
      'Docker 기본 개념 이해',
      'Linux 명령어 기본 지식',
    ],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 8,
    title: '중간고사',
    description: '중간고사',
    sessions: [
      { session: 1, type: 'none', title: '중간고사', hasContent: false },
    ],
    prerequisites: ['Week 1-7 완료'],
    estimatedTime: '180분',
    difficulty: 'intermediate',
  },
  {
    week: 9,
    title: 'CI/CD 파이프라인 구축',
    description:
      'AWS Developer Tools를 활용한 CI/CD 파이프라인 구축 및 자동화를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: 'DevOps와 CI/CD 개요',
        hasContent: false,
        description:
          'DevOps 개요, CI/CD 개요, DevSecOps 개요',
        awsServices: [
          'AWS CodeCommit',
          'AWS CodeBuild',
          'AWS CodeDeploy',
          'AWS CodePipeline',
        ],
        learningObjectives: [
          'DevOps의 개념과 핵심 원칙을 이해하고 생명주기를 설명할 수 있습니다.',
          'CI/CD(Continuous Integration/Continuous Delivery) 파이프라인의 각 단계와 흐름을 이해하고 AWS CI/CD 서비스 구성 요소를 설명할 수 있습니다.',
          'DevSecOps의 개념을 이해하고 CI/CD 파이프라인에 보안을 통합하는 방법을 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS CodeBuild로 컨테이너 이미지 빌드',
        hasContent: true,
        markdownPath: '/content/week9/9-2-codebuild-container.md',
        description:
          'Git 개요, AWS CodeCommit 저장소 관리, AWS CodeBuild 빌드 자동화',
        awsServices: ['AWS CodeBuild', 'AWS CodeCommit', 'Amazon ECR', 'Amazon CloudWatch Logs'],
        learningObjectives: [
          'Git의 개념과 주요 명령어를 이해하고 AWS CodeCommit으로 소스 코드와 브랜치 전략을 관리할 수 있습니다.',
          'buildspec.yml의 구조를 이해하고 AWS CodeBuild로 빌드 프로세스를 구성할 수 있습니다.',
          'AWS CodeBuild와 AWS CodeArtifact를 연동하여 프라이빗 패키지 저장소를 구성하고 의존성을 관리할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'AWS CodePipeline으로 Amazon S3 웹사이트 배포 자동화',
        hasContent: true,
        markdownPath: '/content/week9/9-3-s3-static-website.md',
        description:
          'AWS CodeDeploy 배포 전략, AWS CodePipeline 파이프라인 구성, Kiro를 활용한 AI 주도 개발(AI-DLC)',
        awsServices: ['AWS CodePipeline', 'AWS CodeBuild'],
        learningObjectives: [
          'AWS CodeDeploy의 배포 전략을 비교하고 워크로드에 적합한 전략을 선택할 수 있습니다.',
          'AWS CodePipeline으로 소스, 빌드, 배포 단계를 연결하여 CI/CD(Continuous Integration/Continuous Delivery) 워크플로를 구성할 수 있습니다.',
          'Kiro와 AI-DLC(AI-Driven Development Life Cycle)의 개념을 이해하고 AI 주도 개발 방법론을 설명할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-7 완료',
      'Git 기본 사용법 이해',
      'Docker 및 Kubernetes 기본 개념',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 10,
    title: '캐싱 및 성능 최적화',
    description:
      'Amazon ElastiCache, Amazon CloudFront를 통한 성능 최적화 전략을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: '캐싱 개요',
        hasContent: false,
        description:
          '캐시 개념 및 계층 구조, 캐시 동작 방식, 캐시 제거 정책',
        awsServices: ['Amazon ElastiCache'],
        learningObjectives: [
          '캐시의 개념과 캐시 히트/미스의 동작 방식을 이해하고 설명할 수 있습니다.',
          'TTL(Time To Live), 무효화(Invalidation), LRU(Least Recently Used), LFU(Least Frequently Used) 등 캐시 관리 방법을 이해하고 데이터 접근 패턴에 맞는 적절한 정책을 선택할 수 있습니다.',
          '하드웨어 계층과 웹/서버 계층에서의 캐시 구조를 이해하고 각 계층별 역할과 특징을 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'Amazon ElastiCache로 API 응답 캐싱 구현',
        hasContent: true,
        markdownPath: '/content/week10/10-2-elasticache-caching.md',
        description:
          'Amazon ElastiCache 개요, Amazon ElastiCache 지원 엔진, 캐시 전략 및 운영',
        awsServices: ['Amazon ElastiCache'],
        learningObjectives: [
          'Amazon ElastiCache의 개념과 특징을 이해하고 완전관리형 인메모리 캐싱 서비스로서의 역할을 설명할 수 있습니다.',
          'Redis, Memcached, Valkey 각 엔진의 특징과 차이점을 비교하고 요구사항에 맞는 적절한 엔진을 선택할 수 있습니다.',
          '5가지 캐시 전략의 동작 방식을 이해하고 Amazon ElastiCache에서 Lazy Loading과 Write-Through를 적용할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'Amazon CloudFront Functions로 엣지 로케이션 처리',
        hasContent: true,
        markdownPath: '/content/week10/10-3-cloudfront-demo.md',
        description:
          'Amazon CloudFront 개요, Amazon CloudFront 캐시 설정과 무효화, AWS Lambda@Edge와 Amazon CloudFront Functions',
        awsServices: ['Amazon CloudFront'],
        learningObjectives: [
          'Amazon CloudFront의 개요와 엣지 로케이션·오리진·배포 등 핵심 구성 요소를 설명할 수 있습니다.',
          '캐시 정책을 설정하여 TTL과 캐시 키를 정의하고 콘텐츠 유형에 따라 캐시 동작을 제어하며 무효화를 수행할 수 있습니다.',
          'Amazon CloudFront Functions와 AWS Lambda@Edge의 실행 위치·성능·기능 차이를 비교하고 요구사항에 맞는 엣지 컴퓨팅 방식을 선택할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-9 완료',
      '데이터베이스 기본 개념 이해',
      'API 설계 기본 지식',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 11,
    title: '데이터 레이크 아키텍처',
    description:
      'Amazon S3 데이터 레이크, AWS Glue, Amazon Athena를 활용한 데이터 파이프라인 구축 및 분석을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: '모던 데이터 아키텍처 개요',
        hasContent: false,
        description:
          '데이터 유형과 저장 방식, 모던 데이터 아키텍처, 데이터 레이크와 데이터 웨어하우스',
        awsServices: [
          'Amazon S3',
          'AWS Glue',
          'Amazon Athena',
          'AWS Lake Formation',
          'Amazon Quick Suite',
        ],
        learningObjectives: [
          '정형, 반정형, 비정형 데이터의 차이를 이해하고 행 기반과 열 기반 저장 방식의 특징과 배치(Batch), 스트리밍(Streaming) 수집 방식의 차이를 설명할 수 있습니다.',
          '모던 데이터 아키텍처의 개념과 구성 요소를 이해하고 기존 데이터 사일로 방식과의 차이를 설명할 수 있습니다.',
          '데이터 레이크와 데이터 웨어하우스의 차이를 비교하고 요구사항에 맞는 적절한 저장소를 선택할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS Glue Crawler 설정 및 Data Catalog 확인',
        hasContent: true,
        markdownPath: '/content/week11/11-2-s3-glue-athena-lab.md',
        description:
          '데이터 파이프라인 개요, Amazon S3 기반 데이터 레이크 설계, AWS Glue를 활용한 메타데이터 관리',
        awsServices: ['Amazon S3', 'AWS Glue', 'Amazon Athena'],
        learningObjectives: [
          '데이터 파이프라인의 전체 흐름과 각 단계의 역할을 이해하고 설명할 수 있습니다.',
          'Amazon S3로 데이터 레이크 3계층을 구성하고 압축과 파티셔닝을 활용하여 효율적인 데이터 레이크를 설계할 수 있습니다.',
          'AWS Glue Crawler와 AWS Glue Data Catalog의 역할을 이해하고 메타데이터를 관리할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'AWS Glue를 활용한 데이터 파이프라인 구축',
        hasContent: true,
        markdownPath: '/content/week11/11-3-data-pipeline.md',
        description:
          'AWS Glue Job 기반 ETL 파이프라인, 데이터 쿼리 및 시각화, AWS Lake Formation 기반 데이터 거버넌스',
        awsServices: ['AWS Glue', 'Amazon Athena', 'Amazon S3'],
        learningObjectives: [
          'AWS Glue Job으로 ETL(Extract, Transform, Load) 파이프라인을 구성하고 데이터를 변환할 수 있습니다.',
          'Amazon Athena로 데이터를 쿼리하고 Amazon Quick Suite로 시각화할 수 있습니다.',
          'AWS Lake Formation의 중앙 집중식 데이터 거버넌스 개념과 주요 기능을 이해할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-10 완료',
      'SQL 기본 문법 이해',
      '데이터 처리 기본 개념',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 12,
    title: '보안 아키텍처 설계',
    description:
      '자격증명 관리, AWS Config, Amazon GuardDuty를 통한 보안 자동화 및 규정 준수를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'lab',
        title: 'AWS Secrets Manager와 AWS Systems Manager를 활용한 자격증명 관리',
        hasContent: true,
        markdownPath: '/content/week12/12-1-credentials-management.md',
        description:
          '자격증명 관리 아키텍처 설계, AWS Systems Manager Parameter Store 구성, AWS Secrets Manager 구성',
        awsServices: ['AWS Systems Manager', 'AWS Secrets Manager'],
        learningObjectives: [
          '자격증명 관리의 필요성과 중앙 집중식 관리 아키텍처를 이해할 수 있습니다.',
          'AWS Systems Manager Parameter Store의 기능과 구성을 이해할 수 있습니다.',
          'AWS Secrets Manager의 기능과 구성을 이해할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS Config 규칙 생성 및 모니터링',
        hasContent: true,
        markdownPath: '/content/week12/12-2-aws-config-demo.md',
        description:
          '클라우드 규정 준수 개요, AWS Config를 활용한 규정 준수 확인, AWS Config 고급 기능',
        awsServices: ['AWS Config'],
        learningObjectives: [
          '클라우드 환경에서 규정 준수의 필요성과 주요 과제를 설명할 수 있습니다.',
          'AWS Config와 Config Rules로 리소스 규정 준수를 확인할 수 있습니다.',
          'AWS Config의 수정 작업, 적합성 팩 등 고급 기능을 이해할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'demo',
        title: 'Amazon GuardDuty와 AWS Lambda 자동 대응',
        hasContent: true,
        markdownPath: '/content/week12/12-3-guardduty-lambda-demo.md',
        description:
          'Amazon GuardDuty 개요, 보안 자동 대응 아키텍처, AWS Security Hub 개요',
        awsServices: ['Amazon GuardDuty', 'AWS Lambda', 'Amazon EventBridge'],
        learningObjectives: [
          'Amazon GuardDuty의 데이터 소스와 위협 탐지 동작 방식을 설명할 수 있습니다.',
          'Amazon GuardDuty, Amazon EventBridge, AWS Lambda를 연계한 보안 자동 대응 아키텍처를 설명할 수 있습니다.',
          'AWS Security Hub를 활용한 통합 보안 관리 방식을 이해할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-11 완료',
      '보안 기본 개념 이해',
      'Lambda 기본 사용법',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 13,
    title: '관찰 가능성 아키텍처 설계',
    description:
      '관찰 가능성 3요소(메트릭, 로그, 트레이스)와 AWS X-Ray 분산 추적, 워크로드별 심화 모니터링을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'theory',
        title: '관찰 가능성 및 Amazon CloudWatch',
        hasContent: false,
        description:
          '관찰 가능성 개념 및 3요소, Amazon CloudWatch 메트릭 수집, Amazon CloudWatch Logs 분석',
        awsServices: ['Amazon CloudWatch'],
        learningObjectives: [
          '관찰 가능성 3요소(메트릭, 로그, 트레이스)의 개념과 역할을 설명할 수 있습니다.',
          'Amazon CloudWatch 메트릭의 네임스페이스, 차원, 통계 기반 수집 구조를 이해할 수 있습니다.',
          'Amazon CloudWatch Logs Insights의 쿼리 언어를 활용하여 로그 패턴을 분석할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'lab',
        title: 'AWS X-Ray를 활용한 서버리스 애플리케이션 추적',
        hasContent: true,
        markdownPath: '/content/week13/13-2-xray-tracing.md',
        description:
          'AWS X-Ray 개요 및 구성요소, 서비스 맵과 트레이스 분석, AWS X-Ray 컨테이너 및 서버리스 적용',
        awsServices: ['AWS X-Ray'],
        learningObjectives: [
          'AWS X-Ray의 구성요소와 분산 추적 방식을 설명할 수 있습니다.',
          'X-Ray Service Map과 Analytics를 활용하여 서비스 간 의존성과 병목 지점을 식별할 수 있습니다.',
          'AWS X-Ray를 컨테이너 및 서버리스 환경에 적용하는 방법을 설명할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'demo',
        title: 'Amazon CloudWatch Container Insights로 Amazon EKS 모니터링',
        hasContent: true,
        markdownPath: '/content/week13/13-3-container-insights-eks.md',
        description:
          '컨테이너 관찰 가능성 개요, 컨테이너 메트릭과 로그 수집, Amazon CloudWatch Container Insights',
        awsServices: ['Amazon CloudWatch', 'Amazon EKS'],
        learningObjectives: [
          '컨테이너 환경에서 관찰 가능성 3요소(메트릭, 로그, 트레이스)의 적용 방식을 설명할 수 있습니다.',
          'Fluent Bit DaemonSet과 Amazon CloudWatch Agent를 활용한 컨테이너 메트릭과 로그 수집 구조를 이해할 수 있습니다.',
          'Amazon CloudWatch Container Insights로 클러스터, 노드, Pod 레벨의 메트릭을 수집하고 분석할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-12 완료',
      '시스템 모니터링 기본 개념 이해',
      'Kubernetes 기본 지식',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 14,
    title: '지능형 클라우드 서비스 설계',
    description:
      'Amazon Bedrock을 활용한 생성형 AI 서비스 구축 및 RAG 시스템 구현을 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'lab',
        title: 'Amazon Bedrock 프롬프트 엔지니어링',
        hasContent: true,
        markdownPath: '/content/week14/14-1-bedrock-prompt-engineering.md',
        description:
          '생성형 AI와 파운데이션 모델, 생성형 AI 애플리케이션 개요, Amazon Bedrock 소개',
        awsServices: ['Amazon Bedrock'],
        learningObjectives: [
          '생성형 AI와 파운데이션 모델의 개념을 설명할 수 있습니다.',
          '생성형 AI 애플리케이션의 구성 요소와 동작 방식을 이해할 수 있습니다.',
          'Amazon Bedrock의 주요 기능과 서비스 구조를 설명할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'demo',
        title: 'Amazon Bedrock Knowledge Bases 기반 RAG 구현',
        hasContent: true,
        markdownPath: '/content/week14/14-2-bedrock-knowledge-bases-rag.md',
        description:
          '프롬프트 엔지니어링, 검색 증강 생성(RAG), Amazon Bedrock Knowledge Bases 구성',
        awsServices: ['Amazon Bedrock', 'Amazon S3', 'Amazon OpenSearch Serverless'],
        learningObjectives: [
          '프롬프트 엔지니어링의 개념과 주요 기법을 설명하고 적용할 수 있습니다.',
          '검색 증강 생성(RAG)의 아키텍처와 동작 원리를 이해할 수 있습니다.',
          'Amazon Bedrock Knowledge Bases를 구성하고 활용할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'Amazon Bedrock Agents 기반 고객 지원 챗봇',
        hasContent: true,
        markdownPath: '/content/week14/14-3-bedrock-agent-chatbot.md',
        description:
          'AI 에이전트 개요, Amazon Bedrock Agents 개요, Agentic AI Kiro 소개',
        awsServices: ['Amazon Bedrock'],
        learningObjectives: [
          'AI 에이전트의 개념과 활용 시나리오를 설명할 수 있습니다.',
          'Amazon Bedrock Agents의 구성 요소와 오케스트레이션 방식을 이해할 수 있습니다.',
          'Agentic AI 도구인 Kiro의 특징과 활용 가능성을 설명할 수 있습니다.',
        ],
      },
    ],
    prerequisites: [
      'Week 1-13 완료',
      'AI/ML 기본 개념 이해',
      'Lambda 및 DynamoDB 사용 경험',
    ],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
  {
    week: 15,
    title: '기말고사',
    description: '기말고사',
    sessions: [
      { session: 1, type: 'none', title: '기말고사', hasContent: false },
    ],
    prerequisites: ['Week 1-14 완료'],
    estimatedTime: '180분',
    difficulty: 'advanced',
  },
];

// 세션 타입별 아이콘 및 레이블
export const sessionTypeConfig = {
  theory: { icon: 'file', label: '이론', color: 'grey', emoji: '📄' },
  lab: { icon: 'settings', label: '실습', color: 'blue', emoji: '🔬' },
  demo: { icon: 'video-on', label: '데모', color: 'green', emoji: '🎥' },
  none: { icon: 'edit', label: '시험', color: 'red', emoji: '📝' },
} as const;
