<?php
/**
 * Plugin Name: NewsForge Pro
 * Description: AI 기반 뉴스 콘텐츠 생성 워드프레스 플러그인 - FastAPI 백엔드 연동 및 애드센스 수익화
 * Version: 1.0.0
 * Author: NewsForge Team
 * Text Domain: newsforge-pro
 */

// 직접 접근 방지
if (!defined('ABSPATH')) {
    exit;
}

// 플러그인 상수 정의
define('NEWSFORGE_PLUGIN_URL', plugin_dir_url(__FILE__));
define('NEWSFORGE_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('NEWSFORGE_FASTAPI_URL', 'http://127.0.0.1:8000');

// 메인 플러그인 클래스
class NewsForgeProPlugin {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('rest_api_init', array($this, 'register_api_routes'));
        add_action('admin_menu', array($this, 'admin_menu'));
        
        // 플러그인 활성화/비활성화 훅
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
    }
    
    public function init() {
        // 쇼트코드 등록
        add_shortcode('newsforge_converter', array($this, 'converter_shortcode'));
        add_shortcode('newsforge_stats', array($this, 'stats_shortcode'));
        
        // 프리미엄 사용자 역할 생성
        $this->create_premium_role();
    }
    
    public function enqueue_scripts() {
        wp_enqueue_style('newsforge-style', NEWSFORGE_PLUGIN_URL . 'assets/style.css', array(), '1.0.0');
        wp_enqueue_script('newsforge-script', NEWSFORGE_PLUGIN_URL . 'assets/script.js', array('jquery'), '1.0.0', true);
        
        // JavaScript에 설정값 전달
        wp_localize_script('newsforge-script', 'newsforge_config', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'api_url' => home_url('/wp-json/newsforge/v1/'),
            'nonce' => wp_create_nonce('newsforge_nonce'),
            'fastapi_url' => NEWSFORGE_FASTAPI_URL,
            'is_logged_in' => is_user_logged_in(),
            'is_premium' => $this->is_premium_user()
        ));
    }
    
    // 메인 변환기 쇼트코드
    public function converter_shortcode($atts) {
        $atts = shortcode_atts(array(
            'show_ads' => 'true',
            'theme' => 'default'
        ), $atts);
        
        ob_start();
        ?>
        <div id="newsforge-converter" class="newsforge-widget">
            <?php if ($atts['show_ads'] === 'true'): ?>
                <!-- 상단 AdSense 배너 -->
                <div class="newsforge-ad-banner">
                    <?php echo $this->get_adsense_code('banner'); ?>
                </div>
            <?php endif; ?>
            
            <div class="newsforge-converter-container">
                <div class="newsforge-main-content">
                    <h2>🚀 뉴스 콘텐츠 생성기</h2>
                    <p class="newsforge-description">뉴스 기사를 체계적인 콘텐츠로 변환하세요</p>
                    
                    <!-- API 키 설정 영역 -->
                    <div class="newsforge-api-section">
                        <div class="newsforge-api-status">
                            <span id="api-status-text">API 키가 설정되지 않았습니다</span>
                            <button id="setup-api-btn" class="newsforge-btn-primary">API 키 설정</button>
                        </div>
                        
                        <div id="api-key-form" class="newsforge-api-form" style="display:none;">
                            <select id="api-provider">
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic</option>
                            </select>
                            <input type="password" id="api-key-input" placeholder="API 키를 입력하세요" class="newsforge-input">
                            <div class="newsforge-api-buttons">
                                <button id="save-api-btn" class="newsforge-btn-primary">저장</button>
                                <button id="cancel-api-btn" class="newsforge-btn-secondary">취소</button>
                            </div>
                        </div>
                    </div>
                    
                    <?php if ($atts['show_ads'] === 'true'): ?>
                        <!-- 콘텐츠 내 AdSense -->
                        <div class="newsforge-ad-content">
                            <?php echo $this->get_adsense_code('content'); ?>
                        </div>
                    <?php endif; ?>
                    
                    <!-- URL 입력 및 변환 영역 -->
                    <div class="newsforge-input-section">
                        <label for="news-url">뉴스 URL 입력</label>
                        <div class="newsforge-input-group">
                            <input type="url" id="news-url" placeholder="뉴스 기사 URL을 입력하세요" class="newsforge-input">
                            <button id="clear-url" class="newsforge-btn-clear">✕</button>
                        </div>
                        <button id="generate-btn" class="newsforge-btn-generate" disabled>콘텐츠 생성</button>
                    </div>
                    
                    <!-- 로딩 상태 -->
                    <div id="loading-section" class="newsforge-loading" style="display:none;">
                        <div class="newsforge-spinner"></div>
                        <span id="loading-text">콘텐츠 생성 중...</span>
                    </div>
                    
                    <!-- 결과 영역 -->
                    <div id="result-section" class="newsforge-result" style="display:none;">
                        <h3>생성된 콘텐츠</h3>
                        <div id="result-content" class="newsforge-content"></div>
                        <div class="newsforge-result-actions">
                            <button id="copy-btn" class="newsforge-btn-primary">복사하기</button>
                            <button id="download-btn" class="newsforge-btn-secondary">다운로드</button>
                        </div>
                    </div>
                </div>
                
                <div class="newsforge-sidebar">
                    <?php if ($atts['show_ads'] === 'true'): ?>
                        <!-- 사이드바 AdSense -->
                        <div class="newsforge-ad-sidebar">
                            <?php echo $this->get_adsense_code('sidebar'); ?>
                        </div>
                    <?php endif; ?>
                    
                    <!-- 사용 통계 -->
                    <div class="newsforge-stats-widget">
                        <h4>사용 통계</h4>
                        <div id="usage-stats">
                            <?php if (is_user_logged_in()): ?>
                                <p>오늘: <span id="today-usage">0</span>회</p>
                                <p>이번 달: <span id="month-usage">0</span>회</p>
                                <p>전체: <span id="total-usage">0</span>회</p>
                            <?php else: ?>
                                <p>회원가입하여 사용 통계를 확인하세요</p>
                                <a href="<?php echo wp_registration_url(); ?>" class="newsforge-btn-premium">회원가입</a>
                            <?php endif; ?>
                        </div>
                    </div>
                    
                    <!-- 프리미엄 업그레이드 -->
                    <?php if (!$this->is_premium_user()): ?>
                        <div class="newsforge-premium-widget">
                            <h4>💎 프리미엄 업그레이드</h4>
                            <ul>
                                <li>✅ 무제한 변환</li>
                                <li>✅ 배치 처리</li>
                                <li>✅ 우선 지원</li>
                                <li>✅ API 액세스</li>
                            </ul>
                            <a href="/premium" class="newsforge-btn-premium">업그레이드</a>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    // 통계 쇼트코드
    public function stats_shortcode($atts) {
        if (!is_user_logged_in()) {
            return '<p>통계를 보려면 로그인이 필요합니다.</p>';
        }
        
        $stats = $this->get_user_stats();
        
        ob_start();
        ?>
        <div class="newsforge-stats-dashboard">
            <h3>사용 통계</h3>
            <div class="newsforge-stats-grid">
                <div class="newsforge-stat-item">
                    <div class="newsforge-stat-number"><?php echo $stats['today']; ?></div>
                    <div class="newsforge-stat-label">오늘</div>
                </div>
                <div class="newsforge-stat-item">
                    <div class="newsforge-stat-number"><?php echo $stats['week']; ?></div>
                    <div class="newsforge-stat-label">이번 주</div>
                </div>
                <div class="newsforge-stat-item">
                    <div class="newsforge-stat-number"><?php echo $stats['month']; ?></div>
                    <div class="newsforge-stat-label">이번 달</div>
                </div>
                <div class="newsforge-stat-item">
                    <div class="newsforge-stat-number"><?php echo $stats['total']; ?></div>
                    <div class="newsforge-stat-label">전체</div>
                </div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
    
    // REST API 엔드포인트 등록
    public function register_api_routes() {
        // 콘텐츠 변환 API
        register_rest_route('newsforge/v1', '/convert', array(
            'methods' => 'POST',
            'callback' => array($this, 'api_convert_content'),
            'permission_callback' => '__return_true',
            'args' => array(
                'url' => array('required' => true, 'sanitize_callback' => 'esc_url_raw'),
                'api_key' => array('required' => true, 'sanitize_callback' => 'sanitize_text_field'),
                'provider' => array('required' => true, 'sanitize_callback' => 'sanitize_text_field')
            )
        ));
        
        // API 키 검증 API
        register_rest_route('newsforge/v1', '/validate-key', array(
            'methods' => 'POST',
            'callback' => array($this, 'api_validate_key'),
            'permission_callback' => '__return_true'
        ));
        
        // 사용 통계 API
        register_rest_route('newsforge/v1', '/stats', array(
            'methods' => 'GET',
            'callback' => array($this, 'api_get_stats'),
            'permission_callback' => 'is_user_logged_in'
        ));
    }
    
    // API: 콘텐츠 변환
    public function api_convert_content($request) {
        $url = $request->get_param('url');
        $api_key = $request->get_param('api_key');
        $provider = $request->get_param('provider');
        
        // 사용량 제한 확인
        if (!$this->check_usage_limit()) {
            return new WP_Error('limit_exceeded', '사용 한도를 초과했습니다.', array('status' => 429));
        }
        
        // FastAPI 서버로 요청 전달
        $response = $this->call_fastapi_convert($url, $api_key, $provider);
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        // 사용량 업데이트
        $this->update_usage();
        
        // 애널리틱스 이벤트 기록
        $this->track_conversion_event($provider, $url);
        
        return rest_ensure_response($response);
    }
    
    // API: API 키 검증
    public function api_validate_key($request) {
        $api_key = $request->get_param('api_key');
        $provider = $request->get_param('provider');
        
        $fastapi_response = wp_remote_post(NEWSFORGE_FASTAPI_URL . '/api/v1/validate-key', array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode(array(
                'api_key' => $api_key,
                'provider' => $provider
            )),
            'timeout' => 10
        ));
        
        if (is_wp_error($fastapi_response)) {
            return new WP_Error('api_error', 'FastAPI 서버 연결 실패', array('status' => 500));
        }
        
        $body = wp_remote_retrieve_body($fastapi_response);
        return rest_ensure_response(json_decode($body, true));
    }
    
    // API: 사용 통계
    public function api_get_stats($request) {
        $stats = $this->get_user_stats();
        return rest_ensure_response($stats);
    }
    
    // FastAPI 변환 호출
    private function call_fastapi_convert($url, $api_key, $provider) {
        $response = wp_remote_post(NEWSFORGE_FASTAPI_URL . '/api/v1/convert', array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode(array(
                'url' => $url,
                'platforms' => array('markdown'),
                'converter_type' => $provider,
                'api_key' => $api_key,
                'api_provider' => $provider
            )),
            'timeout' => 70
        ));
        
        if (is_wp_error($response)) {
            return new WP_Error('api_error', 'FastAPI 서버 연결 실패', array('status' => 500));
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (!$data || !isset($data['task_id'])) {
            return new WP_Error('conversion_failed', '변환 요청 실패', array('status' => 500));
        }
        
        // 결과 폴링
        return $this->poll_conversion_result($data['task_id']);
    }
    
    // 변환 결과 폴링
    private function poll_conversion_result($task_id) {
        $max_attempts = 90;
        $poll_interval = 1;
        
        for ($i = 0; $i < $max_attempts; $i++) {
            sleep($poll_interval);
            
            $response = wp_remote_get(NEWSFORGE_FASTAPI_URL . "/api/v1/conversion/{$task_id}", array(
                'timeout' => 10
            ));
            
            if (!is_wp_error($response)) {
                $body = wp_remote_retrieve_body($response);
                $data = json_decode($body, true);
                
                if ($data && $data['status'] === 'completed') {
                    return array(
                        'success' => true,
                        'content' => $data['result'],
                        'message' => '변환이 성공적으로 완료되었습니다.'
                    );
                } elseif ($data && $data['status'] === 'failed') {
                    return new WP_Error('conversion_failed', $data['error'] ?? '변환 실패', array('status' => 500));
                }
            }
        }
        
        return new WP_Error('timeout', '변환 시간이 초과되었습니다.', array('status' => 408));
    }
    
    // 사용량 제한 확인
    private function check_usage_limit() {
        if ($this->is_premium_user()) {
            return true; // 프리미엄 사용자는 무제한
        }
        
        if (!is_user_logged_in()) {
            // 비로그인 사용자: IP 기반 일일 5회 제한
            $user_ip = $_SERVER['REMOTE_ADDR'];
            $usage_key = 'newsforge_usage_' . md5($user_ip . date('Y-m-d'));
            $current_usage = get_transient($usage_key) ?: 0;
            return $current_usage < 5;
        }
        
        // 일반 사용자: 일일 20회 제한
        $user_id = get_current_user_id();
        $usage_count = $this->get_daily_usage($user_id);
        return $usage_count < 20;
    }
    
    // 사용량 업데이트
    private function update_usage() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsforge_usage';
        
        $user_id = is_user_logged_in() ? get_current_user_id() : 0;
        $ip_address = $_SERVER['REMOTE_ADDR'];
        
        $wpdb->insert(
            $table_name,
            array(
                'user_id' => $user_id,
                'ip_address' => $ip_address,
                'created_at' => current_time('mysql')
            ),
            array('%d', '%s', '%s')
        );
        
        // 비로그인 사용자의 경우 임시 카운터 업데이트
        if (!is_user_logged_in()) {
            $usage_key = 'newsforge_usage_' . md5($ip_address . date('Y-m-d'));
            $current_usage = get_transient($usage_key) ?: 0;
            set_transient($usage_key, $current_usage + 1, DAY_IN_SECONDS);
        }
    }
    
    // 애드센스 코드 가져오기
    private function get_adsense_code($type) {
        $code = get_option("newsforge_adsense_{$type}");
        if ($code) {
            return $code;
        }
        
        // 기본 광고 플레이스홀더
        $sizes = array(
            'banner' => '728x90',
            'sidebar' => '300x250',
            'content' => '336x280'
        );
        
        return '<div class="newsforge-ad-placeholder">광고 영역 (' . $sizes[$type] . ')</div>';
    }
    
    // 사용자 통계 가져오기
    private function get_user_stats() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsforge_usage';
        $user_id = get_current_user_id();
        
        $today = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND DATE(created_at) = CURDATE()",
            $user_id
        ));
        
        $week = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND YEARWEEK(created_at) = YEARWEEK(CURDATE())",
            $user_id
        ));
        
        $month = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())",
            $user_id
        ));
        
        $total = $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d",
            $user_id
        ));
        
        return array(
            'today' => intval($today),
            'week' => intval($week),
            'month' => intval($month),
            'total' => intval($total)
        );
    }
    
    // 일일 사용량 가져오기
    private function get_daily_usage($user_id) {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsforge_usage';
        
        return $wpdb->get_var($wpdb->prepare(
            "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND DATE(created_at) = CURDATE()",
            $user_id
        ));
    }
    
    // 프리미엄 사용자 확인
    private function is_premium_user() {
        if (!is_user_logged_in()) {
            return false;
        }
        
        $user = wp_get_current_user();
        return in_array('premium_user', $user->roles);
    }
    
    // 프리미엄 사용자 역할 생성
    private function create_premium_role() {
        if (!get_role('premium_user')) {
            add_role('premium_user', '프리미엄 회원', array(
                'read' => true,
                'premium_features' => true,
                'unlimited_conversions' => true
            ));
        }
    }
    
    // 애널리틱스 이벤트 기록
    private function track_conversion_event($provider, $url) {
        // Google Analytics 이벤트 트래킹 코드
        if (get_option('newsforge_ga_id')) {
            add_action('wp_footer', function() use ($provider, $url) {
                ?>
                <script>
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'content_conversion', {
                        'event_category': 'NewsForge',
                        'event_label': '<?php echo esc_js($provider); ?>',
                        'value': 1,
                        'custom_parameters': {
                            'provider': '<?php echo esc_js($provider); ?>',
                            'source_domain': '<?php echo esc_js(parse_url($url, PHP_URL_HOST)); ?>'
                        }
                    });
                }
                </script>
                <?php
            });
        }
    }
    
    // 관리자 메뉴
    public function admin_menu() {
        add_menu_page(
            'NewsForge Pro',
            'NewsForge Pro',
            'manage_options',
            'newsforge-admin',
            array($this, 'admin_page'),
            'dashicons-edit-page',
            30
        );
        
        add_submenu_page(
            'newsforge-admin',
            '설정',
            '설정',
            'manage_options',
            'newsforge-settings',
            array($this, 'settings_page')
        );
        
        add_submenu_page(
            'newsforge-admin',
            '사용 통계',
            '사용 통계',
            'manage_options',
            'newsforge-stats',
            array($this, 'admin_stats_page')
        );
    }
    
    // 관리자 메인 페이지
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>NewsForge Pro</h1>
            <p>AI 기반 뉴스 콘텐츠 생성 플러그인 관리 페이지입니다.</p>
            
            <div class="newsforge-admin-dashboard">
                <h2>서버 상태</h2>
                <div id="server-status" class="newsforge-status-box">확인 중...</div>
                
                <h2>오늘의 통계</h2>
                <div class="newsforge-stats-summary">
                    <?php
                    global $wpdb;
                    $table_name = $wpdb->prefix . 'newsforge_usage';
                    $today_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE DATE(created_at) = CURDATE()");
                    ?>
                    <p><strong>오늘 변환 횟수:</strong> <?php echo intval($today_count); ?>회</p>
                </div>
            </div>
        </div>
        
        <script>
        // FastAPI 서버 상태 확인
        fetch('<?php echo NEWSFORGE_FASTAPI_URL; ?>/api/v1/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('server-status').innerHTML = '✅ FastAPI 서버 정상 작동';
                document.getElementById('server-status').className = 'newsforge-status-box success';
            })
            .catch(error => {
                document.getElementById('server-status').innerHTML = '❌ FastAPI 서버 연결 실패';
                document.getElementById('server-status').className = 'newsforge-status-box error';
            });
        </script>
        
        <style>
        .newsforge-status-box {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background: #f1f1f1;
        }
        .newsforge-status-box.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .newsforge-status-box.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        </style>
        <?php
    }
    
    // 설정 페이지
    public function settings_page() {
        if (isset($_POST['submit'])) {
            update_option('newsforge_adsense_banner', sanitize_textarea_field($_POST['adsense_banner']));
            update_option('newsforge_adsense_sidebar', sanitize_textarea_field($_POST['adsense_sidebar']));
            update_option('newsforge_adsense_content', sanitize_textarea_field($_POST['adsense_content']));
            update_option('newsforge_ga_id', sanitize_text_field($_POST['ga_id']));
            echo '<div class="notice notice-success"><p>설정이 저장되었습니다.</p></div>';
        }
        
        $adsense_banner = get_option('newsforge_adsense_banner', '');
        $adsense_sidebar = get_option('newsforge_adsense_sidebar', '');
        $adsense_content = get_option('newsforge_adsense_content', '');
        $ga_id = get_option('newsforge_ga_id', '');
        ?>
        <div class="wrap">
            <h1>NewsForge Pro 설정</h1>
            
            <form method="post" action="">
                <table class="form-table">
                    <tr>
                        <th scope="row">상단 배너 AdSense 코드 (728x90)</th>
                        <td><textarea name="adsense_banner" rows="5" cols="50"><?php echo esc_textarea($adsense_banner); ?></textarea></td>
                    </tr>
                    <tr>
                        <th scope="row">사이드바 AdSense 코드 (300x250)</th>
                        <td><textarea name="adsense_sidebar" rows="5" cols="50"><?php echo esc_textarea($adsense_sidebar); ?></textarea></td>
                    </tr>
                    <tr>
                        <th scope="row">콘텐츠 내 AdSense 코드 (336x280)</th>
                        <td><textarea name="adsense_content" rows="5" cols="50"><?php echo esc_textarea($adsense_content); ?></textarea></td>
                    </tr>
                    <tr>
                        <th scope="row">Google Analytics ID</th>
                        <td><input type="text" name="ga_id" value="<?php echo esc_attr($ga_id); ?>" placeholder="G-XXXXXXXXXX"></td>
                    </tr>
                </table>
                
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }
    
    // 관리자 통계 페이지
    public function admin_stats_page() {
        global $wpdb;
        $table_name = $wpdb->prefix . 'newsforge_usage';
        
        // 통계 데이터 가져오기
        $today_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE DATE(created_at) = CURDATE()");
        $week_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE YEARWEEK(created_at) = YEARWEEK(CURDATE())");
        $month_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())");
        
        ?>
        <div class="wrap">
            <h1>사용 통계</h1>
            
            <div class="newsforge-stats-grid">
                <div class="newsforge-stat-card">
                    <h3>오늘</h3>
                    <div class="newsforge-stat-number"><?php echo intval($today_count); ?></div>
                    <div class="newsforge-stat-label">변환 횟수</div>
                </div>
                <div class="newsforge-stat-card">
                    <h3>이번 주</h3>
                    <div class="newsforge-stat-number"><?php echo intval($week_count); ?></div>
                    <div class="newsforge-stat-label">변환 횟수</div>
                </div>
                <div class="newsforge-stat-card">
                    <h3>이번 달</h3>
                    <div class="newsforge-stat-number"><?php echo intval($month_count); ?></div>
                    <div class="newsforge-stat-label">변환 횟수</div>
                </div>
            </div>
            
            <h2>최근 사용 내역</h2>
            <?php
            $recent_usage = $wpdb->get_results(
                "SELECT u.*, us.display_name FROM {$table_name} u 
                 LEFT JOIN {$wpdb->users} us ON u.user_id = us.ID 
                 ORDER BY u.created_at DESC LIMIT 50",
                ARRAY_A
            );
            
            if ($recent_usage) {
                echo '<table class="wp-list-table widefat fixed striped">';
                echo '<thead><tr><th>사용자</th><th>IP 주소</th><th>시간</th></tr></thead><tbody>';
                
                foreach ($recent_usage as $usage) {
                    $username = $usage['display_name'] ?: '비회원';
                    echo '<tr>';
                    echo '<td>' . esc_html($username) . '</td>';
                    echo '<td>' . esc_html($usage['ip_address']) . '</td>';
                    echo '<td>' . esc_html($usage['created_at']) . '</td>';
                    echo '</tr>';
                }
                
                echo '</tbody></table>';
            } else {
                echo '<p>사용 내역이 없습니다.</p>';
            }
            ?>
        </div>
        
        <style>
        .newsforge-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .newsforge-stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .newsforge-stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #0073aa;
        }
        .newsforge-stat-label {
            color: #666;
            margin-top: 5px;
        }
        </style>
        <?php
    }
    
    // 플러그인 활성화
    public function activate() {
        $this->create_database_tables();
        $this->create_premium_role();
        
        // 기본 설정값 설정
        add_option('newsforge_adsense_banner', '');
        add_option('newsforge_adsense_sidebar', '');
        add_option('newsforge_adsense_content', '');
        add_option('newsforge_ga_id', '');
        
        flush_rewrite_rules();
    }
    
    // 플러그인 비활성화
    public function deactivate() {
        flush_rewrite_rules();
    }
    
    // 데이터베이스 테이블 생성
    private function create_database_tables() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'newsforge_usage';
        
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) DEFAULT 0,
            ip_address varchar(45) NOT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY user_id (user_id),
            KEY created_at (created_at),
            KEY ip_address (ip_address)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
}

// 플러그인 인스턴스 초기화
new NewsForgeProPlugin();

?> 