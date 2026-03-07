---
title: "AWS Infrastructure Composer를 활용한 서버리스 템플릿 설계"
week: 6
session: 3
awsServices:
  - AWS CloudFormation
  - AWS Infrastructure Composer
learningObjectives:
  - AWS Infrastructure Composer의 시각적 설계 기능을 이해할 수 있습니다.
  - Amazon DynamoDB, AWS Lambda, AWS IAM 역할을 드래그 앤 드롭으로 추가하고 연결할 수 있습니다.
  - Amazon API Gateway를 추가하고 AWS Lambda 함수와 통합할 수 있습니다.
  - 생성된 AWS CloudFormation 템플릿을 검토하고 배포할 수 있습니다.
prerequisites:
  - Week 6-1 AWS CloudFormation 개요 이해
  - Week 6-2 AWS CloudFormation 템플릿 작성 완료
  - AWS Lambda 및 서버리스 기본 개념 이해
---

이 실습에서는 AWS Infrastructure Composer를 사용하여 비주얼 디자이너와 Template 탭 코드 편집을 결합하여 서버리스 애플리케이션을 구축합니다. AWS Lambda, Amazon API Gateway, Amazon DynamoDB를 드래그 앤 드롭으로 추가하고, Template 탭에서 세부 설정을 코드로 작성하여 간단한 REST API를 구현합니다.

> [!IMPORTANT] AWS Infrastructure Composer 지원 리소스
> 
> **AWS Infrastructure Composer는 주로 서버리스 리소스를 지원합니다:**
> 
> - ✅ **지원**: AWS Lambda, Amazon API Gateway, Amazon DynamoDB, Amazon S3, AWS Step Functions, Amazon SNS, Amazon SQS 등
> - ❌ **제한적 지원**: Amazon VPC, Amazon EC2, 네트워킹 리소스 (드래그 앤 드롭 불가, Template 탭에서 직접 코드 편집 필요)
> 
> **이 실습의 변경사항:**
> 
> - Week 6-2에서 작성했던 Amazon VPC + Amazon EC2 웹 서버 대신 **서버리스 REST API**를 구축합니다.
> - AWS Lambda 함수, Amazon API Gateway, Amazon DynamoDB 테이블을 드래그 앤 드롭으로 설계합니다.
> - Infrastructure Composer의 강점인 서버리스 아키텍처 설계에 집중합니다.

> [!NOTE] AWS Infrastructure Composer UI 변경 안내
> 
> AWS Infrastructure Composer는 AWS가 지속적으로 개선하고 있는 서비스로, UI가 변경될 수 있습니다.
> 이 가이드는 2025년 2월 기준으로 작성되었으며, 실제 화면과 다를 수 있습니다.
> 
> **UI가 변경된 경우**:
> - 기본 개념(리소스 팔레트, 캔버스, 속성 패널)은 동일하게 유지됩니다.
> - 버튼 이름이나 위치가 다를 수 있지만 유사한 기능을 찾아 진행합니다.
> - 예: "Create project" → "New project", "Template format" → "Format" 등
> - 리소스 팔레트의 카테고리 구조가 변경될 수 있지만 리소스 이름은 동일합니다.
> - 검색 기능을 활용하면 리소스를 쉽게 찾을 수 있습니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
> AWS Lambda 함수와 Amazon DynamoDB 테이블은 프리 티어 범위 내에서 사용 가능하지만, 프리 티어를 초과하면 비용이 발생할 수 있습니다.

## 태스크 1: AWS Infrastructure Composer 시작

