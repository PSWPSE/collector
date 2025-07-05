<?php
/**
 * NewsForge Pro WordPress Theme
 * 메인 템플릿 파일
 */

get_header(); ?>

<div class="container">
    <!-- 상단 AdSense 배너 -->
    <div class="adsense-banner">
        <?php if (get_theme_mod('adsense_banner_code')): ?>
            <?php echo get_theme_mod('adsense_banner_code'); ?>
        <?php else: ?>
            <div>광고 영역 (728x90)</div>
        <?php endif; ?>
    </div>

    <div class="main-content">
        <div class="content-area">
            <!-- 서비스 소개 -->
            <div class="service-section">
                <h1 class="service-title">🚀 뉴스 기사 콘텐츠 생성기 📰➡️📝</h1>
                <p class="text-muted mb-4">뉴스 기사를 체계적인 콘텐츠로 변환하세요</p>
                
                <?php if (!is_user_logged_in()): ?>
                    <div class="premium-notice">
                        <strong>💎 프리미엄 기능 사용 가능!</strong>
                        <p>회원가입하고 무제한 콘텐츠 생성을 경험하세요.</p>
                        <a href="/wp-login.php?action=register" class="premium-btn">회원가입</a>
                    </div>
                <?php endif; ?>
                
                <!-- API 키 설정 섹션 -->
                <div id="api-key-section" class="mb-4">
                    <h3>API 키 설정</h3>
                    <div id="api-key-status" class="mb-2">
                        <span class="text-muted">API 키가 설정되지 않았습니다</span>
                    </div>
                    <div id="api-key-form" style="display: none;">
                        <select id="api-provider" class="mb-2">
                            <option value="openai">OpenAI</option>
                            <option value="anthropic">Anthropic</option>
                        </select>
                        <input type="password" id="api-key-input" placeholder="API 키를 입력하세요" class="url-input">
                        <button id="save-api-key" class="generate-btn">저장</button>
                        <button id="cancel-api-key" class="generate-btn" style="background: #6b7280;">취소</button>
                    </div>
                    <button id="setup-api-key" class="generate-btn">API 키 설정</button>
                </div>

                <!-- 콘텐츠 내 AdSense -->
                <div class="adsense-content">
                    <?php if (get_theme_mod('adsense_content_code')): ?>
                        <?php echo get_theme_mod('adsense_content_code'); ?>
                    <?php else: ?>
                        <div>광고 영역 (336x280)</div>
                    <?php endif; ?>
                </div>

                <!-- 뉴스 URL 입력 -->
                <div class="service-section">
                    <h3>뉴스 URL 입력</h3>
                    <input type="url" id="news-url" class="url-input" placeholder="뉴스 기사 URL을 입력하세요">
                    <button id="generate-content" class="generate-btn" disabled>콘텐츠 생성</button>
                </div>

                <!-- 로딩 상태 -->
                <div id="loading-state" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <span>콘텐츠 생성 중...</span>
                </div>

                <!-- 결과 영역 -->
                <div id="result-section" class="result-area" style="display: none;">
                    <h3>생성된 콘텐츠</h3>
                    <div id="result-content" class="result-content"></div>
                    <button id="copy-content" class="generate-btn mt-4">복사하기</button>
                </div>
            </div>
        </div>

        <div class="sidebar">
            <!-- 사이드바 AdSense -->
            <div class="adsense-sidebar">
                <?php if (get_theme_mod('adsense_sidebar_code')): ?>
                    <?php echo get_theme_mod('adsense_sidebar_code'); ?>
                <?php else: ?>
                    <div>광고 영역 (300x250)</div>
                <?php endif; ?>
            </div>

            <!-- 사용 통계 -->
            <div class="service-section">
                <h3>사용 통계</h3>
                <div class="text-muted">
                    <?php if (is_user_logged_in()): ?>
                        <p>오늘 사용: <span id="today-usage">0</span>회</p>
                        <p>이번 달: <span id="month-usage">0</span>회</p>
                        <p>전체: <span id="total-usage">0</span>회</p>
                    <?php else: ?>
                        <p>회원가입하여 사용 통계를 확인하세요</p>
                    <?php endif; ?>
                </div>
            </div>

            <!-- 최근 변환 내역 -->
            <div class="service-section">
                <h3>최근 변환 내역</h3>
                <div id="recent-conversions" class="text-muted">
                    <?php if (is_user_logged_in()): ?>
                        <p>변환 내역이 없습니다</p>
                    <?php else: ?>
                        <p>로그인하여 변환 내역을 확인하세요</p>
                    <?php endif; ?>
                </div>
            </div>

            <!-- 프리미엄 업그레이드 -->
            <?php if (is_user_logged_in() && !current_user_can('premium_features')): ?>
                <div class="premium-notice">
                    <strong>💎 프리미엄으로 업그레이드</strong>
                    <p>• 무제한 변환</p>
                    <p>• 배치 처리</p>
                    <p>• 우선 지원</p>
                    <p>• API 액세스</p>
                    <a href="/premium" class="premium-btn">업그레이드</a>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
