---
title: 'AWS CodeBuild를 활용한 CI/CD 파이프라인 구축'
week: 9
session: 2
awsServices:
  - AWS CodeBuild
  - AWS CodeCommit
  - Amazon ECR
  - Amazon CloudWatch Logs
learningObjectives:
  - CI/CD의 개념과 AWS CodeBuild의 빌드 프로세스를 이해할 수 있습니다.
  - buildspec.yml 파일을 분석하고 빌드 단계를 이해할 수 있습니다.
  - AWS CodeBuild 프로젝트를 생성하고 Docker 이미지를 빌드할 수 있습니다.
  - 빌드를 실행하고 Amazon ECR에 푸시된 이미지를 검증할 수 있습니다.
prerequisites:
  - Week 7 완료 (Docker 기본 개념)
  - Git 기본 명령어 이해
  - Amazon ECR 기본 개념 이해
---

이 실습에서는 AWS CodeBuild를 사용하여 Docker 컨테이너 이미지를 자동으로 빌드하고 Amazon ECR에 푸시하는 CI/CD 파이프라인을 구축합니다. buildspec.yml 파일을 분석하고 활용하여 빌드 프로세스를 이해하며, 환경 변수와 빌드 로그를 통해 문제를 해결하는 방법을 학습합니다.

> [!DOWNLOAD]
> [week9-2-cicd-lab.zip](/files/week9/week9-2-cicd-lab.zip)
>
> - `week9-2-cicd-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon ECR 리포지토리 및 CodeCommit 리포지토리 자동 생성)
> - `app.js` - Node.js Express 애플리케이션 (태스크 1에서 CodeCommit에 푸시)
> - `package.json` - Node.js 의존성 정의 (태스크 1에서 CodeCommit에 푸시)
> - `Dockerfile` - Docker 이미지 빌드 설정 (태스크 1에서 CodeCommit에 푸시)
> - `buildspec.yml` - AWS CodeBuild 빌드 스펙 (태스크 2에서 분석 및 푸시)
>
> **관련 태스크:**
>
> - 태스크 0: 실습 환경 구축 (AWS CloudFormation으로 Amazon ECR 리포지토리 및 CodeCommit 리포지토리 자동 생성)
> - 태스크 1: 애플리케이션 코드 준비 (app.js, package.json, Dockerfile을 CodeCommit에 푸시)
> - 태스크 2: buildspec.yml 분석 및 푸시 (AWS CodeBuild 빌드 단계 이해 및 CodeCommit에 푸시)
> - 태스크 3: AWS CodeBuild 프로젝트 생성 (빌드 환경 설정 및 Amazon ECR 연동)
> - 태스크 4: 빌드 실행 및 검증 (이미지 빌드 및 Amazon ECR 푸시 확인)

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

이 실습을 시작하기 전에 AWS 콘솔 우측 상단에서 리전이 **Asia Pacific (Seoul) ap-northeast-2**로 설정되어 있는지 확인합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon ECR 리포지토리**: Docker 이미지를 저장할 프라이빗 컨테이너 레지스트리
- **AWS CodeCommit 리포지토리**: 소스 코드를 저장할 Git 리포지토리
- **AWS IAM 역할**: AWS CodeBuild가 Amazon ECR과 CodeCommit에 접근할 수 있는 권한

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week9-2-cicd-lab.zip` 파일의 압축을 해제합니다.
2. `week9-2-cicd-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.

<img src="/images/week9/9-2-task0-create-stack.png" alt="CloudFormation Create stack 드롭다운에서 With new resources (standard) 선택" class="guide-img-md" />

5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week9-2-cicd-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week9-2-codebuild-stack`을 입력합니다.
10. **Parameters** 섹션에서 기본값을 확인합니다:
    - **CodeCommitRepositoryName**: `cicd-demo-repo`
    - **CreatedByTag**: `CloudFormation`
    - **ECRRepositoryName**: `cicd-demo-app`
    - **ProjectTag**: `AWS-Lab`
    - **WeekTag**: `9-2`
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지가 열립니다.

> [!NOTE]
> 태그는 Parameters에서 설정한 값이 리소스와 스택 태그에 자동으로 적용됩니다. 필요에 따라 Tags 섹션에서 추가 태그를 넣을 수도 있습니다.

13. 페이지 하단의 **Capabilities** 섹션으로 스크롤합니다.
14. `I acknowledge that AWS CloudFormation might create IAM resources with customised names` 체크박스를 선택합니다.

    <img src="/images/week9/9-2-task0-capabilities.png" alt="CloudFormation Capabilities 체크박스" class="guide-img-md" />

> [!NOTE]
> 이 체크박스는 AWS CloudFormation이 AWS IAM 역할을 생성할 수 있는 권한을 부여하는 것입니다. 체크하지 않으면 스택 생성이 실패합니다.

