# News to Social Web Service

뉴스 기사를 소셜 미디어용 콘텐츠로 변환하는 웹 서비스입니다. OpenAI와 Anthropic API를 지원하며, 애드센스 최적화 디자인으로 수익화를 지원합니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **AI 기반 콘텐츠 변환**: OpenAI GPT-4 및 Anthropic Claude를 이용한 고품질 콘텐츠 생성
- **다중 API 지원**: OpenAI와 Anthropic API 동시 지원으로 안정성 확보
- **실시간 변환**: 60초 내 빠른 콘텐츠 생성
- **클립보드 복사**: 원클릭 복사 기능으로 편리한 사용

### 🎨 디자인 최적화
- **애드센스 최적화**: 전략적 광고 배치로 수익 극대화
- **반응형 디자인**: 모든 디바이스에서 최적화된 사용자 경험
- **공간 효율성**: 컴팩트한 레이아웃으로 콘텐츠 집중도 향상
- **모바일 최적화**: 모바일 사용자를 위한 특별한 UI/UX

### 💰 수익화 기능
- **전략적 광고 배치**: 
  - 상단 배너 (728x90)
  - 사이드바 광고 (300x250)
  - 본문 내 광고 (336x280)
  - 하단 배너 (728x90)
  - 모바일 앵커 광고 (320x50)
- **사용자 경험 보존**: 광고가 사용자 경험을 방해하지 않도록 설계

## 🚀 기술 스택

### Frontend
- **Next.js 15**: React 기반 풀스택 프레임워크
- **TypeScript**: 타입 안전성 확보
- **Tailwind CSS**: 유틸리티 기반 스타일링
- **React Hooks**: 상태 관리 및 사이드 이펙트 처리

### Backend API 연동
- **FastAPI**: Python 기반 고성능 API 서버
- **RESTful API**: 표준 HTTP 메서드 사용
- **실시간 상태 추적**: 변환 진행 상태 실시간 모니터링

### AI 서비스
- **OpenAI GPT-4**: 자연어 처리 및 콘텐츠 생성
- **Anthropic Claude**: 대안 AI 서비스 지원

## 📱 사용자 인터페이스

### 레이아웃 구조
```
[상단 배너 광고]
[헤더 + API 키 설정]
[사이드바] [입력 섹션] [결과 섹션]
[광고]   [본문 내 광고]  [출력 영역]
[하단 배너 광고]
[모바일 앵커 광고 - 모바일 전용]
```

### 주요 개선사항
1. **URL 입력 개선**:
   - 클릭 시 전체 텍스트 자동 선택
   - 원클릭 클리어 버튼
   - 실시간 URL 유효성 검사

2. **공간 효율성**:
   - 컴팩트한 컴포넌트 디자인
   - 더 작은 패딩과 마진
   - 중요 정보 우선 배치

3. **애드센스 최적화**:
   - 업계 권장사항 적용
   - 30% 이하 광고 밀도 유지
   - 사용자 경험 저해 방지

## 🛠️ 설치 및 실행

### 전제조건
- Node.js 18+ 
- npm 또는 yarn
- OpenAI 또는 Anthropic API 키

### 설치
```bash
# 의존성 설치
npm install

# 또는
yarn install
```

### 환경 설정
`.env.local` 파일을 생성하고 다음 내용을 추가:
```env
# API 키들은 사용자가 직접 입력하므로 여기서는 필요 없음
# 다만 개발용으로 설정할 수 있음
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 개발 서버 실행
```bash
npm run dev
# 또는
yarn dev
```

브라우저에서 `http://localhost:3001`로 접속

## 🎯 사용법

### 1. API 키 설정
1. "API 키 설정" 버튼 클릭
2. OpenAI 또는 Anthropic 선택
3. API 키 입력 후 "확인" 클릭
4. 녹색 표시로 연결 확인

### 2. 콘텐츠 생성
1. 뉴스 기사 URL 입력
2. "콘텐츠 생성" 버튼 클릭
3. AI 처리 대기 (최대 60초)
4. 생성된 콘텐츠 확인

### 3. 결과 활용
1. "복사" 버튼으로 클립보드에 복사
2. 소셜 미디어 플랫폼에 붙여넣기
3. 필요시 추가 편집

## 🎨 광고 컴포넌트

### AdSenseUnit 컴포넌트
재사용 가능한 애드센스 광고 컴포넌트:

```typescript
<AdSenseUnit 
  slot="ad-slot-id"
  size="banner" // 'banner' | 'rectangle' | 'leaderboard' | 'mobile-banner' | 'sidebar' | 'in-content'
  isPreview={true} // 개발 모드에서 플레이스홀더 표시
  className="custom-styles"
/>
```

### MobileAnchorAd 컴포넌트
모바일 전용 앵커 광고:

```typescript
<MobileAnchorAd 
  slot="mobile-anchor-slot"
  isPreview={true}
/>
```

## 📊 애드센스 최적화 가이드

### 권장 광고 크기
- **리더보드**: 728x90 (상단/하단)
- **중형 사각형**: 300x250 (사이드바)
- **대형 사각형**: 336x280 (본문 내)
- **모바일 배너**: 320x50 (모바일 앵커)

### 배치 전략
1. **Above the Fold**: 스크롤 없이 보이는 영역에 최소 1개 광고
2. **본문 내 배치**: 콘텐츠와 자연스럽게 통합
3. **사이드바 활용**: 데스크톱에서 지속적 노출
4. **모바일 앵커**: 모바일 사용자 대상 고정 광고

### 성능 최적화
- 광고 밀도 30% 미만 유지
- 페이지 로딩 속도 최적화
- 사용자 경험 우선 고려
- A/B 테스트를 통한 지속적 개선

## 🔧 개발자 가이드

### 프로젝트 구조
```
src/
├── app/                 # Next.js App Router
│   ├── page.tsx        # 메인 페이지
│   ├── layout.tsx      # 레이아웃
│   └── globals.css     # 글로벌 스타일
├── components/         # 재사용 컴포넌트
│   └── ads/           # 광고 관련 컴포넌트
│       ├── AdSenseUnit.tsx
│       └── MobileAnchorAd.tsx
└── lib/               # 유틸리티
    └── hooks/         # 커스텀 훅
        └── useResponsive.ts
```

### 반응형 훅 사용
```typescript
import { useResponsive } from '@/lib/hooks/useResponsive';

function Component() {
  const { isMobile, isDesktop, breakpoint } = useResponsive();
  
  return (
    <div>
      {isMobile ? <MobileView /> : <DesktopView />}
    </div>
  );
}
```

## 🚀 배포

### Vercel 배포 (권장)
1. GitHub에 코드 푸시
2. Vercel에서 프로젝트 임포트
3. 자동 배포 설정
4. 환경 변수 설정

### 기타 플랫폼
- Netlify
- AWS Amplify
- Google Cloud Platform

## 📈 성능 모니터링

### 핵심 지표
- **페이지 로딩 시간**: 2초 이하 목표
- **모바일 성능 점수**: 90점 이상
- **접근성 점수**: 95점 이상
- **광고 뷰어빌리티**: 70% 이상

### 도구
- Google PageSpeed Insights
- Google Analytics
- AdSense 성능 보고서
- Web Vitals

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 감사의 말

- OpenAI 및 Anthropic의 뛰어난 AI 서비스
- Next.js와 React 커뮤니티
- Tailwind CSS 팀
- Google AdSense 최적화 가이드라인

---

**Made with ❤️ for content creators and publishers**
