"""
AWS Lambda 함수: GuardDuty 자동 대응 시스템

이 Lambda 함수는 Amazon GuardDuty에서 탐지된 보안 위협(Finding)을
자동으로 처리하고 대응합니다.

주요 기능:
    1. GuardDuty Finding 정보 추출 및 분석
    2. 심각도 기반 자동 대응 (High/Critical: 인스턴스 격리)
    3. 격리 보안 그룹 자동 생성 및 관리
    4. SNS를 통한 보안 알림 전송

환경 변수:
    SNS_TOPIC_ARN (str): SNS 토픽 ARN (보안 알림 전송용)

트리거:
    EventBridge 규칙 (GuardDuty Finding 이벤트)

작성자: AWS 실습 가이드
버전: 1.0.0
"""

import json
import boto3
import os
from datetime import datetime

# AWS 클라이언트 초기화
ec2 = boto3.client('ec2')  # EC2 인스턴스 및 보안 그룹 관리
sns = boto3.client('sns')  # SNS 알림 전송
guardduty = boto3.client('guardduty')  # GuardDuty Finding 조회

# 환경 변수
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')  # SNS 토픽 ARN
ISOLATION_SG_NAME = 'GuardDuty-Isolation-SG'  # 격리 보안 그룹 이름


def lambda_handler(event, context):
    """
    GuardDuty Finding을 처리하고 자동 대응을 수행하는 Lambda 함수
    
    EventBridge에서 전달된 GuardDuty Finding 이벤트를 분석하고,
    심각도에 따라 자동으로 대응 조치를 수행합니다.
    
    대응 로직:
        - High/Critical (7.0+): EC2 인스턴스를 격리 보안 그룹으로 이동
        - Medium (4.0-6.9): 수동 검토 권장 알림만 전송
        - Low (0.1-3.9): 로그 기록만 수행
    
    Args:
        event (dict): EventBridge에서 전달된 GuardDuty Finding 이벤트
            - detail (dict): Finding 상세 정보
                - id (str): Finding ID
                - type (str): Finding 타입
                - severity (float): 심각도 (0.1-10.0)
                - title (str): Finding 제목
                - description (str): Finding 설명
                - resource (dict): 영향받는 리소스 정보
        context (LambdaContext): Lambda 실행 컨텍스트
    
    Returns:
        dict: HTTP 응답 형식
            - statusCode (int): 200 (성공)
            - body (str): JSON 형식의 처리 결과
                - message: 처리 완료 메시지
                - finding_id: Finding ID
                - action: 수행된 대응 조치
    
    Raises:
        Exception: Finding 처리 중 오류 발생 시
    
    Example:
        >>> event = {
        ...     'detail': {
        ...         'id': 'abc123',
        ...         'type': 'Recon:EC2/PortProbeUnprotectedPort',
        ...         'severity': 8.0,
        ...         'title': 'Port probe detected',
        ...         'description': 'Suspicious port scanning activity',
        ...         'resource': {
        ...             'instanceDetails': {
        ...                 'instanceId': 'i-1234567890abcdef0'
        ...             }
        ...         }
        ...     }
        ... }
        >>> result = lambda_handler(event, None)
        >>> print(result['statusCode'])
        200
    """
    # 이벤트 전체 내용을 로그에 출력 (디버깅용)
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # GuardDuty Finding 정보 추출
        detail = event['detail']  # EventBridge 이벤트의 detail 섹션
        finding_id = detail['id']  # Finding 고유 ID
        finding_type = detail['type']  # Finding 타입 (예: Recon:EC2/PortProbeUnprotectedPort)
        severity = detail['severity']  # 심각도 점수 (0.1-10.0)
        title = detail['title']  # Finding 제목
        description = detail['description']  # Finding 상세 설명
        
        # 리소스 정보 추출
        # get()을 사용하여 키가 없을 경우 빈 딕셔너리 반환
        resource = detail.get('resource', {})
        instance_details = resource.get('instanceDetails', {})
        instance_id = instance_details.get('instanceId')  # 영향받는 EC2 인스턴스 ID
        
        # 처리 시작 로그 출력
        print(f"Processing Finding: {finding_type}")
        print(f"Severity: {severity}")
        print(f"Instance ID: {instance_id}")
        
        # 심각도에 따른 자동 대응
        response_action = ""
        
        if severity >= 7.0:  # High or Critical
            # 심각한 위협: EC2 인스턴스 격리
            if instance_id:
                # 인스턴스 ID가 있으면 격리 수행
                response_action = isolate_instance(instance_id)
            else:
                # EC2 인스턴스가 아닌 리소스 (예: S3, IAM)
                response_action = "No instance to isolate (non-EC2 resource)"
        elif severity >= 4.0:  # Medium
            # 중간 수준 위협: 수동 검토 권장
            response_action = "Manual review recommended"
        else:  # Low
            # 낮은 수준 위협: 로그 기록만
            response_action = "Logged for monitoring"
        
        # SNS 알림 전송
        # 모든 심각도에 대해 알림 전송 (심각도에 따라 메시지 내용 다름)
        send_notification(
            finding_type=finding_type,
            severity=severity,
            title=title,
            description=description,
            instance_id=instance_id,
            response_action=response_action
        )
        
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
    EC2 인스턴스를 격리 보안 그룹으로 이동
    
    의심스러운 EC2 인스턴스의 보안 그룹을 격리 보안 그룹으로 변경하여
    모든 네트워크 트래픽을 차단합니다. 이를 통해 추가 피해 확산을 방지하고
    포렌식 분석을 위한 상태를 보존합니다.
    
    Args:
        instance_id (str): 격리할 EC2 인스턴스 ID
    
    Returns:
        str: 수행된 조치 설명 또는 오류 메시지
    
    Example:
        >>> action = isolate_instance('i-1234567890abcdef0')
        >>> print(action)
        Instance i-1234567890abcdef0 isolated with security group sg-0abc123def456
    """
    try:
        # 인스턴스 정보 조회
        # describe_instances()는 인스턴스의 모든 정보를 반환
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        vpc_id = instance['VpcId']  # 인스턴스가 속한 VPC ID
        
        # 격리 보안 그룹 확인 또는 생성
        # VPC별로 격리 보안 그룹을 생성하여 재사용
        isolation_sg_id = get_or_create_isolation_sg(vpc_id)
        
        # 인스턴스의 보안 그룹을 격리 보안 그룹으로 변경
        # 기존 보안 그룹은 모두 제거되고 격리 보안 그룹만 적용됨
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
    
    VPC별로 격리 보안 그룹을 생성하고 재사용합니다.
    격리 보안 그룹은 모든 인바운드/아웃바운드 트래픽을 차단하여
    완전한 네트워크 격리를 제공합니다.
    
    Args:
        vpc_id (str): VPC ID
    
    Returns:
        str: 격리 보안 그룹 ID
    
    Raises:
        Exception: 보안 그룹 생성 또는 조회 실패 시
    
    Example:
        >>> sg_id = get_or_create_isolation_sg('vpc-0abc123def456')
        >>> print(sg_id)
        sg-0abc123def456
    """
    try:
        # 기존 격리 보안 그룹 확인
        # describe_security_groups()로 이름과 VPC로 필터링
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
            Description='Isolation security group for GuardDuty auto-response',
            VpcId=vpc_id
        )
        
        sg_id = response['GroupId']
        print(f"Created isolation security group: {sg_id}")
        
        # 기본 egress 규칙 제거 (모든 아웃바운드 차단)
        # 보안 그룹 생성 시 기본적으로 모든 아웃바운드 허용 규칙이 추가되므로 제거
        ec2.revoke_security_group_egress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # 모든 프로토콜
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # 모든 IP
                }
            ]
        )
        
        # 생성된 보안 그룹 ID 반환
        return sg_id
        
    except Exception as e:
        # 오류 발생 시 로그 출력 및 예외 재발생
        print(f"Error managing isolation security group: {str(e)}")
        raise


