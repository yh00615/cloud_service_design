// CloudFront Demo JavaScript - Week 10-3

// 페이지 로드 시 타임스탬프 표시
document.addEventListener('DOMContentLoaded', function () {
    const timestampElement = document.getElementById('timestamp');
    if (timestampElement) {
        const now = new Date();
        const formattedTime = now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        timestampElement.textContent = formattedTime;
    }

    // 콘솔에 CloudFront 정보 출력
    console.log('%c CloudFront Demo - Week 10-3 ', 'background: #232f3e; color: #ff9900; font-size: 16px; padding: 10px;');
    console.log('이 페이지는 CloudFront를 통해 전달되고 있습니다.');
    console.log('Network 탭에서 응답 헤더를 확인하세요:');
    console.log('- X-Cache: Hit from cloudfront (캐시됨) 또는 Miss from cloudfront (캐시 미스)');
    console.log('- X-Amz-Cf-Pop: 엣지 로케이션');
    console.log('- X-Amz-Cf-Id: CloudFront 요청 ID');
});

// 이미지 로드 테스트
function loadImage() {
    const resultDiv = document.getElementById('test-result');
    resultDiv.innerHTML = '<p>이미지를 로드하는 중...</p>';

    const img = new Image();
    const startTime = performance.now();

    img.onload = function () {
        const endTime = performance.now();
        const loadTime = (endTime - startTime).toFixed(2);

        resultDiv.innerHTML = `
            <p><strong>✅ 이미지 로드 성공</strong></p>
            <p>로드 시간: ${loadTime}ms</p>
            <p>이미지 크기: ${img.width}x${img.height}</p>
            <p>Network 탭에서 X-Cache 헤더를 확인하세요.</p>
        `;
    };

    img.onerror = function () {
        resultDiv.innerHTML = `
            <p><strong>❌ 이미지 로드 실패</strong></p>
            <p>이미지 파일이 S3 버킷에 업로드되었는지 확인하세요.</p>
        `;
    };

    // 캐시 무효화를 위해 타임스탬프 추가
    img.src = 'images/banner.jpg?' + new Date().getTime();
}

// CSS 캐싱 테스트
function loadCSS() {
    const resultDiv = document.getElementById('test-result');
    resultDiv.innerHTML = '<p>CSS 파일을 로드하는 중...</p>';

    const startTime = performance.now();

    fetch('style.css?' + new Date().getTime())
        .then(response => {
            const endTime = performance.now();
            const loadTime = (endTime - startTime).toFixed(2);

            // 응답 헤더 확인
            const cacheHeader = response.headers.get('X-Cache') || '헤더 없음';
            const cfPop = response.headers.get('X-Amz-Cf-Pop') || '헤더 없음';

            resultDiv.innerHTML = `
                <p><strong>✅ CSS 로드 성공</strong></p>
                <p>로드 시간: ${loadTime}ms</p>
                <p>파일 크기: ${(response.headers.get('content-length') / 1024).toFixed(2)} KB</p>
                <p>X-Cache: ${cacheHeader}</p>
                <p>X-Amz-Cf-Pop: ${cfPop}</p>
                <p>Network 탭에서 상세 정보를 확인하세요.</p>
            `;
        })
        .catch(error => {
            resultDiv.innerHTML = `
                <p><strong>❌ CSS 로드 실패</strong></p>
                <p>오류: ${error.message}</p>
            `;
        });
}

// JavaScript 캐싱 테스트
function loadJS() {
    const resultDiv = document.getElementById('test-result');
    resultDiv.innerHTML = '<p>JavaScript 파일을 로드하는 중...</p>';

    const startTime = performance.now();

    fetch('script.js?' + new Date().getTime())
        .then(response => {
            const endTime = performance.now();
            const loadTime = (endTime - startTime).toFixed(2);

            const cacheHeader = response.headers.get('X-Cache') || '헤더 없음';
            const cfPop = response.headers.get('X-Amz-Cf-Pop') || '헤더 없음';

            resultDiv.innerHTML = `
                <p><strong>✅ JavaScript 로드 성공</strong></p>
                <p>로드 시간: ${loadTime}ms</p>
                <p>파일 크기: ${(response.headers.get('content-length') / 1024).toFixed(2)} KB</p>
                <p>X-Cache: ${cacheHeader}</p>
                <p>X-Amz-Cf-Pop: ${cfPop}</p>
                <p>Network 탭에서 상세 정보를 확인하세요.</p>
            `;
        })
        .catch(error => {
            resultDiv.innerHTML = `
                <p><strong>❌ JavaScript 로드 실패</strong></p>
                <p>오류: ${error.message}</p>
            `;
        });
}

// 캐시 정보 표시
function showCacheInfo() {
    const resultDiv = document.getElementById('test-result');

    // Performance API를 사용하여 리소스 로딩 정보 가져오기
    const resources = performance.getEntriesByType('resource');

    let cacheInfo = '<p><strong>📊 리소스 캐시 정보</strong></p>';
    cacheInfo += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">';
    cacheInfo += '<tr style="background: #232f3e; color: white;"><th style="padding: 8px; text-align: left;">파일</th><th style="padding: 8px; text-align: left;">로드 시간</th><th style="padding: 8px; text-align: left;">크기</th></tr>';

    resources.forEach(resource => {
        const fileName = resource.name.split('/').pop().split('?')[0];
        const loadTime = (resource.duration).toFixed(2);
        const size = resource.transferSize ? (resource.transferSize / 1024).toFixed(2) + ' KB' : 'N/A';

        if (fileName && !fileName.includes('localhost')) {
            cacheInfo += `<tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;">${fileName}</td>
                <td style="padding: 8px;">${loadTime}ms</td>
                <td style="padding: 8px;">${size}</td>
            </tr>`;
        }
    });

    cacheInfo += '</table>';
    cacheInfo += '<p style="margin-top: 10px;"><em>💡 팁: 페이지를 새로고침하면 캐시된 리소스는 더 빠르게 로드됩니다.</em></p>';

    resultDiv.innerHTML = cacheInfo;
}

// 페이지 성능 측정
window.addEventListener('load', function () {
    const perfData = performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;

    console.log('%c 페이지 성능 정보 ', 'background: #ff9900; color: white; font-size: 14px; padding: 5px;');
    console.log('페이지 로드 시간:', pageLoadTime + 'ms');
    console.log('DNS 조회 시간:', (perfData.domainLookupEnd - perfData.domainLookupStart) + 'ms');
    console.log('서버 응답 시간:', (perfData.responseEnd - perfData.requestStart) + 'ms');
    console.log('DOM 처리 시간:', (perfData.domComplete - perfData.domLoading) + 'ms');
});

// CloudFront 헤더 확인 함수
async function checkCloudFrontHeaders() {
    try {
        const response = await fetch(window.location.href, { method: 'HEAD' });
        const headers = {};

        response.headers.forEach((value, key) => {
            if (key.toLowerCase().includes('x-cache') ||
                key.toLowerCase().includes('x-amz-cf') ||
                key.toLowerCase().includes('cloudfront')) {
                headers[key] = value;
            }
        });

        console.log('%c CloudFront 헤더 ', 'background: #0073bb; color: white; font-size: 14px; padding: 5px;');
        console.table(headers);
    } catch (error) {
        console.error('헤더 확인 실패:', error);
    }
}

// 페이지 로드 후 CloudFront 헤더 확인
setTimeout(checkCloudFrontHeaders, 1000);
