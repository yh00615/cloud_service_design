# Week 10-3: CloudFront Demo Files

## 📦 포함된 파일

### HTML 파일
- **index.html** - 메인 페이지 (CloudFront 기능 소개)
- **about.html** - 실습 정보 페이지 (아키텍처, 모범 사례)

### CSS 파일
- **style.css** - 스타일시트 (캐싱 테스트용)

### JavaScript 파일
- **script.js** - 인터랙티브 기능 (캐싱 테스트, 성능 측정)

### 이미지 파일 (직접 준비 필요)
- **images/logo.png** - AWS 로고 (80x80px 권장)
- **images/banner.jpg** - 배너 이미지 (800x400px 권장)

## 🖼️ 이미지 파일 준비

이미지 파일은 저작권 문제로 포함되지 않았습니다. 다음 방법으로 준비하세요:

### 방법 1: AWS 로고 다운로드
1. [AWS 로고 다운로드](https://aws.amazon.com/ko/architecture/icons/)
2. `logo.png` 파일을 `images/` 폴더에 저장

### 방법 2: Placeholder 이미지 사용
```bash
# logo.png (80x80px)
curl -o images/logo.png "https://via.placeholder.com/80x80/232F3E/FFFFFF?text=AWS"

# banner.jpg (800x400px)
curl -o images/banner.jpg "https://via.placeholder.com/800x400/FF9900/FFFFFF?text=CloudFront+Demo"
```

### 방법 3: 직접 제작
- **logo.png**: 80x80px PNG 파일
- **banner.jpg**: 800x400px JPG 파일
- 온라인 이미지 편집 도구 사용 (Canva, Figma 등)

## 🚀 사용 방법

### 1. S3 버킷 생성 및 파일 업로드

#### S3 버킷 생성
1. AWS Management Console에 로그인
2. S3 서비스로 이동
3. **Create bucket** 클릭
4. **Bucket name**: `demo-cloudfront-origin-본인이름-12345` (고유한 이름)
5. **Region**: `ap-northeast-2` 선택
6. **Block all public access**: 체크 유지 (CloudFront OAC 사용)
7. **Create bucket** 클릭

#### 파일 업로드
1. 생성한 버킷 선택
2. **Upload** 클릭
3. 다음 파일들을 업로드:
   ```
   index.html
   about.html
   style.css
   script.js
   images/logo.png
   images/banner.jpg
   ```
4. **Upload** 클릭

### 2. CloudFront 배포 생성

Week 10-3 실습 가이드를 따라 진행합니다:
1. CloudFront 배포 생성
2. S3 버킷을 오리진으로 설정
3. OAC(Origin Access Control) 설정
4. S3 버킷 정책 업데이트
5. 배포 완료 대기 (10-15분)

### 3. 웹사이트 접속 및 테스트

#### 접속
1. CloudFront 콘솔에서 배포의 **Distribution domain name** 복사
2. 브라우저에서 `https://[distribution-domain-name]/index.html` 접속

#### 캐싱 테스트
1. 브라우저 개발자 도구(F12) 열기
2. **Network** 탭 선택
3. 페이지 새로고침
4. 각 리소스의 **Headers** 확인:
   - `X-Cache`: Hit from cloudfront (캐시됨) 또는 Miss from cloudfront (캐시 미스)
   - `X-Amz-Cf-Pop`: 엣지 로케이션 (예: ICN54-C1)
   - `X-Amz-Cf-Id`: CloudFront 요청 ID

#### 인터랙티브 테스트
페이지의 버튼을 클릭하여 다양한 캐싱 테스트 수행:
- **이미지 로드 테스트**: 이미지 캐싱 확인
- **CSS 캐싱 테스트**: CSS 파일 캐싱 확인
- **JavaScript 캐싱 테스트**: JS 파일 캐싱 확인
- **캐시 정보 표시**: 모든 리소스의 로드 시간 확인

## 📊 파일별 캐싱 전략

### HTML 파일 (index.html, about.html)
- **TTL**: 짧게 설정 (300초 = 5분)
- **이유**: 콘텐츠가 자주 변경될 수 있음
- **Cache-Control**: `max-age=300`

### CSS 파일 (style.css)
- **TTL**: 중간 설정 (3600초 = 1시간)
- **이유**: 스타일은 가끔 변경됨
- **Cache-Control**: `max-age=3600`

### JavaScript 파일 (script.js)
- **TTL**: 중간 설정 (3600초 = 1시간)
- **이유**: 스크립트는 가끔 변경됨
- **Cache-Control**: `max-age=3600`

### 이미지 파일 (logo.png, banner.jpg)
- **TTL**: 길게 설정 (86400초 = 24시간)
- **이유**: 이미지는 거의 변경되지 않음
- **Cache-Control**: `max-age=86400`

## 🔄 캐시 무효화 (Invalidation)

파일을 수정한 후 즉시 반영하려면 캐시 무효화를 수행하세요.

### AWS Console 사용
1. CloudFront 콘솔로 이동
2. 배포 선택
3. **Invalidations** 탭 선택
4. **Create invalidation** 클릭
5. **Object paths** 입력:
   - 모든 파일: `/*`
   - 특정 파일: `/index.html`
   - 특정 폴더: `/images/*`
6. **Create invalidation** 클릭

### AWS CLI 사용
```bash
# 모든 파일 무효화
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

# 특정 파일만 무효화
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/index.html" "/style.css"
```

## 💰 비용 정보

**CloudFront 비용** (ap-northeast-2 리전 기준):
- 데이터 전송: 처음 10TB까지 GB당 $0.085
- HTTP/HTTPS 요청: 10,000건당 $0.0075
- 무효화 요청: 처음 1,000개 경로 무료, 이후 경로당 $0.005

**S3 비용**:
- 스토리지: GB당 $0.025/월
- GET 요청: 1,000건당 $0.0004

**예상 비용** (실습용):
- 파일 크기: 약 50KB
- 요청 수: 100회
- **총 비용**: $0.01 미만 (거의 무료)

## 🧹 리소스 정리

### 1. CloudFront 배포 삭제
1. CloudFront 콘솔로 이동
2. 배포 선택
3. **Disable** 클릭 (먼저 비활성화 필요)
4. 상태가 "Deployed"가 될 때까지 대기 (10-15분)
5. 배포 선택 후 **Delete** 클릭

### 2. S3 버킷 삭제
1. S3 콘솔로 이동
2. 버킷 선택
3. **Empty** 클릭 (모든 파일 삭제)
4. 확인 후 **Empty** 클릭
5. 버킷 선택 후 **Delete** 클릭
6. 버킷 이름 입력 후 **Delete bucket** 클릭

## 🔍 트러블슈팅

### 403 Forbidden 오류
**문제**: CloudFront URL 접속 시 403 오류 발생

**원인**: S3 버킷 정책이 CloudFront OAC를 허용하지 않음

**해결**:
1. CloudFront 콘솔에서 배포 선택
2. **Origins** 탭 선택
3. 오리진 선택 후 **Edit** 클릭
4. **Copy policy** 버튼 클릭 (버킷 정책 복사)
5. S3 콘솔로 이동
6. 버킷 선택 > **Permissions** 탭
7. **Bucket policy** > **Edit** 클릭
8. 복사한 정책 붙여넣기
9. **Save changes** 클릭

### 오래된 콘텐츠가 표시됨
**문제**: 파일을 수정했는데 이전 버전이 표시됨

**원인**: CloudFront 캐시가 아직 만료되지 않음

**해결**:
1. 캐시 무효화(Invalidation) 생성
2. 또는 TTL이 만료될 때까지 대기
3. 또는 브라우저 캐시 삭제 (Ctrl+Shift+Delete)

### 이미지가 표시되지 않음
**문제**: 이미지 파일이 로드되지 않음

**원인**: 
- 이미지 파일이 S3에 업로드되지 않음
- 파일 경로가 잘못됨

**해결**:
1. S3 버킷에서 `images/logo.png`, `images/banner.jpg` 파일 확인
2. 파일명과 경로가 정확한지 확인
3. 파일 권한 확인 (CloudFront OAC 설정 필요)

### 느린 첫 로딩
**문제**: 첫 페이지 로딩이 느림

**원인**: 캐시 미스 (Miss from cloudfront)

**정상**: 
- 첫 요청은 오리진(S3)에서 가져오므로 느릴 수 있음
- 이후 요청은 엣지 로케이션 캐시에서 가져와 빠름
- Network 탭에서 `X-Cache: Hit from cloudfront` 확인

## 📚 추가 리소스

- [Amazon CloudFront 개발자 가이드](https://docs.aws.amazon.com/cloudfront/)
- [CloudFront 캐싱 모범 사례](https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html)
- [OAC를 사용한 S3 오리진 보호](https://docs.aws.amazon.com/ko_kr/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)

## ❓ 자주 묻는 질문

**Q: CloudFront 배포 생성에 시간이 오래 걸리나요?**
A: 네, 첫 배포는 10-15분 정도 소요됩니다. 전 세계 엣지 로케이션에 설정을 배포하기 때문입니다.

**Q: 무료 티어가 있나요?**
A: 네, AWS 프리 티어에서 매월 50GB 데이터 전송과 2,000,000건의 HTTP/HTTPS 요청을 무료로 제공합니다.

**Q: HTTPS를 사용할 수 있나요?**
A: 네, CloudFront는 기본적으로 HTTPS를 지원합니다. 커스텀 도메인을 사용하려면 ACM 인증서가 필요합니다.

**Q: 다른 리전에서도 빠른가요?**
A: 네, CloudFront는 전 세계 450개 이상의 엣지 로케이션을 통해 모든 리전에서 빠른 콘텐츠 전달을 제공합니다.
