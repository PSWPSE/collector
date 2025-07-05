# 🚀 뉴스 소셜 변환기 (News to Social Converter)

> AI를 활용한 뉴스 기사 소셜미디어 최적화 서비스

## 📋 프로젝트 개요

뉴스 기사 URL을 입력하면 AI가 자동으로 소셜미디어(X/Twitter, Threads)에 최적화된 콘텐츠로 변환해주는 웹 서비스입니다.

### 🎯 주요 기능

- **🔗 URL 입력**: 뉴스 기사 링크만 입력하면 OK
- **🤖 AI 변환**: Anthropic Claude & OpenAI GPT 지원
- **🔐 API 키 관리**: 개인 API 키 안전 저장
- **📱 소셜 최적화**: X(Twitter), Threads 플랫폼 맞춤 변환
- **📄 원클릭 기능**: 복사, 다운로드, 공유 기능
- **📊 사용량 추적**: 실시간 변환 이력 및 통계
- **💰 광고 수익**: AdSense 통합 수익 모델

## 🛠️ 기술 스택

### Frontend
- **Next.js 15** (App Router)
- **TypeScript**
- **TailwindCSS** + **shadcn/ui**
- **NextAuth.js v5** (Google OAuth)

### Backend
- **Next.js API Routes**
- **PostgreSQL** + **Prisma ORM**
- **Anthropic API** + **OpenAI API**
- **Python Integration** (기존 변환 엔진)

### 배포 & 수익화
- **Vercel** 배포
- **Google AdSense** 광고
- **WordPress** 연동 지원

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/news-to-social-web.git
cd news-to-social-web
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 환경 변수 설정
```bash
cp .env.example .env.local
```

`.env.local` 파일을 열어 다음 값들을 설정하세요:

```env
# 데이터베이스
DATABASE_URL="postgresql://username:password@localhost:5432/news_to_social"

# NextAuth (Google OAuth)
NEXTAUTH_SECRET="your-secret-key"
NEXTAUTH_URL="http://localhost:3000"
GOOGLE_CLIENT_ID="your-google-oauth-client-id"
GOOGLE_CLIENT_SECRET="your-google-oauth-client-secret"

# 암호화 키
ENCRYPTION_SECRET="your-32-character-encryption-key"

# API 키 (시스템 테스트용, 선택사항)
ANTHROPIC_API_KEY="your-anthropic-api-key"
OPENAI_API_KEY="your-openai-api-key"

# AdSense
GOOGLE_ADSENSE_ID="your-adsense-id"
```

### 4. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성 후
npx prisma migrate dev
npx prisma generate
```

### 5. 개발 서버 실행
```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 확인하세요.

## 📖 사용법

### 1. Google 로그인
- 우상단 "로그인" 버튼 클릭
- Google 계정으로 인증

### 2. API 키 등록 (선택사항)
- 대시보드 → API 키 관리
- Anthropic 또는 OpenAI API 키 추가
- 키 없이도 Local 변환기 사용 가능

### 3. 뉴스 변환
- 메인 페이지에 뉴스 URL 입력
- AI 변환 버튼 클릭
- 결과를 복사/다운로드/공유

## 🔧 API 엔드포인트

### 변환 API
```http
POST /api/convert
Content-Type: application/json

{
  "url": "https://finance.yahoo.com/news/...",
  "apiKeyId": "optional-api-key-id"
}
```

### API 키 관리
```http
GET /api/api-keys        # 키 목록
POST /api/api-keys       # 키 추가
DELETE /api/api-keys?id=xxx # 키 삭제
```

## 🏗️ 프로젝트 구조

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes
│   │   ├── auth/          # NextAuth
│   │   ├── convert/       # 변환 API
│   │   └── api-keys/      # API 키 관리
│   ├── page.tsx           # 메인 페이지
│   └── layout.tsx         # Root Layout
├── components/            # React 컴포넌트
│   ├── converter/         # 변환 기능
│   ├── layout/           # 헤더/푸터
│   ├── ads/              # 광고 컴포넌트
│   └── ui/               # shadcn/ui 컴포넌트
├── lib/                  # 유틸리티
│   ├── prisma.ts         # DB 클라이언트
│   ├── auth.ts           # NextAuth 설정
│   └── crypto.ts         # 암호화 함수
└── types/                # TypeScript 타입
```

## 🎨 주요 컴포넌트

### NewsConverter
- 뉴스 URL 입력 및 변환 처리
- API 키 선택 및 설정
- 실시간 진행 상태 표시
- 결과 미리보기 및 다운로드

### API Key Manager
- 안전한 API 키 저장 (AES 암호화)
- 키 유효성 실시간 테스트
- 사용량 추적 및 관리

### AdSpace
- 반응형 광고 공간
- 개발/프로덕션 환경 분리
- AdSense 통합 지원

## 🔐 보안 기능

- **API 키 암호화**: AES-256 암호화로 안전 저장
- **세션 관리**: NextAuth.js JWT 토큰
- **입력 검증**: 서버사이드 유효성 검사
- **CORS 보호**: Next.js 내장 보안
- **환경 변수**: 민감 정보 분리 관리

## 📊 수익화 전략

### AdSense 통합
- 헤더 배너 (728×90)
- 사이드바 광고 (300×250)
- 인콘텐츠 광고 (336×280)
- 반응형 모바일 최적화

### 프리미엄 기능 (향후 계획)
- 무제한 변환
- 고급 AI 모델 사용
- 일괄 처리 기능
- 우선 지원

## 🌐 배포

### Vercel 배포
```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel --prod
```

### 환경 변수 설정
Vercel 대시보드에서 프로덕션 환경 변수를 설정하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## �� 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 글

- [Next.js](https://nextjs.org/) - React 프레임워크
- [Tailwind CSS](https://tailwindcss.com/) - CSS 프레임워크
- [shadcn/ui](https://ui.shadcn.com/) - UI 컴포넌트
- [Anthropic](https://anthropic.com/) - Claude AI API
- [OpenAI](https://openai.com/) - GPT API
- [Prisma](https://prisma.io/) - 데이터베이스 ORM

## 📞 지원 및 문의

- 📧 이메일: support@news-to-social.com
- 🐛 버그 리포트: [GitHub Issues](https://github.com/your-username/news-to-social-web/issues)
- 💬 토론: [GitHub Discussions](https://github.com/your-username/news-to-social-web/discussions)

---

**Made with ❤️ by News to Social Team** 