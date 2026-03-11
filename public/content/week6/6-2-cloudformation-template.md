---
title: "AWS CloudFormation 템플릿 분석 및 스택 배포"
week: 6
session: 2
awsServices:
  - AWS CloudFormation
  - Amazon VPC
learningObjectives:
  - AWS CloudFormation 템플릿의 기본 구조(Resources, Parameters, Outputs, Mappings)를 이해할 수 있습니다.
  - Amazon VPC, 서브넷, 보안 그룹, Amazon EC2 인스턴스 템플릿 구조를 분석할 수 있습니다.
  - AWS CloudFormation 스택을 생성하고 리소스를 배포할 수 있습니다.
  - 스택 리소스를 확인하고 웹 서버 동작을 테스트할 수 있습니다.
prerequisites:
  - Amazon VPC 및 Amazon EC2 기본 개념 이해
  - YAML 문법 기본 지식
---

> [!DOWNLOAD]
> [week6-2-cloudformation-lab.zip](/files/week6/week6-2-cloudformation-lab.zip)
> - `vpc-ec2-template.yaml` - 완전한 Amazon VPC + Amazon EC2 인프라 템플릿 (태스크 2에서 템플릿 분석, 태스크 4에서 스택 생성)
> 
> **관련 태스크:**
> 
> - 태스크 2: Amazon VPC 템플릿 구조 확인 (vpc-ec2-template.yaml 분석)
> - 태스크 4: AWS CloudFormation 스택 생성 (vpc-ec2-template.yaml로 Amazon VPC 인프라 생성)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 스택을 삭제해야 합니다.
> 
> **예상 비용** (ap-northeast-2 리전 기준):
> 
> | 리소스 | 타입 | 시간당 비용 | Free Tier |
> |--------|------|------------|-----------|
> | Amazon EC2 인스턴스 | t3.micro | 약 $0.0116 | 월 750시간 무료 (12개월) |
> | AWS CloudFormation | - | 무료 | - |
> 
> **참고**: AWS Free Tier 계정(가입 후 12개월 이내)에서는 t3.micro 인스턴스를 월 750시간까지 무료로 사용할 수 있습니다.

## 태스크 1: AWS CloudFormation 템플릿 기본 구조 이해

> [!NOTE] Week 6-1 복습
> Week 6-1 데모에서 AWS CloudFormation의 IaC 개념, 템플릿 구조, 스택 생명주기를 학습했습니다.
> 이번 실습에서는 실제 Amazon VPC 환경을 구축하는 템플릿을 분석하고 배포합니다.

AWS CloudFormation 템플릿은 다음 섹션으로 구성됩니다:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 템플릿 설명

Parameters:
  # 사용자 입력 파라미터

Resources:
  # 생성할 AWS 리소스 (필수)

Outputs:
  # 스택 출력값