이 태스크에서는 AWS Application Composer 콘솔에 접속하여 AWS Infrastructure Composer를 시작합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Application Composer`을 입력하고 선택합니다.

> [!NOTE]
> AWS Infrastructure Composer는 AWS Application Composer 서비스의 일부입니다. 검색 시 "Application Composer"로 검색하면 됩니다.

2. [[Create project]] 버튼을 클릭합니다.
3. **Project name**에 `serverless-rest-api`를 입력합니다.
4. **Template format**에서 `YAML`을 선택합니다.
5. [[Create]] 버튼을 클릭합니다.

> [!NOTE]
> AWS Infrastructure Composer는 비주얼 디자이너로 인프라를 설계하면 자동으로 AWS CloudFormation 템플릿을 생성합니다.
> 왼쪽에는 리소스 팔레트, 중앙에는 캔버스, 오른쪽에는 생성된 YAML 코드가 표시됩니다.

✅ **태스크 완료**: AWS Infrastructure Composer 프로젝트가 생성되었습니다.

## 태스크 2: Amazon DynamoDB 테이블 추가

이 태스크에서는 드래그 앤 드롭으로 Amazon DynamoDB 테이블을 캔버스에 추가하여 데이터를 저장할 데이터베이스를 생성합니다.

6. 왼쪽 리소스 팔레트에서 **Database** 카테고리를 확장합니다.
7. **Amazon DynamoDB Table**을 찾아서 중앙 캔버스로 드래그합니다.
8. 캔버스에 배치된 Amazon DynamoDB Table 리소스를 클릭합니다.

> [!TIP]
> 리소스 팔레트의 카테고리 이름이 변경된 경우 검색 기능을 사용하여 "Amazon DynamoDB"를 직접 검색합니다.
9. 오른쪽 속성 패널에서 **Logical ID**를 `ItemsTable`로 변경합니다.
10. **Properties** 섹션을 확장합니다.
11. **AttributeDefinitions** 섹션을 확장합니다.
12. [[Add item]] 버튼을 클릭합니다.
13. 첫 번째 속성을 다음과 같이 설정합니다:
   - **AttributeName**: `id`
   - **AttributeType**: `S`
14. **KeySchema** 섹션을 확장합니다.
15. [[Add item]] 버튼을 클릭합니다.
16. 키 스키마를 다음과 같이 설정합니다:
    - **AttributeName**: `id`
    - **KeyType**: `HASH`
17. **BillingMode**에서 `PAY_PER_REQUEST`를 선택합니다.

> [!NOTE]
> 속성을 변경하면 오른쪽 YAML 코드가 실시간으로 업데이트됩니다.
> `PAY_PER_REQUEST` 모드는 프로비저닝된 용량 없이 사용한 만큼만 비용을 지불합니다.

✅ **태스크 완료**: Amazon DynamoDB 테이블이 추가되었습니다.

## 태스크 3: AWS Lambda 함수 추가

이 태스크에서는 Amazon DynamoDB 테이블에 데이터를 저장하고 조회하는 AWS Lambda 함수를 추가합니다.

> [!NOTE] Template 탭 코드 편집
> 
> 이 태스크부터는 **Template 탭에서 YAML 코드를 직접 편집**합니다.
> Infrastructure Composer는 비주얼 디자인과 코드 편집을 결합하여 사용하는 도구입니다.
> AWS Lambda 함수 코드와 같은 세부 설정은 Template 탭에서 작성하는 것이 더 효율적입니다.

18. 왼쪽 리소스 팔레트에서 **Compute** 카테고리를 확장합니다.
19. **AWS Lambda Function**을 찾아서 캔버스로 드래그합니다.
20. AWS Lambda Function 리소스를 클릭합니다.
21. 오른쪽 속성 패널에서 **Logical ID**를 `ItemsFunction`로 변경합니다.
22. **Properties** 섹션을 확장합니다.
23. **Runtime**에서 `python3.12`를 선택합니다.

> [!NOTE]
> 2026년 시점에서 `python3.12` 런타임이 지원되지 않을 경우, 콘솔에 표시되는 최신 Python 3.x 버전을 선택합니다.

24. **Handler**에 `index.lambda_handler`를 입력합니다.
25. 오른쪽 패널에서 **Template** 탭을 선택합니다.
26. `ItemsFunction` 리소스의 `Properties` 섹션을 찾습니다.
27. `Handler` 속성 다음에 `Code` 속성을 추가합니다:

```yaml
Code:
  ZipFile: |
    import json
    import boto3
    import os

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])

    def lambda_handler(event, context):
        http_method = event['httpMethod']
        
        if http_method == 'GET':
            response = table.scan()
            items = response.get('Items', [])
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(items, default=str)
            }
        
        elif http_method == 'POST':
            body = json.loads(event['body'])
            table.put_item(Item=body)
            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Item created'})
            }
        
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported method'})
        }
