// 사이트 기본 설정 - 과정명, 학기, 교수 정보 등을 여기서 수정하세요

export const siteConfig = {
    // 대학교명
    university: '한양대학교',
    // 과정명
    courseName: '클라우드 서비스 설계',
    // 학기 정보
    semester: '2026학년도 1학기',
    // 교수명
    professor: '오주현',
    // 영문 과정명 (홈 배지용)
    courseNameEn: 'Cloud Service Design',
    // 과정 설명
    courseDescription: '15주 커리큘럼으로 배우는 AWS 클라우드 서비스 설계 및 구축',

    // 학점·시수
    credits: '3학점 / 3시수',
    // 교과구분
    courseCategory: '전공선택',
    // 평가유형
    evaluationType: '상대평가',

    // 교과목개요
    courseOverview:
        '본 교육과정은 클라우드 플랫폼의 핵심 서비스와 아키텍처를 체계적으로 학습하는 실무 중심의 교육과정이며, 클라우드 인프라 구축부터 보안, 데이터베이스, 모니터링까지 AWS의 주요 서비스들을 단계적으로 배우고, 실제 운영 환경에서 필요한 클라우드 솔루션 설계 및 구현 능력을 배양한다.',

    // 수업목표
    courseObjectives: [
        '클라우드 플랫폼의 핵심 아키텍처와 서비스 모델에 대한 이해를 바탕으로, 컴퓨팅·스토리지·네트워크·데이터베이스 등 주요 인프라 서비스의 구성과 활용 역량을 갖춘다.',
        'IAM 기반의 접근 제어 및 보안 정책에 대한 실무 능력을 함양한다.',
        '모니터링과 비용 최적화 관점에서 클라우드 운영 전략을 기획한다.',
        '실무 프로젝트를 통해 종합적인 클라우드 솔루션을 구현할 수 있는 역량을 기른다.',
    ],

    // 홈 페이지 피처 아이콘
    homeFeatures: [
        { icon: '☁️', text: '서비스 설계' },
        { icon: '🔬', text: '실전 프로젝트' },
        { icon: '🚀', text: '클라우드 전문가' },
    ],
} as const;

// 조합된 문자열 헬퍼
export const siteTitle = `${siteConfig.university} ${siteConfig.courseName}`;
export const semesterInfo = `${siteConfig.semester} · ${siteConfig.professor} 교수님`;
export const copyright = `© ${new Date().getFullYear()} ${siteTitle}`;