```

> [!NOTE]
> **Resources** 섹션만 필수이며, 나머지는 선택사항입니다.
> 
> - **Parameters**: 스택 생성 시 사용자가 입력하는 값 (Amazon VPC CIDR, 인스턴스 타입 등)
> - **Resources**: 생성할 AWS 리소스 정의 (Amazon VPC, 서브넷, Amazon EC2 등)
> - **Outputs**: 스택 생성 후 출력할 값 (Amazon VPC ID, 인스턴스 IP 등)

✅ **태스크 완료**: 템플릿 구조를 확인했습니다.

## 태스크 2: Amazon VPC 템플릿 구조 확인

이 태스크에서는 제공된 `vpc-ec2-template.yaml` 템플릿의 구조를 확인합니다. 이 템플릿에는 Amazon VPC, 서브넷, 라우팅 테이블, 보안 그룹, Amazon EC2 인스턴스가 모두 정의되어 있습니다.

1. 다운로드한 `week6-2-cloudformation-lab.zip` 파일의 압축을 해제합니다.
2. `vpc-ec2-template.yaml` 파일을 텍스트 에디터로 엽니다.
3. 템플릿 구조를 확인합니다:
	- **Parameters**: EnvironmentName, VpcCIDR, PublicSubnetCIDR, InstanceType, LatestAmiId
	- **Resources**: Amazon VPC, InternetGateway, Subnet, RouteTable, SecurityGroup, Amazon EC2 Instance
	- **Outputs**: VPCId, PublicSubnetId, WebServerPublicIP, WebServerURL

> [!NOTE]
> 이 템플릿은 완전한 웹 서버 환경을 구축하는 모든 리소스를 포함하고 있습니다.
> Week 6-2에서는 이 템플릿을 사용하여 스택을 생성하고 관리하는 방법을 학습합니다.

### Parameters 섹션

4. Parameters 섹션을 확인합니다:

```yaml
Parameters:
  EnvironmentName:
    Type: String
    Default: Lab
    Description: Environment name prefix for resources
  
  VpcCIDR:
    Type: String
    Default: 10.0.0.0/16
    Description: CIDR block for Amazon VPC
  
  PublicSubnetCIDR:
    Type: String
    Default: 10.0.1.0/24
    Description: CIDR block for public subnet
  
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues:
      - t2.micro
      - t2.small
      - t3.micro
    Description: Amazon EC2 instance type
  
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
    Description: Latest Amazon Linux 2023 AMI ID from SSM Parameter Store

  ProjectTag:
    Type: String
    Default: 'AWS-Lab'
    Description: Project tag value

  WeekTag:
    Type: String
    Default: '6-2'
    Description: Week tag value

  CreatedByTag:
    Type: String
    Default: 'CloudFormation'
    Description: CreatedBy tag value
```

> [!NOTE] Parameters 주요 속성
> 
> - **Type**: 파라미터 타입 (String, Number, List 등)
> - **Default**: 기본값 (사용자가 입력하지 않으면 사용)
> - **AllowedValues**: 허용된 값 목록 (드롭다운으로 표시)
> - **AWS::SSM::Parameter::Value**: SSM Parameter Store에서 최신 AMI ID 자동 조회

### Resources 섹션 - Amazon VPC 및 네트워크

5. VPC 정의를 확인합니다:

```yaml
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCIDR
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-VPC'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
```

6. InternetGateway 및 연결을 확인합니다:

```yaml
  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-IGW'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
  
  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway
```

> [!NOTE] VPC 및 InternetGateway
> 
> - **!Ref VpcCIDR**: Parameters에서 정의한 VpcCIDR 값 참조
> - **!Sub**: 문자열 치환 - `${EnvironmentName}`을 실제 값으로 대체
> - **VPCGatewayAttachment**: VPC와 InternetGateway를 연결

7. 서브넷 정의를 확인합니다:

```yaml
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Ref PublicSubnetCIDR
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-Public-Subnet'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
```

> [!NOTE] 서브넷 및 내장 함수
> 
> - **!Ref VPC**: VPC 리소스의 ID 참조
> - **!GetAZs ''**: 현재 리전의 모든 가용 영역 목록을 가져옴
> - **!Select [0, !GetAZs '']**: 첫 번째 가용 영역을 선택
> - **MapPublicIpOnLaunch**: Public 서브넷에서 인스턴스 생성 시 자동으로 퍼블릭 IP 할당

8. 라우팅 테이블 정의를 확인합니다:

```yaml
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-Public-RT'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway
```

> [!NOTE] 라우팅 및 DependsOn
> 
> - **DependsOn**: 리소스 생성 순서를 명시적으로 지정
> - AttachGateway가 완료된 후 DefaultPublicRoute 생성
> - **0.0.0.0/0**: 모든 외부 트래픽을 InternetGateway로 라우팅

9. 서브넷과 라우팅 테이블 연결을 확인합니다:

```yaml
  SubnetRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet
      RouteTableId: !Ref PublicRouteTable
