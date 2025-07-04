# 뉴스 기사 마크다운 변환기

TXT 형식의 뉴스 기사를 마크다운 형식으로 변환하는 도구입니다. Anthropic Claude API와 OpenAI GPT API를 모두 지원합니다.

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정 (`.env` 파일 생성):
```env
# Anthropic API 사용시
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI API 사용시
OPENAI_API_KEY=your_openai_api_key_here
```

## 사용법

### 기본 사용법 (Anthropic API)
```bash
python converter.py <txt_file_or_directory>
```

### OpenAI API 사용
```bash
python converter.py <txt_file_or_directory> openai
```

### 예시
```bash
# 단일 파일 변환 (Anthropic)
python converter.py article.txt

# 단일 파일 변환 (OpenAI)
python converter.py article.txt openai

# 디렉토리 내 모든 TXT 파일 변환 (Anthropic)
python converter.py ./articles/

# 디렉토리 내 모든 TXT 파일 변환 (OpenAI)
python converter.py ./articles/ openai
```

## 입력 파일 형식

TXT 파일은 다음 형식을 따라야 합니다:

```
제목: 기사 제목
==========================================
메타 정보:
description: 기사 요약 설명
------------------------------------------
본문:
기사의 실제 내용이 여기에 들어갑니다.
여러 줄에 걸쳐 작성할 수 있습니다.
```

## 출력 형식

변환된 마크다운 파일은 `converted_articles/` 디렉토리에 저장되며, 다음 형식을 따릅니다:

```markdown
💰 제목 (이모지 포함)

▶ 주요 내용:
• 첫 번째 핵심 내용
• 두 번째 핵심 내용

▶ 세부 사항:
1. 첫 번째 세부 사항
2. 두 번째 세부 사항

#키워드1 #키워드2 #키워드3 #키워드4 #키워드5
```

## 특징

- **이중 API 지원**: Anthropic Claude와 OpenAI GPT 모두 사용 가능
- **자동 이모지 선택**: 내용에 맞는 적절한 이모지 자동 선택
- **키워드 추출**: 기사 내용에서 관련 키워드를 자동으로 추출하여 해시태그 생성
- **주식 심볼 포맷팅**: 주식 종목명이 언급되면 자동으로 $심볼 형식으로 변환
- **일관된 형식**: 모든 변환된 기사가 동일한 마크다운 형식을 따름

## API 모델

- **Anthropic**: `claude-3-opus-20240229`
- **OpenAI**: `gpt-4o`

## 주의사항

1. API 키가 환경 변수에 올바르게 설정되어 있는지 확인하세요.
2. 사용하는 API에 따라 적절한 API 키를 설정하세요.
3. 대용량 파일 처리 시 API 비용이 발생할 수 있습니다.
4. 변환된 파일은 타임스탬프가 포함된 파일명으로 저장됩니다.

## 오류 해결

### "API key not found" 오류
- `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
- 환경 변수 이름이 정확한지 확인 (`ANTHROPIC_API_KEY` 또는 `OPENAI_API_KEY`)

### "Invalid API provider" 오류
- API 제공자는 `anthropic` 또는 `openai`만 사용 가능
- 대소문자 구분 없이 입력 가능

### 파일 읽기 오류
- 입력 파일이 올바른 TXT 형식을 따르는지 확인
- 파일 경로가 정확한지 확인 