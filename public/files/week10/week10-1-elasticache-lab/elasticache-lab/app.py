"""
AWS 실습: ElastiCache 캐싱 데모

이 FastAPI 애플리케이션은 Cache-Aside 패턴을 구현하여
ElastiCache Redis와 RDS MySQL을 연동합니다.

주요 기능:
    1. 사용자 정보 조회 (캐시 우선)
    2. 상품 목록 조회 (캐시 적용)
    3. 캐시 통계 및 관리

환경 변수:
    REDIS_HOST (str): ElastiCache Redis 엔드포인트
    REDIS_PORT (int): Redis 포트 (기본값: 6379)
    DB_HOST (str): RDS MySQL 엔드포인트
    DB_USER (str): 데이터베이스 사용자명
    DB_PASSWORD (str): 데이터베이스 비밀번호
    DB_NAME (str): 데이터베이스 이름

실행 방법:
    uvicorn app:app --host 0.0.0.0 --port 5000
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import redis
import pymysql
import json
import time
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="ElastiCache Lab API",
    description="Amazon ElastiCache for Redis 캐싱 전략 실습 API",
    version="1.0.0"
)

# Redis 연결
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True,
    socket_connect_timeout=5
)

# RDS 연결 설정
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'labdb'),
    'connect_timeout': 5
}


# Pydantic 모델 정의
class UserResponse(BaseModel):
    """사용자 조회 응답 모델"""
    source: str
    data: Dict[str, Any]
    responseTimeMs: float


class ProductsResponse(BaseModel):
    """상품 목록 조회 응답 모델"""
    source: str
    count: int
    data: List[Dict[str, Any]]
    responseTimeMs: float


class CacheStatsResponse(BaseModel):
    """캐시 통계 응답 모델"""
    totalConnections: int
    totalCommands: int
    keyspaceHits: int
    keyspaceMisses: int
    hitRate: float


class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    redis: str
    database: str


class MessageResponse(BaseModel):
    """일반 메시지 응답 모델"""
    message: str


class ErrorResponse(BaseModel):
    """오류 응답 모델"""
    error: str
    errorCode: Optional[str] = None


def get_db_connection() -> pymysql.connections.Connection:
    """
    RDS MySQL 데이터베이스 연결을 생성합니다
    
    Returns:
        pymysql.connections.Connection: 데이터베이스 연결 객체
    
    Raises:
        Exception: 데이터베이스 연결 실패 시
    """
    return pymysql.connect(**db_config)


@app.get("/", response_model=Dict[str, Any])
async def index():
    """
    API 엔드포인트 목록을 반환합니다
    
    Returns:
        dict: API 정보 및 엔드포인트 목록
    """
    return {
        "message": "ElastiCache Lab API",
        "version": "1.0.0",
        "endpoints": {
            "/user/{userId}": "Get user by ID (with cache)",
            "/user/{userId}/nocache": "Get user by ID (without cache)",
            "/products": "Get all products (with cache)",
            "/cache/stats": "Get cache statistics",
            "/cache/clear": "Clear all cache",
            "/health": "Health check",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }


@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Cache-Aside 패턴으로 사용자 정보를 조회합니다
    
    1. Redis 캐시에서 조회 시도
    2. 캐시 미스 시 RDS MySQL에서 조회
    3. 조회 결과를 캐시에 저장 (TTL 1시간)
    
    Args:
        user_id (int): 사용자 고유 ID
    
    Returns:
        UserResponse: HTTP 응답 형식
            - source (str): 'cache' 또는 'database'
            - data (dict): 사용자 정보
            - responseTimeMs (float): 응답 시간 (밀리초)
    
    Raises:
        HTTPException: 404 - 사용자를 찾을 수 없음
        HTTPException: 500 - 데이터베이스 연결 오류
    """
    start_time = time.time()
    cache_key = f"user:{user_id}"
    
    # 1. Redis 캐시에서 조회 시도
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        # 캐시 히트: 응답 시간 계산 후 반환
        elapsed = (time.time() - start_time) * 1000
        return UserResponse(
            source="cache",
            data=json.loads(cached_data),
            responseTimeMs=round(elapsed, 2)
        )
    
    # 2. 캐시 미스: RDS MySQL에서 조회
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            # 3. 조회 결과를 캐시에 저장 (TTL 1시간)
            redis_client.setex(
                cache_key,
                3600,
                json.dumps(user_data, default=str)
            )
            
            elapsed = (time.time() - start_time) * 1000
            return UserResponse(
                source="database",
                data=user_data,
                responseTimeMs=round(elapsed, 2)
            )
        else:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "errorCode": "USER_NOT_FOUND", "userId": user_id}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "errorCode": "DATABASE_ERROR"}
        )


