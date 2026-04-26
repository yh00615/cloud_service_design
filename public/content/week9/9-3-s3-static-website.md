---
title: 'AWS CodePipeline으로 Amazon S3 정적 웹사이트 배포 자동화'
week: 9
session: 3
awsServices:
  - AWS CodePipeline
  - AWS CodeBuild
  - AWS CodeCommit
  - Amazon S3
  - AWS CloudFormation
learningObjectives:
  - AWS CodePipeline의 파이프라인 단계(Source, Build)를 이해할 수 있습니다.
  - 정적 웹사이트 파일을 AWS CodeCommit에 푸시하고 파이프라인을 트리거할 수 있습니다.
  - AWS CodePipeline을 통해 Amazon S3에 자동 배포되는 과정을 확인할 수 있습니다.
  - 코드 변경 후 자동 배포를 테스트하고 웹사이트를 확인할 수 있습니다.
prerequisites:
  - Week 1 완료 (Amazon S3 기본 개념)
  - Week 9-2 완료 (AWS CodeBuild 기본)
  - Git 기본 명령어 이해
---

이 실습에서는 AWS CodePipeline을 사용하여 정적 웹사이트를 Amazon S3에 자동으로 배포하는 CI/CD 파이프라인을 구축하는 방법을 학습합니다.

AWS CodeCommit에 소스 코드를 저장하고, 코드 변경 시 AWS CodePipeline이 자동으로 AWS CodeBuild를 실행하여 Amazon S3에 배포하는 전체 워크플로우를 구현합니다.

