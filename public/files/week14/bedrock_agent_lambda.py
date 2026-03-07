"""
Bedrock Agent 예약 관리 Lambda 함수

이 Lambda 함수는 Amazon Bedrock Agent의 Action Group으로 동작하며,
레스토랑 예약 관리 기능을 제공합니다.

주요 기능:
- 예약 조회 (get_reservation)
- 예약 생성 (create_reservation)
- 예약 목록 조회 (list_reservations)
- 예약 취소 (cancel_reservation)

환경 변수:
- TABLE_NAME: DynamoDB 테이블 이름 (기본값: RestaurantReservations)
"""

import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# DynamoDB 리소스 초기화
# 환경 변수에서 테이블 이름을 가져오거나 기본값 사용
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'RestaurantReservations'))

def lambda_handler(event, context):
    """
    Lambda 함수의 메인 핸들러
    
    Bedrock Agent로부터 요청을 받아 적절한 함수로 라우팅하고,
    결과를 Bedrock Agent 응답 형식으로 반환합니다.
    
    Args:
        event (dict): Bedrock Agent로부터 전달된 이벤트 객체
            - agent (dict): Agent 정보 (name, id, alias, version)
            - actionGroup (str): Action Group 이름
            - function (str): 호출할 함수 이름
            - parameters (list): 함수 파라미터 목록
            - sessionId (str): 세션 ID
            - sessionAttributes (dict): 세션 속성
        context (object): Lambda 실행 컨텍스트
    
    Returns:
        dict: Bedrock Agent 응답 형식의 딕셔너리
            - messageVersion (str): 메시지 버전 (1.0)
            - response (dict): 응답 객체
                - actionGroup (str): Action Group 이름
                - function (str): 실행된 함수 이름
                - functionResponse (dict): 함수 실행 결과
    
    Example:
        >>> event = {
        ...     'actionGroup': 'ReservationActions',
        ...     'function': 'get_reservation',
        ...     'parameters': [{'name': 'reservation_id', 'value': 'RES001'}]
        ... }
        >>> lambda_handler(event, {})
        {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': 'ReservationActions',
                'function': 'get_reservation',
                'functionResponse': {...}
            }
        }
    """
    # 디버깅을 위한 이벤트 로깅
    print(f"Received event: {json.dumps(event)}")
    
    # Bedrock Agent에서 전달된 정보 추출
    agent = event.get('agent', {})  # Agent 정보 (선택사항)
    action_group = event.get('actionGroup', '')  # Action Group 이름
    function = event.get('function', '')  # 호출할 함수 이름
    parameters = event.get('parameters', [])  # 파라미터 리스트
    
    # 파라미터를 딕셔너리로 변환
    # [{'name': 'key', 'value': 'val'}] → {'key': 'val'}
    params = {p['name']: p['value'] for p in parameters}
    
    # 디버깅을 위한 함수 호출 정보 로깅
    print(f"Action: {action_group}, Function: {function}")
    print(f"Parameters: {params}")
    
    # 함수 라우팅: 함수 이름에 따라 적절한 핸들러 호출
    if function == 'get_reservation':
        result = get_reservation(params)
    elif function == 'create_reservation':
        result = create_reservation(params)
    elif function == 'list_reservations':
        result = list_reservations(params)
    elif function == 'cancel_reservation':
        result = cancel_reservation(params)
    else:
        # 알 수 없는 함수 이름인 경우 오류 반환
        result = {
            'error': f'Unknown function: {function}'
        }
    
    # Bedrock Agent 응답 형식으로 변환
    # Agent는 이 형식을 파싱하여 사용자에게 응답 생성
    response = {
        'messageVersion': '1.0',  # 메시지 버전 (필수)
        'response': {
            'actionGroup': action_group,  # Action Group 이름 (필수)
            'function': function,  # 실행된 함수 이름 (필수)
            'functionResponse': {
                'responseBody': {
                    'TEXT': {
                        # 결과를 JSON 문자열로 변환
                        # ensure_ascii=False: 한글 유지
                        'body': json.dumps(result, ensure_ascii=False)
                    }
                }
            }
        }
    }
    
    # 디버깅을 위한 응답 로깅
    print(f"Response: {json.dumps(response, ensure_ascii=False)}")
    return response

