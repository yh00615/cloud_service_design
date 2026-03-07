---
title: 'Amazon GuardDuty와 AWS Lambda 자동 대응'
week: 12
session: 3
awsServices:
  - Amazon GuardDuty
  - AWS Lambda
  - Amazon EventBridge
learningObjectives:
  - Amazon GuardDuty의 위협 탐지 원리와 자동 대응 아키텍처를 이해할 수 있습니다.
  - Amazon EventBridge 규칙으로 GuardDuty 결과를 AWS Lambda로 전달할 수 있습니다.
  - AWS Lambda 함수로 의심스러운 IAM 사용자를 자동으로 비활성화할 수 있습니다.
  - GuardDuty 콘솔에서 탐지된 위협을 확인하고 분석할 수 있습니다.

prerequisites:
  - AWS 계정 및 관리자 권한
  - 기본적인 보안 개념 이해
  - AWS Lambda 함수 기본 지식
---

이 데모에서는 Amazon GuardDuty를 활성화하고, QuickTable 레스토랑 예약 시스템에 대한 보안 위협이 탐지되었을 때 AWS Lambda 함수를 통해 자동으로 대응하는 시스템을 구축합니다.

Week 4-3에서 구축한 QuickTable 예약 API는 전 세계 사용자가 접근하는 퍼블릭 서비스이므로, 봇 공격, 과도한 예약 시도, 비정상적인 API 호출 패턴 등 다양한 보안 위협에 노출될 수 있습니다. 이 데모에서는 Amazon GuardDuty를 사용하여 QuickTable 인프라(Amazon API Gateway, AWS Lambda, Amazon DynamoDB)에 대한 위협을 실시간으로 탐지하고, Amazon EventBridge를 통해 AWS Lambda 함수로 자동 대응하는 보안 모니터링 시스템을 구현합니다.

위협 수준에 따라 자동으로 Amazon EC2 인스턴스를 격리하고, Amazon SNS 알림을 전송하는 실제 보안 자동화 시나리오를 시연합니다.

> [!DOWNLOAD]
> [week12-3-guardduty-lambda-lab.zip](/files/week12/week12-3-guardduty-lambda-lab.zip)
>
> - `lambda_function.py` - QuickTable 보안 자동 대응 AWS Lambda 함수 (태스크 4에서 AWS Lambda 함수 코드로 사용, Amazon GuardDuty Finding 처리 로직 포함, 상세한 주석 및 DocString 포함)
>
> **관련 태스크:**
>
> - 태스크 4: AWS Lambda 자동 대응 함수 생성 (lambda_function.py를 참고하여 QuickTable API 보안 위협 탐지 및 자동 대응 로직 구현)

> [!WARNING]
> Amazon GuardDuty는 30일 무료 평가판을 제공합니다. 평가판 이후에는 분석된 이벤트 수에 따라 비용이 발생합니다. 데모 완료 후 반드시 Amazon GuardDuty를 비활성화합니다.

## 태스크 1: Amazon GuardDuty 활성화

이 태스크에서는 Amazon GuardDuty를 활성화하고 위협 탐지를 시작합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `GuardDuty`을 입력하고 선택합니다.
2. [[Get Started]] 버튼을 클릭합니다.
3. [[Enable Amazon GuardDuty]] 버튼을 클릭합니다.
4. Amazon GuardDuty가 활성화되면 대시보드가 표시됩니다.

> [!CONCEPT] Amazon GuardDuty 작동 원리
> Amazon GuardDuty는 다음 데이터 소스를 지속적으로 분석합니다:
>
> **데이터 소스**:
>
> - **Amazon VPC Flow Logs**: 네트워크 트래픽 패턴 분석
> - **CloudTrail Event Logs**: API 호출 및 관리 활동 분석
> - **DNS Logs**: DNS 쿼리 패턴 분석
> - **Kubernetes Audit Logs**: Amazon EKS 클러스터 활동 분석 (선택적)
> - **Amazon S3 Data Events**: Amazon S3 버킷 접근 패턴 분석 (선택적)
>
> **위협 인텔리전스**:
>
> - AWS Security가 관리하는 위협 인텔리전스 피드
> - CrowdStrike, Proofpoint 등 파트너 피드
> - 머신러닝 기반 이상 탐지
>
> **Finding 심각도**:
>
> - **Low (1.0-3.9)**: 의심스러운 활동, 즉각적인 조치 불필요
> - **Medium (4.0-6.9)**: 잠재적 위협, 조사 권장
> - **High (7.0-8.9)**: 명확한 위협, 신속한 대응 필요
> - **Critical (9.0-10.0)**: 치명적 위협, 즉각적인 대응 필수 (2024년 추가)
>
> **자동 대응 임계값**:
>
> - 이 데모의 AWS Lambda 함수는 **7.0 이상** (High와 Critical 모두)에서 동일한 자동 대응(인스턴스 격리)을 수행합니다
> - High(7.0-8.9)와 Critical(9.0-10.0)은 심각도 레이블은 다르지만, 대응 조치는 동일합니다

5. 왼쪽 메뉴에서 **Settings**를 선택합니다.
6. **Finding export options**에서 Amazon S3 버킷 설정을 확인합니다 (선택사항).
7. **Sample findings** 옵션이 활성화되어 있는지 확인합니다.

✅ **태스크 완료**: Amazon GuardDuty가 활성화되었습니다.

## 태스크 2: Amazon SNS 토픽 생성 및 구독

이 태스크에서는 보안 알림을 받을 Amazon SNS 토픽을 생성하고 이메일 구독을 설정합니다.