> [!DOWNLOAD]
> [week9-3-s3-website-lab.zip](/files/week9/week9-3-s3-website-lab.zip)
> - `week9-3-s3-website-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, CodeCommit, AWS CodeBuild, AWS CodePipeline 자동 생성)
> - `index.html` - 메인 페이지 (CI/CD Pipeline Demo, 태스크 1에서 CodeCommit에 푸시)
> - `about.html` - 소개 페이지 (프로젝트 및 AWS 서비스 설명, 태스크 1에서 CodeCommit에 푸시)
> - `style.css` - 스타일시트 (태스크 1에서 CodeCommit에 푸시)
> - `script.js` - JavaScript 파일 (인터랙티브 기능, 태스크 1에서 CodeCommit에 푸시)
> - `buildspec.yml` - AWS CodeBuild 빌드 스펙 (태스크 1에서 CodeCommit에 푸시)
> 
> **관련 태스크:**
> 
> - 태스크 0: 실습 환경 구축 (week9-3-s3-website-lab.yaml을 사용하여 Amazon S3 버킷, CodeCommit 리포지토리, AWS CodeBuild 프로젝트, AWS CodePipeline 자동 생성)
> - 태스크 1: 웹사이트 코드 준비 및 CodeCommit에 푸시 (index.html, about.html, style.css, script.js, buildspec.yml을 CodeCommit에 업로드)
> - 태스크 2: AWS CodePipeline 확인 및 첫 번째 배포

> [!WARNING]
> 이 실습에서 생성하는 리소스는 실습 종료 후 반드시 삭제해야 합니다.

## 태스크 0: 실습 환경 구축

이 태스크에서는 AWS CloudFormation을 사용하여 실습에 필요한 기본 인프라를 자동으로 생성합니다.

### 환경 구성 요소

AWS CloudFormation 스택은 다음 리소스를 생성합니다:

- **Amazon S3 버킷**: 정적 웹사이트 호스팅용 버킷 (퍼블릭 액세스 허용)
- **AWS CodeCommit 리포지토리**: 소스 코드 저장소
- **AWS CodeBuild 프로젝트**: 빌드 및 Amazon S3 배포 자동화
- **AWS CodePipeline**: 소스-빌드-배포 파이프라인
- **AWS IAM 역할**: AWS CodeBuild, CodePipeline에 필요한 권한

### 상세 단계

> [!NOTE]
> AWS CloudFormation 콘솔 UI는 주기적으로 업데이트됩니다.  
> 버튼명이나 화면 구성이 가이드와 다를 수 있으나, 전체 흐름(템플릿 업로드 → 스택 이름 입력 → 태그 추가 → 생성)은 동일합니다.

1. 다운로드한 `week9-3-s3-website-lab.zip` 파일의 압축을 해제합니다.
2. `week9-3-s3-website-lab.yaml` 파일을 확인합니다.
3. AWS Management Console에 로그인한 후 상단 검색창에 `CloudFormation`을 입력하고 선택합니다.
4. [[Create stack]] 드롭다운을 클릭한 후 **With new resources (standard)**를 선택합니다.
5. **Prerequisite - Prepare template**에서 `Choose an existing template`를 선택합니다.
6. **Specify template**에서 `Upload a template file`을 선택합니다.
7. [[Choose file]] 버튼을 클릭한 후 `week9-3-s3-website-lab.yaml` 파일을 선택합니다.
8. [[Next]] 버튼을 클릭합니다.
9. **Stack name**에 `week9-3-s3-website-stack`을 입력합니다.
10. **Parameters** 섹션에서 필요한 파라미터를 확인합니다 (대부분 기본값 사용).
11. [[Next]] 버튼을 클릭합니다.
12. **Configure stack options** 페이지에서 아래로 스크롤하여 **Tags** 섹션을 확인합니다.
13. [[Add new tag]] 버튼을 클릭한 후 다음 태그를 추가합니다:

| Key | Value |
|-----|-------|
| `Project` | `AWS-Lab` |
| `Week` | `9-3` |
| `CreatedBy` | `CloudFormation` |

> [!NOTE]
> 이 태그들은 AWS CloudFormation 스택이 생성하는 모든 리소스(Amazon S3 버킷, CodeCommit 리포지토리, AWS CodeBuild 프로젝트, AWS CodePipeline, AWS IAM 역할)에 자동으로 전파됩니다.

14. **Capabilities** 섹션에서 `I acknowledge that AWS CloudFormation might create AWS IAM resources`를 체크합니다.
15. [[Next]] 버튼을 클릭합니다.
16. **Review** 페이지에서 설정을 확인합니다.
17. [[Submit]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 생성에 2-3분이 소요됩니다. 상태가 "CREATE_IN_PROGRESS"에서 "**CREATE_COMPLETE**"로 변경될 때까지 기다립니다.
> **Events** 탭에서 생성 과정을 확인할 수 있습니다. 대기하는 동안 다음 태스크를 미리 읽어봅니다.

18. **Outputs** 탭을 선택합니다.
19. 출력값들을 확인하고 메모장에 복사합니다:
    - `WebsiteBucketName`: Amazon S3 버킷 이름
    - `WebsiteURL`: Amazon S3 정적 웹사이트 URL
    - `CodeCommitRepositoryUrl`: CodeCommit 리포지토리 HTTPS URL
    - `CodeBuildProjectName`: AWS CodeBuild 프로젝트 이름
    - `CodePipelineName`: AWS CodePipeline 이름

> [!IMPORTANT]
> 이 출력값들은 다음 태스크에서 사용됩니다. 반드시 메모장에 저장합니다.

✅ **태스크 완료**: 실습 환경이 준비되었습니다.

## 태스크 1: 웹사이트 코드 준비 및 CodeCommit에 푸시

이 태스크에서는 CI/CD Demo 정적 웹사이트 파일들을 CodeCommit 리포지토리에 푸시합니다.

이 파일들은 CI/CD 파이프라인에서 자동으로 빌드되고 Amazon S3에 배포됩니다.

### 상세 단계

20. 태스크 0에서 압축 해제한 `week9-3-s3-website-lab` 폴더를 엽니다.
21. 폴더 내에 다음 파일들이 있는지 확인합니다:
	- `index.html`
	- `about.html`
   - `style.css`
   - `script.js`
   - `buildspec.yml`
   - `week9-3-s3-website-lab.yaml` (태스크 0에서 사용)

> [!NOTE]
> 실습 파일의 디렉토리 구조:
> ```
> week9-3-s3-website-lab/
> ├── week9-3-s3-website-lab.yaml
> ├── index.html
> ├── about.html
> ├── style.css
> ├── script.js
> └── buildspec.yml
> ```

22. AWS Management Console 상단 우측의 AWS CloudShell 아이콘을 클릭합니다.

> [!NOTE]
> CloudShell이 시작될 때까지 기다립니다. CloudShell은 AWS CLI와 Git이 사전 설치된 브라우저 기반 셸 환경입니다.

23. 작업 디렉토리를 생성합니다:

```bash
mkdir ~/quicktable-frontend
cd ~/quicktable-frontend
```

24. git-remote-codecommit 헬퍼를 설치합니다:

```bash
pip install --user git-remote-codecommit
```

> [!NOTE]
> git-remote-codecommit은 AWS IAM 자격 증명을 사용하여 CodeCommit에 인증하는 Git 헬퍼입니다.
> CloudShell에는 AWS CLI가 사전 설치되어 있고 자격 증명이 자동으로 구성되므로 별도 설정이 필요 없습니다.
> `--user` 플래그는 사용자 레벨에 패키지를 설치하여 권한 문제를 방지합니다.

25. 다음 명령어를 실행하여 CodeCommit 리포지토리를 복제합니다:

```bash
git clone codecommit::ap-northeast-2://<repository-name>
```

> [!NOTE]
> `<repository-name>`은 태스크 0에서 생성된 CodeCommit 리포지토리 이름으로 대체합니다.
> 예: `git clone codecommit::ap-northeast-2://week9-3-s3-website-repo`
> 
> HTTPS URL 대신 `codecommit::` 프로토콜을 사용하면 git-remote-codecommit 헬퍼가 자동으로 인증을 처리합니다.

