# 📋 NewsForge Pro - 상용서비스 구현 계획

## 🎯 **즉시 실행 계획 (8주 완성)**

### **Phase 1: 프로덕션 환경 구축 (Week 1-2)**

#### 1.1 새로운 프로젝트 구조 생성
```bash
# 현재 디렉토리 백업
mv collector collector-prototype-backup
mkdir newsforge-pro
cd newsforge-pro

# 프로덕션 구조 생성
mkdir -p {backend/{app/{api,core,models,schemas,services},tests},frontend/wordpress-theme,infrastructure/{docker,k8s},docs}
```

#### 1.2 FastAPI 백엔드 핵심 서비스
```python
# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import asyncio
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine

app = FastAPI(
    title="NewsForge Pro API",
    description="News to Social Content Converter",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://newsforge.pro", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 핵심 의존성
security = HTTPBearer()
redis_client = redis.from_url("redis://localhost:6379")
database_url = "postgresql+asyncpg://user:pass@localhost/newsforge"
engine = create_async_engine(database_url)

# 핵심 서비스 임포트
from .services.converter_service import NewsConverterService
from .services.user_service import UserService
from .services.billing_service import BillingService

# 서비스 초기화
converter_service = NewsConverterService(redis_client)
user_service = UserService(engine)
billing_service = BillingService()

@app.post("/api/v1/convert")
async def convert_news(
    request: ConversionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """뉴스 기사를 소셜 콘텐츠로 변환"""
    
    # 사용량 확인
    if not await user_service.check_usage_limit(current_user["id"]):
        raise HTTPException(
            status_code=429,
            detail="Usage limit exceeded. Upgrade to premium for unlimited access."
        )
    
    # 백그라운드에서 변환 처리
    task_id = await converter_service.convert_async(
        url=request.url,
        user_id=current_user["id"],
        platforms=request.platforms
    )
    
    # 사용량 증가
    background_tasks.add_task(
        user_service.increment_usage,
        current_user["id"]
    )
    
    return {"success": True, "task_id": task_id}

@app.get("/api/v1/conversion/{task_id}")
async def get_conversion_result(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """변환 결과 조회"""
    result = await converter_service.get_result(task_id, current_user["id"])
    return result

@app.post("/api/v1/subscribe")
async def create_subscription(
    plan: str,
    current_user: dict = Depends(get_current_user)
):
    """프리미엄 구독 생성"""
    checkout_session = await billing_service.create_checkout_session(
        user_id=current_user["id"],
        plan=plan
    )
    return {"checkout_url": checkout_session.url}
```

#### 1.3 WordPress 테마 기본 구조
```php
<?php
// frontend/wordpress-theme/functions.php

// AdSense 최적화 설정
function newsforge_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    
    // Google AdSense 자동 광고
    add_action('wp_head', 'newsforge_adsense_head');
    
    // React 컴포넌트 로드
    add_action('wp_enqueue_scripts', 'newsforge_enqueue_assets');
}
add_action('after_setup_theme', 'newsforge_setup');

function newsforge_adsense_head() {
    if (!is_user_premium()) {
        echo '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-YOUR-ID" crossorigin="anonymous"></script>';
    }
}

function newsforge_enqueue_assets() {
    wp_enqueue_script(
        'newsforge-converter',
        get_template_directory_uri() . '/assets/js/converter-app.js',
        ['wp-element'],
        '1.0.0',
        true
    );
    
    wp_localize_script('newsforge-converter', 'newsforge_ajax', [
        'ajax_url' => admin_url('admin-ajax.php'),
        'api_url' => 'https://api.newsforge.pro',
        'nonce' => wp_create_nonce('newsforge_nonce'),
        'user_plan' => get_user_plan_type()
    ]);
}

// 사용자 플랜 확인
function get_user_plan_type() {
    if (!is_user_logged_in()) return 'free';
    
    $user_id = get_current_user_id();
    $plan = get_user_meta($user_id, 'subscription_plan', true);
    
    return $plan ?: 'free';
}

function is_user_premium() {
    return get_user_plan_type() !== 'free';
}

// 메인 변환 페이지 숏코드
function newsforge_converter_shortcode($atts) {
    ob_start();
    ?>
    <div id="newsforge-converter-app" class="newsforge-converter">
        <div class="converter-container">
            <h2>뉴스를 소셜 콘텐츠로 변환하세요</h2>
            
            <!-- 광고 영역 (무료 사용자만) -->
            <?php if (!is_user_premium()) : ?>
                <div class="ad-banner">
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-YOUR-ID"
                         data-ad-slot="YOUR-SLOT-ID"
                         data-ad-format="auto"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            <?php endif; ?>
            
            <!-- React 컴포넌트가 여기에 렌더링됩니다 -->
            <div id="converter-interface"></div>
            
            <!-- 사이드바 광고 -->
            <?php if (!is_user_premium()) : ?>
                <div class="ad-sidebar">
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-YOUR-ID"
                         data-ad-slot="YOUR-SIDEBAR-SLOT-ID"
                         data-ad-format="rectangle"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>
            <?php endif; ?>
        </div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('newsforge_converter', 'newsforge_converter_shortcode');
?>
```

