// QuickTable - CloudFront CDN Demo JavaScript (Week 10-3)

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
      second: '2-digit',
    });
    timestampElement.textContent = formattedTime;
  }

  // 콘솔에 CloudFront 정보 출력
  console.log(
    '%c QuickTable - CloudFront CDN Demo (Week 10-3) ',
    'background: #232f3e; color: #ff9900; font-size: 16px; padding: 10px;',
  );
  console.log('이 페이지는 Amazon CloudFront를 통해 전달되고 있습니다.');
  console.log('');
  console.log('Network 탭에서 다음 응답 헤더를 확인하세요:');
  console.log(
    '  x-cache       : Hit from cloudfront (캐시 히트) 또는 Miss from cloudfront (캐시 미스)',
  );
  console.log(
    '  x-amz-cf-pop  : 요청을 처리한 엣지 로케이션 (예: ICN54-C1은 서울)',
  );
  console.log('  age           : 캐시된 시간 (초 단위)');
});

// CSS 캐싱 테스트
function testCSS() {
  var resultDiv = document.getElementById('test-result');
  resultDiv.innerHTML = '<p>CSS 파일을 요청하는 중...</p>';

  var startTime = performance.now();

  fetch('style.css')
    .then(function (response) {
      var endTime = performance.now();
      var loadTime = (endTime - startTime).toFixed(2);

      resultDiv.innerHTML =
        '<p><strong>✅ CSS 로드 완료</strong></p>' +
        '<p>응답 시간: ' +
        loadTime +
        'ms</p>' +
        '<p>HTTP 상태: ' +
        response.status +
        '</p>' +
        '<p><em>💡 Network 탭에서 style.css 요청의 x-cache 헤더를 확인하세요.</em></p>' +
        '<p><em>CORS 정책으로 인해 JavaScript에서 CloudFront 응답 헤더를 직접 읽을 수 없습니다. 브라우저 개발자 도구의 Network 탭에서 확인해야 합니다.</em></p>';
    })
    .catch(function (error) {
      resultDiv.innerHTML =
        '<p><strong>❌ CSS 로드 실패</strong></p>' +
        '<p>오류: ' +
        error.message +
        '</p>';
    });
}

// JavaScript 캐싱 테스트
function testJS() {
  var resultDiv = document.getElementById('test-result');
  resultDiv.innerHTML = '<p>JavaScript 파일을 요청하는 중...</p>';

  var startTime = performance.now();

  fetch('script.js')
    .then(function (response) {
      var endTime = performance.now();
      var loadTime = (endTime - startTime).toFixed(2);

      resultDiv.innerHTML =
        '<p><strong>✅ JavaScript 로드 완료</strong></p>' +
        '<p>응답 시간: ' +
        loadTime +
        'ms</p>' +
        '<p>HTTP 상태: ' +
        response.status +
        '</p>' +
        '<p><em>💡 Network 탭에서 script.js 요청의 x-cache 헤더를 확인하세요.</em></p>' +
        '<p><em>CORS 정책으로 인해 JavaScript에서 CloudFront 응답 헤더를 직접 읽을 수 없습니다. 브라우저 개발자 도구의 Network 탭에서 확인해야 합니다.</em></p>';
    })
    .catch(function (error) {
      resultDiv.innerHTML =
        '<p><strong>❌ JavaScript 로드 실패</strong></p>' +
        '<p>오류: ' +
        error.message +
        '</p>';
    });
}

// 리소스 로딩 정보 표시 (PerformanceResourceTiming API 사용)
function showCacheInfo() {
  var resultDiv = document.getElementById('test-result');
  var resources = performance.getEntriesByType('resource');

  var html = '<p><strong>📊 리소스 로딩 정보</strong></p>';
  html +=
    '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">';
  html += '<tr style="background: #232f3e; color: white;">';
  html += '<th style="padding: 8px; text-align: left;">파일</th>';
  html += '<th style="padding: 8px; text-align: left;">로드 시간</th>';
  html += '<th style="padding: 8px; text-align: left;">전송 크기</th>';
  html += '</tr>';

  resources.forEach(function (resource) {
    var fileName = resource.name.split('/').pop().split('?')[0];
    var loadTime = resource.duration.toFixed(2);
    var size =
      resource.transferSize > 0
        ? (resource.transferSize / 1024).toFixed(2) + ' KB'
        : '(캐시)';

    if (fileName && fileName.length > 0) {
      html += '<tr style="border-bottom: 1px solid #ddd;">';
      html += '<td style="padding: 8px;">' + fileName + '</td>';
      html += '<td style="padding: 8px;">' + loadTime + 'ms</td>';
      html += '<td style="padding: 8px;">' + size + '</td>';
      html += '</tr>';
    }
  });

  html += '</table>';
  html +=
    '<p style="margin-top: 10px;"><em>💡 페이지를 새로고침하면 캐시된 리소스는 더 빠르게 로드됩니다.</em></p>';
  html +=
    '<p><em>전송 크기가 "(캐시)"로 표시되면 브라우저 캐시에서 로드된 것입니다. CloudFront 캐시 여부는 Network 탭의 x-cache 헤더로 확인하세요.</em></p>';

  resultDiv.innerHTML = html;
}