26. 복제된 디렉토리로 이동합니다:

```bash
cd <repository-name>
```

> [!NOTE]
> `<repository-name>`은 리포지토리 이름으로 대체합니다. 예: `cd week9-3-s3-website-repo`

27. Git 사용자 정보를 설정합니다:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

> [!NOTE]
> Git 사용자 정보는 커밋 이력에 기록됩니다. 실제 이름과 이메일을 입력하거나 테스트용 정보를 사용할 수 있습니다.

28. AWS CloudShell 상단의 **Actions** > `Upload file`을 선택합니다.
29. 파일 선택 창이 열리면 압축 해제한 폴더로 이동합니다.
30. `index.html` 파일을 선택합니다.
31. [[Open]] 또는 [[열기]] 버튼을 클릭하여 업로드를 시작합니다.

> [!NOTE]
> AWS CloudShell의 Upload file 기능은 한 번에 1개 파일만 업로드할 수 있습니다.
> 5개의 파일을 모두 업로드하려면 이 과정을 5번 반복해야 합니다.
> `week9-3-s3-website-lab.yaml` 파일은 태스크 0에서 이미 사용했으므로 CodeCommit에 푸시할 필요가 없습니다.

32. 업로드가 완료되면 같은 방법으로 나머지 파일들을 하나씩 업로드합니다:
    - `about.html`
    - `style.css`
    - `script.js`
    - `buildspec.yml`

> [!NOTE]
> 각 파일 업로드에 10-20초가 소요됩니다. AWS CloudShell 하단에 업로드 진행 상황이 표시됩니다.

33. 모든 파일 업로드가 완료되면 다음 명령어를 실행하여 파일을 리포지토리 디렉토리로 이동합니다:

```bash
mv ~/index.html ~/about.html ~/style.css ~/script.js ~/buildspec.yml .
```

> [!TIP]
> 마지막의 `.` (점)은 현재 디렉토리를 의미합니다. 이 명령어는 홈 디렉토리의 파일들을 Git 리포지토리 디렉토리로 이동시킵니다.

34. 파일이 정상적으로 복사되었는지 확인합니다:

```bash
ls -la
```

> [!OUTPUT]
> ```
> drwxr-xr-x 3 cloudshell-user cloudshell-user   96 Feb  7 10:00 .git
> -rw-r--r-- 1 cloudshell-user cloudshell-user 2048 Feb  7 10:00 index.html
> -rw-r--r-- 1 cloudshell-user cloudshell-user 1536 Feb  7 10:00 about.html
> -rw-r--r-- 1 cloudshell-user cloudshell-user 3072 Feb  7 10:00 style.css
> -rw-r--r-- 1 cloudshell-user cloudshell-user 1024 Feb  7 10:00 script.js
> -rw-r--r-- 1 cloudshell-user cloudshell-user  384 Feb  7 10:00 buildspec.yml
> ```

35. 5개의 파일과 .git 디렉토리가 모두 표시되는지 확인합니다.
36. 모든 파일을 Git에 추가합니다:

```bash
git add .
```

37. 추가된 파일을 확인합니다:

```bash
git status
```