15. [[Next]] 버튼을 클릭합니다.
16. **Review and create** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> **Status** 열은 스택의 현재 상태를 보여줍니다:
>
> - **CREATE_IN_PROGRESS** (파란색): AWS CloudFormation이 리소스를 생성하고 있습니다.
> - **CREATE_COMPLETE** (초록색): 모든 리소스가 성공적으로 생성되었습니다.
> - **CREATE_FAILED** (빨간색): 생성 중 오류가 발생했습니다. (Events 탭에서 원인 확인 필요)
>
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. **Outputs** 탭을 선택합니다.
19. 출력값들을 확인하고 메모장에 복사합니다:
    - `ECRRepositoryUri`: Amazon ECR 리포지토리 URI (예: `123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/cicd-demo-app`)
    - `CodeCommitRepositoryName`: CodeCommit 리포지토리 이름 (예: `cicd-demo-repo`)
    - `CodeBuildRoleArn`: AWS CodeBuild IAM 역할 ARN

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.
>
> - `CodeCommitRepositoryName`은 태스크 1에서 Git 리포지토리를 복제할 때 필요합니다.
> - `ECRRepositoryUri`는 태스크 3에서 환경 변수 설정 시 필요합니다.
> - `CodeBuildRoleArn`은 태스크 3에서 AWS IAM 역할 설정 시 필요합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: 애플리케이션 코드 준비

이 태스크에서는 간단한 Node.js 애플리케이션과 Dockerfile을 CodeCommit 리포지토리에 푸시합니다. 이 파일들은 다음 태스크에서 AWS CodeBuild가 Docker 이미지를 빌드하는 데 사용됩니다.

### 파일 구성

실습 파일에는 다음 3개의 파일이 포함되어 있습니다:

- **app.js**: Node.js Express 웹 애플리케이션 (간단한 "Hello World" 웹 서버)
- **package.json**: Node.js 의존성 정의 (Express 프레임워크 포함)
- **Dockerfile**: Docker 이미지 빌드 설정 (Node.js 18 Alpine 기반)

### 상세 단계

20. 태스크 0에서 압축 해제한 `week9-2-cicd-lab` 폴더를 엽니다.
21. 폴더 내에 위의 3개 파일이 모두 있는지 확인합니다.
22. AWS Management Console 왼쪽 하단의 CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell이 시작될 때까지 기다립니다.

23. 작업 디렉토리를 생성합니다:

```bash
mkdir ~/codebuild-lab
cd ~/codebuild-lab
```

24. git-remote-codecommit 헬퍼를 설치합니다:

```bash
pip install --user git-remote-codecommit
```

> [!TIP]
> git-remote-codecommit은 AWS IAM 자격 증명을 사용하여 CodeCommit에 인증하는 Git 헬퍼입니다. CloudShell에는 AWS CLI가 사전 설치되어 있어 별도 설정이 필요 없으며, `--user` 플래그는 사용자 레벨에 패키지를 설치하여 권한 문제를 방지합니다.

25. 다음 명령어를 실행하여 CodeCommit 리포지토리를 복제합니다:

```bash
git clone codecommit::ap-northeast-2://<repository-name>
```

> [!NOTE]
> `<repository-name>`은 태스크 0의 Outputs 탭에서 확인한 `CodeCommitRepositoryName` 값으로 대체합니다.
> 예: `git clone codecommit::ap-northeast-2://cicd-demo-repo`
>
> 빈 리포지토리를 clone했다는 경고(`warning: You appear to have cloned an empty repository`)가 표시되면 정상입니다.
> AWS CloudFormation은 빈 리포지토리만 생성하며, 소스 코드는 이후 단계에서 직접 푸시합니다.
> 기본 브랜치가 `master`로 설정될 수 있으며, 이 경우 이후 push 명령에서 `main` 대신 `master`를 사용합니다.

26. 복제된 디렉토리로 이동합니다:

```bash
cd <repository-name>
```

> [!TIP]
> `<repository-name>`은 리포지토리 이름으로 대체합니다. 예: `cd cicd-demo-repo`

27. Git 사용자 정보를 설정합니다:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

28. AWS CloudShell 우측 상단의 **Actions** 드롭다운을 클릭한 후 `Upload file`을 선택합니다.

> [!NOTE]
> AWS CloudShell의 Upload file 기능은 한 번에 1개 파일만 업로드할 수 있습니다.
> 다음 순서로 업로드합니다: ① `app.js` ② `package.json` ③ `Dockerfile`

29. 파일 선택 창이 열리면 압축 해제한 폴더로 이동합니다.
30. `app.js` 파일을 선택합니다.
31. [[Open]] 또는 [[열기]] 버튼을 클릭하여 업로드를 시작합니다.

> [!NOTE]
> 파일을 연속으로 빠르게 업로드하면 "Too Many Requests" 오류가 발생할 수 있습니다. 이 경우 몇 초 기다린 후 다시 시도합니다.

32. 업로드가 완료되면 같은 방법으로 `package.json` 파일을 업로드합니다.
33. 마지막으로 `Dockerfile` 파일을 업로드합니다.
34. 업로드가 완료되면 다음 명령어를 실행하여 파일을 리포지토리 디렉토리로 이동합니다:

```bash
mv ~/app.js ~/package.json ~/Dockerfile .
```

> [!TIP]
> 마지막의 `.` (점)은 현재 디렉토리를 의미합니다. 이 명령어는 홈 디렉토리의 파일들을 Git 리포지토리 디렉토리로 이동시킵니다.

35. 파일이 정상적으로 복사되었는지 확인합니다:

```bash
ls -la
```

