import requests
import time
import statistics

BASE_URL = "http://localhost:5000"

def benchmark_endpoint(url, iterations=100):
    """엔드포인트 성능 측정"""
    response_times = []
    
    print(f"\n테스트 중: {url}")
    print(f"반복 횟수: {iterations}")
    
    for i in range(iterations):
        start = time.time()
        response = requests.get(url)
        elapsed = (time.time() - start) * 1000
        response_times.append(elapsed)
        
        if (i + 1) % 10 == 0:
            print(f"  진행: {i + 1}/{iterations}")
    
    return response_times

def print_stats(name, times):
    """통계 출력"""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    print(f"평균 응답 시간: {statistics.mean(times):.2f} ms")
    print(f"중앙값: {statistics.median(times):.2f} ms")
    print(f"최소값: {min(times):.2f} ms")
    print(f"최대값: {max(times):.2f} ms")
    print(f"표준편차: {statistics.stdev(times):.2f} ms")

def main():
    print("ElastiCache 성능 벤치마크")
    print("="*60)
    
    # 캐시 초기화
    print("\n캐시 초기화 중...")
    requests.post(f"{BASE_URL}/cache/clear")
    time.sleep(1)
    
    # 1. 캐시 없이 조회 (첫 번째)
    print("\n[테스트 1] 캐시 없이 DB 조회")
    nocache_times = benchmark_endpoint(f"{BASE_URL}/user/1/nocache", 50)
    print_stats("캐시 미사용", nocache_times)
    
    # 2. 캐시 적용 - 첫 번째 요청 (Cache Miss)
    print("\n[테스트 2] 캐시 적용 - 첫 번째 요청 (Cache Miss)")
    requests.post(f"{BASE_URL}/cache/clear")
    time.sleep(1)
    first_request = requests.get(f"{BASE_URL}/user/1")
    print(f"첫 번째 요청 (Cache Miss): {first_request.json()['response_time_ms']:.2f} ms")
    
    # 3. 캐시 적용 - 이후 요청 (Cache Hit)
    print("\n[테스트 3] 캐시 적용 - 이후 요청 (Cache Hit)")
    cache_times = benchmark_endpoint(f"{BASE_URL}/user/1", 50)
    print_stats("캐시 사용", cache_times)
    
    # 4. 성능 비교
    print("\n" + "="*60)
    print("성능 비교 결과")
    print("="*60)
    avg_nocache = statistics.mean(nocache_times)
    avg_cache = statistics.mean(cache_times)
    improvement = ((avg_nocache - avg_cache) / avg_nocache) * 100
    
    print(f"캐시 미사용 평균: {avg_nocache:.2f} ms")
    print(f"캐시 사용 평균: {avg_cache:.2f} ms")
    print(f"성능 향상: {improvement:.1f}%")
    print(f"속도 배수: {avg_nocache / avg_cache:.1f}x 빠름")
    
    # 5. 캐시 통계
    print("\n[캐시 통계]")
    stats = requests.get(f"{BASE_URL}/cache/stats").json()
    print(f"캐시 히트: {stats['keyspace_hits']}")
    print(f"캐시 미스: {stats['keyspace_misses']}")
    print(f"캐시 히트율: {stats['hit_rate']:.2f}%")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n오류: 애플리케이션에 연결할 수 없습니다.")
        print("먼저 'python app.py'로 서버를 실행하세요.")
    except Exception as e:
        print(f"\n오류 발생: {e}")
