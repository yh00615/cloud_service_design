---
title: "AWS CodeBuild를 활용한 CI/CD 파이프라인 구축"
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

### 실습 파일 구조

압축 해제 후 다음과 같은 파일 구조를 확인할 수 있습니다:

```
week9-2-cicd-lab/
├── week9-2-cicd-lab.yaml
├── app.js
├── package.json
├── Dockerfile
└── buildspec.yml
```

> [!DOWNLOAD]
> [week9-2-cicd-lab.zip](/files/week9/week9-2-cicd-lab.zip)
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
> 
> **예상 비용** (ap-northeast-2 리전 기준):
> 
> | 리소스 | 타입 | 시간당 비용 |
> |--------|------|------------|
> | AWS CodeBuild | build.general1.small | 월 100분 무료, 초과 시 분당 약 $0.005 |
> | Amazon ECR | 스토리지 | 월 500MB 무료, 초과 시 GB당 $0.10 |
> | Amazon CloudWatch Logs | 로그 저장 | 월 5GB 무료, 초과 시 GB당 $0.50 |

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

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
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week9-2-cicd-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week9-2-codebuild-stack`을 입력합니다.
10. **Parameters** 섹션에서 필요한 파라미터를 확인합니다 (대부분 기본값 사용).
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key | Value |
|-----|-------|
| `Project` | `AWS-Lab` |
| `Week` | `9-2` |
| `CreatedBy` | `Student` |

14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
15. [[Next]] 버튼을 클릭합니다.
16. **Review** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.
18. 스택 생성이 시작됩니다. 상태가 "CREATE_IN_PROGRESS"로 표시됩니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. **Events** 탭에서 생성 과정을 확인할 수 있습니다.
> 대기하는 동안 다음 태스크를 미리 읽어봅니다.

19. 상태가 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
20. **Outputs** 탭을 선택합니다.
21. 출력값들을 확인하고 메모장에 복사합니다:
    - `ECRRepositoryUri`: Amazon ECR 리포지토리 URI (예: `123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/week9-2-codebuild-repo`)
    - `CodeCommitRepositoryName`: CodeCommit 리포지토리 이름 (예: `week9-2-codebuild-repo`)
    - `CodeBuildRoleArn`: AWS CodeBuild AWS IAM 역할 ARN

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.
> - `CodeCommitRepositoryName`은 태스크 1에서 Git 리포지토리를 복제할 때 필요합니다
> - `ECRRepositoryUri`는 태스크 3에서 환경 변수 설정 시 필요합니다
> - `CodeBuildRoleArn`은 태스크 3에서 AWS IAM 역할 설정 시 필요합니다

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: 애플리케이션 코드 준비

이 태스크에서는 간단한 Node.js 애플리케이션과 Dockerfile을 CodeCommit 리포지토리에 푸시합니다. 이 파일들은 다음 태스크에서 AWS CodeBuild가 Docker 이미지를 빌드하는 데 사용됩니다.

### 파일 구성

실습 파일에는 다음 3개의 파일이 포함되어 있습니다:

- **app.js**: Node.js Express 웹 애플리케이션 (간단한 "Hello World" 웹 서버)
- **package.json**: Node.js 의존성 정의 (Express 프레임워크 포함)
- **Dockerfile**: Docker 이미지 빌드 설정 (Node.js 18 Alpine 기반)

### 상세 단계

22. 태스크 0에서 압축 해제한 `week9-2-cicd-lab` 폴더를 엽니다.
23. 폴더 내에 위의 3개 파일이 모두 있는지 확인합니다.
24. AWS Management Console 상단 우측의 AWS CloudShell 아이콘을 클릭합니다.
25. CloudShell이 시작될 때까지 기다립니다.
26. 작업 디렉토리를 생성합니다:

```bash
mkdir ~/codebuild-lab
cd ~/codebuild-lab
```

27. git-remote-codecommit 헬퍼를 설치합니다:

```bash
pip install --user git-remote-codecommit
```

💡 git-remote-codecommit은 AWS IAM 자격 증명을 사용하여 CodeCommit에 인증하는 Git 헬퍼입니다. CloudShell에는 AWS CLI가 사전 설치되어 있어 별도 설정이 필요 없으며, `--user` 플래그는 사용자 레벨에 패키지를 설치하여 권한 문제를 방지합니다.

28. 다음 명령어를 실행하여 CodeCommit 리포지토리를 복제합니다:

```bash
git clone codecommit::ap-northeast-2://<repository-name>
```

> [!NOTE]
> `<repository-name>`은 태스크 0의 Outputs 탭에서 확인한 `CodeCommitRepositoryName` 값으로 대체합니다.
> 예: `git clone codecommit::ap-northeast-2://week9-2-codebuild-repo`