8. 상단 검색창에 `SNS`를 입력하고 **Simple Notification Service**를 선택합니다.
9. 왼쪽 메뉴에서 **Topics**를 선택합니다.
10. [[Create topic]] 버튼을 클릭합니다.
11. **Type**에서 `Standard`를 선택합니다.
12. **Name**에 `Amazon GuardDuty-Security-Alerts`를 입력합니다.
13. **Display name**에 `Amazon GuardDuty Alerts`를 입력합니다.
14. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-3`    |
| `CreatedBy` | `Student` |

15. [[Create topic]] 버튼을 클릭합니다.
16. 생성된 토픽의 상세 페이지에서 [[Create subscription]] 버튼을 클릭합니다.
17. **Protocol**에서 `Email`을 선택합니다.
18. **Endpoint**에 알림을 받을 이메일 주소를 입력합니다.
19. [[Create subscription]] 버튼을 클릭합니다.
20. 입력한 이메일 주소로 확인 메일이 발송됩니다.
21. 이메일을 열고 **Confirm subscription** 링크를 클릭합니다.
22. Amazon SNS 콘솔에서 구독 상태가 "Confirmed"로 변경되었는지 확인합니다.
23. 토픽 상세 페이지에서 **ARN**을 복사합니다.
24. 메모장에 저장합니다 (AWS Lambda 함수에서 사용).

> [!NOTE]
> Amazon SNS 토픽 ARN은 다음과 같은 형식입니다:
> `arn:aws:sns:ap-northeast-2:123456789012:Amazon GuardDuty-Security-Alerts`

✅ **태스크 완료**: Amazon SNS 토픽이 생성되고 이메일 구독이 확인되었습니다.

## 태스크 3: AWS Lambda 실행 역할 생성

이 태스크에서는 AWS Lambda 함수가 필요한 AWS 서비스에 접근할 수 있도록 AWS IAM 역할을 생성합니다.

25. 상단 검색창에 `IAM`을 입력한 후 선택합니다.
26. 왼쪽 메뉴에서 **Roles**를 선택합니다.
27. [[Create role]] 버튼을 클릭합니다.
28. **Trusted entity type**에서 `AWS service`를 선택합니다.
29. **Use case**에서 `AWS Lambda`를 선택합니다.
30. [[Next]] 버튼을 클릭합니다.
31. 검색창에 `AWSLambdaBasicExecutionRole`을 입력하고 체크합니다.
32. [[Next]] 버튼을 클릭합니다.
33. **Role name**에 `Amazon GuardDuty-AWS Lambda-AutoResponse-Role`을 입력합니다.
34. **Description**에 `AWS Lambda function role for Amazon GuardDuty auto-response`를 입력합니다.
35. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-3`    |
| `CreatedBy` | `Student` |

36. [[Create role]] 버튼을 클릭합니다.
37. 생성된 역할을 클릭하여 상세 페이지로 이동합니다.
38. **Permissions** 탭에서 [[Add permissions]] → **Create inline policy**를 클릭합니다.
39. **JSON** 탭을 클릭합니다.

40. 다음 정책을 입력합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeSecurityGroups",
        "ec2:ModifyInstanceAttribute",
        "ec2:CreateSecurityGroup",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupEgress"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "arn:aws:sns:ap-northeast-2:{본인의 계정 ID}:Amazon GuardDuty-Security-Alerts"
    },
    {
      "Effect": "Allow",
      "Action": ["guardduty:GetFindings", "guardduty:ListFindings"],
      "Resource": "*"
    }
  ]
}
```

> [!WARNING]
> **Amazon SNS ARN 수정 필수**: `{본인의 계정 ID}` 부분을 태스크 2에서 복사한 실제 Amazon SNS 토픽 ARN의 계정 ID로 교체해야 합니다. 예: `arn:aws:sns:ap-northeast-2:123456789012:Amazon GuardDuty-Security-Alerts`

41. [[Next]] 버튼을 클릭합니다.
42. **Policy name**에 `Amazon GuardDuty-AutoResponse-Policy`를 입력합니다.
43. [[Create policy]] 버튼을 클릭합니다.

> [!CONCEPT] 최소 권한 원칙
> 이 정책은 AWS Lambda 함수가 필요한 최소한의 권한만 부여합니다:
>
> **Amazon EC2 권한**:
>
> - `DescribeInstances`: 인스턴스 정보 조회
> - `DescribeSecurityGroups`: 보안 그룹 정보 조회
> - `ModifyInstanceAttribute`: 인스턴스의 보안 그룹 변경 (이 권한은 인스턴스 타입, 커널, 사용자 데이터 등도 변경할 수 있으므로 프로덕션에서는 Condition으로 제한 권장)
> - `CreateSecurityGroup`: 격리 보안 그룹 생성 (필요시)
> - `AuthorizeSecurityGroup*`: 보안 그룹 규칙 설정
> - `RevokeSecurityGroupEgress`: 아웃바운드 규칙 제거
>
> **Amazon SNS 권한**:
>
> - `Publish`: 특정 Amazon SNS 토픽에만 메시지 발행
>
> **Amazon GuardDuty 권한**:
>
> - `GetFindings`: Finding 상세 정보 조회
> - `ListFindings`: Finding 목록 조회
>
> **프로덕션 환경 개선사항**:
>
> - Amazon EC2 Resource를 특정 Amazon VPC나 태그로 제한
> - Amazon SNS Resource ARN을 정확히 지정
> - Condition을 사용하여 특정 조건에서만 권한 허용
> - `ec2:ModifyInstanceAttribute`는 Condition으로 보안 그룹 변경만 허용하도록 제한

✅ **태스크 완료**: AWS Lambda 실행 역할이 생성되었습니다.

## 태스크 4: AWS Lambda 자동 대응 함수 생성

이 태스크에서는 Amazon GuardDuty Finding을 처리하고 자동 대응하는 AWS Lambda 함수를 생성합니다.

44. 상단 검색창에 `Lambda`를 입력한 후 선택합니다.
45. [[Create function]] 버튼을 클릭합니다.
46. **Function name**에 `Amazon GuardDuty-AutoResponse`를 입력합니다.
47. **Runtime**에서 `Python 3.13`을 선택합니다.
48. **Architecture**에서 `x86_64`를 선택합니다.
49. **Permissions** 섹션을 확장합니다.
50. **Execution role**에서 `Use an existing role`을 선택합니다.
51. **Existing role**에서 `Amazon GuardDuty-AWS Lambda-AutoResponse-Role`을 선택합니다.
52. **Advanced settings** 섹션을 확장합니다.
53. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-3`    |
| `CreatedBy` | `Student` |