> [!OUTPUT]
> ```
> On branch main
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
>         new file:   about.html
>         new file:   buildspec.yml
>         new file:   index.html
>         new file:   script.js
>         new file:   style.css
> ```

38. 5개의 파일이 모두 "new file"로 표시되는지 확인합니다.
39. 커밋을 생성합니다:

```bash
git commit -m "Initial commit: CI/CD Demo website files"
```

> [!OUTPUT]
> ```
> [main abc1234] Initial commit: CI/CD Demo website files
>  5 files changed, 200 insertions(+)
>  create mode 100644 about.html
>  create mode 100644 buildspec.yml
>  create mode 100644 index.html
>  create mode 100644 script.js
>  create mode 100644 style.css
> ```

40. CodeCommit에 푸시합니다:

```bash
git push origin main
```

> [!NOTE]
> 브랜치 이름이 `master`인 경우 `git push origin master`를 사용합니다.

> [!OUTPUT]
> ```
> Enumerating objects: 7, done.
> Counting objects: 100% (7/7), done.
> Delta compression using up to 2 threads
> Compressing objects: 100% (5/5), done.
> Writing objects: 100% (6/6), 2.0 KiB | 2.0 MiB/s, done.
> Total 6 (delta 0), reused 0 (delta 0)
> To codecommit::ap-northeast-2://...
>    abc1234..def5678  main -> main
> ```

41. 푸시가 성공적으로 완료되었는지 확인합니다.
42. CodeCommit 콘솔로 이동합니다.
43. 생성한 리포지토리를 선택합니다.
44. **Code** 탭에서 5개의 파일이 모두 표시되는지 확인합니다.

> [!TIP]
> 각 파일을 클릭하여 내용을 확인할 수 있습니다. `index.html`은 CI/CD Pipeline Demo 메인 페이지이며, `about.html`은 프로젝트 소개 페이지입니다.

✅ **태스크 완료**: 웹사이트 코드가 CodeCommit에 푸시되었습니다.

## 태스크 2: AWS CodePipeline 확인 및 첫 번째 배포

이 태스크에서는 AWS CloudFormation이 자동으로 생성한 CodePipeline을 확인하고 첫 번째 파이프라인 실행을 시작합니다.

### 상세 단계

45. AWS Management Console 상단 검색창에 `CodePipeline`을 입력하고 선택합니다.
46. 왼쪽 메뉴에서 **Pipelines**를 선택합니다.
47. 태스크 0에서 복사한 `CodePipelineName` 값의 파이프라인을 선택합니다.

> [!NOTE]
> AWS CloudFormation 스택이 자동으로 생성한 CodePipeline입니다. 파이프라인 이름은 `week9-3-s3-website-Pipeline` 형식입니다.

48. 파이프라인 구조를 확인합니다:
	- **Source 단계**: CodeCommit에서 소스 코드 가져오기
	- **Build 단계**: AWS CodeBuild로 빌드 및 Amazon S3 배포

> [!NOTE]
> Amazon S3 배포는 AWS CodeBuild의 buildspec.yml에서 `aws s3 sync` 명령으로 수행하므로 별도의 Deploy 단계가 없습니다.

49. **Pipeline settings** 탭을 선택합니다.
50. **Service role** 섹션에서 AWS IAM 역할을 확인합니다.

> [!NOTE]
> AWS CloudFormation 스택이 생성한 AWS IAM 역할로, CodeCommit 및 AWS CodeBuild 접근 권한이 포함되어 있습니다.

51. **Execution history** 탭을 선택합니다.
52. 파이프라인 실행 이력을 확인합니다.

> [!NOTE]
> 태스크 1에서 코드를 푸시하면 Amazon EventBridge 규칙이 자동으로 파이프라인을 트리거합니다.
> 
> **파이프라인 상태 확인:**
> 
> - 스택 생성 직후 CodeCommit이 비어 있어 파이프라인이 자동 실행되었다가 실패했을 수 있습니다
> - 태스크 1 푸시 후 자동 트리거되어 이미 실행 중이거나 완료된 상태일 수 있습니다
> - 파이프라인이 실패 상태이거나 자동 시작되지 않은 경우 [[Release change]]를 클릭하여 다시 실행합니다

