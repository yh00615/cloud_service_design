---
title: 'AWS Infrastructure Composer를 활용한 서버리스 템플릿 설계'
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
>
> - 기본 개념(리소스 팔레트, 캔버스, Resource properties panel)은 동일하게 유지됩니다.
> - 버튼 이름이나 위치가 다를 수 있지만 유사한 기능을 찾아 진행합니다.
> - 예: "Create project" → "New project", "Template format" → "Format" 등
> - 리소스 팔레트의 카테고리 구조가 변경될 수 있지만 리소스 이름은 동일합니다.
> - 검색 기능을 활용하면 리소스를 쉽게 찾을 수 있습니다.

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.
> AWS Lambda 함수와 Amazon DynamoDB 테이블은 프리 티어 범위 내에서 사용 가능하지만, 프리 티어를 초과하면 비용이 발생할 수 있습니다.

## 태스크 1: AWS Infrastructure Composer 시작

이 태스크에서는 AWS Infrastructure Composer 콘솔에 접속하여 새 프로젝트를 시작합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

1. AWS Management Console에 로그인한 후 상단 검색창에 `Infrastructure Composer`을 입력하고 선택합니다.
2. Home 페이지에서 [[Create project]] 버튼을 클릭합니다.

> [!NOTE]
> Create project를 클릭하면 빈 캔버스가 열립니다. 프로젝트 이름이나 템플릿 형식을 별도로 설정하는 단계는 없습니다.
>
> **화면 구성**:
>
> - **왼쪽**: Resources 팔레트 (Enhanced components / Standard IaC resources)
> - **중앙**: Canvas (비주얼 디자인 영역)
> - **상단**: Canvas / Template 탭 전환
>
> **저장 방법**: 작업 완료 후 Template 탭에서 YAML 코드를 복사하거나, Menu > **Save template file**로 파일을 다운로드합니다.

✅ **태스크 완료**: AWS Infrastructure Composer 프로젝트가 생성되었습니다.

## 태스크 2: Amazon DynamoDB 테이블 추가

이 태스크에서는 드래그 앤 드롭으로 Amazon DynamoDB 테이블을 캔버스에 추가하여 데이터를 저장할 데이터베이스를 생성합니다.

> [!NOTE] 태스크 2~3의 목적
>
> 태스크 2~3에서는 Infrastructure Composer의 **비주얼 디자인 기능**을 학습합니다.
> Enhanced components를 드래그 앤 드롭으로 추가하고, Resource properties panel에서 설정하는 방법을 익힙니다.
> 이 과정에서 생성되는 템플릿은 AWS SAM 형식이므로, 태스크 4에서 AWS CloudFormation 형식으로 변환하여 배포합니다.

3. 왼쪽 Resources 팔레트에서 **Enhanced components** 섹션을 확인합니다.
4. `DynamoDB table`을 찾아서 중앙 캔버스로 드래그합니다.
5. 캔버스에 배치된 DynamoDB table 카드를 클릭하여 선택합니다.
6. 카드 상단에 나타나는 **Details**를 클릭합니다.

> [!NOTE]
> 카드를 클릭하면 상단에 Details | Group | Delete 버튼이 나타납니다. **Details**를 클릭하면 우측에 Resource properties 패널이 열립니다.