29. 복제된 디렉토리로 이동합니다:

```bash
cd <repository-name>
```

💡 `<repository-name>`은 리포지토리 이름으로 대체합니다. 예: `cd week9-2-codebuild-repo`

30. Git 사용자 정보를 설정합니다:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

31. AWS CloudShell 우측 상단의 **Actions** 드롭다운을 클릭한 후 `Upload file`을 선택합니다.

> [!NOTE]
> AWS CloudShell의 Upload file 기능은 한 번에 1개 파일만 업로드할 수 있습니다. 
> 다음 순서로 업로드합니다: ① `app.js` ② `package.json` ③ `Dockerfile`

32. 파일 선택 창이 열리면 압축 해제한 폴더로 이동합니다.
33. `app.js` 파일을 선택합니다.
34. [[Open]] 또는 [[열기]] 버튼을 클릭하여 업로드를 시작합니다.
35. 업로드가 완료되면 같은 방법으로 `package.json` 파일을 업로드합니다.
36. 마지막으로 `Dockerfile` 파일을 업로드합니다.
37. 업로드가 완료되면 다음 명령어를 실행하여 파일을 리포지토리 디렉토리로 이동합니다:

```bash
mv ~/app.js ~/package.json ~/Dockerfile .
```

> [!TIP]
> 마지막의 `.` (점)은 현재 디렉토리를 의미합니다. 이 명령어는 홈 디렉토리의 파일들을 Git 리포지토리 디렉토리로 이동시킵니다.

38. 파일이 정상적으로 복사되었는지 확인합니다:

```bash
ls -la
```

> [!OUTPUT]
> ```
> drwxr-xr-x 3 cloudshell-user cloudshell-user   96 Feb  7 10:00 .git
> -rw-r--r-- 1 cloudshell-user cloudshell-user  256 Feb  7 10:00 app.js
> -rw-r--r-- 1 cloudshell-user cloudshell-user  128 Feb  7 10:00 package.json
> -rw-r--r-- 1 cloudshell-user cloudshell-user  192 Feb  7 10:00 Dockerfile
> ```

39. 3개의 파일과 .git 디렉토리가 모두 표시되는지 확인합니다.
40. 모든 파일을 Git에 추가합니다:

```bash
git add .
```

41. 추가된 파일을 확인합니다:

```bash
git status
```

> [!OUTPUT]
> ```
> On branch main
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
>         new file:   Dockerfile
>         new file:   app.js
>         new file:   package.json
> ```

42. 3개의 파일이 모두 "new file"로 표시되는지 확인합니다.
43. 커밋을 생성합니다:

```bash
git commit -m "Add application code and Dockerfile"
```

> [!OUTPUT]
> ```
> [main abc1234] Add application code and Dockerfile
>  3 files changed, 50 insertions(+)
>  create mode 100644 Dockerfile
>  create mode 100644 app.js
>  create mode 100644 package.json
> ```

44. CodeCommit에 푸시합니다:

```bash
git push origin main
```

> [!NOTE]
> 브랜치 이름이 `master`인 경우 `git push origin master`를 사용합니다.