53. [[Release change]] 버튼을 클릭하여 파이프라인 실행을 시작합니다.
54. 확인 창에서 [[Release]] 버튼을 클릭합니다.
55. Source 단계가 "In progress"로 표시되는 것을 확인합니다.

> [!NOTE]
> Source 단계가 "Succeeded"로 변경될 때까지 기다립니다.

56. Build 단계가 자동으로 시작되는 것을 확인합니다.

> [!NOTE]
> 전체 파이프라인 실행에 3-5분이 소요됩니다. 각 단계의 **Details** 링크를 클릭하여 상세 진행 상황을 확인할 수 있습니다.
> 대기하는 동안 이전 차시 내용을 복습하거나 다음 태스크를 미리 읽어봅니다.
> 페이지를 새로고침하여 최신 상태를 확인할 수 있습니다.
> Build 단계가 "Succeeded"로 변경될 때까지 기다립니다.

✅ **태스크 완료**: CodePipeline이 확인되고 첫 번째 배포가 완료되었습니다.

## 태스크 3: 배포 확인 및 웹사이트 접근

이 태스크에서는 Amazon S3에 배포된 정적 웹사이트가 정상적으로 접근 가능한지 확인합니다.

### 상세 단계

> [!NOTE]
> AWS CodePipeline 콘솔에서 파이프라인 실행이 완료될 때까지 기다립니다. 전체 파이프라인 실행에 3-5분이 소요됩니다. Source와 Build 단계가 모두 "Succeeded"로 표시되어야 합니다.

57. Amazon S3 콘솔로 이동합니다.
58. 태스크 0에서 복사한 `WebsiteBucketName` 값의 버킷을 선택합니다.
59. **Objects** 탭에서 배포된 파일들을 확인합니다:
	- `index.html`
	- `about.html`
   - `style.css`
   - `script.js`

> [!NOTE]
> buildspec.yml은 빌드 스펙 파일이므로 Amazon S3에 배포되지 않습니다.

60. 새 브라우저 탭을 엽니다.
61. 태스크 0에서 복사한 `WebsiteURL` 값을 주소창에 붙여넣고 Enter를 누릅니다.
62. CI/CD Pipeline Demo 메인 페이지가 정상적으로 표시되는지 확인합니다.

> [!NOTE]
> 메인 페이지에는 "🚀 AWS CI/CD Pipeline Demo" 제목과 함께 CodeCommit, CodeBuild, CodePipeline, Amazon S3 서비스 소개가 표시됩니다.
> 배포 프로세스 설명과 "소개 페이지로 이동" 버튼이 포함되어 있습니다.

63. 웹사이트에서 "소개 페이지로 이동" 버튼을 클릭합니다.
64. `about.html` 페이지가 정상적으로 표시되는지 확인합니다.

✅ **태스크 완료**: 정적 웹사이트가 Amazon S3에 성공적으로 배포되고 접근 가능합니다.

## 태스크 4: 코드 변경 및 자동 배포 테스트

이 태스크에서는 QuickTable 프론트엔드 코드를 수정하고 CodeCommit에 푸시하여 CI/CD 파이프라인이 자동으로 실행되는지 테스트합니다.

### 상세 단계

65. CloudShell에서 리포지토리 디렉토리로 이동합니다:

```bash
cd ~/quicktable-frontend/<repository-name>
```

66. 변경할 문자열이 있는지 먼저 확인합니다:

```bash
grep "Version: 1.0" index.html
```

> [!OUTPUT]
> ```
>                 <p class="version">Version: 1.0</p>
> ```

67. `index.html` 파일을 편집합니다:

```bash
sed -i 's/Version: 1.0/Version: 2.0/g' index.html
```

68. 변경사항을 확인합니다:

```bash
cat index.html | grep -i "Version:"
```

> [!OUTPUT]
> ```
>                 <p class="version">Version: 2.0</p>
> ```

69. 변경사항을 Git에 추가합니다:

```bash
git add index.html
```

70. 커밋을 생성합니다:

```bash
git commit -m "Update version to 2.0"
```

71. CodeCommit에 푸시합니다:

```bash
git push origin main
```

72. AWS CodePipeline 콘솔로 이동합니다.
73. 태스크 0에서 복사한 `CodePipelineName` 값의 파이프라인을 선택합니다.
74. 파이프라인이 자동으로 실행되는지 확인합니다.