54. [[Create function]] 버튼을 클릭합니다.
55. **Code** 탭에서 `lambda_function.py` 파일의 내용을 다음으로 교체합니다:

> [!TIP]
> 다운로드한 `lambda_function.py` 파일의 코드를 참고할 수 있습니다. 파일에는 상세한 주석과 DocString이 포함되어 있어 코드 이해에 도움이 됩니다.

```python
"""
AWS Lambda 함수: QuickTable 보안 자동 대응 시스템

이 AWS Lambda 함수는 Amazon GuardDuty에서 탐지된 QuickTable 레스토랑 예약 시스템에 대한
보안 위협(Finding)을 자동으로 처리하고 대응합니다.

주요 기능:
    1. Amazon GuardDuty Finding 정보 추출 및 분석 (QuickTable API 위협 패턴 감지).
    2. 심각도 기반 자동 대응 (High: 인스턴스 격리).
    3. 격리 보안 그룹 자동 생성 및 관리.
    4. Amazon SNS를 통한 보안 알림 전송 (QuickTable 운영팀).

환경 변수:
    Amazon SNS_TOPIC_ARN (str): Amazon SNS 토픽 ARN (보안 알림 전송용)

트리거:
    Amazon EventBridge 규칙 (Amazon GuardDuty Finding 이벤트)

QuickTable 보안 시나리오:
    - 봇 공격 탐지 → 로그 분석 및 알림
    - 과도한 예약 시도 → 사용자 계정 일시 정지
    - 비정상적인 API 호출 패턴 → 로그 분석 및 알림
    - Amazon EC2 인스턴스 침해 → 인스턴스 격리
"""

import json
import boto3
import os
from datetime import datetime

# AWS 클라이언트 초기화
ec2 = boto3.client('ec2')  # Amazon EC2 인스턴스 및 보안 그룹 관리
sns = boto3.client('sns')  # Amazon SNS 알림 전송

# 환경 변수
Amazon SNS_TOPIC_ARN = os.environ.get('Amazon SNS_TOPIC_ARN')  # Amazon SNS 토픽 ARN
ISOLATION_SG_NAME = 'Amazon GuardDuty-Isolation-SG'  # 격리 보안 그룹 이름


def lambda_handler(event, context):
    """
    Amazon GuardDuty Finding을 처리하고 자동 대응을 수행하는 AWS Lambda 함수

    Amazon EventBridge에서 전달된 Amazon GuardDuty Finding 이벤트를 분석하고,
    심각도에 따라 자동으로 대응 조치를 수행합니다.

    대응 로직:
        - High/Critical (7.0+): Amazon EC2 인스턴스를 격리 보안 그룹으로 이동 (High와 Critical 모두 동일한 대응)
        - Medium (4.0-6.9): 수동 검토 권장 알림만 전송
        - Low (0.1-3.9): 로그 기록만 수행

    Args:
        event (dict): Amazon EventBridge에서 전달된 Amazon GuardDuty Finding 이벤트
        context (LambdaContext): AWS Lambda 실행 컨텍스트

    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공)
            - body (str): JSON 형식의 처리 결과
    """
    # 환경 변수 검증 (Amazon SNS_TOPIC_ARN 필수)
    if not Amazon SNS_TOPIC_ARN:
        error_msg = "Amazon SNS_TOPIC_ARN environment variable is not set"
        print(f"ERROR: {error_msg}")
        raise ValueError(error_msg)

    # 이벤트 전체 내용을 로그에 출력 (디버깅용)
    print(f"Received event: {json.dumps(event)}")

    try:
        # Amazon GuardDuty Finding 정보 추출
        detail = event['detail']  # Amazon EventBridge 이벤트의 detail 섹션
        finding_id = detail['id']  # Finding 고유 ID
        finding_type = detail['type']  # Finding 타입
        severity = detail['severity']  # 심각도 점수 (0.1-10.0)
        title = detail['title']  # Finding 제목
        description = detail['description']  # Finding 상세 설명

        # 리소스 정보 추출
        resource = detail.get('resource', {})
        instance_details = resource.get('instanceDetails', {})
        instance_id = instance_details.get('instanceId')  # 영향받는 Amazon EC2 인스턴스 ID

        # 처리 시작 로그 출력
        print(f"Processing Finding: {finding_type}")
        print(f"Severity: {severity}")
        print(f"Instance ID: {instance_id}")

        # 심각도에 따른 자동 대응
        response_action = ""

        if severity >= 7.0:  # High/Critical (7.0+)
            # 심각한 위협: Amazon EC2 인스턴스 격리 (High와 Critical 모두 동일한 대응)
            if instance_id:
                response_action = isolate_instance(instance_id)
            else:
                response_action = "No instance to isolate (non-Amazon EC2 resource)"
            # Amazon SNS 알림 전송 (High/Critical만)
            send_notification(
                finding_type=finding_type,
                severity=severity,
                title=title,
                description=description,
                instance_id=instance_id,
                response_action=response_action
            )
        elif severity >= 4.0:  # Medium
            # 중간 수준 위협: 수동 검토 권장
            response_action = "Manual review recommended"
            print(response_action)  # Medium 처리 결과 로그 출력
            # Amazon SNS 알림 전송 (Medium)
            send_notification(
                finding_type=finding_type,
                severity=severity,
                title=title,
                description=description,
                instance_id=instance_id,
                response_action=response_action
            )
        else:  # Low
            # 낮은 수준 위협: 로그 기록만 (Amazon SNS 알림 없음)
            response_action = "Logged for monitoring"

        # 성공 응답 반환
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Auto-response completed',
                'finding_id': finding_id,
                'action': response_action
            })
        }

    except Exception as e:
        # 오류 발생 시 로그 출력 및 예외 재발생
        print(f"Error processing finding: {str(e)}")
        raise


def isolate_instance(instance_id):
    """
    Amazon EC2 인스턴스를 격리 보안 그룹으로 이동

    의심스러운 Amazon EC2 인스턴스의 보안 그룹을 격리 보안 그룹으로 변경하여
    모든 네트워크 트래픽을 차단합니다.

    Args:
        instance_id (str): 격리할 Amazon EC2 인스턴스 ID

    Returns:
        str: 수행된 조치 설명 또는 오류 메시지
    """
    try:
        # 인스턴스 정보 조회
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        vpc_id = instance['VpcId']  # 인스턴스가 속한 Amazon VPC ID

        # 격리 보안 그룹 확인 또는 생성
        isolation_sg_id = get_or_create_isolation_sg(vpc_id)

        # 인스턴스의 보안 그룹을 격리 보안 그룹으로 변경
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[isolation_sg_id]  # 보안 그룹 목록 (격리 SG만)
        )

        # 성공 메시지 생성 및 로그 출력
        action = f"Instance {instance_id} isolated with security group {isolation_sg_id}"
        print(action)
        return action

    except Exception as e:
        # 격리 실패 시 오류 메시지 반환
        error_msg = f"Failed to isolate instance {instance_id}: {str(e)}"
        print(error_msg)
        return error_msg


def get_or_create_isolation_sg(vpc_id):
    """
    격리 보안 그룹을 조회하거나 생성

    Amazon VPC별로 격리 보안 그룹을 생성하고 재사용합니다.
    격리 보안 그룹은 모든 인바운드/아웃바운드 트래픽을 차단합니다.

    Args:
        vpc_id (str): Amazon VPC ID

    Returns:
        str: 격리 보안 그룹 ID
    """
    try:
        # 기존 격리 보안 그룹 확인
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [ISOLATION_SG_NAME]},
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )

        # 기존 보안 그룹이 있으면 ID 반환
        if response['SecurityGroups']:
            return response['SecurityGroups'][0]['GroupId']

        # 격리 보안 그룹 생성 (모든 트래픽 차단)
        response = ec2.create_security_group(
            GroupName=ISOLATION_SG_NAME,
            Description='Isolation security group for Amazon GuardDuty auto-response',
            VpcId=vpc_id
        )

        sg_id = response['GroupId']
        print(f"Created isolation security group: {sg_id}")

        # 기본 egress 규칙 제거 (모든 아웃바운드 차단)
        # IPv4 규칙 제거
        try:
            ec2.revoke_security_group_egress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # 모든 프로토콜
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # 모든 IPv4
                    }
                ]
            )
        except Exception as e:
            # IPv4 규칙이 없는 경우 무시
            print(f"IPv4 egress rule not found (Amazon VPC may not have default IPv4 egress rule): {str(e)}")

        # IPv6 규칙 제거 (IPv6가 활성화된 Amazon VPC에서 완전한 격리를 위해 필요)
        try:
            ec2.revoke_security_group_egress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': '-1',  # 모든 프로토콜
                        'Ipv6Ranges': [{'CidrIpv6': '::/0'}]  # 모든 IPv6
                    }
                ]
            )
        except Exception as e:
            # IPv6 규칙이 없는 경우 무시
            print(f"IPv6 egress rule not found (Amazon VPC may not have IPv6 enabled): {str(e)}")

        # 생성된 보안 그룹 ID 반환
        return sg_id

    except Exception as e:
        # 오류 발생 시 로그 출력 및 예외 재발생
        print(f"Error managing isolation security group: {str(e)}")
        raise


def send_notification(finding_type, severity, title, description, instance_id, response_action):
    """
    Amazon SNS를 통해 보안 알림 전송

    Amazon GuardDuty Finding 정보와 수행된 대응 조치를 포함한
    구조화된 알림 메시지를 Amazon SNS 토픽으로 전송합니다.

    Args:
        finding_type (str): Finding 타입
        severity (float): 심각도 점수 (0.1-10.0)
        title (str): Finding 제목
        description (str): Finding 설명
        instance_id (str): 영향받는 인스턴스 ID (없으면 None)
        response_action (str): 수행된 대응 조치
    """
    try:
        # 심각도를 레이블로 변환
        severity_label = get_severity_label(severity)

        # 구조화된 알림 메시지 생성
        message = f"""
🚨 Amazon GuardDuty Security Alert

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Finding Type: {finding_type}
Severity: {severity_label} ({severity})
Title: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Description:
{description}

Affected Resource:
Instance ID: {instance_id or 'N/A'}

Auto-Response Action:
{response_action}

Timestamp: {datetime.utcnow().isoformat()}Z

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Please review this finding in the Amazon GuardDuty console.
        """

        # 이메일 제목 생성
        subject = f"[{severity_label}] Amazon GuardDuty Alert: {finding_type}"

        # Amazon SNS 토픽으로 메시지 발행
        sns.publish(
            TopicArn=Amazon SNS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )

        # 알림 전송 성공 로그
        print(f"Notification sent to Amazon SNS topic: {Amazon SNS_TOPIC_ARN}")

    except Exception as e:
        # 알림 전송 실패 시 로그 출력
        print(f"Error sending notification: {str(e)}")


def get_severity_label(severity):
    """
    숫자 심각도를 레이블로 변환

    Args:
        severity (float): 심각도 점수 (0.1-10.0)

    Returns:
        str: 심각도 레이블 (CRITICAL, HIGH, MEDIUM, LOW)
    """
    if severity >= 9.0:
        return "CRITICAL"  # 9.0-10.0: 즉각적인 대응 필수
    elif severity >= 7.0:
        return "HIGH"  # 7.0-8.9: 신속한 대응 필요
    elif severity >= 4.0:
        return "MEDIUM"  # 4.0-6.9: 조사 권장
    else:
        return "LOW"  # 0.1-3.9: 모니터링
```