> [!OUTPUT]
> ```
> Enumerating objects: 5, done.
> Counting objects: 100% (5/5), done.
> Delta compression using up to 2 threads
> Compressing objects: 100% (3/3), done.
> Writing objects: 100% (4/4), 1.2 KiB | 1.2 MiB/s, done.
> Total 4 (delta 0), reused 0 (delta 0)
> To codecommit::ap-northeast-2://week9-2-codebuild-repo
>    abc1234..def5678  main -> main
> ```

45. 푸시가 성공적으로 완료되었는지 확인합니다.
46. CodeCommit 콘솔로 이동합니다.
47. 생성한 리포지토리를 선택합니다.
48. **Code** 탭에서 3개의 파일이 모두 표시되는지 확인합니다.

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

49. CloudShell에서 Git 리포지토리 디렉토리에 있는지 확인합니다:

```bash
pwd
```

> [!OUTPUT]
> ```
> /home/cloudshell-user/codebuild-lab/<repository-name>
> ```

50. 디렉토리가 다르면 이동합니다:

```bash
cd ~/codebuild-lab/<repository-name>
```

51. AWS CloudShell 우측 상단의 **Actions** 드롭다운을 클릭한 후 `Upload file`을 선택합니다.
52. 파일 선택 창이 열리면 압축 해제한 폴더로 이동합니다.
53. `buildspec.yml` 파일을 선택합니다.
54. [[Open]] 또는 [[열기]] 버튼을 클릭하여 업로드를 시작합니다.
55. 업로드가 완료되면 다음 명령어를 실행하여 파일을 리포지토리 디렉토리로 이동합니다:

```bash
mv ~/buildspec.yml .
```

56. 파일이 정상적으로 복사되었는지 확인합니다:

```bash
ls -la buildspec.yml
```

> [!OUTPUT]
> ```
> -rw-r--r-- 1 cloudshell-user cloudshell-user 1024 Feb  7 10:00 buildspec.yml
> ```

57. buildspec.yml 파일의 내용을 확인합니다:

```bash
cat buildspec.yml
```

> [!OUTPUT]
> ```yaml
> version: 0.2
> 
> phases:
>   pre_build:
>     commands:
>       - echo Logging in to Amazon ECR...
>       - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
>       - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_REPO_NAME
>       - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
>       - IMAGE_TAG=${COMMIT_HASH:=latest}
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
> 
> artifacts:
>   files:
>     - imagedefinitions.json
> ```

58. 파일 내용이 올바르게 표시되는지 확인합니다.

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
> - `$AWS_ACCOUNT_ID`, `$AWS_REGION`: 태스크 3에서 설정할 환경 변수
> - `$IMAGE_REPO_NAME`, `$CONTAINER_NAME`: 태스크 3에서 설정할 환경 변수
> - `$CODEBUILD_RESOLVED_SOURCE_VERSION`: AWS CodeBuild가 자동으로 제공하는 Git 커밋 해시
> 
> **이미지 태그 전략:**
> 
> - `latest`: 항상 최신 이미지를 가리킴 (개발 환경)
> - `$IMAGE_TAG`: Git 커밋 해시 기반 (프로덕션 환경, 롤백 가능)

59. Git에 추가합니다:

```bash
git add buildspec.yml
```

60. 추가된 파일을 확인합니다:

```bash
git status
```

> [!OUTPUT]
> ```
> On branch main
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
>         new file:   buildspec.yml
> ```

61. buildspec.yml이 "new file"로 표시되는지 확인합니다.
62. 커밋을 생성합니다:

```bash
git commit -m "Add buildspec.yml for AWS CodeBuild"
```

> [!OUTPUT]
> ```
> [main def5678] Add buildspec.yml for AWS CodeBuild
>  1 file changed, 30 insertions(+)
>  create mode 100644 buildspec.yml
> ```

63. CodeCommit에 푸시합니다:

```bash
git push origin main
```

> [!OUTPUT]
> ```
> Enumerating objects: 4, done.
> Counting objects: 100% (4/4), done.
> Delta compression using up to 2 threads
> Compressing objects: 100% (3/3), done.
> Writing objects: 100% (3/3), 1.5 KiB | 1.5 MiB/s, done.
> Total 3 (delta 0), reused 0 (delta 0)
> To codecommit::ap-northeast-2://week9-2-codebuild-repo
>    def5678..ghi9012  main -> main
> ```