```

28. `Code` 속성 다음에 `Environment` 속성을 추가합니다:

```yaml
Environment:
  Variables:
    TABLE_NAME: !Ref ItemsTable
```

> [!NOTE] AWS Lambda 함수 코드 편집 및 Infrastructure Composer 한계
> 
> **AWS Lambda 함수 코드**: Amazon DynamoDB 테이블에서 데이터를 조회(GET)하고 생성(POST)하는 간단한 REST API를 구현합니다.
> 
> **Infrastructure Composer 한계**: Infrastructure Composer에서 AWS Lambda 함수 코드는 비주얼로 설정할 수 없어 Template 탭에서 직접 코드 편집이 필요합니다. 이는 현실적 한계이며, 복잡한 설정은 Template 탭에서 직접 편집해야 합니다.

29. **Canvas** 탭을 선택합니다.
30. AWS Lambda Function과 Amazon DynamoDB Table 사이에 연결선이 표시되는지 확인합니다.

> [!WARNING] Template 탭 코드 편집 주의사항
> 
> Template 탭에서 코드를 직접 편집한 후 Canvas 탭을 선택하면, Infrastructure Composer가 코드를 파싱하여 캔버스를 업데이트합니다.
> YAML 문법 오류(들여쓰기, 콜론 누락 등)가 있으면 편집 내용이 손실되거나 리소스가 캔버스에서 사라질 수 있습니다.
> Canvas 탭으로 전환하기 전에 YAML 문법이 올바른지 확인합니다.

> [!NOTE]
> `!Ref ItemsTable`을 사용하면 Infrastructure Composer가 자동으로 AWS Lambda 함수와 Amazon DynamoDB 테이블 간의 관계를 시각화합니다.

✅ **태스크 완료**: AWS Lambda 함수가 추가되었습니다.

## 태스크 4: AWS IAM 역할 추가 및 AWS Lambda 함수 권한 설정

이 태스크에서는 AWS Lambda 함수가 Amazon DynamoDB 테이블에 접근할 수 있도록 AWS IAM 역할을 추가하고 권한을 설정합니다.

> [!NOTE] Template 탭 코드 편집
> 
> 이 태스크에서도 **Template 탭에서 YAML 코드를 직접 편집**합니다.
> AWS IAM 역할의 정책 문서는 비주얼로 설정할 수 없어 Template 탭에서 직접 작성해야 합니다.

31. 왼쪽 리소스 팔레트에서 **Security, Identity, & Compliance** 카테고리를 확장합니다.
32. **AWS IAM Role**을 찾아서 캔버스로 드래그합니다.
33. AWS IAM Role 리소스를 클릭합니다.
34. 오른쪽 속성 패널에서 **Logical ID**를 `ItemsFunctionRole`로 변경합니다.
35. 오른쪽 패널에서 **Template** 탭을 선택합니다.
36. `ItemsFunctionRole` 리소스를 찾습니다.
37. 기존 자동 생성된 `ItemsFunctionRole` 블록 전체를 다음으로 교체합니다:

```yaml
ItemsFunctionRole:
  Type: AWS::AWS IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: DynamoDBAccess
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:PutItem
                - dynamodb:GetItem
                - dynamodb:Scan
                - dynamodb:Query
              Resource: !GetAtt ItemsTable.Arn