### **Phase 2: 핵심 기능 구현 (Week 3-4)**

#### 2.1 고성능 변환 서비스
```python
# backend/app/services/converter_service.py
from celery import Celery
import asyncio
from typing import Dict, List, Optional
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

celery_app = Celery('newsforge', broker='redis://localhost:6379')

class NewsConverterService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def convert_async(self, url: str, user_id: int, platforms: List[str]) -> str:
        """비동기 변환 작업 시작"""
        
        task_id = f"convert_{user_id}_{int(time.time())}"
        
        # Redis에 작업 상태 저장
        await self.redis.setex(
            f"task:{task_id}",
            3600,  # 1시간
            json.dumps({
                "status": "pending",
                "url": url,
                "platforms": platforms,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            })
        )
        
        # Celery 작업 큐에 추가
        convert_task.delay(task_id, url, user_id, platforms)
        
        return task_id
    
    async def get_result(self, task_id: str, user_id: int) -> Dict:
        """변환 결과 조회"""
        
        task_data = await self.redis.get(f"task:{task_id}")
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_info = json.loads(task_data)
        
        # 사용자 권한 확인
        if task_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return task_info

@celery_app.task
def convert_task(task_id: str, url: str, user_id: int, platforms: List[str]):
    """Celery 백그라운드 작업"""
    
    try:
        # 작업 시작 상태 업데이트
        update_task_status(task_id, "processing", {"step": "extracting"})
        
        # 1. 뉴스 추출
        extractor = NewsExtractor()
        article_data = extractor.extract(url)
        
        if not article_data["success"]:
            raise Exception(f"Extraction failed: {article_data['error']}")
        
        update_task_status(task_id, "processing", {"step": "converting"})
        
        # 2. AI 변환
        converter = AIConverter()
        results = {}
        
        for platform in platforms:
            content = converter.convert_for_platform(
                article_data["content"],
                platform
            )
            results[platform] = content
        
        # 3. 결과 저장
        final_result = {
            "status": "completed",
            "url": url,
            "original_title": article_data["title"],
            "converted_content": results,
            "platforms": platforms,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        update_task_status(task_id, "completed", final_result)
        
        # 4. 사용량 로깅
        log_conversion_usage(user_id, url, platforms, True)
        
    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }
        
        update_task_status(task_id, "failed", error_result)
        log_conversion_usage(user_id, url, platforms, False, str(e))

def update_task_status(task_id: str, status: str, data: Dict):
    """작업 상태 업데이트"""
    redis_client = redis.from_url("redis://localhost:6379")
    
    current_data = redis_client.get(f"task:{task_id}")
    if current_data:
        task_info = json.loads(current_data)
        task_info.update(data)
        task_info["status"] = status
        
        redis_client.setex(
            f"task:{task_id}",
            3600,
            json.dumps(task_info)
        )
```