64. 푸시가 성공적으로 완료되었는지 확인합니다.
65. CodeCommit 콘솔로 이동합니다.
66. 생성한 리포지토리를 선택합니다.
67. **Code** 탭에서 `buildspec.yml` 파일이 표시되는지 확인합니다.
68. `buildspec.yml` 파일을 클릭하여 내용을 확인합니다.

✅ **태스크 완료**: buildspec.yml이 분석되고 CodeCommit에 푸시되었습니다.

## 태스크 3: AWS CodeBuild 프로젝트 생성

이 태스크에서는 AWS CodeBuild 프로젝트를 생성하여 Docker 이미지를 빌드하도록 설정합니다.

### 상세 단계

> [!NOTE]
> AWS 콘솔 UI는 주기적으로 업데이트됩니다. 화면 구성이 다를 수 있지만, 동일한 설정 항목을 찾아 적용하면 됩니다.

69. AWS Management Console 상단 검색창에 `CodeBuild`을 입력하고 선택합니다.
70. [[Create project]] 버튼을 클릭합니다.
71. **Project name**에 `week9-2-container-build`를 입력합니다.
72. **Description**에 `Build Docker container image`를 입력합니다.
73. **Source** 섹션에서 다음을 설정합니다:
	- **Source provider**에서 `AWS CodeCommit`을 선택합니다.
	- **Repository**에서 생성한 CodeCommit 리포지토리를 선택합니다.
	- **Branch**에서 `main` 또는 `master`를 선택합니다.
74. **Environment** 섹션에서 다음을 설정합니다:
	- **Environment image**에서 `Managed image`를 선택합니다.
	- **Operating system**에서 `Amazon Linux`를 선택합니다 (콘솔에 표시되는 최신 버전 사용).
	- **Runtime(s)**에서 `Standard`를 선택합니다.
   - **Image**에서 최신 버전을 선택합니다.
   - **Privileged**를 체크합니다.

> [!IMPORTANT]
> Docker 이미지를 빌드하려면 **Privileged** 옵션을 반드시 활성화해야 합니다.

75. **Service role**에서 `Existing service role`을 선택합니다.
76. **Role ARN**에 태스크 0에서 복사한 `CodeBuildRoleArn` 값을 입력합니다.

> [!TIP]
> **Allow AWS CodeBuild to modify this service role** 체크박스가 표시되면 체크 해제합니다.
> AWS CloudFormation이 생성한 역할의 정책이 변경되지 않도록 하는 모범 사례입니다.

77. **Buildspec** 섹션에서 `Use a buildspec file`을 선택합니다.
78. **Buildspec name**에 `buildspec.yml`을 입력합니다.
79. **Environment variables** 섹션으로 스크롤합니다.
80. AWS 계정 ID를 확인합니다:
    - AWS Management Console 우측 상단의 계정 이름을 클릭합니다.
    - 드롭다운 메뉴에서 12자리 계정 ID를 확인합니다.
    - 계정 ID를 메모장에 복사합니다.
81. Amazon ECR 리포지토리 이름을 추출합니다:
    - 태스크 0의 Outputs에서 복사한 `ECRRepositoryUri`를 확인합니다.
    - URI에서 `/` 뒤의 리포지토리 이름 부분만 추출합니다.
    - 예: `123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/week9-2-codebuild-repo` → `week9-2-codebuild-repo`
82. [[Add environment variable]] 버튼을 클릭하여 첫 번째 환경 변수를 추가합니다:
    - **Name**: `AWS_ACCOUNT_ID`
    - **Value**: 12단계에서 확인한 계정 ID 입력
    - **Type**: `Plaintext`
83. [[Add environment variable]] 버튼을 클릭하여 두 번째 환경 변수를 추가합니다:
    - **Name**: `IMAGE_REPO_NAME`
    - **Value**: 13단계에서 추출한 리포지토리 이름 입력
    - **Type**: `Plaintext`