> [!OUTPUT]
>
> ```
> drwxr-xr-x 3 cloudshell-user cloudshell-user   96 Feb  7 10:00 .git
> -rw-r--r-- 1 cloudshell-user cloudshell-user  256 Feb  7 10:00 app.js
> -rw-r--r-- 1 cloudshell-user cloudshell-user  128 Feb  7 10:00 package.json
> -rw-r--r-- 1 cloudshell-user cloudshell-user  192 Feb  7 10:00 Dockerfile
> ```

36. 3개의 파일과 .git 디렉토리가 모두 표시되는지 확인합니다.
37. 모든 파일을 Git에 추가합니다:

```bash
git add .
```

38. 추가된 파일을 확인합니다:

```bash
git status
```

> [!OUTPUT]
>
> ```
> On branch main
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
>         new file:   Dockerfile
>         new file:   app.js
>         new file:   package.json
> ```

39. 3개의 파일이 모두 "new file"로 표시되는지 확인합니다.
40. 커밋을 생성합니다:

```bash
git commit -m "Add application code and Dockerfile"
```

> [!OUTPUT]
>
> ```
> [main abc1234] Add application code and Dockerfile
>  3 files changed, 50 insertions(+)
>  create mode 100644 Dockerfile
>  create mode 100644 app.js
>  create mode 100644 package.json
> ```

41. CodeCommit에 푸시합니다:

```bash
git push origin main
```

> [!TIP]
> 기본 브랜치가 `master`로 생성된 경우 다음 명령어로 `main`으로 변경할 수 있습니다:
>
> ```bash
> git branch -m master main
> ```
>
> 변경하지 않으려면 `git push origin master`를 사용합니다.

> [!OUTPUT]
>
> ```
> Enumerating objects: 5, done.
> Counting objects: 100% (5/5), done.
> Delta compression using up to 2 threads
> Compressing objects: 100% (3/3), done.
> Writing objects: 100% (4/4), 1.2 KiB | 1.2 MiB/s, done.
> Total 4 (delta 0), reused 0 (delta 0)
> To codecommit::ap-northeast-2://cicd-demo-repo
>    abc1234..def5678  main -> main
> ```

42. 푸시가 성공적으로 완료되었는지 확인합니다.
43. CodeCommit 콘솔로 이동합니다.
44. 생성한 리포지토리를 선택합니다.
45. **Code** 탭에서 3개의 파일이 모두 표시되는지 확인합니다.

> [!TIP]
> 각 파일을 클릭하여 내용을 확인할 수 있습니다. 특히 `Dockerfile`은 다음 태스크에서 AWS CodeBuild가 이미지를 빌드하는 데 사용하는 중요한 파일입니다.

✅ **태스크 완료**: 애플리케이션 코드가 CodeCommit에 푸시되었습니다.

## 태스크 2: buildspec.yml 분석 및 푸시

이 태스크에서는 AWS CodeBuild가 사용할 빌드 스펙 파일을 분석하고 CodeCommit에 푸시합니다.

### 태스크 설명

buildspec.yml은 AWS CodeBuild가 빌드를 수행하는 방법을 정의하는 파일입니다. 이 파일은 다음 3단계로 빌드 프로세스를 정의합니다:

- **pre_build**: Amazon ECR 로그인 및 환경 변수 설정
- **build**: Docker 이미지 빌드 및 태그 지정
- **post_build**: Amazon ECR에 이미지 푸시 및 아티팩트 생성

### 상세 단계

46. CloudShell에서 Git 리포지토리 디렉토리에 있는지 확인합니다:

```bash
pwd
```

> [!OUTPUT]
>
> ```
> /home/cloudshell-user/codebuild-lab/<repository-name>
> ```

47. 디렉토리가 다르면 이동합니다:

```bash
cd ~/codebuild-lab/<repository-name>
```

48. AWS CloudShell 우측 상단의 **Actions** 드롭다운을 클릭한 후 `Upload file`을 선택합니다.
49. 파일 선택 창이 열리면 압축 해제한 폴더로 이동합니다.
50. `buildspec.yml` 파일을 선택합니다.
51. [[Open]] 또는 [[열기]] 버튼을 클릭하여 업로드를 시작합니다.
52. 업로드가 완료되면 다음 명령어를 실행하여 파일을 리포지토리 디렉토리로 이동합니다:

```bash
mv ~/buildspec.yml .
```

53. 파일이 정상적으로 복사되었는지 확인합니다:

```bash
ls -la buildspec.yml
```

> [!OUTPUT]
>
> ```
> -rw-r--r-- 1 cloudshell-user cloudshell-user 1024 Feb  7 10:00 buildspec.yml
> ```

54. buildspec.yml 파일의 내용을 확인합니다:

```bash
cat buildspec.yml
```

> [!OUTPUT]
>
> ```yaml
> version: 0.2
>
> phases:
>   pre_build:
>     commands:
>       - echo Logging in to Amazon ECR...
>       - AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
>       - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
>       - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME
>       - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
>       - IMAGE_TAG=${COMMIT_HASH:=latest}
>       - echo "Building image with tag $IMAGE_TAG"
>   build:
>     commands:
>       - echo Build started on `date`
>       - echo Building the Docker image...
>       - docker build -t $REPOSITORY_URI:latest .
>       - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
>   post_build:
>     commands:
>       - echo Build completed on `date`
>       - echo Pushing the Docker images...
>       - docker push $REPOSITORY_URI:latest
>       - docker push $REPOSITORY_URI:$IMAGE_TAG
>       - echo Writing image definitions file...
>       - printf '[{"name":"%s","imageUri":"%s"}]' $CONTAINER_NAME $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json
>       - cat imagedefinitions.json
>
> artifacts:
>   files:
>     - imagedefinitions.json
> ```