@app.get("/user/{user_id}/nocache", response_model=UserResponse)
async def get_user_nocache(user_id: int):
    """
    캐시 없이 데이터베이스에서 직접 사용자 정보를 조회합니다
    
    Args:
        user_id (int): 사용자 고유 ID
    
    Returns:
        UserResponse: HTTP 응답 형식
            - source (str): 'database'
            - data (dict): 사용자 정보
            - responseTimeMs (float): 응답 시간 (밀리초)
    
    Raises:
        HTTPException: 404 - 사용자를 찾을 수 없음
        HTTPException: 500 - 데이터베이스 연결 오류
    """
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        elapsed = (time.time() - start_time) * 1000
        
        if user_data:
            return UserResponse(
                source="database",
                data=user_data,
                responseTimeMs=round(elapsed, 2)
            )
        else:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "errorCode": "USER_NOT_FOUND", "userId": user_id}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "errorCode": "DATABASE_ERROR"}
        )


@app.get("/products", response_model=ProductsResponse)
async def get_products():
    """
    상품 목록을 조회합니다 (캐시 적용)
    
    1. Redis 캐시에서 조회 시도
    2. 캐시 미스 시 RDS MySQL에서 조회
    3. 조회 결과를 캐시에 저장 (TTL 5분)
    
    Returns:
        ProductsResponse: HTTP 응답 형식
            - source (str): 'cache' 또는 'database'
            - count (int): 상품 개수
            - data (list): 상품 목록
            - responseTimeMs (float): 응답 시간 (밀리초)
    
    Raises:
        HTTPException: 500 - 데이터베이스 연결 오류
    """
    start_time = time.time()
    cache_key = "products:all"
    
    # 캐시 확인
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        elapsed = (time.time() - start_time) * 1000
        products = json.loads(cached_data)
        return ProductsResponse(
            source="cache",
            count=len(products),
            data=products,
            responseTimeMs=round(elapsed, 2)
        )
    
    # DB 조회
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products LIMIT 100")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 캐시 저장 (TTL 5분)
        redis_client.setex(
            cache_key,
            300,
            json.dumps(products, default=str)
        )
        
        elapsed = (time.time() - start_time) * 1000
        return ProductsResponse(
            source="database",
            count=len(products),
            data=products,
            responseTimeMs=round(elapsed, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "errorCode": "DATABASE_ERROR"}
        )


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """
    캐시 통계를 조회합니다
    
    Returns:
        CacheStatsResponse: 캐시 통계 정보
            - totalConnections (int): 총 연결 수
            - totalCommands (int): 총 명령 수
            - keyspaceHits (int): 캐시 히트 수
            - keyspaceMisses (int): 캐시 미스 수
            - hitRate (float): 캐시 히트율 (%)
    
    Raises:
        HTTPException: 500 - Redis 연결 오류
    """
    try:
        info = redis_client.info('stats')
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        total = keyspace_hits + keyspace_misses
        
        return CacheStatsResponse(
            totalConnections=info.get('total_connections_received', 0),
            totalCommands=info.get('total_commands_processed', 0),
            keyspaceHits=keyspace_hits,
            keyspaceMisses=keyspace_misses,
            hitRate=round(keyspace_hits / max(total, 1) * 100, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "errorCode": "REDIS_ERROR"}
        )


@app.post("/cache/clear", response_model=MessageResponse)
async def clear_cache():
    """
    모든 캐시를 삭제합니다
    
    Returns:
        MessageResponse: 성공 메시지
    
    Raises:
        HTTPException: 500 - Redis 연결 오류
    """
    try:
        redis_client.flushdb()
        return MessageResponse(message="Cache cleared successfully")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "errorCode": "REDIS_ERROR"}
        )


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    헬스 체크 엔드포인트
    
    Redis와 데이터베이스 연결 상태를 확인합니다.
    
    Returns:
        HealthResponse: 연결 상태
            - redis (str): 'connected' 또는 'disconnected'
            - database (str): 'connected' 또는 'disconnected'
    """
    redis_status = 'connected'
    db_status = 'connected'
    
    # Redis 연결 확인
    try:
        redis_client.ping()
    except:
        redis_status = 'disconnected'
    
    # 데이터베이스 연결 확인
    try:
        conn = get_db_connection()
        conn.close()
    except:
        db_status = 'disconnected'
    
    return HealthResponse(
        redis=redis_status,
        database=db_status
    )