def send_notification(finding_type, severity, title, description, instance_id, response_action):
    """
    SNS를 통해 보안 알림 전송
    
    GuardDuty Finding 정보와 수행된 대응 조치를 포함한
    구조화된 알림 메시지를 SNS 토픽으로 전송합니다.
    
    Args:
        finding_type (str): Finding 타입
        severity (float): 심각도 점수 (0.1-10.0)
        title (str): Finding 제목
        description (str): Finding 설명
        instance_id (str): 영향받는 인스턴스 ID (없으면 None)
        response_action (str): 수행된 대응 조치
    
    Returns:
        None
    
    Example:
        >>> send_notification(
        ...     finding_type='Recon:EC2/PortProbeUnprotectedPort',
        ...     severity=8.0,
        ...     title='Port probe detected',
        ...     description='Suspicious activity',
        ...     instance_id='i-1234567890abcdef0',
        ...     response_action='Instance isolated'
        ... )
    """
    try:
        # 심각도를 레이블로 변환 (CRITICAL, HIGH, MEDIUM, LOW)
        severity_label = get_severity_label(severity)
        
        # 구조화된 알림 메시지 생성
        # 이모지와 구분선을 사용하여 가독성 향상
        message = f"""
🚨 GuardDuty Security Alert

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
Please review this finding in the GuardDuty console.
        """
        
        # 이메일 제목 생성 (심각도와 Finding 타입 포함)
        subject = f"[{severity_label}] GuardDuty Alert: {finding_type}"
        
        # SNS 토픽으로 메시지 발행
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,  # 환경 변수에서 가져온 SNS 토픽 ARN
            Subject=subject,  # 이메일 제목
            Message=message  # 이메일 본문
        )
        
        # 알림 전송 성공 로그
        print(f"Notification sent to SNS topic: {SNS_TOPIC_ARN}")
        
    except Exception as e:
        # 알림 전송 실패 시 로그 출력 (예외는 재발생하지 않음)
        # 알림 실패가 전체 함수 실행을 중단하지 않도록 함
        print(f"Error sending notification: {str(e)}")


def get_severity_label(severity):
    """
    숫자 심각도를 레이블로 변환
    
    GuardDuty의 숫자 심각도 점수를 사람이 읽기 쉬운
    레이블로 변환합니다.
    
    Args:
        severity (float): 심각도 점수 (0.1-10.0)
    
    Returns:
        str: 심각도 레이블 (CRITICAL, HIGH, MEDIUM, LOW)
    
    Example:
        >>> label = get_severity_label(9.5)
        >>> print(label)
        CRITICAL
        >>> label = get_severity_label(5.0)
        >>> print(label)
        MEDIUM
    """
    if severity >= 9.0:
        return "CRITICAL"  # 9.0-10.0: 즉각적인 대응 필수
    elif severity >= 7.0:
        return "HIGH"  # 7.0-8.9: 신속한 대응 필요
    elif severity >= 4.0:
        return "MEDIUM"  # 4.0-6.9: 조사 권장
    else:
        return "LOW"  # 0.1-3.9: 모니터링