// NewsForge Pro 클라이언트 스크립트
document.addEventListener('DOMContentLoaded', function() {
    const setupApiKeyBtn = document.getElementById('setup-api-key');
    const apiKeyForm = document.getElementById('api-key-form');
    const apiKeyStatus = document.getElementById('api-key-status');
    const saveApiKeyBtn = document.getElementById('save-api-key');
    const cancelApiKeyBtn = document.getElementById('cancel-api-key');
    const newsUrlInput = document.getElementById('news-url');
    const generateBtn = document.getElementById('generate-content');
    const loadingState = document.getElementById('loading-state');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    const copyBtn = document.getElementById('copy-content');

    let apiKey = localStorage.getItem('newsforge_api_key');
    let apiProvider = localStorage.getItem('newsforge_api_provider') || 'openai';

    // API 키 상태 업데이트
    function updateApiKeyStatus() {
        if (apiKey) {
            apiKeyStatus.innerHTML = `<span style="color: #10b981;">✅ ${apiProvider.toUpperCase()} API 키가 설정되었습니다</span>`;
            setupApiKeyBtn.textContent = 'API 키 변경';
            generateBtn.disabled = false;
        } else {
            apiKeyStatus.innerHTML = '<span class="text-muted">API 키가 설정되지 않았습니다</span>';
            setupApiKeyBtn.textContent = 'API 키 설정';
            generateBtn.disabled = true;
        }
    }

    // 초기 상태 설정
    updateApiKeyStatus();

    // API 키 설정 버튼
    setupApiKeyBtn.addEventListener('click', function() {
        apiKeyForm.style.display = 'block';
        setupApiKeyBtn.style.display = 'none';
        document.getElementById('api-provider').value = apiProvider;
        document.getElementById('api-key-input').value = apiKey || '';
    });

    // API 키 저장
    saveApiKeyBtn.addEventListener('click', function() {
        const keyInput = document.getElementById('api-key-input');
        const providerSelect = document.getElementById('api-provider');
        
        if (keyInput.value.trim()) {
            apiKey = keyInput.value.trim();
            apiProvider = providerSelect.value;
            localStorage.setItem('newsforge_api_key', apiKey);
            localStorage.setItem('newsforge_api_provider', apiProvider);
            
            apiKeyForm.style.display = 'none';
            setupApiKeyBtn.style.display = 'block';
            updateApiKeyStatus();
            
            // 서버에 API 키 유효성 검사 요청
            validateApiKey();
        } else {
            alert('API 키를 입력해주세요.');
        }
    });

    // API 키 취소
    cancelApiKeyBtn.addEventListener('click', function() {
        apiKeyForm.style.display = 'none';
        setupApiKeyBtn.style.display = 'block';
        document.getElementById('api-key-input').value = '';
    });

    // API 키 유효성 검사
    async function validateApiKey() {
        if (!apiKey) return;

        try {
            const response = await fetch('/wp-json/newsforge/v1/validate-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    provider: apiProvider
                })
            });

            const result = await response.json();
            
            if (!result.valid) {
                alert('API 키가 유효하지 않습니다. 다시 확인해주세요.');
                apiKey = null;
                localStorage.removeItem('newsforge_api_key');
                updateApiKeyStatus();
            }
        } catch (error) {
            console.error('API 키 검증 실패:', error);
        }
    }

    // 콘텐츠 생성
    generateBtn.addEventListener('click', async function() {
        const url = newsUrlInput.value.trim();
        
        if (!url) {
            alert('뉴스 URL을 입력해주세요.');
            return;
        }

        if (!apiKey) {
            alert('API 키를 먼저 설정해주세요.');
            return;
        }

        loadingState.style.display = 'flex';
        resultSection.style.display = 'none';
        generateBtn.disabled = true;

        try {
            const response = await fetch('/wp-json/newsforge/v1/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    api_key: apiKey,
                    provider: apiProvider
                })
            });

            const result = await response.json();
            
            if (result.success) {
                resultContent.textContent = result.content;
                resultSection.style.display = 'block';
                
                // 사용 통계 업데이트
                updateUsageStats();
            } else {
                alert('변환 실패: ' + result.message);
            }
        } catch (error) {
            console.error('변환 실패:', error);
            alert('변환 중 오류가 발생했습니다. 다시 시도해주세요.');
        } finally {
            loadingState.style.display = 'none';
            generateBtn.disabled = false;
        }
    });

    // 복사하기
    copyBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(resultContent.textContent).then(() => {
            copyBtn.textContent = '복사 완료!';
            setTimeout(() => {
                copyBtn.textContent = '복사하기';
            }, 2000);
        });
    });

    // 사용 통계 업데이트
    function updateUsageStats() {
        // 워드프레스 AJAX로 사용 통계 업데이트 요청
        if (typeof ajaxurl !== 'undefined') {
            fetch(ajaxurl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'action=update_usage_stats'
            });
        }
    }
});
</script>

<?php get_footer(); ?> 