> [!NOTE]
> Source 단계가 "Succeeded"로 표시될 때까지 기다립니다.

75. Build 단계가 진행되는 것을 확인합니다.

> [!NOTE]
> 전체 파이프라인 실행에 3-5분이 소요됩니다. 각 단계의 로그를 클릭하여 상세 진행 상황을 확인할 수 있습니다.
> Build 단계가 완료될 때까지 기다립니다.

76. 웹 브라우저에서 Amazon S3 웹사이트 URL을 새로고침합니다.
77. 버전이 "Version: 2.0"으로 업데이트되었는지 확인합니다.

✅ **태스크 완료**: 코드 변경이 자동으로 빌드되고 Amazon S3에 배포되었습니다.

## 마무리

다음을 성공적으로 수행했습니다:

- AWS CloudFormation으로 Amazon S3 버킷과 CI/CD 인프라를 자동으로 구축했습니다
- CodeCommit에 정적 웹사이트 코드를 저장했습니다
- AWS CodeBuild로 웹사이트를 빌드하고 Amazon S3에 배포했습니다
- CodePipeline으로 전체 CI/CD 워크플로우를 자동화했습니다
- 코드 변경 시 자동으로 Amazon S3에 배포되는 파이프라인을 테스트했습니다

# 🗑️ 리소스 정리

> [!WARNING]
> 다음 단계를 **반드시 수행**하여 불필요한 비용을 방지합니다.

### 방법 1: Tag Editor로 리소스 찾기 (권장)

1. AWS Management Console에 로그인한 후 상단 검색창에 `Resource Groups & Tag Editor`을 입력하고 선택합니다.
2. 왼쪽 메뉴에서 **Tag Editor**를 선택합니다.
3. **Regions**에서 `ap-northeast-2`를 선택합니다.
4. **Resource types**에서 `All supported resource types`를 선택합니다.
5. **Tags** 섹션에서 다음을 입력합니다:
	- **Tag key**: `Week`
	- **Tag value**: `9-3`
6. [[Search resources]] 버튼을 클릭합니다.

> [!OUTPUT]
> 이 실습에서 생성한 모든 리소스가 표시됩니다.

> [!NOTE]
> Tag Editor는 리소스를 찾는 용도로만 사용됩니다. 실제 삭제는 각 서비스 콘솔에서 수행해야 합니다.

### 방법 2: AWS CloudFormation 스택 삭제

> [!IMPORTANT]
> Amazon S3 버킷을 먼저 비워야 AWS CloudFormation 스택 삭제가 성공합니다.

#### Amazon S3 웹사이트 버킷 비우기

