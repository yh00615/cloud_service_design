# CI/CD 파이프라인 실습 파일

이 패키지는 AWS CodePipeline을 사용한 CI/CD 파이프라인 구축 실습을 위한 파일들입니다.

## 📦 포함된 파일

- `app.js` - Node.js Express 애플리케이션
- `package.json` - Node.js 의존성 정의
- `Dockerfile` - Docker 이미지 빌드 설정
- `buildspec.yml` - CodeBuild 빌드 스펙
- `README.md` - 이 파일

## 🚀 로컬 테스트

### 1. Node.js로 실행

```bash
npm install
npm start
```

브라우저에서 `http://localhost:3000` 접속

### 2. Docker로 실행

```bash
docker build -t cicd-demo-app .
docker run -p 3000:3000 cicd-demo-app
```

브라우저에서 `http://localhost:3000` 접속

## 📋 파일 설명

### app.js
- Express 웹 서버
- `/` - 메인 페이지 (HTML)
- `/health` - 헬스 체크 엔드포인트 (JSON)

### Dockerfile
- Node.js 18 Alpine 이미지 사용
- 프로덕션 의존성만 설치
- 헬스 체크 포함
- 포트 3000 노출

### buildspec.yml
- **pre_build**: ECR 로그인, 이미지 태그 설정
- **build**: Docker 이미지 빌드 및 태그
- **post_build**: ECR에 이미지 푸시, imagedefinitions.json 생성

**중요**: `AWS_ACCOUNT_ID`는 `aws sts get-caller-identity`로 동적으로 가져옵니다.

## 🔧 CodeBuild 환경 변수

CodeBuild 프로젝트에서 다음 환경 변수를 설정하세요:

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `AWS_DEFAULT_REGION` | `ap-northeast-2` | AWS 리전 |
| `IMAGE_REPO_NAME` | `cicd-demo-app` | ECR 리포지토리 이름 |
| `CONTAINER_NAME` | `cicd-demo-container` | ECS 컨테이너 이름 |

**주의**: `AWS_ACCOUNT_ID`는 환경 변수로 설정하지 않아도 됩니다. buildspec.yml에서 자동으로 가져옵니다.

## 📝 버전 업데이트 방법

`app.js` 파일에서 버전 번호를 변경하세요:

```javascript
<p class="version">Version 2.0</p>  // 1.0 → 2.0

// 그리고
version: '2.0',  // health 엔드포인트
```

변경 후 Git에 커밋하고 푸시하면 자동으로 파이프라인이 실행됩니다:

```bash
git add app.js
git commit -m "Update to version 2.0"
git push origin main
```

## 🏗️ 아키텍처

```
CodeCommit (소스) 
    ↓
CodePipeline (오케스트레이션)
    ↓
CodeBuild (빌드)
    ↓
ECR (이미지 저장소)
    ↓
ECS Fargate (배포)
```

## 🔍 트러블슈팅

### CodeBuild 빌드 실패

**오류**: `denied: Your authorization token has expired`
- **해결**: ECR 권한 확인, IAM 역할에 `AmazonEC2ContainerRegistryPowerUser` 정책 추가

**오류**: `Cannot connect to the Docker daemon`
- **해결**: CodeBuild 환경에서 "Privileged" 옵션 활성화

### ECS 배포 실패

**오류**: `Service does not exist`
- **해결**: ECS 서비스가 생성되었는지 확인

**오류**: `Task failed to start`
- **해결**: CloudWatch Logs에서 컨테이너 로그 확인

## 📚 학습 포인트

1. **CI/CD 자동화**: 코드 푸시 → 자동 빌드 → 자동 배포
2. **컨테이너화**: Docker를 사용한 일관된 환경
3. **이미지 버전 관리**: Git 커밋 해시로 이미지 태그
4. **무중단 배포**: ECS Rolling Update
5. **인프라 as 코드**: buildspec.yml로 빌드 프로세스 정의

## 🔗 추가 리소스

- [AWS CodePipeline 문서](https://docs.aws.amazon.com/codepipeline/)
- [AWS CodeBuild 문서](https://docs.aws.amazon.com/codebuild/)
- [ECS 배포 가이드](https://docs.aws.amazon.com/ko_kr/AmazonECS/latest/developerguide/)
