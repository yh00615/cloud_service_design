# Week 1-1 Tag Editor Lab - CloudFormation 스택 배포 가이드

## 개요

이 CloudFormation 템플릿은 Week 1-1 Tag Editor 실습을 위한 QuickTable 레스토랑 예약 시스템의 기본 AWS 리소스를 자동으로 생성합니다.

## 생성되는 리소스

### 1. Amazon S3 버킷 (2개)

- **quicktable-reservations-{계정ID}**: QuickTable 예약 데이터 저장용 버킷
- **quicktable-logs-{계정ID}**: QuickTable 로그 저장용 버킷

**설정**:
- 퍼블릭 액세스 차단 활성화
- 버전 관리 비활성화 (기본값)
- 암호화 비활성화 (기본값)

### 2. AWS Lambda 함수 (1개)

- **QuickTableGetReservation**: QuickTable 예약 조회 함수

**설정**:
- Runtime: Python 3.12
- Handler: index.lambda_handler
- 메모리: 128MB (기본값)
- 타임아웃: 3초 (기본값)
- 환경 변수: TABLE_NAME=QuickTableReservations

**코드**:
```python
import json
import os

def lambda_handler(event, context):
    """
    QuickTable 예약 조회 Lambda 함수
    
    이 함수는 QuickTable 레스토랑 예약 시스템에서 예약 정보를 조회합니다.
    Tag Editor 실습에서 Lambda 함수 태그 관리를 연습하기 위한 샘플 함수입니다.
    """
    table_name = os.environ.get('TABLE_NAME', 'QuickTableReservations')
    
    # 샘플 응답 (실제 DynamoDB 조회는 Week 4-2에서 구현)
    response = {
        'message': 'QuickTable Reservation System',
        'tableName': table_name,
        'status': 'Ready for reservations'
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

### 3. Amazon DynamoDB 테이블 (1개)

- **QuickTableReservations**: QuickTable 예약 데이터 테이블

**설정**:
- Billing Mode: PAY_PER_REQUEST (온디맨드)
- Partition Key: userId (String)
- Sort Key: reservationId (String)

### 4. IAM 역할 (1개)

- **QuickTableLambdaExecutionRole**: Lambda 함수 실행 역할

**권한**:
- AWSLambdaBasicExecutionRole (CloudWatch Logs 쓰기 권한)
- QuickTableDynamoDBReadPolicy (DynamoDB 읽기 권한)

## 태그 전략

모든 리소스에 다음 태그가 자동으로 추가됩니다:

| Tag Key | Tag Value | 설명 |
|---------|-----------|------|
| `Project` | `AWS-Lab` | 프로젝트 식별자 |
| `Week` | `1-1` | 주차 및 세션 번호 |
| `CreatedBy` | `CloudFormation` | 생성 방법 |
| `Component` | `Storage`, `Database`, `API`, `Security`, `Logging` | 시스템 컴포넌트 |

> [!NOTE]
> 실습 중에 S3 버킷에 수동으로 태그를 추가하여 `CreatedBy` 값을 `Student`로 변경합니다.

## 배포 방법

### 1. AWS Management Console 사용

1. AWS Management Console에 로그인합니다.
2. CloudFormation 서비스로 이동합니다.
3. [[Create stack]] 버튼을 클릭합니다.
4. **Upload a template file**을 선택하고 `tag-editor-lab-stack.yaml` 파일을 업로드합니다.
5. 스택 이름: `week1-1-tag-editor-lab-stack`
6. 파라미터는 기본값을 사용합니다.
7. [[Next]] → [[Next]] → [[Submit]] 버튼을 클릭합니다.
8. 스택 생성이 완료될 때까지 기다립니다 (2-3분 소요).

### 2. AWS CLI 사용

```bash
aws cloudformation create-stack \
  --stack-name week1-1-tag-editor-lab-stack \
  --template-body file://tag-editor-lab-stack.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-2