7. Amazon S3 콘솔로 이동합니다.
8. 태스크 0에서 복사한 `WebsiteBucketName` 값의 버킷을 선택합니다.
9. [[Empty]] 버튼을 클릭합니다.
10. 확인 창에서 `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

> [!NOTE]
> Amazon S3 버킷을 삭제하기 전에 반드시 버킷을 비워야 합니다.

#### CodePipeline 아티팩트 버킷 비우기 (선택사항)

11. Amazon S3 콘솔에서 버킷 목록을 확인합니다.
12. `codepipeline-ap-northeast-2-` 접두사로 시작하는 버킷이 있는지 확인합니다.

> [!NOTE]
> CodePipeline은 아티팩트를 저장하기 위한 별도의 Amazon S3 버킷을 자동으로 생성합니다.
> AWS CloudFormation 스택 삭제 시 이 버킷이 자동으로 삭제되지 않을 수 있습니다.
> 버킷이 비어 있지 않으면 스택 삭제가 실패할 수 있으므로 먼저 비워야 합니다.

13. CodePipeline 아티팩트 버킷이 있으면 선택한 후 [[Empty]] 버튼을 클릭합니다.
14. 확인 창에서 `permanently delete`를 입력하고 [[Empty]] 버튼을 클릭합니다.

#### AWS CloudFormation 스택 삭제

15. AWS CloudFormation 콘솔로 이동합니다.
16. `week9-3-s3-website-stack` 스택을 선택합니다.
17. [[Delete]] 버튼을 클릭합니다.
18. 확인 창에서 [[Delete]] 버튼을 클릭합니다.

> [!NOTE]
> 스택 삭제가 완료될 때까지 기다립니다. 스택 삭제에 2-3분이 소요됩니다. AWS CloudFormation 스택을 삭제하면 CodeCommit 리포지토리, AWS CodeBuild 프로젝트, AWS CodePipeline, AWS IAM 역할 등 모든 리소스가 자동으로 삭제됩니다.

✅ **실습 종료**: 모든 리소스가 정리되었습니다.

## 추가 학습 리소스

- [AWS CodePipeline 사용 설명서](https://docs.aws.amazon.com/ko_kr/codepipeline/latest/userguide/welcome.html)
- [Amazon S3 정적 웹사이트 호스팅](https://docs.aws.amazon.com/ko_kr/AmazonS3/latest/userguide/WebsiteHosting.html)
- [AWS CodeBuild buildspec 참조](https://docs.aws.amazon.com/ko_kr/codebuild/latest/userguide/build-spec-ref.html)

## 📚 참고: Amazon S3 정적 웹사이트 호스팅 및 CI/CD 아키텍처

### Amazon S3 정적 웹사이트 호스팅

Amazon S3는 정적 웹사이트를 호스팅할 수 있는 기능을 제공합니다. HTML, CSS, JavaScript 파일을 Amazon S3 버킷에 업로드하면 웹사이트로 제공할 수 있습니다.

**주요 특징:**
- 서버 관리 불필요
- 높은 가용성 및 확장성
- 저렴한 비용
- Amazon CloudFront와 통합 가능

### CI/CD Demo 웹사이트 구성

**구성 요소:**
- **index.html**: 메인 페이지 (CI/CD Pipeline Demo, 서비스 소개, 배포 프로세스 설명)
- **about.html**: 소개 페이지 (프로젝트 설명, 사용된 AWS 서비스, 학습 목표)
- **script.js**: 인터랙티브 기능 (애니메이션, 배포 정보 로깅)
- **style.css**: 반응형 디자인 (그리드 레이아웃, 호버 효과)

### buildspec.yml의 Amazon S3 배포 단계

**Amazon S3 동기화:**
```bash
aws s3 sync . s3://$BUCKET_NAME --delete --exclude "buildspec.yml"
```

**옵션 설명:**
- `--delete`: Amazon S3에 있지만 로컬에 없는 파일 삭제
- `--exclude`: 특정 파일 제외 (buildspec.yml은 배포하지 않음)

### CodePipeline과 Amazon S3 통합

**파이프라인 단계:**
- **Source**: CodeCommit에서 소스 코드 가져오기
- **Build**: AWS CodeBuild로 빌드 및 Amazon S3 동기화

**자동 트리거:**
- CodeCommit에 푸시하면 Amazon EventBridge 규칙이 파이프라인을 자동으로 시작합니다
- 코드 변경 사항이 즉시 웹사이트에 반영됩니다

### Amazon S3 버킷 정책

**퍼블릭 액세스 허용:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::bucket-name/*"
  }]
}
```

### CI/CD 파이프라인 전체 아키텍처

**Week 9-2 (빌드):**
- AWS CodeBuild: Docker 이미지 빌드
- AWS CodeCommit: 소스 코드 저장소
- Amazon ECR: 컨테이너 이미지 레지스트리

**Week 9-3 (배포):**
- Amazon S3: 정적 웹사이트 호스팅
- AWS CodePipeline: CI/CD 자동화
- Amazon EventBridge: 코드 변경 감지 및 파이프라인 트리거

**데이터 흐름:**
- 개발자가 CodeCommit에 코드를 푸시합니다.
- Amazon EventBridge가 변경 사항을 감지합니다.
- AWS CodePipeline이 자동으로 실행됩니다.
- AWS CodeBuild가 파일을 Amazon S3에 동기화합니다.
- 웹사이트가 자동으로 업데이트됩니다.

### 모범 사례

**보안:**
- Amazon CloudFront를 사용하여 HTTPS 제공 (Week 10-3에서 학습)
- Amazon S3 버킷 직접 액세스 차단
- OAC (Origin Access Control) 사용

**성능:**
- Amazon CloudFront CDN 활용 (Week 10-3에서 학습)
- 파일 압축 (gzip)
- 캐시 헤더 설정

**비용 최적화:**
- Amazon S3 Intelligent-Tiering 사용
- Amazon CloudFront 캐싱으로 Amazon S3 요청 감소
- 불필요한 파일 정리