84. [[Add environment variable]] 버튼을 클릭하여 세 번째 환경 변수를 추가합니다:
    - **Name**: `CONTAINER_NAME`
    - **Value**: `app`
    - **Type**: `Plaintext`
85. 3개의 환경 변수가 모두 올바르게 입력되었는지 확인합니다.

> [!IMPORTANT]
> 환경 변수는 buildspec.yml에서 `$AWS_ACCOUNT_ID`, `$IMAGE_REPO_NAME`, `$CONTAINER_NAME`으로 참조됩니다.
> 값이 정확하지 않으면 빌드가 실패하므로 반드시 확인합니다.

86. **Logs** 섹션에서 `Amazon CloudWatch logs`를 체크합니다.
87. [[Create build project]] 버튼을 클릭합니다.

✅ **태스크 완료**: AWS CodeBuild 프로젝트가 생성되었습니다.

## 태스크 4: 빌드 실행 및 검증

이 태스크에서는 AWS CodeBuild 프로젝트를 실행하여 Docker 이미지를 빌드하고 Amazon ECR에 푸시합니다.

### 상세 단계

88. AWS CodeBuild 콘솔에서 생성한 프로젝트를 선택합니다.
89. [[Start build]] 버튼을 클릭합니다.
90. **Start build** 페이지에서 기본값을 유지하고 [[Start build]] 버튼을 클릭합니다.

> [!NOTE]
> 빌드에 3-5분이 소요됩니다. 대기하는 동안 다음 단계에서 빌드 로그를 확인하여 각 단계가 정상적으로 실행되는지 모니터링합니다.

91. **Build logs** 탭을 선택합니다.
92. 빌드 로그가 실시간으로 표시되는지 확인합니다.
93. **PRE_BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
> ```
> [Container] 2024/02/07 10:00:00 Running command echo Logging in to Amazon ECR...
> Logging in to Amazon ECR...
> 
> [Container] 2024/02/07 10:00:01 Running command aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
> WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
> Configure a credential helper to remove this warning. See
> https://docs.docker.com/engine/reference/commandline/login/#credentials-store
> 
> Login Succeeded
> ```

94. Amazon ECR 로그인이 성공했는지 확인합니다 ("Login Succeeded" 메시지).
95. **BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
> ```
> [Container] 2024/02/07 10:00:05 Running command echo Build started on `date`
> Build started on Wed Feb  7 10:00:05 UTC 2024
> 
> [Container] 2024/02/07 10:00:05 Running command echo Building the Docker image...
> Building the Docker image...
> 
> [Container] 2024/02/07 10:00:05 Running command docker build -t $REPOSITORY_URI:latest .
> Sending build context to Docker daemon  15.36kB
> Step 1/6 : FROM node:18-alpine
> 18-alpine: Pulling from library/node
> 4abcf2066143: Pulling fs layer
> ...
> Successfully built a1b2c3d4e5f6
> Successfully tagged 123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/week9-2-codebuild-repo:latest
> ```

96. Docker 이미지 빌드가 성공했는지 확인합니다 ("Successfully built" 및 "Successfully tagged" 메시지).
97. **POST_BUILD** 단계의 로그를 확인합니다:

> [!OUTPUT]
> ```
> [Container] 2024/02/07 10:00:30 Running command echo Build completed on `date`
> Build completed on Wed Feb  7 10:00:30 UTC 2024
> 
> [Container] 2024/02/07 10:00:30 Running command echo Pushing the Docker images...
> Pushing the Docker images...
> 
> [Container] 2024/02/07 10:00:30 Running command docker push $REPOSITORY_URI:latest
> The push refers to repository [123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/week9-2-codebuild-repo]
> a1b2c3d: Pushed
> ...
> latest: digest: sha256:abc123... size: 1234
> 
> [Container] 2024/02/07 10:00:45 Running command docker push $REPOSITORY_URI:$IMAGE_TAG
> The push refers to repository [123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/week9-2-codebuild-repo]
> a1b2c3d: Layer already exists
> ...
> a1b2c3d: digest: sha256:abc123... size: 1234
> ```