def get_reservation(params):
    """
    예약 번호로 예약 정보를 조회합니다.
    
    Args:
        params (dict): 함수 파라미터
            - reservation_id (str): 조회할 예약 번호 (예: RES001)
    
    Returns:
        dict: 조회 결과
            성공 시:
                - success (bool): True
                - reservation (dict): 예약 정보
                    - reservation_id (str): 예약 번호
                    - customer_name (str): 고객 이름
                    - date (str): 예약 날짜 (YYYY-MM-DD)
                    - time (str): 예약 시간 (HH:MM)
                    - party_size (int): 인원수
                    - status (str): 예약 상태 (confirmed/cancelled)
            실패 시:
                - success (bool): False
                - message (str): 오류 메시지
                - error (str): 예외 메시지 (예외 발생 시)
    
    Example:
        >>> get_reservation({'reservation_id': 'RES001'})
        {
            'success': True,
            'reservation': {
                'reservation_id': 'RES001',
                'customer_name': '김철수',
                'date': '2024-02-15',
                'time': '19:00',
                'party_size': 4,
                'status': 'confirmed'
            }
        }
    """
    # 파라미터에서 예약 번호 추출
    reservation_id = params.get('reservation_id')
    
    try:
        # DynamoDB에서 예약 정보 조회
        # get_item: Primary Key로 단일 항목 조회 (빠름)
        response = table.get_item(Key={'reservation_id': reservation_id})
        
        # 조회 결과 확인
        if 'Item' in response:
            # 예약이 존재하는 경우
            item = response['Item']
            return {
                'success': True,
                'reservation': {
                    'reservation_id': item['reservation_id'],
                    'customer_name': item['customer_name'],
                    'date': item['date'],
                    'time': item['time'],
                    'party_size': int(item['party_size']),  # Decimal → int 변환
                    'status': item['status']
                }
            }
        else:
            # 예약이 존재하지 않는 경우
            return {
                'success': False,
                'message': f'예약 번호 {reservation_id}를 찾을 수 없습니다.'
            }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def create_reservation(params):
    """
    새로운 예약을 생성합니다.
    
    Args:
        params (dict): 함수 파라미터
            - customer_name (str): 고객 이름
            - date (str): 예약 날짜 (YYYY-MM-DD)
            - time (str): 예약 시간 (HH:MM)
            - party_size (str|int): 인원수 (기본값: 2)
    
    Returns:
        dict: 생성 결과
            성공 시:
                - success (bool): True
                - message (str): 성공 메시지
                - reservation (dict): 생성된 예약 정보
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지
    
    Example:
        >>> create_reservation({
        ...     'customer_name': '김철수',
        ...     'date': '2024-02-15',
        ...     'time': '19:00',
        ...     'party_size': '4'
        ... })
        {
            'success': True,
            'message': '김철수님의 예약이 완료되었습니다.',
            'reservation': {
                'reservation_id': 'RESABC12345',
                'customer_name': '김철수',
                'date': '2024-02-15',
                'time': '19:00',
                'party_size': 4,
                'status': 'confirmed'
            }
        }
    """
    import uuid
    
    # 고유한 예약 번호 생성
    # RES + UUID 앞 8자리 (대문자)
    # 예: RESABC12345
    reservation_id = f"RES{str(uuid.uuid4())[:8].upper()}"
    
    # 파라미터에서 예약 정보 추출
    customer_name = params.get('customer_name')
    date = params.get('date')
    time = params.get('time')
    party_size = int(params.get('party_size', 2))  # 기본값: 2명
    
    try:
        # DynamoDB에 예약 정보 저장
        # put_item: 새 항목 생성 또는 기존 항목 덮어쓰기
        table.put_item(Item={
            'reservation_id': reservation_id,  # Primary Key
            'customer_name': customer_name,
            'date': date,
            'time': time,
            'party_size': party_size,
            'status': 'confirmed',  # 초기 상태: 확정
            'created_at': datetime.now().isoformat()  # 생성 시간 (ISO 8601 형식)
        })
        
        # 성공 응답 반환
        return {
            'success': True,
            'message': f'{customer_name}님의 예약이 완료되었습니다.',
            'reservation': {
                'reservation_id': reservation_id,
                'customer_name': customer_name,
                'date': date,
                'time': time,
                'party_size': party_size,
                'status': 'confirmed'
            }
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def list_reservations(params):
    """
    예약 목록을 조회합니다.
    
    특정 날짜의 예약만 조회하거나 모든 예약을 조회할 수 있습니다.
    
    Args:
        params (dict): 함수 파라미터
            - date (str, optional): 조회할 날짜 (YYYY-MM-DD)
                                   지정하지 않으면 모든 예약 조회
    
    Returns:
        dict: 조회 결과
            성공 시:
                - success (bool): True
                - count (int): 예약 개수
                - reservations (list): 예약 목록
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지
    
    Note:
        - 날짜 필터링은 scan 연산을 사용하므로 성능이 낮습니다
        - 프로덕션 환경에서는 GSI (Global Secondary Index)를 사용해야 합니다
    
    Example:
        >>> list_reservations({'date': '2024-02-15'})
        {
            'success': True,
            'count': 3,
            'reservations': [
                {'reservation_id': 'RES001', 'customer_name': '김철수', ...},
                {'reservation_id': 'RES002', 'customer_name': '이영희', ...},
                {'reservation_id': 'RES003', 'customer_name': '박민수', ...}
            ]
        }
    """
    # 파라미터에서 날짜 추출 (선택사항)
    date = params.get('date')
    
    try:
        if date:
            # 특정 날짜의 예약 조회
            # scan: 전체 테이블 스캔 (느림, 비용 높음)
            # FilterExpression: 스캔 후 필터링
            # 주의: 프로덕션에서는 GSI 사용 권장
            response = table.scan(
                FilterExpression='#d = :date',
                # ExpressionAttributeNames: 예약어 회피
                # 'date'는 DynamoDB 예약어이므로 #d로 대체
                ExpressionAttributeNames={'#d': 'date'},
                ExpressionAttributeValues={':date': date}
            )
        else:
            # 모든 예약 조회
            # scan: 전체 테이블 스캔
            response = table.scan()
        
        # 조회 결과에서 항목 추출
        items = response.get('Items', [])
        
        # 각 항목을 표준 형식으로 변환
        reservations = [
            {
                'reservation_id': item['reservation_id'],
                'customer_name': item['customer_name'],
                'date': item['date'],
                'time': item['time'],
                'party_size': int(item['party_size']),  # Decimal → int 변환
                'status': item['status']
            }
            for item in items
        ]
        
        # 성공 응답 반환
        return {
            'success': True,
            'count': len(reservations),
            'reservations': reservations
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }

def cancel_reservation(params):
    """
    예약을 취소합니다.
    
    예약 상태를 'cancelled'로 변경합니다.
    실제로 항목을 삭제하지 않고 상태만 변경하여 이력을 유지합니다.
    
    Args:
        params (dict): 함수 파라미터
            - reservation_id (str): 취소할 예약 번호
    
    Returns:
        dict: 취소 결과
            성공 시:
                - success (bool): True
                - message (str): 성공 메시지
            실패 시:
                - success (bool): False
                - error (str): 예외 메시지
    
    Note:
        - 예약이 존재하지 않아도 update_item은 성공합니다
        - 실제 환경에서는 예약 존재 여부를 먼저 확인해야 합니다
    
    Example:
        >>> cancel_reservation({'reservation_id': 'RES001'})
        {
            'success': True,
            'message': '예약 번호 RES001가 취소되었습니다.'
        }
    """
    # 파라미터에서 예약 번호 추출
    reservation_id = params.get('reservation_id')
    
    try:
        # DynamoDB에서 예약 상태 업데이트
        # update_item: 특정 속성만 업데이트 (효율적)
        table.update_item(
            Key={'reservation_id': reservation_id},  # Primary Key
            # UpdateExpression: 업데이트할 속성 지정
            # SET: 속성 값 설정
            UpdateExpression='SET #status = :status',
            # ExpressionAttributeNames: 예약어 회피
            # 'status'는 DynamoDB 예약어이므로 #status로 대체
            ExpressionAttributeNames={'#status': 'status'},
            # ExpressionAttributeValues: 업데이트할 값
            ExpressionAttributeValues={':status': 'cancelled'}
        )
        
        # 성공 응답 반환
        return {
            'success': True,
            'message': f'예약 번호 {reservation_id}가 취소되었습니다.'
        }
    except Exception as e:
        # 예외 발생 시 오류 반환
        return {
            'success': False,
            'error': str(e)
        }
