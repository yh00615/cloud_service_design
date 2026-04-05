# Week 9-2: AWS CodeBuild를 활용한 CI/CD 파이프라인 구축

## 포함 파일

- `week9-2-cicd-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon ECR 리포지토리 및 CodeCommit 리포지토리 자동 생성)
- `app.js` - Node.js Express 애플리케이션 (태스크 1에서 CodeCommit에 푸시)
- `package.json` - Node.js 의존성 정의 (태스크 1에서 CodeCommit에 푸시)
- `Dockerfile` - Docker 이미지 빌드 설정 (태스크 1에서 CodeCommit에 푸시)
- `buildspec.yml` - AWS CodeBuild 빌드 스펙 (태스크 2에서 분석 및 푸시)

## 관련 태스크

- 태스크 0: 실습 환경 구축 (AWS CloudFormation으로 Amazon ECR 리포지토리 및 CodeCommit 리포지토리 자동 생성)
- 태스크 1: 애플리케이션 코드 준비 (app.js, package.json, Dockerfile을 CodeCommit에 푸시)
- 태스크 2: buildspec.yml 분석 및 푸시 (AWS CodeBuild 빌드 단계 이해 및 CodeCommit에 푸시)
- 태스크 3: AWS CodeBuild 프로젝트 생성 (빌드 환경 설정 및 Amazon ECR 연동)
- 태스크 4: 빌드 실행 및 검증 (이미지 빌드 및 Amazon ECR 푸시 확인)