```

✅ **태스크 완료**: Amazon VPC 템플릿 구조를 확인했습니다.

## 태스크 3: 보안 그룹 및 Amazon EC2 인스턴스 확인

이 태스크에서는 템플릿에 정의된 보안 그룹과 Amazon EC2 인스턴스를 확인합니다. 보안 그룹은 Amazon EC2 인스턴스의 인바운드 및 아웃바운드 트래픽을 제어하는 가상 방화벽 역할을 합니다.

### 보안 그룹

10. Resources 섹션에서 보안 그룹 정의를 확인합니다:

```yaml
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub '${EnvironmentName}-Web-SG'
      GroupDescription: Security group for web server
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
          Description: Allow HTTP
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-Web-SG'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
```

> [!NOTE] 보안 그룹 인바운드 규칙
> 
> **SecurityGroupIngress**: 인바운드 규칙 정의
> - 포트 80 (HTTP): 모든 IP에서 접근 허용
> - **CidrIp: 0.0.0.0/0**: 모든 IP 주소에서 접근 허용
> 
> **SSH 포트 제거**: 이 실습에서는 SSH 접속을 하지 않으므로 포트 22를 제거했습니다.
> 프로덕션 환경에서는 AWS Systems Manager Session Manager를 사용하는 것이 권장됩니다.

### Amazon EC2 인스턴스

11. Amazon EC2 인스턴스 정의를 확인합니다:

```yaml
  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: !Ref LatestAmiId
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref WebServerSecurityGroup
      IamInstanceProfile: !Ref WebServerInstanceProfile
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from AWS CloudFormation!</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-Web-Server'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
```

> [!NOTE] Amazon EC2 인스턴스 주요 속성
> 
> - **ImageId**: SSM Parameter Store에서 최신 Amazon Linux 2023 AMI 자동 조회
> - **IamInstanceProfile**: SSM Session Manager 접속을 위한 AWS IAM 역할
> - **UserData**: 인스턴스 시작 시 자동으로 실행되는 스크립트
> - **Fn::Base64**: UserData는 Base64로 인코딩되어야 함
> - **!Sub |**: 여러 줄 문자열을 치환하며, 변수 사용 가능

### AWS IAM 역할 (Session Manager용)

12. AWS IAM 역할 정의를 확인합니다:

```yaml
  WebServerRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Tags:
        - Key: Name
          Value: !Sub '${EnvironmentName}-WebServer-Role'
        - Key: Project
          Value: !Ref ProjectTag
        - Key: Week
          Value: !Ref WeekTag
        - Key: CreatedBy
          Value: !Ref CreatedByTag
  
  WebServerInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref WebServerRole
```

> [!NOTE] AWS IAM 역할 및 Session Manager
> 
> - **AmazonSSMManagedInstanceCore**: Session Manager로 인스턴스에 접속하기 위한 정책
> - **InstanceProfile**: Amazon EC2 인스턴스에 AWS IAM 역할을 연결하는 리소스
> - Key Pair 없이도 Session Manager를 통해 안전하게 인스턴스에 접속 가능

### Outputs 섹션

13. Outputs 섹션을 확인합니다:

```yaml
Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${EnvironmentName}-VPC-ID'
  
  PublicSubnetId:
    Description: Public Subnet ID
    Value: !Ref PublicSubnet
    Export:
      Name: !Sub '${EnvironmentName}-Public-Subnet-ID'
  
  WebServerPublicIP:
    Description: Web Server Public IP
    Value: !GetAtt WebServer.PublicIp
  
  WebServerURL:
    Description: Web Server URL
    Value: !Sub 'http://${WebServer.PublicIp}'
