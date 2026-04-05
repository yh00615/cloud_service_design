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
          'AWS 리소스 태그의 개념과 중요성을 이해할 수 있습니다.',
          'Tag Editor를 사용하여 리소스를 검색하고 관리할 수 있습니다.',
          'Resource Groups를 생성하여 관련 리소스를 그룹화할 수 있습니다.',
          '태그 기반 리소스 정리 방법을 학습할 수 있습니다.',
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
          'AWS Well-Architected Framework의 6가지 핵심 원칙(운영 우수성, 보안, 안정성, 성능 효율성, 비용 최적화, 지속 가능성)을 이해할 수 있습니다.',
          'AWS Well-Architected Tool로 워크로드를 생성하고 평가할 수 있습니다.',
          '운영 우수성, 보안, 안정성 원칙을 평가하고 개선 계획을 수립할 수 있습니다.',
          '평가 결과 보고서를 생성하고 공유할 수 있습니다.',
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
          'Draw.io를 사용하여 AWS 아키텍처 다이어그램을 작성할 수 있습니다.',
          'QuickTable 3-Tier 아키텍처 다이어그램을 작성할 수 있습니다.',
          'Multi-AZ 구성으로 고가용성 설계를 적용할 수 있습니다.',
          '아키텍처 다이어그램을 PNG 파일로 내보낼 수 있습니다.',
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
          'AWS IAM 정책의 구조(Effect, Action, Resource, Condition)를 이해할 수 있습니다.',
          'MFA 강제, IP 주소 제한, 시간 기반 Condition 정책을 생성할 수 있습니다.',
          '복합 조건(AND 연산)을 사용하여 여러 Condition 키를 조합한 고급 정책을 작성할 수 있습니다.',
          'Condition 정책의 동작을 테스트하고 검증할 수 있습니다.',
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
          'Amazon S3 읽기 전용 역할을 생성하고 신뢰 정책을 구성할 수 있습니다.',
          '최소 권한 사용자에게 특정 역할을 맡을 수 있는 AssumeRole 권한을 부여할 수 있습니다.',
          'AWS CLI에서 AWS STS AssumeRole로 역할을 전환할 수 있습니다.',
          '임시 자격증명으로 리소스에 접근하여 역할 동작을 확인할 수 있습니다.',
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
          'Amazon VPC Endpoint의 개념과 프라이빗 연결의 이점을 이해할 수 있습니다.',
          'AWS Systems Manager Interface Endpoint를 생성하고 구성할 수 있습니다.',
          'Amazon S3 Gateway Endpoint를 생성하고 라우팅 테이블을 확인할 수 있습니다.',
          'Amazon VPC Endpoint를 통한 프라이빗 연결을 검증하고 동작을 확인할 수 있습니다.',
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
          '보안 그룹과 NACL의 차이점(상태 저장 vs 무상태, 규칙 평가 방식)을 이해할 수 있습니다.',
          '3-tier 아키텍처의 각 계층(ALB, Web, App, DB)에 보안 그룹 규칙을 구성할 수 있습니다.',
          'Public/Private 서브넷용 NACL을 생성하고 서브넷에 연결할 수 있습니다.',
          '보안 그룹 체인과 NACL의 동작을 검증할 수 있습니다.',
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
          'Amazon Cognito User Pool을 생성하고 구성할 수 있습니다.',
          'Amazon API Gateway Authorizer를 생성하고 메서드에 연결할 수 있습니다.',
          'Amazon Cognito 사용자를 생성하고 인증 토큰을 획득할 수 있습니다.',
          '인증된 API 요청을 테스트하고 검증할 수 있습니다.',
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
          'Amazon EventBridge의 이벤트 기반 아키텍처와 이벤트 패턴 매칭을 이해할 수 있습니다.',
          'ReservationCreated 이벤트 규칙을 생성하고 AWS Lambda를 연결할 수 있습니다.',
          'TableUnavailable 이벤트 규칙을 생성하고 알림을 구성할 수 있습니다.',
          '이벤트 기반 워크플로우를 테스트하고 검증할 수 있습니다.',
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
          'Amazon RDS Multi-AZ와 Read Replica의 차이점(고가용성 vs 읽기 확장)을 이해할 수 있습니다.',
          'Amazon RDS MySQL 인스턴스를 Multi-AZ로 생성하고 페일오버를 시뮬레이션할 수 있습니다.',
          'Amazon RDS Read Replica를 생성하고 읽기 부하를 분산할 수 있습니다.',
          '수동 스냅샷과 자동 백업을 생성하고 관리할 수 있습니다.',
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
          'Amazon DynamoDB 테이블을 생성하고 파티션 키/정렬 키를 설계할 수 있습니다.',
          'LSI(Local Secondary Index)를 사용하여 날짜 기반 쿼리를 수행할 수 있습니다.',
          'GSI(Global Secondary Index)를 생성하여 다양한 쿼리 패턴을 지원할 수 있습니다.',
          'AWS CLI와 콘솔을 사용하여 항목을 추가/조회/업데이트할 수 있습니다.',
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
          'Infrastructure as Code의 개념과 AWS CloudFormation의 이점을 이해할 수 있습니다.',
          'AWS CloudFormation 스택을 생성하고 Amazon S3 버킷을 배포할 수 있습니다.',
          '변경 세트를 사용하여 스택을 안전하게 업데이트할 수 있습니다.',
          '드리프트 감지로 수동 변경을 감지하고 스택을 삭제할 수 있습니다.',
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
          'AWS CloudFormation 템플릿의 기본 구조(Resources, Parameters, Outputs, Mappings)를 이해할 수 있습니다.',
          'Amazon VPC, 서브넷, 보안 그룹, Amazon EC2 인스턴스 템플릿 구조를 분석할 수 있습니다.',
          'AWS CloudFormation 스택을 생성하고 리소스를 배포할 수 있습니다.',
          '스택 리소스를 확인하고 웹 서버 동작을 테스트할 수 있습니다.',
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
          'AWS Infrastructure Composer의 시각적 설계 기능을 이해할 수 있습니다.',
          'Amazon DynamoDB, AWS Lambda, AWS IAM 역할을 드래그 앤 드롭으로 추가하고 연결할 수 있습니다.',
          'Amazon API Gateway를 추가하고 AWS Lambda 함수와 통합할 수 있습니다.',
          '생성된 AWS CloudFormation 템플릿을 검토하고 배포할 수 있습니다.',
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
          'Kubernetes의 기본 개념(Pod, Deployment, Service)과 Amazon EKS 아키텍처를 이해할 수 있습니다.',
          'kubectl을 구성하고 Amazon EKS 클러스터에 연결할 수 있습니다.',
          'Pod와 Deployment를 생성하고 롤링 업데이트/롤백을 수행할 수 있습니다.',
          'Kubernetes Service를 생성하고 애플리케이션을 외부에 노출할 수 있습니다.',
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
        awsServices: [],
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
          'CI/CD의 개념과 AWS CodeBuild의 빌드 프로세스를 이해할 수 있습니다.',
          'buildspec.yml 파일을 분석하고 빌드 단계를 이해할 수 있습니다.',
          'AWS CodeBuild 프로젝트를 생성하고 Docker 이미지를 빌드할 수 있습니다.',
          '빌드를 실행하고 Amazon ECR에 푸시된 이미지를 검증할 수 있습니다.',
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
        awsServices: ['AWS CodePipeline', 'AWS CodeBuild', 'AWS CodeCommit', 'Amazon S3', 'AWS CloudFormation'],
        learningObjectives: [
          'AWS CodePipeline의 파이프라인 단계(Source, Build)를 이해할 수 있습니다.',
          '정적 웹사이트 파일을 AWS CodeCommit에 푸시하고 파이프라인을 트리거할 수 있습니다.',
          'AWS CodePipeline을 통해 Amazon S3에 자동 배포되는 과정을 확인할 수 있습니다.',
          '코드 변경 후 자동 배포를 테스트하고 웹사이트를 확인할 수 있습니다.',
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
        title: '캐싱 개요와 전략',
        hasContent: false,
        description:
          '캐시 개념 및 동작 방식, 캐시 관리, 캐시 계층 구조',
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
          '캐싱 전략(Cache-Aside, Write-Through)과 Valkey 데이터 구조를 이해할 수 있습니다.',
          'Amazon ElastiCache Valkey 캐시를 생성하고 엔드포인트를 확인할 수 있습니다.',
          'Amazon EC2 인스턴스에서 Valkey CLI로 기본 명령어를 실습할 수 있습니다.',
          'Cache-Aside 패턴을 적용한 애플리케이션을 테스트할 수 있습니다.',
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
        awsServices: ['Amazon CloudFront', 'Amazon S3'],
        learningObjectives: [
          'CDN의 개념과 Amazon CloudFront의 엣지 로케이션 동작 원리를 이해할 수 있습니다.',
          'Amazon S3 오리진을 준비하고 Amazon CloudFront 배포를 생성할 수 있습니다.',
          '캐시 정책을 구성하고 TTL을 설정할 수 있습니다.',
          '캐시 무효화를 수행하고 Amazon CloudFront 성능을 확인할 수 있습니다.',
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
          '데이터 레이크의 개념과 AWS Glue Data Catalog의 역할을 이해할 수 있습니다.',
          'AWS Glue Crawler를 생성하고 Amazon S3 데이터의 스키마를 자동 검색할 수 있습니다.',
          'Amazon Athena로 AWS Glue 데이터 카탈로그를 쿼리할 수 있습니다.',
          '파티셔닝을 적용하여 쿼리 성능을 최적화할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'AWS Glue를 활용한 데이터 파이프라인 구축',
        hasContent: true,
        markdownPath: '/content/week11/11-3-data-pipeline.md',
        description:
          'AWS Glue Visual ETL 기반 데이터 파이프라인, Amazon Athena 쿼리 분석, EventBridge와 Lambda를 활용한 이벤트 기반 자동화',
        awsServices: ['AWS Glue', 'Amazon Athena', 'Amazon S3', 'AWS Lambda', 'Amazon EventBridge'],
        learningObjectives: [
          'AWS Glue Database를 생성하고 Crawler를 구성하여 Amazon S3 데이터의 스키마를 자동으로 추론하고 Data Catalog 테이블을 생성할 수 있습니다.',
          'AWS Glue Visual ETL Job을 생성하여 CSV 데이터를 Parquet 형식으로 변환하는 ETL 파이프라인을 구성할 수 있습니다.',
          'Amazon Athena로 변환된 데이터를 SQL로 쿼리하고 분석할 수 있습니다.',
          'EventBridge와 AWS Lambda를 활용한 이벤트 기반 데이터 파이프라인 자동화 흐름을 이해할 수 있습니다.',
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
      '자격증명 관리, AWS Config, AWS WAF를 통한 보안 자동화 및 규정 준수를 학습합니다',
    sessions: [
      {
        session: 1,
        type: 'lab',
        title: 'AWS Secrets Manager와 AWS Systems Manager를 활용한 자격증명 관리',
        hasContent: true,
        markdownPath: '/content/week12/12-1-credentials-management.md',
        description:
          '자격증명 관리 아키텍처 설계, AWS Systems Manager Parameter Store 구성, AWS Secrets Manager 구성',
        awsServices: ['AWS Secrets Manager', 'AWS Systems Manager', 'AWS KMS', 'Amazon RDS', 'AWS Lambda'],
        learningObjectives: [
          'AWS Secrets Manager에 Amazon RDS 자격증명을 저장하고 자동 로테이션을 설정할 수 있습니다.',
          'AWS Systems Manager Parameter Store와 AWS Secrets Manager의 차이점을 이해할 수 있습니다.',
          'AWS Lambda 함수에서 Secrets Manager와 Parameter Store를 조회하고 RDS에 연결할 수 있습니다.',
          '자동 로테이션을 통해 비밀번호를 안전하게 관리할 수 있습니다.',
        ],
      },
      {
        session: 2,
        type: 'demo',
        title: 'AWS Config 규칙 생성 및 모니터링',
        hasContent: true,
        markdownPath: '/content/week12/12-2-aws-config-demo.md',
        description:
          '클라우드 규정 준수 개요, AWS Config를 활용한 규정 준수 확인, AWS Config 고급 기능',
        awsServices: ['AWS Config'],
        learningObjectives: [
          'AWS Config의 개념과 규정 준수 모니터링의 중요성을 이해할 수 있습니다.',
          'AWS Config를 활성화하고 리소스 구성 변경을 기록할 수 있습니다.',
          '관리형 규칙을 추가하여 Amazon S3 버킷 암호화를 검증할 수 있습니다.',
          '규정 준수 대시보드를 확인하고 비준수 리소스를 수정할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'AWS WAF와 AWS Shield를 활용한 웹 애플리케이션 보안',
        hasContent: true,
        markdownPath: '/content/week12/12-3-waf-api-protection.md',
        description:
          'AWS WAF 개요 및 동작 원리, WAF 규칙 유형과 관리형 규칙, AWS Shield 및 DDoS 방어 아키텍처',
        awsServices: ['AWS WAF', 'AWS Shield', 'Amazon GuardDuty', 'AWS Security Hub'],
        learningObjectives: [
          'AWS WAF의 구성 요소와 동작 방식을 이해하고 Web ACL과 규칙을 구성할 수 있습니다.',
          'AWS Shield Standard와 Advanced의 차이를 이해하고 DDoS 방어 아키텍처를 설명할 수 있습니다.',
          'Amazon GuardDuty의 위협 탐지 방식과 AWS Security Hub를 활용한 통합 보안 관리 방법을 설명할 수 있습니다.',
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
        type: 'demo',
        title: 'AWS X-Ray를 활용한 서버리스 애플리케이션 추적',
        hasContent: true,
        markdownPath: '/content/week13/13-2-xray-tracing.md',
        description:
          'AWS X-Ray 개요 및 구성요소, 서비스 맵과 트레이스 분석, AWS X-Ray 컨테이너 및 서버리스 적용',
        awsServices: ['AWS X-Ray'],
        learningObjectives: [
          '분산 추적의 개념과 AWS X-Ray의 트레이스 구조를 이해할 수 있습니다.',
          'AWS Lambda 함수에 통합된 AWS X-Ray SDK 코드 패턴을 이해하고 Active tracing 설정을 확인할 수 있습니다.',
          'AWS X-Ray 서비스 맵으로 애플리케이션 구조를 시각화할 수 있습니다.',
          '트레이스를 분석하여 병목 지점과 오류를 파악할 수 있습니다.',
        ],
      },
      {
        session: 3,
        type: 'lab',
        title: 'Amazon CloudWatch Container Insights로 Amazon EKS 모니터링',
        hasContent: true,
        markdownPath: '/content/week13/13-3-container-insights-eks.md',
        description:
          '컨테이너 관찰 가능성 개요, 컨테이너 메트릭과 로그 수집, Amazon CloudWatch Container Insights',
        awsServices: ['Amazon CloudWatch', 'Amazon EKS'],
        learningObjectives: [
          'Container Insights의 개념과 컨테이너 메트릭 수집 구조를 이해할 수 있습니다.',
          'Container Insights를 활성화하고 AWS CloudWatch 에이전트를 배포할 수 있습니다.',
          'AWS CloudWatch 대시보드에서 클러스터 메트릭을 확인할 수 있습니다.',
          'AWS CloudWatch Logs Insights로 컨테이너 로그를 쿼리하고 분석할 수 있습니다.',
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
          'Amazon Bedrock Playground에서 Claude 모델을 선택하고 프롬프트를 실습할 수 있습니다.',
          'Zero-shot, Few-shot, Chain-of-Thought 프롬프팅 기법을 실습할 수 있습니다.',
          '시스템 프롬프트와 파라미터(Temperature, Top P)를 조정할 수 있습니다.',
          '프롬프트 기법별 응답 품질을 비교하고 평가할 수 있습니다.',
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
          'RAG(Retrieval-Augmented Generation)의 개념과 벡터 임베딩 원리를 이해할 수 있습니다.',
          'Amazon S3에 문서를 업로드하고 Amazon Bedrock Knowledge Base를 생성할 수 있습니다.',
          '벡터 임베딩을 생성하고 Amazon OpenSearch Serverless에 저장할 수 있습니다.',
          'Amazon Bedrock Knowledge Base를 쿼리하고 RAG 기반 응답을 확인할 수 있습니다.',
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
          'Amazon Bedrock Agents의 자율 에이전트 아키텍처와 ReAct 프롬프팅을 이해할 수 있습니다.',
          'AWS Lambda 함수로 Action Group을 생성하고 에이전트와 연결할 수 있습니다.',
          'Amazon Bedrock Knowledge Base를 에이전트에 연결하여 RAG 기능을 통합할 수 있습니다.',
          '에이전트를 테스트하고 다단계 작업을 수행할 수 있습니다.',
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
