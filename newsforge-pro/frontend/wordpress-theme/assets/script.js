/**
 * NewsForge Pro WordPress Plugin JavaScript
 * FastAPI 백엔드 연동 및 UI 인터랙션
 */

(function($) {
    'use strict';

    // 전역 변수
    let apiKey = localStorage.getItem('newsforge_api_key');
    let apiProvider = localStorage.getItem('newsforge_api_provider') || 'openai';
    let isConverting = false;

    // DOM 요소
    const elements = {
        setupApiBtn: $('#setup-api-btn'),
        apiForm: $('#api-key-form'),
        apiStatusText: $('#api-status-text'),
        apiProviderSelect: $('#api-provider'),
        apiKeyInput: $('#api-key-input'),
        saveApiBtn: $('#save-api-btn'),
        cancelApiBtn: $('#cancel-api-btn'),
        newsUrlInput: $('#news-url'),
        clearUrlBtn: $('#clear-url'),
        generateBtn: $('#generate-btn'),
        loadingSection: $('#loading-section'),
        loadingText: $('#loading-text'),
        resultSection: $('#result-section'),
        resultContent: $('#result-content'),
        copyBtn: $('#copy-btn'),
        downloadBtn: $('#download-btn'),
        todayUsage: $('#today-usage'),
        monthUsage: $('#month-usage'),
        totalUsage: $('#total-usage')
    };

    // 초기화
    function init() {
        updateApiKeyStatus();
        bindEvents();
        loadUsageStats();
        
        // Google Analytics 설정
        if (typeof gtag !== 'undefined') {
            gtag('config', newsforge_config.ga_id || 'G-XXXXXXXXXX', {
                page_title: 'NewsForge Pro',
                page_location: window.location.href
            });
        }
    }

    // 이벤트 바인딩
    function bindEvents() {
        // API 키 설정 관련
        elements.setupApiBtn.on('click', showApiKeyForm);
        elements.saveApiBtn.on('click', saveApiKey);
        elements.cancelApiBtn.on('click', hideApiKeyForm);

        // URL 입력 관련
        elements.newsUrlInput.on('input', validateInput);
        elements.clearUrlBtn.on('click', clearUrl);

        // 변환 관련
        elements.generateBtn.on('click', generateContent);

        // 결과 관련
        elements.copyBtn.on('click', copyToClipboard);
        elements.downloadBtn.on('click', downloadContent);

        // 키보드 이벤트
        elements.newsUrlInput.on('keypress', function(e) {
            if (e.which === 13 && elements.generateBtn.prop('disabled') === false) {
                generateContent();
            }
        });

        elements.apiKeyInput.on('keypress', function(e) {
            if (e.which === 13) {
                saveApiKey();
            }
        });
    }

    // API 키 상태 업데이트
    function updateApiKeyStatus() {
        if (apiKey) {
            elements.apiStatusText.html(`<span style="color: #10b981;">✅ ${apiProvider.toUpperCase()} API 키가 설정되었습니다</span>`);
            elements.setupApiBtn.text('API 키 변경');
            elements.generateBtn.prop('disabled', false);
        } else {
            elements.apiStatusText.html('<span style="color: #6b7280;">API 키가 설정되지 않았습니다</span>');
            elements.setupApiBtn.text('API 키 설정');
            elements.generateBtn.prop('disabled', true);
        }
    }

    // API 키 폼 표시
    function showApiKeyForm() {
        elements.apiForm.slideDown(300);
        elements.setupApiBtn.hide();
        elements.apiProviderSelect.val(apiProvider);
        elements.apiKeyInput.val(apiKey || '').focus();
    }

    // API 키 폼 숨기기
    function hideApiKeyForm() {
        elements.apiForm.slideUp(300);
        elements.setupApiBtn.show();
        elements.apiKeyInput.val('');
    }

    // API 키 저장
    function saveApiKey() {
        const keyInput = elements.apiKeyInput.val().trim();
        const providerSelect = elements.apiProviderSelect.val();

        if (!keyInput) {
            showNotification('API 키를 입력해주세요.', 'error');
            return;
        }

        // API 키 형식 검증
        if (providerSelect === 'openai' && !keyInput.startsWith('sk-')) {
            showNotification('OpenAI API 키는 sk-로 시작해야 합니다.', 'error');
            return;
        }

        if (providerSelect === 'anthropic' && !keyInput.startsWith('sk-ant-')) {
            showNotification('Anthropic API 키는 sk-ant-로 시작해야 합니다.', 'error');
            return;
        }

        // 로컬 스토리지에 저장
        apiKey = keyInput;
        apiProvider = providerSelect;
        localStorage.setItem('newsforge_api_key', apiKey);
        localStorage.setItem('newsforge_api_provider', apiProvider);

        hideApiKeyForm();
        updateApiKeyStatus();

        // 서버에서 API 키 유효성 검사
        validateApiKey();

        showNotification('API 키가 저장되었습니다.', 'success');

        // Google Analytics 이벤트
        trackEvent('api_key_saved', {
            'provider': apiProvider
        });
    }

    // API 키 유효성 검사
    function validateApiKey() {
        if (!apiKey) return;

        $.ajax({
            url: newsforge_config.api_url + 'validate-key',
            method: 'POST',
            data: JSON.stringify({
                api_key: apiKey,
                provider: apiProvider
            }),
            contentType: 'application/json',
            timeout: 10000,
            success: function(response) {
                if (!response.valid) {
                    showNotification('API 키가 유효하지 않습니다. 다시 확인해주세요.', 'error');
                    apiKey = null;
                    localStorage.removeItem('newsforge_api_key');
                    updateApiKeyStatus();
                }
            },
            error: function() {
                console.warn('API 키 검증을 할 수 없습니다.');
            }
        });
    }

    // 입력 검증
    function validateInput() {
        const url = elements.newsUrlInput.val().trim();
        const isValidUrl = isValidURL(url);
        
        elements.generateBtn.prop('disabled', !isValidUrl || !apiKey || isConverting);
        
        // Clear 버튼 표시/숨김
        if (url) {
            elements.clearUrlBtn.show();
        } else {
            elements.clearUrlBtn.hide();
        }
    }

    // URL 유효성 검사
    function isValidURL(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }

    // URL 입력 삭제
    function clearUrl() {
        elements.newsUrlInput.val('').trigger('input');
        elements.clearUrlBtn.hide();
    }

    // 콘텐츠 생성
    function generateContent() {
        const url = elements.newsUrlInput.val().trim();

        if (!url) {
            showNotification('뉴스 URL을 입력해주세요.', 'error');
            return;
        }

        if (!apiKey) {
            showNotification('API 키를 먼저 설정해주세요.', 'error');
            return;
        }

        if (isConverting) {
            return;
        }

        isConverting = true;
        
        // UI 상태 변경
        elements.generateBtn.prop('disabled', true).text('변환 중...');
        elements.loadingSection.show();
        elements.resultSection.hide();
        elements.loadingText.text('콘텐츠 생성 중...');

        // Google Analytics 이벤트
        trackEvent('conversion_started', {
            'provider': apiProvider,
            'source_domain': getDomainFromUrl(url)
        });

        // AJAX 요청
        $.ajax({
            url: newsforge_config.api_url + 'convert',
            method: 'POST',
            data: JSON.stringify({
                url: url,
                api_key: apiKey,
                provider: apiProvider
            }),
            contentType: 'application/json',
            timeout: 120000, // 2분 타임아웃
            xhr: function() {
                const xhr = new window.XMLHttpRequest();
                
                // 진행 상황 시뮬레이션
                let progress = 0;
                const progressInterval = setInterval(function() {
                    progress += Math.random() * 10;
                    if (progress > 90) progress = 90;
                    
                    const messages = [
                        '뉴스 기사를 분석하는 중...',
                        'AI가 콘텐츠를 생성하는 중...',
                        '최종 검토를 진행하는 중...',
                        '거의 완료되었습니다...'
                    ];
                    
                    const messageIndex = Math.floor(progress / 25);
                    elements.loadingText.text(messages[messageIndex] || messages[3]);
                }, 2000);

                xhr.addEventListener('loadend', function() {
                    clearInterval(progressInterval);
                });

                return xhr;
            },
            success: function(response) {
                if (response.success) {
                    displayResult(response.content);
                    loadUsageStats(); // 통계 업데이트
                    
                    // Google Analytics 이벤트
                    trackEvent('conversion_completed', {
                        'provider': apiProvider,
                        'content_length': response.content.length
                    });
                } else {
                    showNotification('변환 실패: ' + (response.message || '알 수 없는 오류'), 'error');
                }
            },
            error: function(xhr, status, error) {
                let errorMessage = '변환 중 오류가 발생했습니다.';
                
                if (xhr.status === 429) {
                    errorMessage = '사용 한도를 초과했습니다. 잠시 후 다시 시도하거나 프리미엄으로 업그레이드하세요.';
                } else if (xhr.status === 408 || status === 'timeout') {
                    errorMessage = '변환 시간이 초과되었습니다. 다시 시도해주세요.';
                } else if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                
                showNotification(errorMessage, 'error');
                
                // Google Analytics 이벤트
                trackEvent('conversion_failed', {
                    'provider': apiProvider,
                    'error_code': xhr.status || 0,
                    'error_message': error
                });
            },
            complete: function() {
                isConverting = false;
                elements.generateBtn.prop('disabled', false).text('콘텐츠 생성');
                elements.loadingSection.hide();
            }
        });
    }

    // 결과 표시
    function displayResult(content) {
        elements.resultContent.text(content);
        elements.resultSection.show();
        
        // 결과 영역으로 스크롤
        $('html, body').animate({
            scrollTop: elements.resultSection.offset().top - 100
        }, 500);
    }

    // 클립보드 복사
    function copyToClipboard() {
        const content = elements.resultContent.text();
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(content).then(function() {
                elements.copyBtn.text('복사 완료!');
                setTimeout(function() {
                    elements.copyBtn.text('복사하기');
                }, 2000);
                
                trackEvent('content_copied', {
                    'content_length': content.length
                });
            }).catch(function() {
                fallbackCopyToClipboard(content);
            });
        } else {
            fallbackCopyToClipboard(content);
        }
    }

    // 클립보드 복사 fallback
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                elements.copyBtn.text('복사 완료!');
                setTimeout(function() {
                    elements.copyBtn.text('복사하기');
                }, 2000);
            } else {
                showNotification('복사에 실패했습니다.', 'error');
            }
        } catch (err) {
            showNotification('복사에 실패했습니다.', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    // 콘텐츠 다운로드
    function downloadContent() {
        const content = elements.resultContent.text();
        const url = elements.newsUrlInput.val().trim();
        const domain = getDomainFromUrl(url);
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        const filename = `newsforge-${domain}-${timestamp}.md`;
        
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
        const link = document.createElement('a');
        
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            trackEvent('content_downloaded', {
                'filename': filename,
                'content_length': content.length
            });
        } else {
            showNotification('다운로드가 지원되지 않는 브라우저입니다.', 'error');
        }
    }

    // 사용 통계 로드
    function loadUsageStats() {
        if (!newsforge_config.is_logged_in) {
            return;
        }

        $.ajax({
            url: newsforge_config.api_url + 'stats',
            method: 'GET',
            headers: {
                'X-WP-Nonce': newsforge_config.nonce
            },
            success: function(response) {
                elements.todayUsage.text(response.today || 0);
                elements.monthUsage.text(response.month || 0);
                elements.totalUsage.text(response.total || 0);
            },
            error: function() {
                console.warn('사용 통계를 로드할 수 없습니다.');
            }
        });
    }

    // 알림 표시
    function showNotification(message, type = 'info') {
        const notification = $(`
            <div class="newsforge-notification newsforge-${type}" style="
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
                max-width: 400px;
                word-wrap: break-word;
            ">
                ${message}
                <button style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.2em;
                    cursor: pointer;
                    float: right;
                    margin-left: 10px;
                ">&times;</button>
            </div>
        `);

        // 타입별 스타일 설정
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        notification.css('background-color', colors[type] || colors.info);

        $('body').append(notification);

        // 애니메이션
        setTimeout(function() {
            notification.css({
                opacity: 1,
                transform: 'translateX(0)'
            });
        }, 100);

        // 자동 제거
        setTimeout(function() {
            notification.css({
                opacity: 0,
                transform: 'translateX(100%)'
            });
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 5000);

        // 수동 제거
        notification.find('button').on('click', function() {
            notification.css({
                opacity: 0,
                transform: 'translateX(100%)'
            });
            setTimeout(function() {
                notification.remove();
            }, 300);
        });
    }

    // Google Analytics 이벤트 트래킹
    function trackEvent(eventName, parameters = {}) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'NewsForge',
                ...parameters
            });
        }
    }

    // URL에서 도메인 추출
    function getDomainFromUrl(url) {
        try {
            return new URL(url).hostname.replace('www.', '');
        } catch (e) {
            return 'unknown';
        }
    }

    // 페이지 로드 시 초기화
    $(document).ready(function() {
        init();
        
        // FastAPI 서버 상태 확인
        checkServerStatus();
        
        // 페이지 뷰 트래킹
        trackEvent('page_view', {
            'page_title': document.title,
            'page_location': window.location.href
        });
    });

    // FastAPI 서버 상태 확인
    function checkServerStatus() {
        $.ajax({
            url: newsforge_config.fastapi_url + '/api/v1/health',
            method: 'GET',
            timeout: 5000,
            success: function() {
                console.log('✅ FastAPI 서버 정상 작동');
            },
            error: function() {
                console.warn('⚠️ FastAPI 서버 연결 실패');
                showNotification('서버 연결에 문제가 있습니다. 관리자에게 문의하세요.', 'warning');
            }
        });
    }

    // 전역으로 노출할 함수들
    window.NewsForge = {
        generateContent: generateContent,
        copyToClipboard: copyToClipboard,
        loadUsageStats: loadUsageStats,
        trackEvent: trackEvent
    };

})(jQuery); 