56. [[Deploy]] 버튼을 클릭하여 코드를 저장합니다.

이 AWS Lambda 함수는 `print(f"Received event: {json.dumps(event)}")`로 Amazon GuardDuty Finding 이벤트 전체를 Amazon CloudWatch Logs에 출력합니다. 이는 디버깅에 유용하지만, 민감한 보안 정보(IP 주소, 인스턴스 ID 등)가 로그에 기록됩니다. 프로덕션 환경에서는 필요한 정보만 선택적으로 로깅하는 것을 권장합니다.

> [!CONCEPT] AWS Lambda 함수 로직 설명
> **주요 기능**:
>
> **Finding 정보 추출:**
>
> - Amazon EventBridge에서 전달된 Amazon GuardDuty Finding 이벤트 파싱
> - 심각도, 타입, 영향받는 리소스 정보 추출
>
> **심각도 기반 자동 대응:**
>
> - **High/Critical (7.0+)**: Amazon EC2 인스턴스를 격리 보안 그룹으로 이동 + Amazon SNS 알림
> - **Medium (4.0-6.9)**: 수동 검토 권장 알림만 전송 (Amazon SNS)
> - **Low (0.1-3.9)**: 로그 기록만 수행 (Amazon SNS 알림 없음)
>
> **격리 보안 그룹 관리:**
>
> - Amazon VPC별로 격리 보안 그룹 자동 생성
> - 모든 인바운드/아웃바운드 트래픽 차단
> - 재사용 가능한 격리 인프라
>
> **Amazon SNS 알림:**
>
> - 구조화된 알림 메시지 생성
> - 심각도에 따른 제목 설정
> - 수행된 자동 대응 조치 포함
>
> **에러 처리:**
>
> - 각 단계별 try-except 블록으로 안전성 확보
> - 알림 실패 시에도 함수 계속 실행
> - 상세한 로그 출력으로 디버깅 용이

