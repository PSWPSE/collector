# 🤖 뉴스 변환기 (New Converter System)

뉴스 기사 TXT 파일을 고품질 마크다운으로 변환하는 AI 기반 도구입니다.

## ✨ 주요 특징

### 🎯 **자동 변환기 선택**
- API 키 상태에 따라 자동으로 최적의 변환기 선택
- 우선순위: Anthropic Claude > OpenAI GPT > 로컬 규칙 기반

### 🧠 **3가지 변환 방식**
1. **Anthropic Claude** (최고 품질) - Claude-3-Opus
2. **OpenAI GPT** (고품질) - GPT-4o
3. **로컬 규칙 기반** (API 불필요) - 규칙 기반 알고리즘

### 📝 **일관된 출력 형식**
- 한국어 스타일 마크다운
- 이모지 포함 제목
- 구조화된 섹션 (▶ 형식)
- 주식 심볼 자동 포맷팅 ($SYMBOL)
- AI 기반 해시태그 생성

## 🚀 빠른 시작

### 1. 설치
```bash
# 의존성 설치
pip install -r requirements.txt

# 패키지 설치 (선택사항)
pip install -e .
```

### 2. API 키 설정 (선택사항)
```bash
# .env 파일 생성
cp .env.example .env

# API 키 설정 (둘 중 하나 또는 둘 다)
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
echo "OPENAI_API_KEY=sk-your-openai-key-here" >> .env
```

**⚠️ API 키가 없어도 로컬 변환기로 사용 가능합니다!**

### 3. 사용법

#### 🎮 **대화형 모드** (추천)
```bash
python converter_runner.py
```

#### 📁 **디렉토리 변환**
```bash
python converter_runner.py extracted_articles/
```

#### 📄 **단일 파일 변환**
```bash
python converter_runner.py article.txt
```

#### 🎯 **특정 변환기 지정**
```bash
# Anthropic 강제 사용
python converter_runner.py -t anthropic article.txt

# OpenAI 강제 사용  
python converter_runner.py -t openai article.txt

# 로컬 변환기 강제 사용
python converter_runner.py -t local article.txt
```

#### 📊 **변환기 상태 확인**
```bash
python converter_runner.py --status
```

## 📁 프로젝트 구조

```
collector/
├── converter_runner.py          # 🎯 메인 실행 스크립트
├── converters/                  # 🧠 변환기 패키지
│   ├── __init__.py
│   ├── base_converter.py        # 공통 기능 베이스 클래스
│   ├── anthropic_converter.py   # Anthropic Claude 변환기
│   ├── openai_converter.py      # OpenAI GPT 변환기
│   ├── local_converter.py       # 로컬 규칙 기반 변환기
│   └── factory.py               # 자동 변환기 선택 팩토리
├── converter.py                 # 🏆 기존 변환기 (유지됨)
├── extractors/                  # 📰 뉴스 추출기
├── tools/                       # 🛠️ 유틸리티 도구
├── extracted_articles/          # 📥 추출된 TXT 파일
├── converted_articles/          # 📤 변환된 마크다운 파일
└── .env                         # 🔐 API 키 설정
```

## 🎨 출력 예시

```markdown
💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시

▶ 주요 발표 내용:
• 크라켄이 새로운 P2P 결제 플랫폼 출시 발표
• 기존 거래소 기능과 통합된 종합 금융 서비스 제공
• 사용자 간 직접 암호화폐 송금 기능 지원

▶ 시장 영향:
• 바이낸스, 코인베이스 등 기존 플레이어와 경쟁 심화
• 암호화폐 결제 시장 확대 기대
• 규제 리스크 여전히 존재

#크라켄 #암호화폐 #P2P결제 #블록체인 #핀테크 #금융혁신
```

## ⚙️ 고급 설정

### 🎛️ **변환기 우선순위 커스터마이징**
`converters/factory.py`에서 우선순위 수정:
```python
priority_order = ['anthropic', 'openai', 'local']
```

### 📂 **출력 디렉토리 변경**
```bash
python converter_runner.py -o my_articles/ extracted_articles/
```

### 🔧 **API 모델 변경**
각 변환기 파일에서 모델 수정:
- `anthropic_converter.py`: `claude-3-opus-20240229`
- `openai_converter.py`: `gpt-4o`

## 🆚 변환기 비교

| 변환기 | 품질 | 속도 | 비용 | API 필요 | 특징 |
|--------|------|------|------|----------|------|
| **Anthropic** | ⭐⭐⭐⭐⭐ | 보통 | 높음 | ✅ | 가장 자연스러운 한국어 |
| **OpenAI** | ⭐⭐⭐⭐ | 빠름 | 보통 | ✅ | 일관성 있는 구조화 |
| **Local** | ⭐⭐⭐ | 매우 빠름 | 무료 | ❌ | API 불필요, 규칙 기반 |

## 🔄 기존 converter.py와의 차이점

### ✅ **새로운 시스템의 장점**
- 🎯 자동 변환기 선택
- 🧠 3가지 변환 옵션
- 🎮 사용자 친화적 대화형 모드
- 📊 변환기 상태 모니터링
- 🛠️ 모듈화된 구조

### 🔒 **기존 converter.py**
- 여전히 사용 가능
- 직접 API 호출 방식
- 기존 워크플로우 유지

## 🚨 문제 해결

### ❌ **API 키 오류**
```
⚠️ API 키 테스트 실패 (anthropic): Invalid API key
```
**해결:** `.env` 파일의 API 키 확인

### ❌ **의존성 오류**
```
ModuleNotFoundError: No module named 'anthropic'
```
**해결:** `pip install -r requirements.txt`

### ❌ **파일 없음 오류**
```
❌ extracted_articles/ 디렉토리에서 TXT 파일을 찾을 수 없습니다.
```
**해결:** TXT 파일이 있는 올바른 경로 확인

## 📞 지원

### 🎮 **대화형 모드 사용**
가장 쉬운 방법입니다:
```bash
python converter_runner.py
```

### 📖 **도움말 보기**
```bash
python converter_runner.py --help
```

### 🔍 **상태 확인**
```bash
python converter_runner.py --status
```

---

**💡 팁:** API 키가 없어도 로컬 변환기로 충분히 좋은 품질의 마크다운을 생성할 수 있습니다! 