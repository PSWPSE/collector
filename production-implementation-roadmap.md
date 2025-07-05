# 🚀 **NewsForge Pro 상용화 구현 로드맵**

## **🎯 즉시 실행 계획 (1주차)**

### **1. 서비스 안정성 개선**

#### **1.1 Health Check 시스템 강화**
```python
# 현재 문제: FastAPI 서버 연결 실패
# 해결책: Robust Health Check + Auto Recovery

# newsforge-pro/backend/app/core/health.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging

class HealthStatus(BaseModel):
    status: str
    version: str
    timestamp: str
    dependencies: dict

async def comprehensive_health_check():
    """포괄적인 헬스 체크"""
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "openai_api": await check_openai_api(),
        "anthropic_api": await check_anthropic_api(),
        "memory_usage": get_memory_usage(),
        "disk_space": get_disk_usage()
    }
    
    all_healthy = all(checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": checks
    }
```

#### **1.2 프로세스 관리 시스템**
```bash
# 현재 문제: 서버가 백그라운드에서 종료됨
# 해결책: Process Manager (PM2) 도입

# pm2 설치 및 설정
npm install -g pm2

# ecosystem.config.js 생성
module.exports = {
  apps: [
    {
      name: 'newsforge-api',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      cwd: './newsforge-pro/backend',
      instances: 2,
      exec_mode: 'cluster',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 8000
      }
    },
    {
      name: 'newsforge-web',
      script: 'npm',
      args: 'start',
      cwd: './news-to-social-web',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M'
    }
  ]
}
```

#### **1.3 자동 재시작 스크립트**
```bash
#!/bin/bash
# auto-restart.sh - 서비스 자동 재시작

check_service() {
    local service_name=$1
    local port=$2
    
    if ! curl -f http://localhost:$port/health &>/dev/null; then
        echo "$(date): $service_name is down, restarting..."
        pm2 restart $service_name
        sleep 10
        
        if curl -f http://localhost:$port/health &>/dev/null; then
            echo "$(date): $service_name restarted successfully"
        else
            echo "$(date): CRITICAL: $service_name failed to restart"
            # 슬랙/이메일 알림 발송
            send_alert "$service_name failed to restart"
        fi
    fi
}

# 5분마다 헬스 체크
while true; do
    check_service "newsforge-api" 8000
    check_service "newsforge-web" 3000
    sleep 300
done
```

### **2. 데이터베이스 설계 개선**

#### **2.1 Production Ready 스키마**
```sql
-- 사용자 관리 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    api_quota_daily INTEGER DEFAULT 5,
    api_quota_used INTEGER DEFAULT 0,
    last_quota_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);

-- API 키 관리 테이블 (암호화된 저장)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    provider VARCHAR(20) NOT NULL, -- 'openai', 'anthropic'
    encrypted_key TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- 변환 요청 로그 테이블
CREATE TABLE conversion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    source_url TEXT NOT NULL,
    target_platform VARCHAR(20) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    content_generated TEXT,
    processing_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6)
);

-- 시스템 메트릭 테이블
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 6) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_conversion_logs_user_id ON conversion_logs(user_id);
CREATE INDEX idx_conversion_logs_created_at ON conversion_logs(created_at);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
```

### **3. 에러 핸들링 및 복구 시스템**

#### **3.1 글로벌 에러 핸들러**
```python
# newsforge-pro/backend/app/core/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

class GlobalExceptionHandler:
    @staticmethod
    async def handle_general_exception(request: Request, exc: Exception):
        """모든 예외를 처리하는 글로벌 핸들러"""
        error_id = str(uuid.uuid4())
        
        # 에러 로깅
        logger.error(f"Error ID: {error_id}")
        logger.error(f"URL: {request.url}")
        logger.error(f"Method: {request.method}")
        logger.error(f"Exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # 사용자에게는 일반적인 에러 메시지
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "message": "An unexpected error occurred. Please try again later."
            }
        )
    
    @staticmethod
    async def handle_ai_service_error(request: Request, exc: Exception):
        """AI 서비스 에러 전용 핸들러"""
        if "rate limit" in str(exc).lower():
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "AI service rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }
            )
        
        if "insufficient_quota" in str(exc).lower():
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Insufficient quota",
                    "message": "Your AI service quota has been exceeded. Please check your billing."
                }
            )
        
        return await GlobalExceptionHandler.handle_general_exception(request, exc)
```