55. 파일 내용이 올바르게 표시되는지 확인합니다.

> [!CONCEPT] buildspec.yml 구조 분석
> buildspec.yml은 AWS CodeBuild가 빌드를 수행하는 방법을 정의하는 YAML 파일입니다.
>
> **주요 구성 요소:**
>
> - **version**: buildspec 파일 버전 (현재 0.2 권장)
> - **phases**: 빌드 프로세스의 각 단계 정의
>   - `pre_build`: Amazon ECR 로그인, 환경 변수 설정
>   - `build`: Docker 이미지 빌드 및 태그 지정
>   - `post_build`: Amazon ECR에 이미지 푸시, 아티팩트 생성
> - **artifacts**: 빌드 출력물 지정 (imagedefinitions.json)
>
> **환경 변수 사용:**
>
> - `$AWS_ACCOUNT_ID`: buildspec 내에서 `aws sts get-caller-identity`로 자동 조회
> - `$AWS_DEFAULT_REGION`: AWS CodeBuild가 자동으로 제공하는 리전 환경 변수
> - `$IMAGE_REPO_NAME`, `$CONTAINER_NAME`: 태스크 3에서 설정할 환경 변수
> - `$CODEBUILD_RESOLVED_SOURCE_VERSION`: AWS CodeBuild가 자동으로 제공하는 Git 커밋 해시
>
> **이미지 태그 전략:**
>
> - `latest`: 항상 최신 이미지를 가리킴 (개발 환경)
> - `$IMAGE_TAG`: Git 커밋 해시 기반 (프로덕션 환경, 롤백 가능)

56. Git에 추가합니다:

```bash
git add buildspec.yml
```

57. 추가된 파일을 확인합니다:

```bash
git status
```

> [!OUTPUT]
>
> ```
> On branch main
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
>         new file:   buildspec.yml
> ```

58. buildspec.yml이 "new file"로 표시되는지 확인합니다.
59. 커밋을 생성합니다:

```bash
git commit -m "Add buildspec.yml for AWS CodeBuild"
```

> [!OUTPUT]
>
> ```
> [main def5678] Add buildspec.yml for AWS CodeBuild
>  1 file changed, 30 insertions(+)
>  create mode 100644 buildspec.yml
> ```

60. CodeCommit에 푸시합니다:

```bash
git push origin main
```

> [!OUTPUT]
>
> ```
> Enumerating objects: 4, done.
> Counting objects: 100% (4/4), done.
> Delta compression using up to 2 threads
> Compressing objects: 100% (3/3), done.
> Writing objects: 100% (3/3), 1.5 KiB | 1.5 MiB/s, done.
> Total 3 (delta 0), reused 0 (delta 0)
> To codecommit::ap-northeast-2://cicd-demo-repo
>    def5678..ghi9012  main -> main
> ```

61. 푸시가 성공적으로 완료되었는지 확인합니다.
62. CodeCommit 콘솔로 이동합니다.
63. 생성한 리포지토리를 선택합니다.
64. **Code** 탭에서 `buildspec.yml` 파일이 표시되는지 확인합니다.
65. `buildspec.yml` 파일을 클릭하여 내용을 확인합니다.

✅ **태스크 완료**: buildspec.yml이 분석되고 CodeCommit에 푸시되었습니다.

## 태스크 3: AWS CodeBuild 프로젝트 생성

이 태스크에서는 AWS CodeBuild 프로젝트를 생성하여 Docker 이미지를 빌드하도록 설정합니다.

### 상세 단계

66. AWS Management Console 상단 검색창에 `CodeBuild`를 입력하고 선택합니다.
67. [[Create project]] 버튼을 클릭합니다.

### Project configuration

68. **Project name**에 `week9-2-container-build`를 입력합니다.
69. **Project type**에서 `Default project`를 선택합니다 (기본값).

> [!NOTE]
> **Additional configuration**을 펼치면 Description, Tags 등을 설정할 수 있습니다.