57. **Configuration** 탭을 클릭합니다.
58. 왼쪽 메뉴에서 **Environment variables**를 선택합니다.
59. [[Edit]] 버튼을 클릭합니다.
60. [[Add environment variable]] 버튼을 클릭합니다.
61. **Key**에 `Amazon SNS_TOPIC_ARN`을 입력합니다.
62. **Value**에 Task 2에서 복사한 Amazon SNS 토픽 ARN을 붙여넣습니다.
63. [[Save]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS Lambda 자동 대응 함수가 생성되었습니다.

## 태스크 5: Amazon EventBridge 규칙 생성

이 태스크에서는 Amazon GuardDuty Finding을 AWS Lambda 함수로 전달하는 Amazon EventBridge 규칙을 생성합니다.

64. 상단 검색창에 `EventBridge`를 입력한 후 선택합니다.
65. 왼쪽 메뉴에서 **Rules**를 선택합니다.
66. [[Create rule]] 버튼을 클릭합니다.
67. **Name**에 `Amazon GuardDuty-AutoResponse-Rule`을 입력합니다.
68. **Description**에 `Route Amazon GuardDuty findings to AWS Lambda for auto-response`를 입력합니다.
69. **Event bus**는 `default`로 유지합니다.
70. **Rule type**에서 `Rule with an event pattern`을 선택합니다.
71. [[Next]] 버튼을 클릭합니다.
72. **Event source**에서 `AWS events or Amazon EventBridge partner events`를 선택합니다.
73. **Event pattern** 섹션에서 **Event pattern form**을 선택합니다.
74. **Event source**에서 `AWS services`를 선택합니다.
75. **AWS service**에서 `Amazon GuardDuty`를 선택합니다.
76. **Event type**에서 `Amazon GuardDuty Finding`을 선택합니다.
77. [[Next]] 버튼을 클릭합니다.
78. **Target types**에서 `AWS service`를 선택합니다.
79. **Select a target**에서 `AWS Lambda function`을 선택합니다.
80. **Function**에서 `Amazon GuardDuty-AutoResponse`를 선택합니다.
81. [[Next]] 버튼을 클릭합니다.
82. **Tags - optional** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `12-3`    |
| `CreatedBy` | `Student` |

83. [[Next]] 버튼을 클릭합니다.
84. 설정을 검토합니다.
85. [[Create rule]] 버튼을 클릭합니다.

✅ **태스크 완료**: Amazon EventBridge 규칙이 생성되었습니다.

## 태스크 6: Amazon GuardDuty 콘솔에서 샘플 Finding 확인

> [!IMPORTANT]
> **이 태스크의 목적**: 이 태스크는 Amazon GuardDuty Finding의 구조와 콘솔 UI를 익히기 위한 것입니다. 샘플 Finding은 Amazon EventBridge로 이벤트를 전송하지 않으므로, AWS Lambda 자동 대응 테스트는 다음 태스크(태스크 7)에서 수행합니다.
>
> **Amazon GuardDuty 샘플 Finding의 제한사항**: Amazon GuardDuty의 "Generate sample findings" 기능으로 생성된 샘플 Finding은 Amazon GuardDuty 콘솔에만 표시되며, **Amazon EventBridge로 이벤트를 전송하지 않습니다**.
>
> 따라서 샘플 Finding만으로는 AWS Lambda 함수가 자동으로 실행되지 않습니다. 다음 태스크에서는 AWS Lambda 콘솔에서 직접 테스트 이벤트를 사용하여 자동 대응 시스템을 테스트합니다.

이 태스크에서는 Amazon GuardDuty 콘솔에서 샘플 Finding을 생성하고 확인합니다.

86. Amazon GuardDuty 콘솔로 이동합니다.
87. 왼쪽 메뉴에서 **Settings**를 선택합니다.
88. **Sample findings** 섹션으로 스크롤합니다.
89. [[Generate sample findings]] 버튼을 클릭합니다.
90. 샘플 Finding이 생성되었다는 확인 메시지가 표시됩니다.
91. 왼쪽 메뉴에서 **Findings**를 선택합니다.
92. 여러 개의 샘플 Finding이 표시됩니다.

> [!NOTE]
> 샘플 Finding은 실제 위협이 아니며, Amazon GuardDuty 콘솔에서 Finding 형식을 확인하는 용도로만 사용됩니다. 각 Finding은 다양한 심각도와 타입을 가지고 있습니다.

93. Finding 목록에서 심각도가 "High" 또는 "Medium"인 Finding을 찾습니다.
94. Finding을 클릭하여 상세 정보를 확인합니다.
95. **Resource affected** 섹션에서 리소스 타입을 확인합니다.

✅ **태스크 완료**: 샘플 Finding을 생성하고 Amazon GuardDuty 콘솔에서 확인했습니다.

## 태스크 7: AWS Lambda 함수 테스트

이 태스크에서는 AWS Lambda 콘솔에서 테스트 이벤트를 사용하여 자동 대응 함수를 직접 실행하고 테스트합니다.

96. AWS Lambda 콘솔로 이동합니다.
97. `Amazon GuardDuty-AutoResponse` 함수를 선택합니다.
98. **Test** 탭을 선택합니다.
99. **Test event action**에서 `Create new event`를 선택합니다.
100. **Event name**에 `GuardDutyFindingTest`를 입력합니다.
101. **Event JSON** 영역에 다음 테스트 이벤트를 입력합니다:

```json
{
  "version": "0",
  "id": "test-event-12345",
  "detail-type": "Amazon GuardDuty Finding",
  "source": "aws.guardduty",
  "account": "{본인의 계정 ID}",
  "time": "2026-02-16T10:00:00Z",
  "region": "ap-northeast-2",
  "resources": [],
  "detail": {
    "schemaVersion": "2.0",
    "accountId": "{본인의 계정 ID}",
    "region": "ap-northeast-2",
    "partition": "aws",
    "id": "test-finding-id-12345",
    "arn": "arn:aws:guardduty:ap-northeast-2:{본인의 계정 ID}:detector/test/finding/test-finding-id-12345",
    "type": "Recon:Amazon EC2/PortProbeUnprotectedPort",
    "resource": {
      "resourceType": "Instance",
      "instanceDetails": {
        "instanceId": null,
        "instanceType": "t3.medium",
        "launchTime": "2026-02-15T08:00:00.000Z",
        "platform": null,
        "productCodes": [],
        "iamInstanceProfile": null,
        "networkInterfaces": [],
        "tags": []
      }
    },
    "service": {
      "serviceName": "guardduty",
      "detectorId": "test-detector-id",
      "action": {
        "actionType": "NETWORK_CONNECTION",
        "networkConnectionAction": {
          "connectionDirection": "INBOUND",
          "remoteIpDetails": {
            "ipAddressV4": "198.51.100.1",
            "organization": {
              "asn": "12345",
              "asnOrg": "Test Organization",
              "isp": "Test ISP",
              "org": "Test Org"
            },
            "country": {
              "countryName": "Test Country"
            },
            "city": {
              "cityName": "Test City"
            },
            "geoLocation": {
              "lat": 0.0,
              "lon": 0.0
            }
          },
          "remotePortDetails": {
            "port": 22,
            "portName": "SSH"
          },
          "localPortDetails": {
            "port": 22,
            "portName": "SSH"
          },
          "protocol": "TCP",
          "blocked": false
        }
      },
      "resourceRole": "TARGET",
      "additionalInfo": {
        "threatListName": "Test Threat List",
        "threatName": "Test Threat"
      },
      "eventFirstSeen": "2026-02-16T09:00:00.000Z",
      "eventLastSeen": "2026-02-16T10:00:00.000Z",
      "archived": false,
      "count": 5
    },
    "severity": 5.0,
    "createdAt": "2026-02-16T09:00:00.000Z",
    "updatedAt": "2026-02-16T10:00:00.000Z",
    "title": "Unprotected port on Amazon EC2 instance is being probed",
    "description": "Amazon EC2 instance has an unprotected port which is being probed by a known malicious host. This is a test finding for QuickTable security demo."
  }
}
```

> [!NOTE]
> 이 테스트 이벤트는 실제 Amazon GuardDuty Finding의 구조를 모방한 것입니다.
>
> - **계정 ID**: `{본인의 계정 ID}` 부분을 본인의 실제 AWS 계정 ID로 직접 교체하여 입력합니다. 이 테스트에서는 AWS Lambda 함수가 해당 필드를 사용하지 않으므로 기능 동작에는 영향이 없지만, 실제 이벤트 구조와 동일하게 맞추는 것을 권장합니다.
> - **severity: 5.0** (Medium) → AWS Lambda 함수는 인스턴스 격리 없이 "Manual review recommended" 메시지를 반환합니다. instanceId가 null이지만, Medium 심각도에서는 인스턴스 격리를 시도하지 않으므로 instanceId 값과 무관합니다.
> - **type: Recon:Amazon EC2/PortProbeUnprotectedPort** → 포트 스캔 공격 시뮬레이션

102. [[Save]] 버튼을 클릭합니다.
103. [[Test]] 버튼을 클릭하여 함수를 실행합니다.
104. **Execution result** 섹션에서 실행 결과를 확인합니다.

> [!OUTPUT]
>
> ```json
> {
>   "statusCode": 200,
>   "body": "{\"message\": \"Auto-response completed\", \"finding_id\": \"test-finding-id-12345\", \"action\": \"Manual review recommended\"}"
> }
> ```

105. **Log output** 섹션을 확장하여 상세 로그를 확인합니다.

> [!OUTPUT]
>
> ```
> START RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Version: $LATEST
> Received event: {"version":"0","id":"test-event-12345",...}
> Processing Finding: Recon:Amazon EC2/PortProbeUnprotectedPort
> Severity: 5.0
> Instance ID: None
> Manual review recommended
> Notification sent to Amazon SNS topic: arn:aws:sns:ap-northeast-2:123456789012:Amazon GuardDuty-Security-Alerts
> END RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
> REPORT RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Duration: 1234.56 ms Billed Duration: 1235 ms Memory Size: 128 MB Max Memory Used: 67 MB
> ```

> [!NOTE]
> 계정 ID는 본인의 AWS 계정 ID로 표시됩니다.

106. 이메일 받은편지함을 확인합니다.
107. Amazon GuardDuty 알림 이메일이 수신되었는지 확인합니다.

> [!SUCCESS]
> 이메일 알림이 정상적으로 수신되었다면, AWS Lambda 함수가 올바르게 작동하고 있는 것입니다.

108. 이메일을 열고 다음 정보를 확인합니다:
    - **Subject**: `[MEDIUM] Amazon GuardDuty Alert: Recon:Amazon EC2/PortProbeUnprotectedPort`
    - **Finding Type**: `Recon:Amazon EC2/PortProbeUnprotectedPort`
    - **Severity**: `MEDIUM (5.0)`
    - **Title**: `Unprotected port on Amazon EC2 instance is being probed`
    - **Auto-Response Action**: `Manual review recommended`

> [!TIP]
> **High Finding 테스트**: 심각도가 높은 Finding을 테스트하려면 테스트 이벤트의 `severity` 값을 `8.0`으로 변경하고 다시 실행합니다. AWS Lambda 함수는 Amazon EC2 인스턴스 격리를 시도하지만, `instanceId`가 `null`이므로 "No instance to isolate (non-Amazon EC2 resource)" 메시지를 반환합니다.

✅ **태스크 완료**: AWS Lambda 함수가 정상적으로 실행되고 Amazon SNS 알림이 전송되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- Amazon GuardDuty를 활성화하고 QuickTable 인프라에 대한 위협 탐지를 시작했습니다
- Amazon SNS 토픽을 생성하고 보안 알림 이메일 구독을 설정했습니다
- AWS Lambda 실행 역할을 생성하고 필요한 권한을 부여했습니다
- Amazon GuardDuty Finding을 처리하는 AWS Lambda 자동 대응 함수를 구현했습니다
- Amazon EventBridge 규칙을 생성하여 Finding을 AWS Lambda로 전달했습니다
- 샘플 Finding을 생성하고 자동 대응 시스템을 테스트했습니다

Week 4-3에서 구축한 QuickTable API와 Week 10-2의 Amazon ElastiCache 인프라를 보호하기 위한 보안 모니터링 및 자동 대응 시스템을 성공적으로 구현했습니다.

## 리소스 정리

> [!WARNING]
> 다음 단계를 반드시 수행하여 불필요한 비용을 방지합니다.

---

## 1단계: 생성된 리소스 확인 (Tag Editor)

실습에서 생성한 모든 리소스를 확인합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `12-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 **찾는 용도**로만 사용됩니다.
> 실제 삭제는 2단계에서 수행합니다.

---

## 2단계: 리소스 삭제

### Amazon EventBridge 규칙 삭제

8. Amazon EventBridge 콘솔로 이동합니다.
9. 왼쪽 메뉴에서 **Rules**를 선택합니다.
10. `Amazon GuardDuty-AutoResponse-Rule`을 선택합니다.
11. [[Delete]] 버튼을 클릭합니다.
12. 확인 창에서 `delete`를 입력합니다.
13. [[Delete]] 버튼을 클릭합니다.

### AWS Lambda 함수 삭제

14. AWS Lambda 콘솔로 이동합니다.
15. `Amazon GuardDuty-AutoResponse` 함수를 선택합니다.
16. **Actions** → `Delete`를 선택합니다.
17. 확인 창에서 `delete`를 입력합니다.
18. [[Delete]] 버튼을 클릭합니다.

### Amazon CloudWatch Logs 삭제

19. Amazon CloudWatch 콘솔로 이동합니다.
20. 왼쪽 메뉴에서 **Log groups**를 선택합니다.
21. `/aws/lambda/Amazon GuardDuty-AutoResponse` 로그 그룹을 선택합니다.
22. **Actions** → `Delete log group(s)`를 선택합니다.
23. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

### 격리 보안 그룹 삭제 (생성된 경우)

24. Amazon EC2 콘솔로 이동합니다.
25. 왼쪽 메뉴에서 **Security Groups**를 선택합니다.
26. 검색창에 `Amazon GuardDuty-Isolation-SG`를 입력합니다.
27. 격리 보안 그룹이 있으면 선택합니다.
28. **Actions** → `Delete security groups`를 선택합니다.
29. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 격리 보안 그룹은 AWS Lambda 함수가 실행되어 Amazon EC2 인스턴스를 격리한 경우에만 생성됩니다. 테스트에서 `instanceId`가 `null`이었다면 보안 그룹이 생성되지 않았을 수 있습니다.

### AWS IAM 역할 삭제

30. AWS IAM 콘솔로 이동합니다.
31. 왼쪽 메뉴에서 **Roles**를 선택합니다.
32. `Amazon GuardDuty-AWS Lambda-AutoResponse-Role`을 선택합니다.
33. [[Delete]] 버튼을 클릭합니다.
34. 확인 창에서 역할 이름을 입력합니다.
35. [[Delete]] 버튼을 클릭합니다.

### Amazon SNS 토픽 삭제

36. Amazon SNS 콘솔로 이동합니다.
37. 왼쪽 메뉴에서 **Topics**를 선택합니다.
38. `Amazon GuardDuty-Security-Alerts` 토픽을 선택합니다.
39. [[Delete]] 버튼을 클릭합니다.
40. 확인 창에서 `delete me`를 입력합니다.
41. [[Delete]] 버튼을 클릭합니다.

### Amazon GuardDuty 비활성화

42. Amazon GuardDuty 콘솔로 이동합니다.
43. 왼쪽 메뉴에서 **Settings**를 선택합니다.
44. **General** 탭을 선택합니다.
45. **Disable Amazon GuardDuty** 섹션으로 스크롤합니다.
46. [[Disable]] 버튼을 클릭합니다.
47. 확인 창에서 비활성화 옵션을 선택합니다.

> [!NOTE]
> **Suspend vs Disable 차이**:
>
> | 옵션        | 설명           | 데이터 보존         | 재활성화       |
> | ----------- | -------------- | ------------------- | -------------- |
> | **Suspend** | 탐지 일시 중지 | Finding 데이터 보존 | 즉시 가능      |
> | **Disable** | 완전 비활성화  | 모든 데이터 삭제    | 초기 설정 필요 |
>
> 실습 종료 후에는 **Suspend**를 선택하여 일시 중지하거나, **Disable**을 선택하여 완전히 비활성화할 수 있습니다. Suspend는 Finding 데이터를 보존하므로 나중에 다시 활성화할 때 유용합니다.

✅ **데모 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [Amazon GuardDuty 사용 설명서](https://docs.aws.amazon.com/ko_kr/guardduty/latest/ug/what-is-guardduty.html)
- [Amazon GuardDuty Finding 타입](https://docs.aws.amazon.com/ko_kr/guardduty/latest/ug/guardduty_finding-types-active.html)
- [Amazon EventBridge를 사용한 자동 대응](https://docs.aws.amazon.com/ko_kr/guardduty/latest/ug/guardduty_findings_cloudwatch.html)
- [AWS Lambda 보안 모범 사례](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/lambda-security.html)

### QuickTable 시리즈 연결

- **Week 4-3**: AWS Lambda + Amazon API Gateway로 QuickTable 예약 API 구축
- **Week 10-2**: Amazon ElastiCache로 API 성능 최적화 (데모)
- **Week 12-3**: Amazon GuardDuty + AWS Lambda로 보안 모니터링 ← 현재
- **Week 13-2**: AWS X-Ray로 성능 추적
- **Week 14-2**: Amazon Bedrock Knowledge Base로 레스토랑 메뉴 RAG
- **Week 14-3**: Amazon Bedrock Agent로 예약 챗봇 완성

## 📚 참고: Amazon GuardDuty 자동 대응 아키텍처

### 이벤트 기반 보안 자동화

**전체 흐름**:

```
48. Amazon GuardDuty → 위협 탐지 (Finding 생성).
49. Amazon EventBridge → Finding 이벤트 감지.
50. AWS Lambda → 자동 대응 로직 실행.
   - 위협 수준 분석
   - 보안 그룹 격리 (High/Critical)
   - Amazon SNS 알림 전송
51. Amazon SNS → 보안 담당자에게 이메일 알림.
```

### 자동 대응 시나리오

**High/Critical Finding (7.0+)**:

- 의심스러운 Amazon EC2 인스턴스의 보안 그룹을 격리 보안 그룹으로 변경
- 모든 인바운드/아웃바운드 트래픽 차단
- 즉각적인 Amazon SNS 알림 전송
- Amazon CloudWatch Logs에 상세 기록

**Medium Finding (4.0-6.9)**:

- Amazon SNS 알림만 전송하여 수동 검토 유도
- Amazon CloudWatch Logs에 기록
- 보안 담당자가 수동으로 조사 및 대응

**Low Finding (0.1-3.9)**:

- Amazon CloudWatch Logs에만 기록
- Amazon SNS 알림 전송 없음 (로그 모니터링으로 충분)
- 정기적인 검토 시 확인

### 격리 보안 그룹

**특징**:

- Amazon VPC별로 자동 생성
- 모든 인바운드 규칙 없음 (기본값)
- 모든 아웃바운드 규칙 제거 (완전 격리)
- 재사용 가능한 인프라

**격리 효과**:

- 외부에서 인스턴스로 접근 불가
- 인스턴스에서 외부로 통신 불가
- 추가 피해 확산 방지
- 포렌식 분석을 위한 상태 보존

### 프로덕션 환경 개선사항

**1. 다단계 대응 워크플로우**:

- AWS Step Functions로 복잡한 대응 프로세스 구현
- 승인 단계 추가 (오탐 방지)
- 자동 롤백 메커니즘

**2. 대응 이력 관리**:

- Amazon DynamoDB에 모든 대응 조치 기록
- 감사 추적 (Audit Trail) 유지
- 대응 효과 분석

**3. 특정 Finding 타입별 대응**:

- Cryptocurrency Mining → 인스턴스 중지
- Data Exfiltration → 네트워크 격리 + Amazon S3 버킷 잠금
- Backdoor → 인스턴스 스냅샷 + 종료

**4. 통합 보안 도구**:

- AWS Security Hub로 중앙 집중식 관리
- AWS Systems Manager로 자동 패치
- Amazon Inspector로 취약점 스캔

**5. 알림 채널 다양화**:

- Slack/Teams 통합
- PagerDuty 연동
- 전화/SMS 알림 (Critical만)

### 보안 모범 사례

**최소 권한 원칙**:

- AWS Lambda 역할에 필요한 최소 권한만 부여
- Resource 제한 (특정 Amazon VPC, 태그)
- Condition 사용 (시간, IP 제한)

**암호화**:

- 환경 변수 암호화 (AWS KMS)
- Amazon SNS 메시지 암호화
- Amazon CloudWatch Logs 암호화

**모니터링**:

- AWS Lambda 실행 실패 알림
- 대응 조치 실패 알림
- 비정상적인 대응 패턴 탐지

**테스트**:

- 정기적인 자동 대응 테스트
- 다양한 Finding 타입 시뮬레이션
- 롤백 프로세스 검증