```

## 출력값 (Outputs)

스택 생성 완료 후 다음 출력값을 확인할 수 있습니다:

| Output Key | 설명 | 예시 값 |
|-----------|------|---------|
| `ReservationsBucketName` | QuickTable 예약 데이터 버킷 이름 | quicktable-reservations-123456789012 |
| `LogsBucketName` | QuickTable 로그 버킷 이름 | quicktable-logs-123456789012 |
| `ReservationsTableName` | QuickTable 예약 DynamoDB 테이블 이름 | QuickTableReservations |
| `GetReservationFunctionName` | QuickTable 예약 조회 Lambda 함수 이름 | QuickTableGetReservation |
| `GetReservationFunctionArn` | QuickTable 예약 조회 Lambda 함수 ARN | arn:aws:lambda:ap-northeast-2:123456789012:function:QuickTableGetReservation |

## 비용 정보

이 스택에서 생성하는 모든 리소스는 AWS 프리티어 범위 내에서 사용 가능합니다:

| 리소스 | 프리티어 | 비용 |
|--------|---------|------|
| S3 버킷 | 5GB 스토리지 | 사용하지 않으면 $0 |
| Lambda 함수 | 100만 요청/월 | 사용하지 않으면 $0 |
| DynamoDB 테이블 | 25GB 스토리지 | 사용하지 않으면 $0 |
| IAM 역할 | 무료 | $0 |

> [!NOTE]
> 실습 종료 후 스택을 삭제하면 모든 리소스가 자동으로 삭제되어 비용이 발생하지 않습니다.

## 스택 삭제

실습 종료 후 다음 방법으로 스택을 삭제합니다:

### 1. AWS Management Console 사용

1. CloudFormation 콘솔로 이동합니다.
2. `week1-1-tag-editor-lab-stack` 스택을 선택합니다.
3. [[Delete]] 버튼을 클릭합니다.
4. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
5. 스택 삭제가 완료될 때까지 기다립니다 (2-3분 소요).

### 2. AWS CLI 사용

```bash
aws cloudformation delete-stack \
  --stack-name week1-1-tag-editor-lab-stack \
  --region ap-northeast-2
```

## 문제 해결

### 문제 1: S3 버킷 이름 충돌

**증상**: "Bucket name already exists" 오류 발생

**원인**: S3 버킷 이름은 전 세계적으로 고유해야 하는데, 이미 사용 중인 이름입니다.

**해결**:
1. CloudFormation 콘솔에서 스택을 삭제합니다.
2. 템플릿의 `BucketSuffix` 파라미터를 수정하여 고유한 값을 사용합니다.
3. 스택을 다시 생성합니다.

### 문제 2: IAM 역할 생성 권한 부족

**증상**: "User is not authorized to perform: iam:CreateRole" 오류 발생

**원인**: IAM 역할을 생성할 권한이 없습니다.

**해결**:
1. AWS 계정 관리자에게 IAM 권한을 요청합니다.
2. 또는 관리자가 스택을 대신 생성합니다.

### 문제 3: 스택 삭제 실패

**증상**: S3 버킷이 비어있지 않아 삭제 실패

**원인**: S3 버킷에 객체가 있으면 CloudFormation이 자동으로 삭제할 수 없습니다.

**해결**:
1. S3 콘솔로 이동합니다.
2. 해당 버킷을 선택하고 모든 객체를 삭제합니다.
3. CloudFormation 스택을 다시 삭제합니다.

## QuickTable 프로젝트 연계

이 실습에서 생성한 리소스는 QuickTable 레스토랑 예약 시스템의 기본 구성 요소입니다:

- **quicktable-reservations 버킷**: 예약 데이터 및 첨부 파일 저장
- **quicktable-logs 버킷**: 시스템 로그 및 감사 로그 저장
- **QuickTableReservations 테이블**: 예약 정보 저장 (userId, reservationId 키 구조)
- **QuickTableGetReservation 함수**: 예약 조회 API (Week 4-2에서 완전한 구현)

앞으로 진행할 QuickTable 관련 실습에서 이러한 리소스 명명 규칙을 일관되게 사용합니다.

## 추가 정보

- [AWS CloudFormation 사용 설명서](https://docs.aws.amazon.com/cloudformation/)
- [AWS 프리티어](https://aws.amazon.com/free/)
- [AWS 리소스 태그 전략](https://docs.aws.amazon.com/ko_kr/general/latest/gr/aws_tagging.html)

---

**마지막 업데이트**: 2025-02-16  
**버전**: 1.0.0