```

> [!WARNING] Template 탭 코드 편집 주의사항
> 
> Template 탭에서 코드를 직접 편집한 후 Canvas 탭을 선택하면, Infrastructure Composer가 코드를 파싱하여 캔버스를 업데이트합니다.
> YAML 문법 오류가 있으면 캔버스가 정상적으로 표시되지 않을 수 있으니, 코드 편집 후 오류가 없는지 확인합니다.

38. `ItemsFunction` 리소스를 찾습니다.
39. `Properties` 섹션에 `Role` 속성을 추가합니다:

```yaml
Role: !GetAtt ItemsFunctionRole.Arn
```

> [!NOTE] AWS IAM 역할 편집 및 Infrastructure Composer 한계
> 
> **AWS IAM 역할**: AWS Lambda 함수가 Amazon DynamoDB 테이블에 접근하고 Amazon CloudWatch Logs에 로그를 기록할 수 있도록 권한을 부여합니다.
> 
> **Infrastructure Composer 한계**: AWS IAM 역할의 정책 문서는 비주얼로 설정할 수 없어 Template 탭에서 직접 코드 편집이 필요합니다.

40. **Canvas** 탭을 선택합니다.
41. AWS Lambda Function과 AWS IAM Role 사이에 연결선이 표시되는지 확인합니다.

✅ **태스크 완료**: AWS IAM 역할이 추가되고 AWS Lambda 함수 권한이 설정되었습니다.

## 태스크 5: Amazon API Gateway 추가 및 AWS Lambda 함수 연결

이 태스크에서는 REST API를 생성하고 AWS Lambda 함수와 연결하여 HTTP 요청을 처리할 수 있도록 구성합니다.

> [!NOTE] Template 탭 코드 편집
> 
> 이 태스크에서도 **Template 탭에서 YAML 코드를 직접 편집**합니다.
> Amazon API Gateway의 리소스, 메서드, 배포, AWS Lambda 권한은 비주얼로 설정할 수 없어 Template 탭에서 직접 작성해야 합니다.

42. 왼쪽 리소스 팔레트에서 **Networking & Content Delivery** 카테고리를 확장합니다.
43. **Amazon API Gateway REST API**를 찾아서 캔버스로 드래그합니다.
44. REST API 리소스를 클릭합니다.
45. 오른쪽 속성 패널에서 **Logical ID**를 `ItemsApi`로 변경합니다.
46. **Properties** 섹션을 확장합니다.
47. **Name**에 `Items API`를 입력합니다.
48. 오른쪽 패널에서 **Template** 탭을 선택합니다.
49. `ItemsApi` 리소스 다음에 다음 리소스들을 추가합니다:

```yaml
ItemsApiResource:
  Type: AWS::ApiGateway::Resource
  Properties:
    RestApiId: !Ref ItemsApi
    ParentId: !GetAtt ItemsApi.RootResourceId
    PathPart: items

ItemsApiMethod:
  Type: AWS::ApiGateway::Method
  Properties:
    RestApiId: !Ref ItemsApi
    ResourceId: !Ref ItemsApiResource
    HttpMethod: ANY
    AuthorizationType: NONE
    Integration:
      Type: AWS_PROXY
      IntegrationHttpMethod: POST
      Uri: !Sub arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${ItemsFunction.Arn}/invocations

ItemsApiDeployment:
  Type: AWS::ApiGateway::Deployment
  DependsOn: ItemsApiMethod
  Properties:
    RestApiId: !Ref ItemsApi
    StageName: prod

LambdaApiPermission:
  Type: AWS::AWS Lambda::Permission
  Properties:
    FunctionName: !Ref ItemsFunction
    Action: lambda:InvokeFunction
    Principal: apigateway.amazonaws.com
    SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ItemsApi}/*/*/items
