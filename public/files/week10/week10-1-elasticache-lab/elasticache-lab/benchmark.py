"""ElastiCache 성능 벤치마크 스크립트"""
import requests
import time
import statistics

BASE_URL = "http://localhost:5000"


def benchmark_endpoint(url, iterations=100):
    response_times = []
    for i in range(iterations):
        start = time.time()
        requests.get(url)
        elapsed = (time.time() - start) * 1000
        response_times.append(elapsed)
    return response_times


def main():
    print('성능 벤치마크 실행 중...\n')

    # 캐시 초기화
    requests.post(f"{BASE_URL}/cache/clear")
    time.sleep(1)

    # 캐시 없이 조회
    nocache_times = benchmark_endpoint(f"{BASE_URL}/user/1/nocache", 100)
    avg_nocache = statistics.mean(nocache_times)
    print(f'캐시 없이 100회 요청:')
    print(f'- 평균 응답 시간: {avg_nocache:.1f}ms')
    print(f'- 총 소요 시간: {sum(nocache_times)/1000:.2f}초\n')

    # 캐시 사용 (첫 요청으로 캐시 워밍)
    requests.post(f"{BASE_URL}/cache/clear")
    time.sleep(0.5)
    requests.get(f"{BASE_URL}/user/1")  # 캐시 워밍
    cache_times = benchmark_endpoint(f"{BASE_URL}/user/1", 100)
    avg_cache = statistics.mean(cache_times)
    print(f'캐시 사용 100회 요청:')
    print(f'- 평균 응답 시간: {avg_cache:.1f}ms')
    print(f'- 총 소요 시간: {sum(cache_times)/1000:.2f}초')

    # 캐시 통계
    stats = requests.get(f"{BASE_URL}/cache/stats").json()
    print(f'- 캐시 히트율: {stats["hitRate"]}%\n')
    print(f'성능 향상: {avg_nocache/max(avg_cache, 0.01):.1f}배')


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("오류: 애플리케이션에 연결할 수 없습니다.")
        print("먼저 uvicorn app:app --host 0.0.0.0 --port 5000 으로 서버를 실행하세요.")