70. **Additional configuration**을 펼칩니다.
71. **Tags** 섹션에서 [[Add tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key         | Value     |
| ----------- | --------- |
| `Project`   | `AWS-Lab` |
| `Week`      | `9-2`     |
| `CreatedBy` | `Student` |

### Source

72. **Source provider**에서 `AWS CodeCommit`을 선택합니다.
73. **Repository**에서 `cicd-demo-repo`를 선택합니다.
74. **Branch**에서 `main`을 선택합니다.

> [!NOTE]
> 태스크 1에서 브랜치 이름을 `main`으로 변경하지 않은 경우 `master`를 선택합니다.

### Environment

75. **Environment image**에서 `Managed image`를 선택합니다 (기본값).
76. **Running mode**에서 `Container`를 선택합니다.

> [!NOTE]
> Docker 이미지를 빌드하려면 Running mode를 반드시 `Container`로 선택해야 합니다.

77. **Operating system**에서 `Amazon Linux`를 선택합니다.
78. **Runtime(s)**에서 `Standard`를 선택합니다.
79. **Image**에서 최신 버전을 선택합니다 (예: `aws/codebuild/amazonlinux-x86_64-standard:6.0`).
80. **Image version**은 `Always use the latest image for this runtime version`을 유지합니다 (기본값).

### Service role

81. **Service role**에서 `Existing service role`을 선택합니다.
82. **Role ARN**에서 태스크 0의 Outputs에서 확인한 `CodeBuildRoleArn` 값을 선택합니다.
83. `Allow AWS CodeBuild to modify this service role so it can be used with this build project` 체크박스를 **해제**합니다.

> [!NOTE]
> AWS CloudFormation이 생성한 역할의 정책이 변경되지 않도록 하는 모범 사례입니다.

### Additional configuration (Environment 섹션 하단)

84. **Additional configuration**을 펼칩니다.
85. **Privileged**를 체크합니다.

> [!IMPORTANT]
> Docker 이미지를 빌드하려면 **Privileged** 옵션을 반드시 활성화해야 합니다.

86. **Environment variables** 섹션에서 [[Add environment variable]] 버튼을 클릭하여 첫 번째 환경 변수를 추가합니다:
    - **Name**: `IMAGE_REPO_NAME`
    - **Value**: 태스크 0의 Outputs에서 확인한 `ECRRepositoryName` 값 입력 (예: `cicd-demo-app`)
    - **Type**: `Plaintext`
87. [[Add environment variable]] 버튼을 클릭하여 두 번째 환경 변수를 추가합니다:
    - **Name**: `CONTAINER_NAME`
    - **Value**: `app`
    - **Type**: `Plaintext`
88. 2개의 환경 변수가 모두 올바르게 입력되었는지 확인합니다.

> [!NOTE]
> `AWS_ACCOUNT_ID`는 buildspec.yml 내에서 `aws sts get-caller-identity` 명령으로 자동 조회하므로 별도 환경 변수 설정이 필요 없습니다.
> `AWS_DEFAULT_REGION`은 AWS CodeBuild가 자동으로 제공하는 환경 변수입니다.

> [!IMPORTANT]
> 환경 변수는 buildspec.yml에서 `$IMAGE_REPO_NAME`, `$CONTAINER_NAME`으로 참조됩니다.
> 값이 정확하지 않으면 빌드가 실패하므로 반드시 확인합니다.

### Buildspec

89. **Build specifications**에서 `Use a buildspec file`을 선택합니다.

> [!NOTE]
> **Buildspec name**은 기본값 `buildspec.yml`이 사용되므로 별도 입력이 필요 없습니다.

### Logs

90. **CloudWatch logs** 체크박스를 선택합니다.

> [!NOTE]
> CloudWatch logs를 활성화하면 빌드 로그를 실시간으로 확인할 수 있습니다.
> 나머지 설정(**Batch configuration**, **Artifacts**, **Cache**, **Encryption key**)은 기본값을 유지합니다.

91. [[Create build project]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS CodeBuild 프로젝트가 생성되었습니다.

## 태스크 4: 빌드 실행 및 검증

이 태스크에서는 AWS CodeBuild 프로젝트를 실행하여 Docker 이미지를 빌드하고 Amazon ECR에 푸시합니다.

### 상세 단계

92. AWS CodeBuild 콘솔에서 생성한 프로젝트를 선택합니다.
93. [[Start build]] 버튼을 클릭합니다.
94. **Start build** 페이지에서 기본값을 유지하고 [[Start build]] 버튼을 클릭합니다.

> [!NOTE]
> 빌드에 3-5분이 소요됩니다. 대기하는 동안 다음 단계에서 빌드 로그를 확인하여 각 단계가 정상적으로 실행되는지 모니터링합니다.

95. **Build logs** 탭을 선택합니다.
96. 빌드 로그가 실시간으로 표시되는지 확인합니다.
97. **PRE_BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
>
> ```
> [Container] Entering phase PRE_BUILD
> [Container] Running command echo Logging in to Amazon ECR...
> Logging in to Amazon ECR...
>
> [Container] Running command AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
>
> [Container] Running command aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
> WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
> Configure a credential helper to remove this warning. See
> https://docs.docker.com/go/credential-store/
>
> Login Succeeded
>
> [Container] Running command REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME
>
> [Container] Running command COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
>
> [Container] Running command IMAGE_TAG=${COMMIT_HASH:=latest}
>
> [Container] Running command echo "Building image with tag $IMAGE_TAG"
> Building image with tag 7585640
>
> [Container] Phase complete: PRE_BUILD State: SUCCEEDED
> ```

98. Amazon ECR 로그인이 성공했는지 확인합니다.

> [!TIP]
> 로그에서 "Login Succeeded"와 "Phase complete: PRE_BUILD State: SUCCEEDED" 메시지가 표시되면 정상입니다.

99. **BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
>
> ```
> [Container] Running command echo Build started on `date`
> Build started on Sat May 2 03:00:37 PM UTC 2026
>
> [Container] Running command echo Building the Docker image...
> Building the Docker image...
>
> [Container] Running command docker build -t $REPOSITORY_URI:latest .
> #0 building with "default" instance using docker driver
> #1 [internal] load build definition from Dockerfile
> ...
> #5 [1/5] FROM docker.io/library/node:18-alpine@sha256:...
> ...
> #9 [5/5] COPY app.js ./
> #9 DONE 0.1s
> #10 exporting to image
> #10 writing image sha256:... done
> #10 naming to <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/cicd-demo-app:latest done
> #10 DONE 0.2s
>
> [Container] Running command docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
>
> [Container] Phase complete: BUILD State: SUCCEEDED
> ```

100. Docker 이미지 빌드가 성공했는지 확인합니다.

> [!TIP]
> 로그에서 "naming to ... done" 및 "Phase complete: BUILD State: SUCCEEDED" 메시지가 표시되면 정상입니다.

101. **POST_BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
>
> ```
> [Container] Entering phase POST_BUILD
> [Container] Running command echo Build completed on `date`
> Build completed on Sat May 2 03:00:46 PM UTC 2026
>
> [Container] Running command echo Pushing the Docker images...
> Pushing the Docker images...
>
> [Container] Running command docker push $REPOSITORY_URI:latest
> The push refers to repository [<account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/cicd-demo-app]
> 092a0a14992d: Pushed
> ...
> latest: digest: sha256:e5cd318a97a0bcb4ff40e607bf47b575ea476087baf92d6cd556989fd0073e95 size: 1990
>
> [Container] Running command docker push $REPOSITORY_URI:$IMAGE_TAG
> The push refers to repository [<account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/cicd-demo-app]
> 82140d9a70a7: Layer already exists
> ...
> 7585640: digest: sha256:e5cd318a97a0bcb4ff40e607bf47b575ea476087baf92d6cd556989fd0073e95 size: 1990
>
> [Container] Running command echo Writing image definitions file...
> Writing image definitions file...
>
> [Container] Running command printf '[{"name":"%s","imageUri":"%s"}]' $CONTAINER_NAME $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json
>
> [Container] Running command cat imagedefinitions.json
> [{"name":"app","imageUri":"<account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/cicd-demo-app:7585640"}]
>
> [Container] Phase complete: POST_BUILD State: SUCCEEDED
> ```

102. Amazon ECR에 이미지가 성공적으로 푸시되었는지 확인합니다.

> [!TIP]
> 로그에서 "digest: sha256:..." 메시지가 표시되면 정상입니다. 두 번째 push에서는 "Layer already exists"로 표시되는데, 같은 이미지에 태그만 다르게 푸시하기 때문입니다.

103. 로그 하단에서 최종 빌드 상태를 확인합니다:

> [!OUTPUT]
>
> ```
> [Container] Phase complete: PRE_BUILD State: SUCCEEDED
> [Container] Phase complete: BUILD State: SUCCEEDED
> [Container] Phase complete: POST_BUILD State: SUCCEEDED
> [Container] Phase complete: UPLOAD_ARTIFACTS State: SUCCEEDED
> ```

104. 모든 단계가 "SUCCEEDED" 상태인지 확인합니다.

> [!TROUBLESHOOTING]
> **문제**: 빌드가 실패하고 "FAILED" 상태로 표시됩니다
>
> **원인 및 해결**:
>
> - **Amazon ECR 로그인 실패**: 환경 변수 `AWS_ACCOUNT_ID`가 올바른지 확인합니다.
> - **Docker 빌드 실패**: Dockerfile 문법 오류를 확인합니다.
> - **Amazon ECR 푸시 실패**: 환경 변수 `IMAGE_REPO_NAME`이 올바른지 확인합니다.
> - **권한 오류**: AWS IAM 역할에 Amazon ECR 푸시 권한이 있는지 확인합니다.
>
> **해결 방법**:
>
> 1. **Build logs** 탭에서 오류 메시지를 확인합니다.
> 2. 오류가 발생한 단계(PRE_BUILD, BUILD, POST_BUILD)를 식별합니다.
> 3. 해당 단계의 명령어와 환경 변수를 확인합니다.
> 4. 문제를 수정한 후 [[Retry build]] 버튼을 클릭하여 다시 빌드합니다.

> [!NOTE]
> 빌드 상태가 "Succeeded"로 변경될 때까지 기다립니다.

105. Amazon ECR 콘솔로 이동합니다.
106. 생성한 Amazon ECR 리포지토리를 선택합니다.
107. 빌드된 Docker 이미지가 푸시되었는지 확인합니다.
108. 이미지 태그를 확인합니다: `latest` 태그와 Git 커밋 해시 태그 (예: `a1b2c3d`)가 표시됩니다.

> [!TIP]
> 이미지 URI를 복사하여 나중에 Amazon ECS 또는 다른 서비스에서 사용할 수 있습니다.

✅ **태스크 완료**: Docker 이미지가 성공적으로 빌드되고 Amazon ECR에 푸시되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- buildspec.yml 파일을 작성하여 빌드 단계를 정의했습니다.
- AWS CodeBuild 프로젝트를 생성하고 Docker 빌드 환경을 설정했습니다.
- Docker 이미지를 자동으로 빌드하고 Amazon ECR에 푸시했습니다.
- 빌드 로그를 통해 각 단계를 모니터링했습니다.

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

> [!IMPORTANT]
> Amazon ECR 리포지토리에 이미지가 있으면 AWS CloudFormation 스택 삭제 시 리포지토리 삭제가 실패합니다.
> **반드시 이미지를 먼저 삭제한 후** AWS CloudFormation 스택을 삭제해야 합니다.

### 단계 1: Tag Editor로 생성된 리소스 확인

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
   - **Tag key**: `Week`
   - **Tag value**: `9-2`
6. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 다음 단계에서 수행합니다.

### 단계 2: Amazon ECR 이미지 및 AWS CodeBuild 프로젝트 삭제

#### 옵션 1: AWS CLI로 삭제

> [!TIP]
> AWS CLI 명령어에 익숙하거나 빠른 삭제를 원하는 경우 이 방법을 사용합니다.
>
> 콘솔 방식이 더 편하다면 아래 [옵션 2](#option-2)를 참고합니다.

7. CloudShell에서 Amazon ECR 리포지토리의 모든 이미지를 삭제합니다:

```bash
aws ecr list-images \
  --repository-name cicd-demo-app \
  --region ap-northeast-2 \
  --query 'imageIds[*]' \
  --output json | \
aws ecr batch-delete-image \
  --repository-name cicd-demo-app \
  --region ap-northeast-2 \
  --image-ids file:///dev/stdin
```

> [!NOTE]
> 이미지가 정상적으로 삭제되면 `imageIds`와 `failures` 목록이 출력됩니다.
> 다음 명령어로 이미지가 모두 삭제되었는지 확인합니다:
>
> ```bash
> aws ecr list-images --repository-name cicd-demo-app --region ap-northeast-2
> ```
>
> `imageIds`가 빈 배열(`[]`)이면 삭제 완료입니다.

8. AWS CodeBuild 프로젝트를 삭제합니다:

```bash
aws codebuild delete-project \
  --name week9-2-container-build \
  --region ap-northeast-2
```

> [!NOTE]
> 정상적으로 삭제되면 별도 출력 없이 완료됩니다.

#### 옵션 2: AWS 콘솔에서 삭제

> [!TIP]
> AWS 콘솔 방식을 선호하거나 각 단계를 확인하면서 삭제하고 싶은 경우 이 방법을 사용합니다.
>
> AWS CLI 명령어에 익숙한 경우 위 [옵션 1](#option-1)을 참고합니다.

9. Amazon ECR 콘솔로 이동합니다.
10. 생성한 Amazon ECR 리포지토리를 선택합니다.
11. 모든 이미지를 선택합니다 (체크박스 클릭).
12. [[Delete]] 버튼을 클릭합니다.
13. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.
14. AWS CodeBuild 콘솔의 왼쪽 메뉴에서 **Build projects**를 선택합니다.
15. `week9-2-container-build` 빌드 프로젝트를 선택합니다.
16. **Actions** > `Delete build project`를 선택합니다.
17. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

### 단계 3: AWS CloudFormation 스택 삭제

18. AWS CloudFormation 콘솔로 이동합니다.
19. `week9-2-codebuild-stack` 스택을 선택합니다.
20. [[Delete stack]] 버튼을 클릭합니다.
21. 확인 창에서 스택 이름 `week9-2-codebuild-stack`을 입력합니다.
22. [[Delete stack]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 Amazon ECR 리포지토리, CodeCommit 리포지토리, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

### 단계 4: 최종 삭제 확인 (Tag Editor 활용)

모든 리소스가 정상적으로 삭제되었는지 Tag Editor로 최종 확인합니다.

23. AWS Management Console에서 `Resource Groups & Tag Editor`로 이동합니다.
24. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
25. **Regions**에서 `ap-northeast-2`를 선택합니다.
26. **Resource types**에서 `All supported resource types`를 선택합니다.
27. **Tags** 섹션에서 다음을 입력합니다:
    - **Tag key**: `Week`
    - **Tag value**: `9-2`
28. [[Search resources]] 버튼을 클릭합니다.

> [!NOTE]
> 검색 결과에 리소스가 표시되지 않으면 모든 리소스가 성공적으로 삭제된 것입니다.
> 삭제 직후에는 일부 리소스가 잠시 남아있을 수 있으나, 시간이 지나면 자동으로 사라집니다.

### Amazon CloudWatch Log Group 삭제

> [!WARNING]
> Amazon CloudWatch Log Group은 AWS CloudFormation 스택 삭제 시 자동으로 삭제되지 않으므로 수동으로 삭제해야 합니다.

29. AWS Management Console 상단 검색창에 `CloudWatch`를 입력하고 선택합니다.
30. 왼쪽 메뉴에서 **Logs** > **Log groups**를 선택합니다.
31. 검색창에 `week9-2`를 입력합니다.
32. `/aws/codebuild/week9-2-container-build` 로그 그룹의 체크박스를 선택합니다.
33. **Actions** > `Delete log group(s)`를 선택합니다.
34. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

### 단계 5: AWS CloudFormation 템플릿 버킷 삭제 (선택)

AWS CloudFormation 스택을 생성하면 템플릿 파일이 `cf-templates-` 접두사의 Amazon S3 버킷에 자동 저장됩니다. 이 버킷은 스택 삭제 시 자동으로 제거되지 않습니다.

> [!NOTE]
> 이 버킷은 다른 스택에서도 공유할 수 있으므로, 해당 리전에서 더 이상 AWS CloudFormation을 사용하지 않는 경우에만 삭제합니다.

35. Amazon S3 콘솔에서 `cf-templates-`로 시작하는 버킷을 찾습니다.
36. 버킷을 선택하고 [[Empty]] 버튼을 클릭합니다.
37. `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.
38. 버킷을 다시 선택하고 [[Delete]] 버튼을 클릭합니다.
39. 버킷 이름을 입력하고 [[Delete bucket]] 버튼을 클릭합니다.

## 추가 학습 리소스

- [AWS CodeBuild 사용 설명서](https://docs.aws.amazon.com/ko_kr/codebuild/latest/userguide/welcome.html)
- [buildspec.yml 참조](https://docs.aws.amazon.com/ko_kr/codebuild/latest/userguide/build-spec-ref.html)
- [Docker 이미지 빌드 및 푸시](https://docs.aws.amazon.com/ko_kr/codebuild/latest/userguide/sample-docker.html)
- [Amazon ECR 사용 설명서](https://docs.aws.amazon.com/ko_kr/AmazonECR/latest/userguide/what-is-ecr.html)

## 📚 참고: AWS CodeBuild 및 buildspec.yml 개념

### 커리큘럼 구성 안내

> [!NOTE]
> 9주차는 CI/CD 파이프라인 구축을 주제로 하며, 9-1은 이론 강의로 진행됩니다.
> 실습 가이드는 9-2 (AWS CodeBuild)와 9-3 (CodePipeline)으로 구성되어 있습니다.

### AWS CodeBuild 개요

AWS CodeBuild는 완전 관리형 빌드 서비스입니다. 소스 코드를 컴파일하고, 테스트를 실행하며, 배포 가능한 소프트웨어 패키지를 생성합니다.

**주요 특징:**

- 서버 프로비저닝 불필요.
- 사용한 만큼만 비용 지불.
- 사전 패키징된 빌드 환경 제공.
- Docker 이미지 빌드 지원.

### buildspec.yml 구조

**version**

- buildspec 파일의 버전을 지정합니다.
- 현재 권장 버전은 `0.2`입니다.

**phases**

- 빌드 프로세스의 각 단계를 정의합니다.
- `install`, `pre_build`, `build`, `post_build` 단계가 있습니다.

**artifacts**

- 빌드 출력물을 지정합니다.
- Amazon S3 버킷에 업로드되거나 다음 단계로 전달됩니다.

### Docker 빌드 프로세스

**1단계: Amazon ECR 로그인**

```bash
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-uri>
```

**2단계: 이미지 빌드**

```bash
docker build -t <repository-uri>:latest .
```

**3단계: 이미지 태그 지정**

```bash
docker tag <repository-uri>:latest <repository-uri>:<commit-hash>
```

**4단계: Amazon ECR에 푸시**

```bash
docker push <repository-uri>:latest
docker push <repository-uri>:<commit-hash>
```

### 환경 변수

**사용자 정의 변수:**

- `AWS_ACCOUNT_ID`: buildspec.yml 내에서 `aws sts get-caller-identity`로 자동 조회.
- `IMAGE_REPO_NAME`: Amazon ECR 리포지토리 이름 (태스크 3에서 환경 변수로 추가).
- `CONTAINER_NAME`: 컨테이너 이름 (태스크 3에서 환경 변수로 추가).

> [!NOTE]
> `CONTAINER_NAME`과 `imagedefinitions.json` 파일은 이 실습에서는 직접 사용되지 않지만, Week 9-3 실습(CodePipeline + Amazon ECS 배포)에서 필요합니다.
> CodePipeline이 Amazon ECS에 배포할 때 어떤 컨테이너를 업데이트할지 식별하는 데 사용됩니다.

**AWS CodeBuild 제공 변수:**

- `AWS_DEFAULT_REGION`: 빌드가 실행되는 리전 (AWS CodeBuild가 자동으로 설정).
- `CODEBUILD_RESOLVED_SOURCE_VERSION`: Git 커밋 해시.
- `CODEBUILD_BUILD_ID`: 빌드 ID.
- `CODEBUILD_BUILD_NUMBER`: 빌드 번호.

### Privileged 모드

Docker 이미지를 빌드하려면 AWS CodeBuild 프로젝트에서 **Privileged** 모드를 활성화해야 합니다.

**이유:**

- Docker 데몬이 컨테이너 내부에서 실행되어야 합니다.
- Docker-in-Docker 방식으로 이미지를 빌드합니다.
- 보안상 기본적으로 비활성화되어 있습니다.

### 이미지 태그 전략

**latest 태그:**

- 항상 최신 이미지를 가리킵니다.
- 개발 환경에서 유용합니다.

**커밋 해시 태그:**

- 특정 버전을 식별할 수 있습니다.
- 롤백 시 유용합니다.
- 프로덕션 환경에서 권장됩니다.

### 모범 사례

**빌드 속도 최적화:**

- Docker 레이어 캐싱을 활용합니다.
- 불필요한 파일을 제외합니다 (.dockerignore).
- 멀티 스테이지 빌드를 사용합니다.

**보안:**

- 최소 권한 원칙을 적용합니다.
- 민감한 정보는 환경 변수로 관리합니다.
- 이미지 스캔을 활성화합니다.

**비용 최적화:**

- 적절한 빌드 인스턴스 타입을 선택합니다.
- 빌드 캐싱을 활용합니다.
- 불필요한 빌드를 방지합니다.