```

> [!NOTE] Outputs 주요 속성
> 
> - **Value**: 출력할 값 (!Ref 또는 !GetAtt 사용)
> - **!GetAtt**: 리소스의 속성값을 가져옴 (예: PublicIp)
> - **Export**: 다른 스택에서 참조할 수 있도록 내보내기
> - **!Sub**: 문자열 치환으로 URL 생성

✅ **태스크 완료**: 보안 그룹, Amazon EC2 인스턴스, AWS IAM 역할, Outputs를 확인했습니다.

## 태스크 4: AWS CloudFormation 스택 생성

이 태스크에서는 완성된 템플릿을 사용하여 AWS CloudFormation 스택을 생성합니다. 스택 생성 과정에서 Amazon VPC, 서브넷, 라우팅 테이블, 보안 그룹, Amazon EC2 인스턴스가 자동으로 생성됩니다.

14. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
15. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
16. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
17. **Specify template**에서 `Upload a template file`을 선택합니다.
18. [[Choose file]] 버튼을 클릭하고 `vpc-ec2-template.yaml` 파일을 선택합니다.
19. [[Next]] 버튼을 클릭합니다.
20. **Stack name**에 `lab-vpc-stack`을 입력합니다.
21. **Parameters** 섹션에서 다음 값을 확인합니다:
	- **EnvironmentName**: `Lab` (기본값 유지)
	- **VpcCIDR**: `10.0.0.0/16` (기본값 유지)
	- **PublicSubnetCIDR**: `10.0.1.0/24` (기본값 유지)
   - **InstanceType**: `t3.micro` (기본값 유지)
   - **LatestAmiId**: 기본값 유지 (최신 Amazon Linux 2023 AMI 자동 조회)
   - **ProjectTag**: `AWS-Lab` (기본값 유지)
   - **WeekTag**: `6-2` (기본값 유지)
   - **CreatedByTag**: `CloudFormation` (기본값 유지)

> [!NOTE]
> 이 템플릿은 Key Pair 없이 AWS Systems Manager Session Manager를 사용하여 인스턴스에 접속할 수 있도록 구성되어 있습니다.
> AWS IAM 역할에 `AmazonSSMManagedInstanceCore` 정책이 연결되어 있어 안전하게 인스턴스를 관리할 수 있습니다.

22. [[Next]] 버튼을 클릭합니다.
23. **Configure stack options** 페이지에서 **Tags** 섹션으로 스크롤합니다.
24. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key | Value |
|-----|-------|
| `Project` | `AWS-Lab` |
| `Week` | `6-2` |
| `CreatedBy` | `CloudFormation` |

25. **Capabilities** 섹션으로 스크롤합니다.
26. ☑️ `I acknowledge that AWS CloudFormation might create IAM resources`를 체크합니다.

> [!NOTE]
> 이 템플릿은 Session Manager 접속을 위한 IAM 역할(`WebServerRole`)과 인스턴스 프로파일(`WebServerInstanceProfile`)을 생성합니다.
> IAM 리소스를 생성하려면 반드시 Capabilities를 확인해야 합니다.

27. [[Next]] 버튼을 클릭합니다.
28. **Review and create** 페이지에서 설정을 확인합니다.
29. [[Submit]] 버튼을 클릭합니다.
30. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 3-5분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

31. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: AWS CloudFormation 스택이 생성되었습니다.

## 태스크 5: 스택 리소스 확인

이 태스크에서는 AWS CloudFormation이 생성한 리소스들을 확인합니다. Resources 탭에서 각 리소스의 Logical ID와 Physical ID 관계를 이해하고, 리소스 생성 순서를 확인합니다.

### Resources 탭 확인

32. `lab-vpc-stack`을 선택합니다.
33. 하단의 **Resources** 탭을 선택합니다.
34. 생성된 리소스 목록을 확인합니다:

| Logical ID | Type | Physical ID |
|-----------|------|-------------|
| VPC | AWS::EC2::VPC | vpc-xxxxx |
| InternetGateway | AWS::EC2::InternetGateway | igw-xxxxx |
| AttachGateway | AWS::EC2::VPCGatewayAttachment | - |
| PublicSubnet | AWS::EC2::Subnet | subnet-xxxxx |
| PublicRouteTable | AWS::EC2::RouteTable | rtb-xxxxx |
| DefaultPublicRoute | AWS::EC2::Route | - |
| SubnetRouteTableAssociation | AWS::EC2::SubnetRouteTableAssociation | - |
| WebServerSecurityGroup | AWS::EC2::SecurityGroup | sg-xxxxx |
| WebServerRole | AWS::IAM::Role | lab-vpc-stack-WebServerRole-xxxxx |
| WebServerInstanceProfile | AWS::IAM::InstanceProfile | lab-vpc-stack-WebServerInstanceProfile-xxxxx |
| WebServer | AWS::EC2::Instance | i-xxxxx |

> [!NOTE] Logical ID vs Physical ID
> 
> - **Logical ID**: 템플릿에서 정의한 리소스 이름 (예: VPC, WebServer)
> - **Physical ID**: AWS가 실제로 생성한 리소스의 고유 ID (예: vpc-xxxxx, i-xxxxx)
> - 일부 리소스(AttachGateway, Route, Association)는 Physical ID가 없습니다 (연결 리소스)

35. **VPC** 리소스의 Physical ID (vpc-xxxxx)를 클릭합니다.
36. VPC 콘솔로 이동하여 VPC 상세 정보를 확인합니다.
37. 브라우저 뒤로가기 버튼을 클릭하여 AWS CloudFormation 콘솔로 이동합니다.
38. **WebServer** 리소스의 Physical ID (i-xxxxx)를 클릭합니다.
39. EC2 콘솔로 이동하여 인스턴스 상세 정보를 확인합니다.

> [!NOTE] 리소스 생성 순서
> 
> AWS CloudFormation은 리소스 간 의존성을 자동으로 파악하여 올바른 순서로 생성합니다:
> 1. VPC → InternetGateway → AttachGateway
> 2. PublicSubnet → PublicRouteTable → DefaultPublicRoute
> 3. SubnetRouteTableAssociation
> 4. WebServerSecurityGroup
> 5. WebServerRole → WebServerInstanceProfile
> 6. WebServer (모든 의존 리소스가 준비된 후 마지막에 생성)

### Outputs 탭 확인

40. AWS CloudFormation 콘솔로 이동합니다.
41. 하단의 **Outputs** 탭을 선택합니다.
42. 출력값을 확인합니다:

| Key | Value | Export Name |
|-----|-------|-------------|
| VPCId | vpc-xxxxx | Lab-VPC-ID |
| PublicSubnetId | subnet-xxxxx | Lab-Public-Subnet-ID |
| WebServerPublicIP | x.x.x.x | - |
| WebServerURL | http://x.x.x.x | - |

> [!NOTE] Outputs 활용
> 
> - **Export Name**: 다른 스택에서 `!ImportValue` 함수로 참조 가능
> - VPCId는 Export되어 있어 다른 스택에서 이 VPC를 참조할 수 있습니다
> - WebServerURL은 바로 복사하여 브라우저에서 테스트 가능

43. **WebServerURL** 값을 복사하여 메모장에 저장합니다.

> [!NOTE]
> 이 URL은 다음 태스크에서 웹 서버 테스트에 사용됩니다.

✅ **태스크 완료**: 스택 리소스와 출력값을 확인했습니다.

## 태스크 6: 웹 서버 테스트

이 태스크에서는 AWS CloudFormation으로 생성된 EC2 인스턴스의 웹 서버가 정상적으로 작동하는지 확인합니다. UserData 스크립트로 자동 설치된 Apache 웹 서버에 접속하여 테스트 페이지를 확인합니다.

44. **Outputs** 탭에서 **WebServerURL** 값을 복사합니다.
45. 새 브라우저 탭을 열고 복사한 URL을 붙여넣습니다.
46. "Hello from AWS CloudFormation!" 메시지가 표시되는지 확인합니다.

> [!NOTE]
> 인스턴스가 완전히 시작되고 웹 서버가 실행되기까지 2-3분이 소요될 수 있습니다.
> 페이지가 표시되지 않으면 1-2분 후 다시 시도합니다.

✅ **태스크 완료**: 웹 서버가 정상적으로 작동합니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation 템플릿의 구조를 이해했습니다
- YAML 형식으로 정의된 Amazon VPC, 서브넷, 보안 그룹, Amazon EC2 인스턴스 템플릿을 분석하고 배포했습니다
- 파라미터와 출력값이 포함된 재사용 가능한 템플릿 구조를 이해했습니다
- 스택을 생성하고 리소스를 확인했습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `6-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 AWS CloudFormation 스택이 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Amazon VPC 스택 삭제