7. **Logical ID**를 `ItemsTable`로 변경합니다.
8. **Partition key**에 `id`를 입력합니다.
9. **Partition key type**에서 `String`을 선택합니다.
10. **Sort key**와 **Expiry key** 체크박스는 선택하지 않습니다 (기본값 유지).
11. 우측 하단의 [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Enhanced component의 DynamoDB table은 간소화된 UI로 설정합니다.
> BillingMode(PAY_PER_REQUEST) 등 추가 설정은 Template 탭에서 확인하거나 수정할 수 있습니다.

> [!NOTE]
> 속성을 변경하면 Template 탭의 YAML 코드가 실시간으로 업데이트됩니다.
> `PAY_PER_REQUEST` 모드는 프로비저닝된 용량 없이 사용한 만큼만 비용을 지불합니다.

✅ **태스크 완료**: Amazon DynamoDB 테이블이 추가되었습니다.

## 태스크 3: AWS Lambda 함수 및 Amazon API Gateway 추가

이 태스크에서는 AWS Lambda 함수와 Amazon API Gateway를 캔버스에 추가하고 기본 설정을 합니다.

12. 왼쪽 Resources 팔레트의 **Enhanced components** 섹션에서 `Lambda function`을 찾아서 캔버스로 드래그합니다.
13. Lambda function 카드를 클릭하여 선택합니다.
14. 카드 상단의 **Details**를 클릭합니다.
15. **Logical ID**를 `ItemsFunction`로 변경합니다.
16. **Runtime**에서 `python3.13`를 선택합니다.

> [!NOTE]
> 2026년 시점에서 `python3.13` 런타임이 지원되지 않을 경우, 콘솔에 표시되는 최신 Python 3.x 버전을 선택합니다.

17. **Handler**에 `index.lambda_handler`를 입력합니다.
18. **Environment variables** 섹션에서 [[Add new item]] 버튼을 클릭합니다.
19. Key에 `TABLE_NAME`, Value에 `ItemsTable`을 입력합니다.
20. [[Save]] 버튼을 클릭합니다.

> [!NOTE]
> Enhanced components의 Lambda function은 `AWS::Serverless::Function` (AWS SAM) 타입으로 생성됩니다.
> AWS SAM 템플릿은 AWS CloudFormation 콘솔에서 직접 배포할 수 없으므로, 태스크 4에서 순수 AWS CloudFormation 형식으로 변환합니다.

21. 왼쪽 Resources 팔레트의 **Enhanced components** 섹션에서 `API Gateway`를 찾아서 캔버스로 드래그합니다.
22. API Gateway 카드를 클릭하여 선택한 후 상단의 **Details**를 클릭합니다.
23. **Logical ID**를 `ItemsApi`로 변경합니다.
24. [[Save]] 버튼을 클릭합니다.

> [!NOTE] API Gateway Resource properties 설명
>
> - **Logical ID**: 템플릿에서 이 리소스를 참조할 때 사용하는 이름
> - **Routes**: API 경로와 HTTP 메서드 설정 (예: `GET /`, `POST /items`). 이 실습에서는 태스크 4에서 AWS CloudFormation 템플릿으로 직접 설정합니다
> - **Default authoriser**: API 인증 방식 (None = 인증 없이 공개 접근 허용)
> - **CORS-allowed origins**: 브라우저에서 다른 도메인의 API를 호출할 때 허용할 출처 설정

✅ **태스크 완료**: AWS Lambda 함수와 Amazon API Gateway가 추가되었습니다.

## 태스크 4: 템플릿을 AWS CloudFormation 형식으로 변환

이 태스크에서는 Infrastructure Composer가 생성한 AWS SAM (Serverless Application Model) 템플릿을 순수 AWS CloudFormation 형식으로 변환합니다. AWS SAM 템플릿은 `sam deploy` 명령어로 배포해야 하지만, 이 실습에서는 AWS CloudFormation 콘솔에서 직접 배포하기 위해 순수 AWS CloudFormation 형식을 사용합니다.

> [!IMPORTANT] AWS SAM vs AWS CloudFormation
>
> Infrastructure Composer의 Enhanced components는 **AWS SAM (Serverless Application Model)** 형식의 템플릿을 생성합니다.
>
> - **AWS SAM 형식**: `AWS::Serverless::Function`, `Transform: AWS::Serverless-2016-10-31` 포함. AWS SAM CLI로 배포 필요
> - **AWS CloudFormation 형식**: `AWS::Lambda::Function`, Transform 없음. AWS CloudFormation 콘솔에서 직접 배포 가능
>
> 이 태스크에서는 비주얼 디자이너로 설계한 아키텍처를 확인한 후, Template 탭에서 AWS CloudFormation 호환 코드로 전체 교체합니다.

25. 상단의 **Template** 탭을 선택합니다.
26. Infrastructure Composer가 자동 생성한 AWS SAM 템플릿을 확인합니다.

> [!NOTE]
> 자동 생성된 템플릿에는 `Transform: AWS::Serverless-2016-10-31`과 `AWS::Serverless::Function` 타입이 포함되어 있습니다.
> 이 형식은 AWS CloudFormation 콘솔에서 직접 배포할 수 없으므로 순수 AWS CloudFormation 형식으로 교체합니다.

27. Template 탭의 **전체 내용을 삭제**하고 다음 코드로 교체합니다:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Serverless REST API - Infrastructure Composer Lab

Resources:
  ItemsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      BillingMode: PAY_PER_REQUEST
      KeySchema:
        - AttributeName: id
          KeyType: HASH

  ItemsFunctionRole:
    Type: AWS::IAM::Role
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

  ItemsFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.13
      Handler: index.lambda_handler
      Role: !GetAtt ItemsFunctionRole.Arn
      Environment:
        Variables:
          TABLE_NAME: !Ref ItemsTable
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

  ItemsApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: Items API

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
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ItemsFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${ItemsApi}/*/*/items

Outputs:
  ApiUrl:
    Description: Amazon API Gateway endpoint URL
    Value: !Sub https://${ItemsApi}.execute-api.${AWS::Region}.amazonaws.com/prod/items
```

> [!WARNING] Template 탭 코드 교체 주의사항
>
> 전체 내용을 교체할 때 YAML 들여쓰기가 정확해야 합니다. 복사-붙여넣기 시 들여쓰기가 깨지지 않도록 주의합니다.
> 교체 후 Canvas 탭으로 전환하면 Infrastructure Composer가 코드를 파싱하여 캔버스를 업데이트합니다.

28. 상단의 **Canvas** 탭을 선택합니다.
29. 캔버스에서 리소스 카드와 연결선이 표시되는지 확인합니다.

> [!NOTE]
> 순수 AWS CloudFormation 형식으로 변환했으므로 일부 카드가 Standard component로 표시될 수 있습니다.
> Enhanced component cards 간에는 실선, Standard component cards 간에는 점선으로 연결됩니다.

✅ **태스크 완료**: 템플릿이 AWS CloudFormation 형식으로 변환되었습니다.

## 태스크 5: AWS CloudFormation 스택 배포

이 태스크에서는 변환된 AWS CloudFormation 템플릿을 사용하여 AWS에 배포합니다.

30. Menu > **Save template file**을 선택하여 YAML 파일을 다운로드합니다.

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

31. 새 브라우저 탭에서 AWS Management Console 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
32. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
33. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
34. **Specify template**에서 `Upload a template file`을 선택합니다.
35. [[Choose file]] 버튼을 클릭한 후 다운로드한 YAML 파일을 선택합니다.
36. [[Next]] 버튼을 클릭합니다.
37. **Stack name**에 `infrastructure-composer-serverless-api`를 입력합니다.
38. [[Next]] 버튼을 클릭합니다.
39. **Configure stack options** 페이지가 열립니다.
40. **Tags** 섹션에서 [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value            |
| ----------- | ---------------- |
| `Project`   | `AWS-Lab`        |
| `Week`      | `6-3`            |
| `CreatedBy` | `CloudFormation` |

41. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
42. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

43. [[Next]] 버튼을 클릭합니다.
44. **Review and create** 페이지에서 설정을 확인합니다.
45. [[Submit]] 버튼을 클릭합니다.
46. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다 (Events 탭에서 원인 확인 필요)
>
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.

47. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: AWS CloudFormation 스택이 배포되었습니다.

## 태스크 6: REST API 테스트

이 태스크에서는 생성된 Amazon API Gateway 엔드포인트로 HTTP 요청을 보내 REST API가 정상적으로 작동하는지 확인합니다.

48. AWS CloudFormation 콘솔에서 `infrastructure-composer-serverless-api` 스택을 선택합니다.
49. **Outputs** 탭을 선택합니다.
50. **Key**가 `ApiUrl`인 출력값의 URL을 복사합니다.

> [!NOTE]
> API URL은 다음과 같은 형식입니다: `https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items`

51. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.
52. 다음 명령어를 실행하여 아이템을 생성합니다 (URL을 복사한 값으로 대체):

```bash
curl -w '\n' -X POST https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items \
  -H "Content-Type: application/json" \
  -d '{"id": "item1", "name": "Sample Item", "description": "Created from Infrastructure Composer"}'
```

> [!OUTPUT]
>
> ```json
> { "message": "Item created" }
> ```

53. 다음 명령어를 실행하여 모든 아이템을 조회합니다:

```bash
curl -s https://xxxxxxxxxx.execute-api.ap-northeast-2.amazonaws.com/prod/items \
  | python3 -m json.tool
```

> [!OUTPUT]
>
> ```json
> [
>   {
>     "id": "item1",
>     "name": "Sample Item",
>     "description": "Created from Infrastructure Composer"
>   }
> ]
> ```

54. 생성한 아이템이 조회되는지 확인합니다.

> [!TIP]
> 추가 아이템을 생성하려면 52번의 명령어를 다른 `id` 값으로 반복 실행합니다.
> 예: `{"id": "item2", "name": "Another Item", "description": "Test data"}`

✅ **태스크 완료**: REST API가 정상적으로 작동합니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS Infrastructure Composer의 비주얼 디자이너로 서버리스 인프라를 설계했습니다.
- Enhanced components를 드래그 앤 드롭으로 Amazon DynamoDB, AWS Lambda, Amazon API Gateway를 추가했습니다.
- AWS SAM 형식의 자동 생성 템플릿을 순수 AWS CloudFormation 형식으로 변환했습니다.
- 변환된 템플릿으로 서버리스 REST API를 배포하고 테스트했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `6-3`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: AWS CloudFormation 스택 삭제

8. AWS CloudFormation 콘솔로 이동합니다.
9. `infrastructure-composer-serverless-api` 스택을 선택합니다.
10. [[Delete stack]] 버튼을 클릭합니다.
11. 확인 창에서 스택 이름 `infrastructure-composer-serverless-api`를 입력합니다.
12. [[Delete stack]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation이 모든 리소스를 자동으로 삭제합니다.
> AWS Lambda 함수, Amazon API Gateway, AWS IAM 역할, Amazon DynamoDB 테이블 순서로 삭제됩니다.

### 단계 3: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

13. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
14. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
15. **Regions**에서 `ap-northeast-2`를 선택합니다.
16. **Resource types**에서 `All supported resource types`를 선택합니다.
17. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `6-3`
18. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS Infrastructure Composer 사용 설명서](https://docs.aws.amazon.com/infrastructure-composer/latest/dg/what-is-composer.html)
- [Infrastructure Composer로 첫 번째 애플리케이션 빌드](https://docs.aws.amazon.com/infrastructure-composer/latest/dg/getting-started-build.html)
- [Infrastructure Composer 카드 구성 및 수정](https://docs.aws.amazon.com/infrastructure-composer/latest/dg/using-composer-cards.html)

## 📚 참고: 코드 vs 하이브리드 비교

### Week 6-2 (코드 방식) vs Week 6-3 (하이브리드 방식)

**Week 6-2: AWS CloudFormation 템플릿 작성 (코드)**

- YAML 문법을 직접 작성
- 리소스 간 참조를 수동으로 설정 (`!Ref`, `!GetAtt`)
- 문법 오류 가능성이 있음
- 코드 리뷰와 버전 관리가 용이
- 복잡한 로직과 조건문 사용 가능

**Week 6-3: Infrastructure Composer (하이브리드 방식)**

- Enhanced components를 드래그 앤 드롭으로 추가
- Template 탭에서 세부 설정을 코드로 편집
- 비주얼 디자이너와 코드 편집을 결합
- 시각적으로 아키텍처를 이해하기 쉬움
- 빠른 프로토타이핑에 적합

### Infrastructure Composer 카드 유형

**Enhanced component cards (14개)**

- AWS가 큐레이션한 서버리스 리소스 카드
- 여러 AWS CloudFormation 리소스를 하나의 카드로 결합
- connector port로 드래그하여 다른 카드와 연결 가능 (실선 표시)
- 예: `API Gateway`, `Lambda function`, `DynamoDB table`, `S3 bucket`, `SNS topic` 등

**Standard IaC resource cards (1519개)**

- 모든 AWS CloudFormation 리소스 타입
- 단일 AWS CloudFormation 리소스를 나타냄
- connector port 없음 — Template에서 참조 설정 시 자동 점선 표시
- 예: `AWS::IAM::Role`, `AWS::ApiGateway::Resource` 등

### 서버리스 아키텍처 구성 요소

이 실습에서 구축한 서버리스 REST API의 데이터 흐름:

- 클라이언트가 Amazon API Gateway 엔드포인트로 HTTP 요청을 보냄
- Amazon API Gateway가 AWS Lambda 함수를 호출
- AWS Lambda 함수가 Amazon DynamoDB 테이블에서 데이터를 조회하거나 생성
- AWS Lambda 함수가 결과를 Amazon API Gateway로 반환
- Amazon API Gateway가 HTTP 응답을 클라이언트에게 전달

### 사용 사례별 권장사항

**Infrastructure Composer 사용 권장**:

- 서버리스 애플리케이션 프로토타이핑
- 아키텍처 설계 및 팀 논의
- AWS CloudFormation 학습 초기 단계
- 간단한 서버리스 인프라 구축

**AWS CloudFormation 템플릿 직접 작성 권장**:

- 프로덕션 환경 배포
- 복잡한 인프라 구성 (Amazon VPC, 네트워킹)
- CI/CD 파이프라인 통합
- 대규모 인프라 관리