#### **3.2 회로 차단기 패턴**
```python
# newsforge-pro/backend/app/core/circuit_breaker.py
import asyncio
from enum import Enum
from typing import Callable, Any
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """회로 차단기를 통한 함수 호출"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (time.time() - self.last_failure_time) > self.recovery_timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# 사용 예시
openai_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
anthropic_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
```

## **🔄 Phase 3: 모니터링 및 관찰 가능성 (2주차)**

### **3.1 실시간 모니터링 시스템**
```python
# newsforge-pro/backend/app/core/monitoring.py
import psutil
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import time

# 메트릭 정의
REQUEST_COUNT = Counter('newsforge_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('newsforge_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('newsforge_active_connections', 'Active connections')
MEMORY_USAGE = Gauge('newsforge_memory_usage_bytes', 'Memory usage')
CPU_USAGE = Gauge('newsforge_cpu_usage_percent', 'CPU usage')

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    async def collect_system_metrics(self):
        """시스템 메트릭 수집"""
        while True:
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)
                
                # 메모리 사용률
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.used)
                
                # 로그 기록
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage: {cpu_percent}%")
                
                if memory.percent > 85:
                    logger.warning(f"High memory usage: {memory.percent}%")
                
                await asyncio.sleep(60)  # 1분마다 수집
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(60)
```

### **3.2 알림 시스템**
```python
# newsforge-pro/backend/app/core/alerts.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json

class AlertManager:
    def __init__(self):
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
        self.slack_webhook = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    
    async def send_critical_alert(self, message: str, details: dict = None):
        """중요 알림 발송"""
        try:
            # 이메일 발송
            await self._send_email(
                subject=f"[CRITICAL] NewsForge Pro Alert",
                body=f"{message}\n\nDetails: {json.dumps(details, indent=2)}"
            )
            
            # 슬랙 알림
            await self._send_slack_notification(message, 'danger')
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def _send_email(self, subject: str, body: str):
        """이메일 발송"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['username']
        msg['To'] = 'admin@newsforge.com'
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['username'], self.email_config['password'])
        server.send_message(msg)
        server.quit()
    
    async def _send_slack_notification(self, message: str, color: str = 'good'):
        """슬랙 알림 발송"""
        payload = {
            "attachments": [{
                "color": color,
                "title": "NewsForge Pro Alert",
                "text": message,
                "ts": int(time.time())
            }]
        }
        
        response = requests.post(self.slack_webhook, json=payload)
        return response.status_code == 200
```

## **🚀 Phase 4: 배포 자동화 (3주차)**

### **4.1 Docker 컨테이너화**
```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# 시스템 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 헬스 체크 스크립트
COPY healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh

# 포트 노출
EXPOSE 8000

# 헬스 체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD /healthcheck.sh

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### **4.2 GitHub Actions CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: |
          pytest tests/ -v
      
      - name: Security scan
        uses: pypa/gh-action-pip-audit@v1.0.8

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: newsforge-pro
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: task-definition.json
          service: newsforge-pro-service
          cluster: newsforge-pro-cluster
          wait-for-service-stability: true
```

## **💡 즉시 실행 가능한 개선사항**

### **현재 환경 개선 (오늘 적용 가능)**
```bash
# 1. 프로세스 매니저 설치
npm install -g pm2

# 2. 서비스 시작 스크립트 개선
cat > start-production.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting NewsForge Pro Production Services..."

# 가상환경 활성화
source venv/bin/activate

# 환경 변수 설정
export NODE_ENV=production
export PYTHONPATH=/Users/alphabridge/collector/newsforge-pro/backend

# PM2로 서비스 시작
pm2 start ecosystem.config.js

# 헬스 체크
sleep 10
pm2 status

echo "✅ Services started successfully!"
echo "🌐 Web: http://localhost:3000"
echo "🔗 API: http://localhost:8000"
echo "📊 Status: pm2 status"
EOF

chmod +x start-production.sh

# 3. 로그 모니터링 설정
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

---

**이 로드맵은 개발 환경에서 안정적인 상용 서비스로 전환하기 위한 완전한 가이드입니다.** 