#### 2.2 React 변환 인터페이스
```jsx
// frontend/wordpress-theme/assets/js/components/ConverterApp.jsx
import React, { useState, useEffect } from 'react';

const ConverterApp = () => {
    const [url, setUrl] = useState('');
    const [platforms, setPlatforms] = useState(['twitter']);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [taskId, setTaskId] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!url.trim()) {
            setError('URL을 입력해주세요.');
            return;
        }
        
        setLoading(true);
        setError(null);
        setResult(null);
        
        try {
            const response = await fetch(`${newsforge_ajax.api_url}/api/v1/convert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({
                    url: url,
                    platforms: platforms
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Conversion failed');
            }
            
            const data = await response.json();
            setTaskId(data.task_id);
            
            // 결과 폴링 시작
            pollForResult(data.task_id);
            
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };
    
    const pollForResult = async (taskId) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(
                    `${newsforge_ajax.api_url}/api/v1/conversion/${taskId}`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                    }
                );
                
                const data = await response.json();
                
                if (data.status === 'completed') {
                    setResult(data);
                    setLoading(false);
                    clearInterval(pollInterval);
                    
                    // Google Analytics 이벤트
                    gtag('event', 'conversion_completed', {
                        'event_category': 'converter',
                        'event_label': platforms.join(','),
                        'value': 1
                    });
                    
                } else if (data.status === 'failed') {
                    setError(data.error || 'Conversion failed');
                    setLoading(false);
                    clearInterval(pollInterval);
                }
                
            } catch (err) {
                setError('결과를 가져오는 중 오류가 발생했습니다.');
                setLoading(false);
                clearInterval(pollInterval);
            }
        }, 2000); // 2초마다 확인
        
        // 5분 후 타임아웃
        setTimeout(() => {
            clearInterval(pollInterval);
            if (loading) {
                setError('변환 시간이 초과되었습니다. 다시 시도해주세요.');
                setLoading(false);
            }
        }, 300000);
    };
    
    const copyToClipboard = async (content) => {
        try {
            await navigator.clipboard.writeText(content);
            alert('클립보드에 복사되었습니다!');
            
            // 복사 이벤트 추적
            gtag('event', 'content_copied', {
                'event_category': 'engagement',
                'event_label': 'clipboard',
                'value': 1
            });
            
        } catch (err) {
            // 폴백: 텍스트 선택
            const textArea = document.createElement('textarea');
            textArea.value = content;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('클립보드에 복사되었습니다!');
        }
    };
    
    return (
        <div className="newsforge-converter-app">
            <form onSubmit={handleSubmit} className="converter-form">
                <div className="form-group">
                    <label htmlFor="url-input">뉴스 기사 URL</label>
                    <input
                        id="url-input"
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com/news-article"
                        className="url-input"
                        disabled={loading}
                    />
                </div>
                
                <div className="form-group">
                    <label>변환할 플랫폼</label>
                    <div className="platform-checkboxes">
                        {['twitter', 'threads', 'linkedin', 'instagram'].map(platform => (
                            <label key={platform} className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={platforms.includes(platform)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setPlatforms([...platforms, platform]);
                                        } else {
                                            setPlatforms(platforms.filter(p => p !== platform));
                                        }
                                    }}
                                    disabled={loading}
                                />
                                {platform.charAt(0).toUpperCase() + platform.slice(1)}
                            </label>
                        ))}
                    </div>
                </div>
                
                <button 
                    type="submit" 
                    className="convert-button"
                    disabled={loading || !url.trim()}
                >
                    {loading ? '변환 중...' : '변환하기'}
                </button>
            </form>
            
            {loading && (
                <div className="loading-section">
                    <div className="spinner"></div>
                    <p>뉴스 기사를 분석하고 소셜 콘텐츠로 변환하고 있습니다...</p>
                </div>
            )}
            
            {error && (
                <div className="error-section">
                    <p>❌ {error}</p>
                </div>
            )}
            
            {result && (
                <div className="result-section">
                    <h3>✅ 변환 완료!</h3>
                    <div className="original-info">
                        <h4>원본 기사: {result.original_title}</h4>
                    </div>
                    
                    {Object.entries(result.converted_content).map(([platform, content]) => (
                        <div key={platform} className="platform-result">
                            <div className="platform-header">
                                <h4>{platform.charAt(0).toUpperCase() + platform.slice(1)}</h4>
                                <button 
                                    onClick={() => copyToClipboard(content)}
                                    className="copy-button"
                                >
                                    📋 복사
                                </button>
                            </div>
                            <div className="content-preview">
                                <pre>{content}</pre>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// WordPress에 마운트
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('converter-interface');
    if (container) {
        ReactDOM.render(<ConverterApp />, container);
    }
});
```

### **Phase 3: 수익화 시스템 (Week 5-6)**

#### 3.1 Stripe 결제 연동
```python
# backend/app/services/billing_service.py
import stripe
from typing import Dict, Optional

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    def __init__(self):
        self.plans = {
            "premium": {
                "price_id": "price_xxx",  # Stripe Price ID
                "amount": 999,  # $9.99
                "features": ["unlimited_conversions", "no_ads", "priority_support"]
            },
            "enterprise": {
                "price_id": "price_yyy",
                "amount": 9999,  # $99.99
                "features": ["api_access", "white_label", "custom_integration"]
            }
        }
    
    async def create_checkout_session(self, user_id: int, plan: str) -> stripe.checkout.Session:
        """Stripe 결제 세션 생성"""
        
        if plan not in self.plans:
            raise ValueError(f"Invalid plan: {plan}")
        
        plan_info = self.plans[plan]
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan_info["price_id"],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"https://newsforge.pro/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://newsforge.pro/pricing",
            metadata={
                'user_id': str(user_id),
                'plan': plan
            }
        )
        
        return session
    
    async def handle_webhook(self, event: Dict) -> bool:
        """Stripe 웹훅 처리"""
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # 사용자 구독 활성화
            user_id = int(session['metadata']['user_id'])
            plan = session['metadata']['plan']
            
            await self.activate_subscription(user_id, plan)
            
        elif event['type'] == 'customer.subscription.deleted':
            # 구독 취소 처리
            subscription = event['data']['object']
            await self.deactivate_subscription(subscription)
        
        return True
    
    async def activate_subscription(self, user_id: int, plan: str):
        """구독 활성화"""
        # 데이터베이스 업데이트
        # 이메일 알림 발송
        pass
```

#### 3.2 AdSense 최적화
```css
/* frontend/wordpress-theme/assets/css/adsense-optimization.css */

/* AdSense 광고 최적화 스타일 */
.ad-container {
    margin: 2rem 0;
    text-align: center;
    position: relative;
}

.ad-container::before {
    content: "광고";
    display: block;
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 0.5rem;
}

/* 상단 배너 광고 */
.ad-banner {
    max-width: 728px;
    height: 90px;
    margin: 1rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 사이드바 광고 */
.ad-sidebar {
    width: 300px;
    height: 250px;
    margin: 1rem 0;
    position: sticky;
    top: 20px;
}

/* 콘텐츠 내 광고 */
.ad-in-content {
    max-width: 336px;
    height: 280px;
    margin: 2rem auto;
    float: right;
    margin-left: 1rem;
}

/* 모바일 광고 */
@media (max-width: 768px) {
    .ad-banner {
        max-width: 320px;
        height: 50px;
    }
    
    .ad-sidebar {
        width: 100%;
        height: 250px;
        position: static;
    }
    
    .ad-in-content {
        float: none;
        margin: 1rem auto;
    }
}

/* 프리미엄 사용자는 광고 숨김 */
.premium-user .ad-container,
.premium-user .ad-banner,
.premium-user .ad-sidebar,
.premium-user .ad-in-content {
    display: none !important;
}

/* 광고 로딩 애니메이션 */
.ad-loading {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### **Phase 4: 운영 및 최적화 (Week 7-8)**

#### 4.1 Docker 배포 설정
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx:/etc/nginx
      - ./ssl:/etc/ssl
    depends_on:
      - wordpress
      - api-gateway

  wordpress:
    image: wordpress:6.4-php8.2-apache
    environment:
      WORDPRESS_DB_HOST: postgres:5432
      WORDPRESS_DB_NAME: newsforge_wp
      WORDPRESS_DB_USER: ${DB_USER}
      WORDPRESS_DB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./frontend/wordpress-theme:/var/www/html/wp-content/themes/newsforge-pro
      - wp_uploads:/var/www/html/wp-content/uploads
    depends_on:
      - postgres

  api-gateway:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/newsforge_api
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      STRIPE_SECRET_KEY: ${STRIPE_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    
  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/newsforge_api
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: newsforge
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  grafana_data:
  wp_uploads:
```

#### 4.2 모니터링 대시보드
```yaml
# infrastructure/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'newsforge-api'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'
    
  - job_name: 'wordpress'
    static_configs:
      - targets: ['wordpress:80']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

## 🚀 **즉시 실행 명령어**

```bash
# 1. 새 프로젝트 시작
git clone --template newsforge-pro-template
cd newsforge-pro

# 2. 환경 설정
cp .env.template .env
# .env 파일 편집 (API 키, DB 비밀번호 등)

# 3. 개발 환경 시작
docker-compose up -d

# 4. 데이터베이스 마이그레이션
docker-compose exec api-gateway alembic upgrade head

# 5. WordPress 초기 설정
docker-compose exec wordpress wp core install \
  --url="http://localhost:3000" \
  --title="NewsForge Pro" \
  --admin_user="admin" \
  --admin_password="secure_password" \
  --admin_email="admin@newsforge.pro"

# 6. 테마 활성화
docker-compose exec wordpress wp theme activate newsforge-pro

# 7. 테스트 실행
docker-compose exec api-gateway pytest
docker-compose exec wordpress wp test
```

## 📊 **예상 성과**

### **6개월 후 목표**
- **MAU**: 50,000 사용자
- **프리미엄 전환율**: 4%
- **월 매출**: $15,000
- **AdSense 수익**: $2,500/월
- **서버 비용**: $800/월
- **순이익**: $13,700/월

### **12개월 후 목표**
- **MAU**: 200,000 사용자
- **프리미엄 전환율**: 6%
- **월 매출**: $65,000
- **AdSense 수익**: $8,000/월
- **서버 비용**: $2,500/월
- **순이익**: $60,500/월

## ✅ **즉시 시작 체크리스트**

- [ ] 도메인 구매 (newsforge.pro)
- [ ] AWS/GCP 계정 설정
- [ ] Stripe 계정 생성
- [ ] Google AdSense 신청 준비
- [ ] OpenAI/Anthropic API 키 발급
- [ ] GitHub 리포지토리 생성
- [ ] 개발 팀 구성 (또는 솔로 개발 계획)
- [ ] 첫 번째 프로토타입 배포 (2주 목표)

**이 계획은 기존 프로토타입의 경험을 바탕으로 바로 실행 가능한 상용서비스를 만들기 위한 완전한 로드맵입니다. 8주 후 실제 수익이 발생하는 서비스 런칭이 목표입니다.** 