8. AWS CloudFormation 콘솔로 이동합니다.
9. `lab-vpc-stack`을 선택합니다.
10. [[Delete]] 버튼을 클릭합니다.
11. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 3-5분이 소요됩니다. AWS CloudFormation이 모든 리소스를 자동으로 삭제합니다.
> Amazon EC2 인스턴스, 보안 그룹, 라우팅 테이블, 인터넷 게이트웨이, 서브넷, Amazon VPC 순서로 삭제됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS CloudFormation 템플릿 레퍼런스](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/template-reference.html)
- [AWS CloudFormation 모범 사례](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/best-practices.html)
- [AWS CloudFormation 내장 함수](https://docs.aws.amazon.com/ko_kr/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html)

## 📚 참고: AWS CloudFormation 핵심 개념

### 템플릿 구조

**AWSTemplateFormatVersion**: 템플릿 형식 버전 (항상 2010-09-09 사용)

**Description**: 템플릿에 대한 설명

**Parameters**: 스택 생성 시 사용자가 입력할 수 있는 값들
- Type: String, Number, List 등
- Default: 기본값
- AllowedValues: 허용된 값 목록 (드롭다운으로 표시)
- AWS::SSM::Parameter::Value: SSM Parameter Store에서 값 자동 가져오기

**Resources**: 생성할 AWS 리소스 정의 (필수 섹션)

**Outputs**: 스택 생성 후 출력할 값들 (다른 스택에서 참조 가능)

### 내장 함수

**!Ref**: 파라미터 값이나 리소스 ID를 반환
```yaml
BucketName: !Ref MyS3Bucket
```

**!Sub**: 문자열 치환 - 변수를 실제 값으로 대체
```yaml
BucketName: !Sub '${BucketNamePrefix}-${AWS::AccountId}'
```

**!GetAtt**: 리소스의 속성값을 가져옴
```yaml
Value: !GetAtt WebServer.PublicIp
```

**!GetAZs**: 현재 리전의 모든 가용 영역 목록
```yaml
AvailabilityZone: !Select [0, !GetAZs '']
```

**Fn::Base64**: 문자열을 Base64로 인코딩 (UserData에 필수)
```yaml
UserData:
  Fn::Base64: !Sub |
    #!/bin/bash
    echo "Hello"
```

### 서브넷 및 라우팅

**MapPublicIpOnLaunch**: Public 서브넷에서 인스턴스 생성 시 자동으로 퍼블릭 IP 할당

**DependsOn**: 리소스 생성 순서를 명시적으로 지정
```yaml
DependsOn: AttachGateway
```

### 보안 그룹

**SecurityGroupIngress**: 인바운드 규칙 정의
- IpProtocol: tcp, udp, icmp 등
- FromPort/ToPort: 포트 범위
- CidrIp: 허용할 IP 범위 (0.0.0.0/0은 모든 IP)

**프로덕션 권장사항**: SSH(22) 포트는 특정 IP로 제한

### UserData

**UserData**: 인스턴스 시작 시 자동으로 실행되는 스크립트
- Base64로 인코딩 필요
- 여러 줄 문자열은 `!Sub |` 사용
- 변수 치환 가능

### Amazon Linux 2023 패키지 관리자

**yum vs dnf**: Amazon Linux 2023에서는 `dnf`가 기본 패키지 관리자이며, `yum`은 `dnf`의 심볼릭 링크로 동작합니다.
- 공식 문서에서는 `dnf` 사용을 권장하지만 `yum` 명령어도 정상 작동합니다
- 기존 스크립트와의 호환성을 위해 `yum` 명령어를 계속 사용할 수 있습니다
