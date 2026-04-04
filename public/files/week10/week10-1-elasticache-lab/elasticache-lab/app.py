"""
AWS 실습: ElastiCache 캐싱 데모

이 FastAPI 애플리케이션은 Cache-Aside 패턴을 구현하여
ElastiCache Valkey와 DynamoDB를 연동합니다.

주요 기능:
    1. 예약 정보 조회 (캐시 우선)
    2. 캐시 통계 및 관리

환경 변수:
    REDIS_HOST (str): ElastiCache Valkey 엔드포인트
    REDIS_PORT (int): Valkey 포트 (기본값: 6379)
    DYNAMODB_TABLE (str): DynamoDB 테이블 이름
    AWS_DEFAULT_REGION (str): AWS 리전 (기본값: ap-northeast-2)

실행 방법:
    uvicorn app:app --host 0.0.0.0 --port 5000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import redis
import boto3
import json
import time
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="ElastiCache Lab API",
    description="Amazon ElastiCache for Valkey 캐싱 전략 실습 API",
    version="1.0.0"
)

# Valkey 연결 (Redis 호환 클라이언트 사용)
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True,
    socket_connect_timeout=5
)

# DynamoDB 연결
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2')
)
table = dynamodb.Table(os.getenv('DYNAMODB_TABLE', 'week10-2-elasticache-lab-APIData'))


class UserResponse(BaseModel):
    source: str
    data: Dict[str, Any]
    responseTimeMs: float


class CacheStatsResponse(BaseModel):
    totalConnections: int
    totalCommands: int
    keyspaceHits: int
    keyspaceMisses: int
    hitRate: float


class HealthResponse(BaseModel):
    redis: str
    database: str


class MessageResponse(BaseModel):
    message: str


@app.get("/")
async def index():
    return {
        "message": "ElastiCache Lab API",
        "version": "1.0.0",
        "endpoints": {
            "/user/{userId}": "Get user by ID (with cache)",
            "/user/{userId}/nocache": "Get user by ID (without cache)",
            "/cache/stats": "Get cache statistics",
            "/cache/clear": "Clear all cache",
            "/health": "Health check"
        }
    }


@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Cache-Aside 패턴으로 사용자 정보를 조회합니다."""
    start_time = time.time()
    cache_key = f"user:{user_id}"

    # 1. Valkey 캐시에서 조회 시도
    cached_data = redis_client.get(cache_key)

    if cached_data:
        elapsed = (time.time() - start_time) * 1000
        return UserResponse(
            source="cache",
            data=json.loads(cached_data),
            responseTimeMs=round(elapsed, 2)
        )

    # 2. 캐시 미스: DynamoDB에서 조회
    try:
        response = table.get_item(Key={'id': user_id})
        item = response.get('Item')

        if item:
            # 3. 조회 결과를 캐시에 저장 (TTL 1시간)
            redis_client.setex(cache_key, 3600, json.dumps(item, default=str))
            elapsed = (time.time() - start_time) * 1000
            return UserResponse(
                source="database",
                data=item,
                responseTimeMs=round(elapsed, 2)
            )
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/nocache", response_model=UserResponse)
async def get_user_nocache(user_id: str):
    """캐시 없이 DynamoDB에서 직접 조회합니다."""
    start_time = time.time()

    try:
        response = table.get_item(Key={'id': user_id})
        item = response.get('Item')
        elapsed = (time.time() - start_time) * 1000

        if item:
            return UserResponse(
                source="database",
                data=item,
                responseTimeMs=round(elapsed, 2)
            )
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats", response_model=CacheStatsResponse)
async def cache_stats():
    """캐시 통계를 조회합니다."""
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear", response_model=MessageResponse)
async def clear_cache():
    """모든 캐시를 삭제합니다."""
    try:
        redis_client.flushdb()
        return MessageResponse(message="Cache cleared successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """헬스 체크 엔드포인트."""
    redis_status = 'connected'
    db_status = 'connected'

    try:
        redis_client.ping()
    except Exception:
        redis_status = 'disconnected'

    try:
        table.table_status
    except Exception:
        db_status = 'disconnected'

    return HealthResponse(redis=redis_status, database=db_status)