```

> [!NOTE] AWS Lambda 권한 SourceArn 패턴 설명
> 
> **SourceArn 패턴**: `arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ItemsApi}/*/*/items`
> - 첫 번째 `*`: 스테이지 이름 (prod, dev 등 모든 스테이지 허용)
> - 두 번째 `*`: HTTP 메서드 (GET, POST 등 모든 메서드 허용)
> - `/items`: API 경로
> 
> 이 패턴은 보안상 문제가 없으며, 모든 스테이지와 메서드에서 `/items` 경로로 AWS Lambda 함수를 호출할 수 있도록 허용합니다.

> [!NOTE] Amazon API Gateway 설정 및 Infrastructure Composer 한계
> 
> **Amazon API Gateway 설정**: `/items` 경로에 ANY 메서드를 생성하여 모든 HTTP 메서드(GET, POST 등)를 AWS Lambda 함수로 프록시합니다.
> 
> **Infrastructure Composer 한계**: Amazon API Gateway의 리소스, 메서드, 배포, AWS Lambda 권한은 비주얼로 설정할 수 없어 Template 탭에서 직접 코드 편집이 필요합니다. 이는 Infrastructure Composer가 주로 간단한 서버리스 아키텍처에 최적화되어 있기 때문입니다.

50. **Canvas** 탭을 선택합니다.
51. Amazon API Gateway와 AWS Lambda Function 사이에 연결선이 표시되는지 확인합니다.

> [!NOTE]
> Infrastructure Composer는 `!Ref`와 `!Sub` 함수를 분석하여 리소스 간 관계를 시각화합니다.

✅ **태스크 완료**: Amazon API Gateway가 추가되고 AWS Lambda 함수와 연결되었습니다.

## 태스크 6: 템플릿 검토 및 AWS CloudFormation 배포

이 태스크에서는 자동으로 생성된 AWS CloudFormation 템플릿을 검토하고 AWS에 배포합니다.

52. 오른쪽 패널에서 **Template** 탭을 선택합니다.
53. 생성된 YAML 템플릿을 검토합니다.
54. 모든 리소스가 올바르게 정의되었는지 확인합니다:
   - `ItemsTable` (Amazon DynamoDB 테이블)
   - `ItemsFunction` (AWS Lambda 함수)
   - `ItemsFunctionRole` (AWS IAM 역할)
   - `ItemsApi` (Amazon API Gateway REST API)
   - `ItemsApiResource`, `ItemsApiMethod`, `ItemsApiDeployment` (Amazon API Gateway 설정)
   - `LambdaApiPermission` (AWS Lambda 권한)

> [!NOTE]
> AWS Infrastructure Composer가 자동으로 생성한 템플릿은 서버리스 REST API를 구현하는 표준 패턴을 따릅니다.
> 차이점은 코드를 직접 작성하지 않고 비주얼 디자이너로 설계했다는 것입니다.

55. 템플릿의 `Resources` 섹션 끝에 `Outputs` 섹션을 추가합니다 (YAML 들여쓰기 수준 주의: `Resources`와 동일한 레벨):

```yaml
Outputs:
  ApiUrl:
    Description: Amazon API Gateway endpoint URL
    Value: !Sub https://${ItemsApi}.execute-api.${AWS::Region}.amazonaws.com/prod/items
