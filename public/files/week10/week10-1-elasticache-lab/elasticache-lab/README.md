# ElastiCache 캐싱 전략 실습 파일

이 패키지는 Amazon ElastiCache for Redis를 활용한 캐싱 전략 실습을 위한 파일들입니다.

## 📦 포함된 파일

- `app.py` - FastAPI 웹 애플리케이션 (Cache-Aside 패턴 구현)
- `requirements.txt` - Python 의존성 패키지
- `.env.example` - 환경 변수 설정 예제
- `init_db.sql` - 데이터베이스 초기화 스크립트
- `benchmark.py` - 성능 벤치마크 스크립트
- `README.md` - 이 파일

## 🚀 사용 방법

### 1. 사전 준비

실습 가이드의 태스크 1-4를 완료하여 다음을 준비하세요:
- ElastiCache Redis 클러스터 생성
- RDS MySQL 인스턴스 생성 (Week 5-1 참고)
- EC2 인스턴스 (Private 서브넷)

### 2. 파일 업로드

EC2 인스턴스에 파일을 업로드합니다:

```bash
# 로컬에서 압축 해제 후
scp -i your-key.pem -r elasticache-lab ec2-user@your-ec2-ip:~/
```

또는 EC2에서 직접 다운로드:

```bash
cd ~
wget https://your-cloudfront-domain/files/week10/week10-2-elasticache-lab.zip
unzip week10-2-elasticache-lab.zip
cd elasticache-lab
```

### 3. 데이터베이스 초기화

RDS MySQL에 접속하여 초기 데이터를 생성합니다:

```bash
mysql -h your-rds-endpoint.rds.amazonaws.com -u admin -p < init_db.sql
```

### 4. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성하고 실제 값으로 수정합니다:

```bash
cp .env.example .env
nano .env
```

다음 값들을 실제 엔드포인트로 변경하세요:
- `REDIS_HOST`: ElastiCache Redis 엔드포인트
- `DB_HOST`: RDS MySQL 엔드포인트
- `DB_PASSWORD`: RDS 비밀번호

### 5. Python 패키지 설치

```bash
# Python 3 및 pip 설치 (Amazon Linux 2023)
sudo yum install -y python3 python3-pip

# 의존성 설치
pip3 install -r requirements.txt
```

### 6. 애플리케이션 실행

```bash
uvicorn app:app --host 0.0.0.0 --port 5000
```

서버가 `http://0.0.0.0:5000`에서 실행됩니다.

> [!NOTE]
> FastAPI는 자동으로 API 문서를 생성합니다:
> - Swagger UI: `http://localhost:5000/docs`
> - ReDoc: `http://localhost:5000/redoc`

### 7. API 테스트

다른 터미널에서 API를 테스트합니다:

```bash
# 헬스 체크
curl http://localhost:5000/health

# 사용자 조회 (캐시 적용)
curl http://localhost:5000/user/1

# 사용자 조회 (캐시 미적용)
curl http://localhost:5000/user/1/nocache

# 상품 목록 조회
curl http://localhost:5000/products

# 캐시 통계
curl http://localhost:5000/cache/stats

# 캐시 초기화
curl -X POST http://localhost:5000/cache/clear
```

### 8. 성능 벤치마크 실행

```bash
# 새 터미널에서
python3 benchmark.py
```

캐시 사용 전후의 성능 차이를 확인할 수 있습니다.

## 📊 예상 결과

### 캐시 미사용
- 평균 응답 시간: 50-100ms
- DB 쿼리 실행

### 캐시 사용 (Cache Hit)
- 평균 응답 시간: 1-5ms
- 10-50배 빠른 응답 속도

### 캐시 히트율
- 80% 이상 권장
- `/cache/stats`에서 확인 가능

## 🔍 주요 API 엔드포인트

| 엔드포인트 | 설명 | 캐시 |
|-----------|------|------|
| `GET /user/{userId}` | 사용자 조회 | ✅ (TTL 1시간) |
| `GET /user/{userId}/nocache` | 사용자 조회 | ❌ |
| `GET /products` | 상품 목록 | ✅ (TTL 5분) |
| `GET /cache/stats` | 캐시 통계 | - |
| `POST /cache/clear` | 캐시 초기화 | - |
| `GET /health` | 헬스 체크 | - |
| `GET /docs` | API 문서 (Swagger UI) | - |
| `GET /redoc` | API 문서 (ReDoc) | - |

## 🛠️ 문제 해결

### Redis 연결 오류
```
redis.exceptions.ConnectionError
```
- Redis 엔드포인트 확인
- 보안 그룹에서 6379 포트 허용 확인
- EC2가 Redis와 같은 VPC에 있는지 확인

### DB 연결 오류
```
pymysql.err.OperationalError
```
- RDS 엔드포인트 확인
- 보안 그룹에서 3306 포트 허용 확인
- DB 사용자 이름/비밀번호 확인

### 패키지 설치 오류
```bash
# pip 업그레이드
pip3 install --upgrade pip

# 개별 설치
pip3 install fastapi uvicorn redis PyMySQL python-dotenv pydantic
```

### uvicorn 실행 오류
```bash
# uvicorn이 설치되지 않은 경우
pip3 install 'uvicorn[standard]'

# 또는 기본 버전
pip3 install uvicorn
```

## 📚 학습 포인트

1. **Cache-Aside 패턴**: 애플리케이션이 캐시를 직접 관리
2. **TTL 설정**: 데이터 특성에 따른 적절한 만료 시간
3. **성능 향상**: 10-50배 빠른 응답 속도
4. **캐시 히트율**: 80% 이상 유지가 목표
5. **캐시 무효화**: 데이터 변경 시 캐시 삭제 전략
6. **FastAPI 장점**: 자동 API 문서 생성, 타입 안전성, 비동기 지원

## 🆚 Flask vs FastAPI

### FastAPI 장점
- ✅ 자동 API 문서 생성 (Swagger UI, ReDoc)
- ✅ Pydantic을 통한 타입 안전성
- ✅ 비동기 처리 지원
- ✅ 더 빠른 성능
- ✅ 최신 Python 기능 활용

### 실행 명령어 비교
```bash
# Flask
python3 app.py

# FastAPI
uvicorn app:app --host 0.0.0.0 --port 5000
```

## 🔗 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Redis Python 클라이언트](https://redis-py.readthedocs.io/)
- [ElastiCache 모범 사례](https://docs.aws.amazon.com/ko_kr/AmazonElastiCache/latest/red-ug/BestPractices.html)
- [Pydantic 문서](https://docs.pydantic.dev/)