98. Amazon ECR에 이미지가 성공적으로 푸시되었는지 확인합니다 ("digest: sha256:..." 메시지).
99. 로그 하단에서 최종 빌드 상태를 확인합니다:

> [!OUTPUT]
> ```
> [Container] 2024/02/07 10:00:50 Phase complete: PRE_BUILD State: SUCCEEDED
> [Container] 2024/02/07 10:00:50 Phase complete: BUILD State: SUCCEEDED
> [Container] 2024/02/07 10:00:50 Phase complete: POST_BUILD State: SUCCEEDED
> [Container] 2024/02/07 10:00:50 Phase complete: UPLOAD_ARTIFACTS State: SUCCEEDED
> [Container] 2024/02/07 10:00:50 Phase complete: FINALIZING State: SUCCEEDED
> [Container] 2024/02/07 10:00:50 Phase complete: COMPLETED State: SUCCEEDED
> ```

100. 모든 단계가 "SUCCEEDED" 상태인지 확인합니다.

> [!TROUBLESHOOTING]
> **문제**: 빌드가 실패하고 "FAILED" 상태로 표시됩니다
> 
> **원인 및 해결**:
> - **Amazon ECR 로그인 실패**: 환경 변수 `AWS_ACCOUNT_ID`가 올바른지 확인합니다
> - **Docker 빌드 실패**: Dockerfile 문법 오류를 확인합니다
> - **Amazon ECR 푸시 실패**: 환경 변수 `IMAGE_REPO_NAME`이 올바른지 확인합니다
> - **권한 오류**: AWS IAM 역할에 Amazon ECR 푸시 권한이 있는지 확인합니다
> 
> **해결 방법**:
> 1. **Build logs** 탭에서 오류 메시지를 확인합니다.
> 2. 오류가 발생한 단계(PRE_BUILD, BUILD, POST_BUILD)를 식별합니다.
> 3. 해당 단계의 명령어와 환경 변수를 확인합니다.
> 4. 문제를 수정한 후 [[Retry build]] 버튼을 클릭하여 다시 빌드합니다.

101. 빌드 상태가 "Succeeded"로 변경될 때까지 기다립니다.
102. Amazon ECR 콘솔로 이동합니다.
103. 생성한 Amazon ECR 리포지토리를 선택합니다.
104. 빌드된 Docker 이미지가 푸시되었는지 확인합니다.
105. 이미지 태그를 확인합니다:
    - `latest` 태그
    - Git 커밋 해시 태그 (예: `a1b2c3d`)

> [!TIP]
> 이미지 URI를 복사하여 나중에 Amazon ECS 또는 다른 서비스에서 사용할 수 있습니다.

✅ **태스크 완료**: Docker 이미지가 성공적으로 빌드되고 Amazon ECR에 푸시되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- buildspec.yml 파일을 작성하여 빌드 단계를 정의했습니다
- AWS CodeBuild 프로젝트를 생성하고 Docker 빌드 환경을 설정했습니다
- Docker 이미지를 자동으로 빌드하고 Amazon ECR에 푸시했습니다
- 빌드 로그를 통해 각 단계를 모니터링했습니다

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
	- **Tag value**: `9-2`
6. [[Search resources]] 버튼을 클릭합니다.
7. 이 실습에서 생성한 AWS CloudFormation 스택이 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: 수동 삭제

#### Amazon ECR 이미지 삭제

> [!IMPORTANT]
> Amazon ECR 리포지토리에 이미지가 있으면 AWS CloudFormation 스택 삭제 시 Amazon ECR 리포지토리 삭제가 실패합니다.
> **반드시 먼저 이미지를 삭제한 후** AWS CloudFormation 스택을 삭제해야 합니다.