```

> [!IMPORTANT] Outputs 섹션 위치
> 
> `Outputs` 섹션은 `Resources` 블록 바깥에 위치해야 합니다. YAML 들여쓰기 수준이 `Resources`와 동일해야 합니다.
> 
> **올바른 구조**:
> ```yaml
> Resources:
>   ItemsTable:
>     Type: AWS::Amazon DynamoDB::Table
>     ...
>   ItemsFunction:
>     Type: AWS::AWS Lambda::Function
>     ...
> 
> Outputs:  # Resources와 동일한 들여쓰기 레벨
>   ApiUrl:
>     Description: ...
> ```

56. **Template** 탭에서 전체 YAML 코드를 복사합니다.
57. 새 브라우저 탭을 엽니다.
58. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
59. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
60. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
61. **Specify template**에서 `Upload a template file`을 선택합니다.
62. 복사한 YAML 코드를 텍스트 파일로 저장합니다 (예: `serverless-api-template.yaml`).
63. [[Choose file]] 버튼을 클릭한 후 저장한 YAML 파일을 선택합니다.
64. [[Next]] 버튼을 클릭합니다.
65. **Stack name**에 `infrastructure-composer-serverless-api`를 입력합니다.
66. [[Next]] 버튼을 클릭합니다.
67. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 찾습니다.
68. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key | Value |
|-----|-------|
| `Project` | `AWS-Lab` |
| `Week` | `6-3` |
| `CreatedBy` | `Student` |

69. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
70. [[Next]] 버튼을 클릭합니다.
71. **Review** 페이지에서 설정을 확인합니다.
72. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> Infrastructure Composer의 Deploy 버튼은 로컬 파일 시스템과 동기화된 프로젝트에서만 정상 작동합니다.
> 브라우저 전용 모드에서는 위의 수동 배포 방법을 사용하는 것이 더 안정적입니다.

73. AWS CloudFormation 콘솔에서 스택 생성이 시작됩니다.
74. **Events** 탭을 선택합니다.

> [!NOTE]
> **Events** 탭에는 리소스 생성 과정이 실시간으로 표시됩니다.
> Amazon DynamoDB 테이블, AWS IAM 역할, AWS Lambda 함수, Amazon API Gateway가 순차적으로 생성됩니다.
> 스택 생성에 2-3분이 소요됩니다. 대기하는 동안 Infrastructure Composer 탭을 선택하여 생성한 아키텍처 다이어그램을 다시 확인하거나, Week 6-1과 6-2에서 학습한 AWS CloudFormation 개념을 복습할 수 있습니다.
> 
> **스택 태그 자동 전파**: 스택에 추가한 태그(`Project`, `Week`, `CreatedBy`)는 스택이 생성하는 모든 리소스(Amazon DynamoDB, AWS Lambda, Amazon API Gateway 등)에 자동으로 전파됩니다.

75. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: AWS CloudFormation 스택이 배포되었습니다.

## 태스크 7: REST API 테스트

이 태스크에서는 생성된 Amazon API Gateway 엔드포인트로 HTTP 요청을 보내 REST API가 정상적으로 작동하는지 확인합니다.

76. AWS CloudFormation 콘솔에서 `infrastructure-composer-serverless-api` 스택을 선택합니다.
77. **Outputs** 탭을 선택합니다.
78. **Key**가 `ApiUrl`인 출력값을 찾습니다.
79. **Value** 열의 URL을 복사합니다.

> [!NOTE]
> API URL은 다음과 같은 형식입니다: `https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items`

80. CloudShell 아이콘을 클릭합니다.
81. CloudShell이 시작될 때까지 기다립니다.

> [!NOTE]
> CloudShell 시작에 1-2분이 소요될 수 있습니다.

82. 다음 명령어를 실행하여 아이템을 생성합니다:

```bash
curl -X POST https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items \
  -H "Content-Type: application/json" \
  -d '{"id": "item1", "name": "Sample Item", "description": "Created from Infrastructure Composer"}'
```

> [!NOTE]
> `https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items` 부분을 복사한 API URL로 대체합니다.

> [!OUTPUT]
> ```json
> {"message": "Item created"}
> ```

83. 다음 명령어를 실행하여 모든 아이템을 조회합니다:

```bash
curl https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items
```

> [!OUTPUT]
> ```json
> [{"id": "item1", "name": "Sample Item", "description": "Created from Infrastructure Composer"}]
> ```

84. 생성한 아이템이 조회되는지 확인합니다.

> [!TIP]
> 추가 아이템을 생성하려면 7단계의 명령어를 다른 `id` 값으로 반복 실행합니다.
> 예: `{"id": "item2", "name": "Another Item", "description": "Test data"}`

✅ **태스크 완료**: REST API가 정상적으로 작동합니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Infrastructure Composer의 비주얼 디자이너로 서버리스 인프라를 설계했습니다
- 드래그 앤 드롭으로 Amazon DynamoDB, AWS Lambda, Amazon API Gateway를 추가했습니다
- 비주얼 디자인이 자동으로 AWS CloudFormation 템플릿으로 변환되는 과정을 확인했습니다
- 비주얼 디자이너와 Template 탭 코드 편집을 결합하여 서버리스 REST API를 구축하고 배포했습니다
- 📚 참고 섹션에서 Week 6-2의 코드 방식과 Week 6-3의 하이브리드 방식을 비교할 수 있습니다

## 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `6-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 모든 리소스(AWS CloudFormation 스택, Amazon DynamoDB 테이블, AWS Lambda 함수, Amazon API Gateway 등)가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: AWS CloudFormation 스택 삭제

