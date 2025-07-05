# ⚡ **NewsForge Pro 즉시 배포 가이드**

## 🎯 **2시간 내 완료 목표**

### **Step 1: Railway 배포 (Backend) - 30분**

1. **Railway 회원가입**
   - https://railway.app 접속
   - GitHub로 로그인

2. **프로젝트 생성**
   ```
   1. "New Project" 클릭
   2. "Deploy from GitHub repo" 선택
   3. PSWPSE/collector 선택
   4. "Deploy Now" 클릭
   ```

3. **서비스 설정**
   ```
   Root Directory: newsforge-pro/backend
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **환경 변수 설정**
   ```bash
   # Settings → Variables 탭에서 추가
   OPENAI_API_KEY=sk-your-openai-key-here
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
   DATABASE_URL=postgresql://railway-provided-url
   CORS_ORIGINS=*.vercel.app
   PORT=8000
   ```

5. **배포 확인**
   - 생성된 URL (예: `https://newsforge-api-xxx.up.railway.app`)
   - 헬스 체크: `https://your-url/api/v1/health`

### **Step 2: Vercel 배포 (Frontend) - 20분**

1. **Vercel 회원가입**
   - https://vercel.com 접속
   - GitHub로 로그인

2. **프로젝트 가져오기**
   ```
   1. "New Project" 클릭
   2. PSWPSE/collector 리포지토리 선택
   3. "Import" 클릭
   ```

3. **빌드 설정**
   ```
   Framework Preset: Next.js
   Root Directory: news-to-social-web
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **환경 변수 설정**
   ```bash
   # Settings → Environment Variables에서 추가
   NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
   ```

5. **배포 완료**
   - 생성된 URL (예: `https://newsforge-pro.vercel.app`)
   - 즉시 접근 가능!

### **Step 3: 도메인 연결 (선택사항) - 10분**

1. **커스텀 도메인 구매**
   - Namecheap, GoDaddy 등에서 구매
   - 예: `newsforge.com`

2. **Vercel 도메인 설정**
   ```
   1. Vercel 프로젝트 → Settings → Domains
   2. 구매한 도메인 입력
   3. DNS 설정 지침 따라하기
   ```

3. **SSL 인증서**
   - Vercel이 자동으로 Let's Encrypt SSL 설정
   - HTTPS 자동 적용

## 🔧 **배포 후 최적화**

### **데이터베이스 설정**
```sql
-- Railway PostgreSQL에서 실행
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    plan_type VARCHAR(20) DEFAULT 'free',
    daily_limit INTEGER DEFAULT 5
);

CREATE TABLE conversions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    source_url TEXT NOT NULL,
    generated_content TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversions_user_id ON conversions(user_id);
CREATE INDEX idx_conversions_created_at ON conversions(created_at);
```

### **모니터링 설정**
```python
# Railway에서 자동으로 제공하는 메트릭
- CPU 사용률
- 메모리 사용률
- 네트워크 트래픽
- 응답 시간
```

### **알림 설정**
```yaml
# Railway Dashboard에서 설정
Alert_Rules:
  - CPU > 80% for 5 minutes
  - Memory > 85% for 5 minutes
  - Error rate > 5% for 2 minutes
  - Response time > 3 seconds
```

## 📊 **예상 성능**

### **Railway (Backend)**
```yaml
Resources:
  CPU: 1 vCPU
  Memory: 512MB - 1GB
  Storage: 5GB SSD
  
Performance:
  Response Time: < 500ms
  Concurrent Users: 100+
  Daily Requests: 10,000+
```

### **Vercel (Frontend)**
```yaml
Features:
  Global CDN: 전 세계 배포
  Edge Functions: 최적화된 성능
  Automatic Scaling: 무제한 확장
  
Performance:
  Page Load: < 1 second
  Global Latency: < 100ms
  Concurrent Users: 무제한
```

## 💰 **비용 계산**

### **무료 시작 (테스트용)**
```yaml
Railway: $0/월 (500시간 무료)
Vercel: $0/월 (Hobby 플랜)
총 비용: $0/월 (제한적 사용)
```

### **상용 서비스**
```yaml
Railway: $10/월 (Developer)
Vercel: $20/월 (Pro)
도메인: $10-15/년
총 비용: $30-35/월
```

### **고트래픽 서비스**
```yaml
Railway: $50/월 (Team)
Vercel: $50/월 (Team)
PostgreSQL: $25/월 (확장된 DB)
총 비용: $125/월
```

## 🚀 **배포 체크리스트**

### **배포 전**
- [ ] GitHub 리포지토리 최신 상태
- [ ] OpenAI API 키 준비
- [ ] Anthropic API 키 준비 (선택)
- [ ] Railway 계정 생성
- [ ] Vercel 계정 생성

### **배포 중**
- [ ] Railway 프로젝트 생성
- [ ] 환경 변수 설정
- [ ] 백엔드 배포 확인
- [ ] Vercel 프로젝트 생성
- [ ] 프론트엔드 배포 확인
- [ ] API 연결 테스트

### **배포 후**
- [ ] 헬스 체크 확인
- [ ] 뉴스 변환 기능 테스트
- [ ] 성능 모니터링 설정
- [ ] 도메인 연결 (선택)
- [ ] SSL 인증서 확인

## 🎯 **성공 지표**

### **기술적 목표**
- API 응답 시간: < 3초
- 웹사이트 로딩: < 2초
- 가용성: 99.9%
- 에러율: < 1%

### **비즈니스 목표**
- 동시 사용자: 100명+
- 일일 변환: 1,000회+
- 사용자 만족도: 4.5/5
- 월 사용자 증가율: 20%

---

**🎉 이 가이드를 따르면 2시간 내에 24/7 접근 가능한 상용 서비스가 완성됩니다!**

**PC가 꺼져도 전 세계 어디서나 서비스를 이용할 수 있게 됩니다! 🌐** 