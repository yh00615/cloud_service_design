# Week 9-3: AWS CodePipeline으로 Amazon S3 정적 웹사이트 배포 자동화

## 포함 파일

- `week9-3-s3-website-lab.yaml` - AWS CloudFormation 템플릿 (태스크 0에서 Amazon S3 버킷, CodeCommit, AWS CodeBuild, AWS CodePipeline 자동 생성)
- `index.html` - 메인 페이지 (CI/CD Pipeline Demo, 태스크 1에서 CodeCommit에 푸시)
- `about.html` - 소개 페이지 (프로젝트 및 AWS 서비스 설명, 태스크 1에서 CodeCommit에 푸시)
- `style.css` - 스타일시트 (태스크 1에서 CodeCommit에 푸시)
- `script.js` - JavaScript 파일 (인터랙티브 기능, 태스크 1에서 CodeCommit에 푸시)
- `buildspec.yml` - AWS CodeBuild 빌드 스펙 (태스크 1에서 CodeCommit에 푸시)

## 관련 태스크

- 태스크 0: 실습 환경 구축 (week9-3-s3-website-lab.yaml을 사용하여 Amazon S3 버킷, CodeCommit 리포지토리, AWS CodeBuild 프로젝트, AWS CodePipeline 자동 생성)
- 태스크 1: 웹사이트 코드 준비 및 CodeCommit에 푸시 (index.html, about.html, style.css, script.js, buildspec.yml을 CodeCommit에 업로드)
- 태스크 2: AWS CodePipeline 확인 및 첫 번째 배포