8. AWS CloudFormation 콘솔로 이동합니다.
9. `infrastructure-composer-serverless-api` 스택을 선택합니다.
10. [[Delete]] 버튼을 클릭합니다.
11. 확인 대화상자에서 [[Delete]] 버튼을 클릭합니다.
12. 스택 삭제가 완료될 때까지 기다립니다 (2-3분 소요).

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 AWS Lambda 함수, Amazon API Gateway, AWS IAM 역할, Amazon DynamoDB 테이블 등 모든 리소스가 자동으로 삭제됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS Application Composer 사용 설명서](https://docs.aws.amazon.com/ko_kr/application-composer/latest/dg/what-is-composer.html)
- [Infrastructure Composer로 인프라 설계](https://docs.aws.amazon.com/ko_kr/application-composer/latest/dg/infrastructure-composer.html)
- [AWS CloudFormation 템플릿 자동 생성](https://docs.aws.amazon.com/ko_kr/application-composer/latest/dg/template-generation.html)

## 📚 참고: 코드 vs 하이브리드 비교

### Week 6-2 (코드 방식) vs Week 6-3 (하이브리드 방식)

**Week 6-2: AWS CloudFormation 템플릿 작성 (코드)**
- YAML 문법을 직접 작성합니다
- 리소스 간 참조를 수동으로 설정합니다 (`!Ref`, `!GetAtt`)
- 문법 오류 가능성이 있습니다
- 코드 리뷰와 버전 관리가 용이합니다
- 복잡한 로직과 조건문을 사용할 수 있습니다

**Week 6-3: Infrastructure Composer (하이브리드 방식)**
- 드래그 앤 드롭으로 기본 리소스를 추가합니다
- Template 탭에서 세부 설정을 코드로 편집합니다
- 비주얼 디자이너와 코드 편집을 결합하여 사용합니다
- 시각적으로 아키텍처를 이해하기 쉽습니다
- 빠른 프로토타이핑에 적합합니다

### 서버리스 아키텍처 구성 요소

이 실습에서 구축한 서버리스 REST API는 다음 구성 요소로 이루어져 있습니다:

**구성 요소**:
- **Amazon DynamoDB**: NoSQL 데이터베이스로 아이템 데이터를 저장합니다
- **AWS Lambda**: Python 함수로 비즈니스 로직을 실행합니다 (GET, POST 요청 처리)
- **Amazon API Gateway**: REST API 엔드포인트를 제공하고 AWS Lambda 함수를 호출합니다
- **AWS IAM**: AWS Lambda 함수가 Amazon DynamoDB에 접근할 수 있도록 권한을 부여합니다

**데이터 흐름**:
13. 클라이언트가 Amazon API Gateway 엔드포인트로 HTTP 요청을 보냅니다.
14. Amazon API Gateway가 AWS Lambda 함수를 호출합니다.
15. AWS Lambda 함수가 Amazon DynamoDB 테이블에서 데이터를 조회하거나 생성합니다.
16. AWS Lambda 함수가 결과를 Amazon API Gateway로 반환합니다.
17. Amazon API Gateway가 HTTP 응답을 클라이언트에게 전달합니다.

### Infrastructure Composer의 장점

**빠른 시작**
- 드래그 앤 드롭으로 기본 리소스를 즉시 추가할 수 있습니다
- AWS 리소스 목록을 탐색하면서 학습할 수 있습니다
- 비주얼 디자이너로 직관적으로 설계할 수 있습니다

**시각적 이해**
- 아키텍처를 다이어그램으로 볼 수 있습니다
- 리소스 간 관계를 시각적으로 확인할 수 있습니다
- 팀원과 아키텍처를 쉽게 공유할 수 있습니다

**자동 코드 생성**
- 비주얼 디자인이 실시간으로 YAML 코드로 변환됩니다
- 생성된 코드를 학습 자료로 활용할 수 있습니다
- 코드를 직접 편집하여 세밀한 조정도 가능합니다

**오류 방지 (드래그 앤 드롭 리소스에 한함)**
- 드래그 앤 드롭으로 추가한 리소스는 기본 문법 오류가 발생하지 않습니다
- 필수 속성을 누락하지 않도록 가이드합니다
- 리소스 간 참조(`!Ref`)가 자동으로 생성됩니다

> [!NOTE]
> Template 탭에서 직접 편집한 코드는 YAML 문법 오류가 발생할 수 있으므로 주의가 필요합니다.

### Infrastructure Composer의 한계

**복잡한 설정은 코드 편집 필요**
- AWS Lambda 함수 코드는 Template 탭에서 직접 편집해야 합니다
- AWS IAM 정책 문서는 비주얼로 설정할 수 없습니다
- Amazon API Gateway의 세부 설정(리소스, 메서드, 배포)은 코드로 작성해야 합니다

**서버리스 리소스 중심**
- Amazon VPC, Amazon EC2, 네트워킹 리소스는 드래그 앤 드롭이 제한적입니다
- 주로 AWS Lambda, Amazon API Gateway, Amazon DynamoDB, Amazon S3, AWS Step Functions 등 서버리스 리소스에 최적화되어 있습니다

**학습 곡선**
- 비주얼 디자이너와 Template 탭을 함께 사용해야 합니다
- 어떤 설정은 비주얼로, 어떤 설정은 코드로 해야 하는지 구분이 필요합니다

### AWS CloudFormation 템플릿 작성의 장점

**세밀한 제어**
- 모든 속성을 직접 제어할 수 있습니다
- 복잡한 조건문과 반복문을 사용할 수 있습니다
- 고급 기능(Nested Stacks, Custom Resources)을 활용할 수 있습니다

**버전 관리**
- Git 등의 버전 관리 시스템에 저장하기 쉽습니다
- 변경 이력을 추적할 수 있습니다
- 코드 리뷰 프로세스를 적용할 수 있습니다

**자동화**
- CI/CD 파이프라인에 통합하기 쉽습니다
- 스크립트로 템플릿을 생성하거나 수정할 수 있습니다
- 대규모 인프라를 효율적으로 관리할 수 있습니다

### 사용 사례별 권장사항

**Infrastructure Composer 사용 권장**:
- 서버리스 애플리케이션 프로토타이핑
- 아키텍처 설계 및 팀 논의
- AWS CloudFormation 학습 초기 단계
- 간단한 서버리스 인프라 구축

**AWS CloudFormation 템플릿 작성 권장**:
- 프로덕션 환경 배포
- 복잡한 인프라 구성 (Amazon VPC, 네트워킹)
- CI/CD 파이프라인 통합
- 대규모 인프라 관리

### 하이브리드 접근 방식

**최적의 워크플로우**:
18. Infrastructure Composer로 초기 서버리스 아키텍처 설계.
19. 자동 생성된 템플릿을 다운로드.
20. 코드 에디터에서 세밀한 조정 (AWS Lambda 코드, AWS IAM 정책 등).
21. Git에 저장하고 버전 관리.
22. CI/CD 파이프라인으로 배포.

이 방식은 두 접근 방식의 장점을 모두 활용할 수 있습니다.