8. Amazon ECR 콘솔로 이동합니다.
9. 생성한 Amazon ECR 리포지토리를 선택합니다.
10. 모든 이미지를 선택합니다 (체크박스 클릭).
11. [[Delete]] 버튼을 클릭합니다.
12. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

#### AWS CodeBuild 프로젝트 삭제

13. AWS CodeBuild 콘솔로 이동합니다.
14. 생성한 빌드 프로젝트를 선택합니다.
15. **Actions** > `Delete build project`를 선택합니다.
16. 확인 창에서 `delete`를 입력하고 [[Delete]] 버튼을 클릭합니다.

#### AWS CloudFormation 스택 삭제

17. AWS CloudFormation 콘솔로 이동합니다.
18. `week9-2-codebuild-stack` 스택을 선택합니다.
19. [[Delete]] 버튼을 클릭합니다.
20. 확인 창에서 [[Delete]] 버튼을 클릭합니다.
21. 스택 삭제가 완료될 때까지 기다립니다 (2-3분 소요).

> [!NOTE]
> AWS CloudFormation 스택을 삭제하면 Amazon ECR 리포지토리, CodeCommit 리포지토리, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

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
- 서버 프로비저닝 불필요
- 사용한 만큼만 비용 지불
- 사전 패키징된 빌드 환경 제공
- Docker 이미지 빌드 지원

### buildspec.yml 구조

**version**
- buildspec 파일의 버전을 지정합니다
- 현재 권장 버전은 `0.2`입니다

**phases**
- 빌드 프로세스의 각 단계를 정의합니다
- `install`, `pre_build`, `build`, `post_build` 단계가 있습니다

**artifacts**
- 빌드 출력물을 지정합니다
- Amazon S3 버킷에 업로드되거나 다음 단계로 전달됩니다

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
- `AWS_ACCOUNT_ID`: AWS 계정 ID (태스크 3에서 환경 변수로 추가)
- `IMAGE_REPO_NAME`: Amazon ECR 리포지토리 이름 (태스크 3에서 환경 변수로 추가)
- `CONTAINER_NAME`: 컨테이너 이름 (태스크 3에서 환경 변수로 추가)

> [!NOTE]
> `CONTAINER_NAME`과 `imagedefinitions.json` 파일은 이 실습에서는 직접 사용되지 않지만, Week 9-3 실습(CodePipeline + Amazon ECS 배포)에서 필요합니다.
> CodePipeline이 Amazon ECS에 배포할 때 어떤 컨테이너를 업데이트할지 식별하는 데 사용됩니다.

**AWS CodeBuild 제공 변수:**
- `AWS_REGION`: 빌드가 실행되는 리전 (AWS CodeBuild가 자동으로 설정)
- `CODEBUILD_RESOLVED_SOURCE_VERSION`: Git 커밋 해시
- `CODEBUILD_BUILD_ID`: 빌드 ID
- `CODEBUILD_BUILD_NUMBER`: 빌드 번호

### Privileged 모드

Docker 이미지를 빌드하려면 AWS CodeBuild 프로젝트에서 **Privileged** 모드를 활성화해야 합니다.

**이유:**
- Docker 데몬이 컨테이너 내부에서 실행되어야 함
- Docker-in-Docker 방식으로 이미지 빌드
- 보안상 기본적으로 비활성화되어 있음

### 이미지 태그 전략

**latest 태그:**
- 항상 최신 이미지를 가리킴
- 개발 환경에서 유용

**커밋 해시 태그:**
- 특정 버전을 식별 가능
- 롤백 시 유용
- 프로덕션 환경에서 권장

### 모범 사례

**빌드 속도 최적화:**
- Docker 레이어 캐싱 활용
- 불필요한 파일 제외 (.dockerignore)
- 멀티 스테이지 빌드 사용

**보안:**
- 최소 권한 원칙 적용
- 민감한 정보는 환경 변수로 관리
- 이미지 스캔 활성화

**비용 최적화:**
- 적절한 빌드 인스턴스 타입 선택
- 빌드 캐싱 활용
- 불필요한 빌드 방지
