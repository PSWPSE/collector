<?php
/**
 * NewsForge Pro WordPress Theme Functions
 * FastAPI 백엔드 연동 및 애드센스 수익화 기능
 */

// 테마 설정
function newsforge_setup() {
    // 테마 지원 기능 추가
    add_theme_support('title-tag');
    add_theme_support('custom-logo');
    add_theme_support('post-thumbnails');
    
    // 메뉴 등록
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'newsforge'),
        'footer' => __('Footer Menu', 'newsforge'),
    ));
}
add_action('after_setup_theme', 'newsforge_setup');

// 스타일시트 및 스크립트 로드
function newsforge_scripts() {
    wp_enqueue_style('newsforge-style', get_stylesheet_uri());
    wp_enqueue_script('newsforge-script', get_template_directory_uri() . '/assets/js/main.js', array('jquery'), '1.0.0', true);
    
    // AJAX URL을 JavaScript에 전달
    wp_localize_script('newsforge-script', 'newsforge_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('newsforge_nonce'),
        'fastapi_url' => 'http://127.0.0.1:8000' // FastAPI 서버 URL
    ));
}
add_action('wp_enqueue_scripts', 'newsforge_scripts');

// 커스터마이저 설정 (애드센스 및 분석)
function newsforge_customize_register($wp_customize) {
    // 애드센스 섹션
    $wp_customize->add_section('adsense_section', array(
        'title' => '애드센스 설정',
        'priority' => 30,
    ));
    
    // 애드센스 퍼블리셔 ID
    $wp_customize->add_setting('adsense_publisher_id', array(
        'default' => '',
        'sanitize_callback' => 'sanitize_text_field',
    ));
    
    $wp_customize->add_control('adsense_publisher_id', array(
        'label' => '애드센스 퍼블리셔 ID',
        'section' => 'adsense_section',
        'type' => 'text',
        'description' => 'ca-pub-XXXXXXXXXXXXXXX 형식으로 입력하세요',
    ));
    
    // 상단 배너 광고 코드
    $wp_customize->add_setting('adsense_banner_code', array(
        'default' => '',
        'sanitize_callback' => 'wp_kses_post',
    ));
    
    $wp_customize->add_control('adsense_banner_code', array(
        'label' => '상단 배너 광고 코드 (728x90)',
        'section' => 'adsense_section',
        'type' => 'textarea',
    ));
    
    // 사이드바 광고 코드
    $wp_customize->add_setting('adsense_sidebar_code', array(
        'default' => '',
        'sanitize_callback' => 'wp_kses_post',
    ));
    
    $wp_customize->add_control('adsense_sidebar_code', array(
        'label' => '사이드바 광고 코드 (300x250)',
        'section' => 'adsense_section',
        'type' => 'textarea',
    ));
    
    // 콘텐츠 내 광고 코드
    $wp_customize->add_setting('adsense_content_code', array(
        'default' => '',
        'sanitize_callback' => 'wp_kses_post',
    ));
    
    $wp_customize->add_control('adsense_content_code', array(
        'label' => '콘텐츠 내 광고 코드 (336x280)',
        'section' => 'adsense_section',
        'type' => 'textarea',
    ));
    
    // Google Analytics 섹션
    $wp_customize->add_section('analytics_section', array(
        'title' => 'Google Analytics',
        'priority' => 31,
    ));
    
    $wp_customize->add_setting('google_analytics_id', array(
        'default' => '',
        'sanitize_callback' => 'sanitize_text_field',
    ));
    
    $wp_customize->add_control('google_analytics_id', array(
        'label' => 'Google Analytics ID',
        'section' => 'analytics_section',
        'type' => 'text',
        'description' => 'G-XXXXXXXXXX 형식으로 입력하세요',
    ));
}
add_action('customize_register', 'newsforge_customize_register');

// REST API 엔드포인트 등록
function newsforge_register_api_routes() {
    // API 키 검증 엔드포인트
    register_rest_route('newsforge/v1', '/validate-key', array(
        'methods' => 'POST',
        'callback' => 'newsforge_validate_api_key',
        'permission_callback' => '__return_true',
    ));
    
    // 콘텐츠 변환 엔드포인트
    register_rest_route('newsforge/v1', '/convert', array(
        'methods' => 'POST',
        'callback' => 'newsforge_convert_content',
        'permission_callback' => '__return_true',
    ));
    
    // 사용 통계 엔드포인트
    register_rest_route('newsforge/v1', '/usage', array(
        'methods' => 'GET',
        'callback' => 'newsforge_get_usage_stats',
        'permission_callback' => 'is_user_logged_in',
    ));
}
add_action('rest_api_init', 'newsforge_register_api_routes');

// API 키 검증 함수
function newsforge_validate_api_key($request) {
    $api_key = sanitize_text_field($request->get_param('api_key'));
    $provider = sanitize_text_field($request->get_param('provider'));
    
    if (empty($api_key) || empty($provider)) {
        return new WP_Error('missing_params', '필수 매개변수가 누락되었습니다.', array('status' => 400));
    }
    
    // FastAPI 서버로 검증 요청 전달
    $fastapi_url = 'http://127.0.0.1:8000/api/v1/validate-key';
    $response = wp_remote_post($fastapi_url, array(
        'headers' => array('Content-Type' => 'application/json'),
        'body' => json_encode(array(
            'api_key' => $api_key,
            'provider' => $provider
        )),
        'timeout' => 10
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'FastAPI 서버 연결 실패', array('status' => 500));
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    return rest_ensure_response($data);
}

// 콘텐츠 변환 함수
function newsforge_convert_content($request) {
    $url = esc_url_raw($request->get_param('url'));
    $api_key = sanitize_text_field($request->get_param('api_key'));
    $provider = sanitize_text_field($request->get_param('provider'));
    
    if (empty($url) || empty($api_key) || empty($provider)) {
        return new WP_Error('missing_params', '필수 매개변수가 누락되었습니다.', array('status' => 400));
    }
    
    // 사용 제한 확인 (비로그인 사용자)
    if (!is_user_logged_in()) {
        $daily_limit = 5;
        $user_ip = $_SERVER['REMOTE_ADDR'];
        $usage_key = 'newsforge_usage_' . md5($user_ip . date('Y-m-d'));
        $current_usage = get_transient($usage_key) ?: 0;
        
        if ($current_usage >= $daily_limit) {
            return new WP_Error('limit_exceeded', '일일 사용 한도를 초과했습니다. 회원가입하여 무제한 사용하세요.', array('status' => 429));
        }
    }
    
    // FastAPI 서버로 변환 요청 전달
    $fastapi_url = 'http://127.0.0.1:8000/api/v1/convert';
    $response = wp_remote_post($fastapi_url, array(
        'headers' => array('Content-Type' => 'application/json'),
        'body' => json_encode(array(
            'url' => $url,
            'platforms' => array('markdown'),
            'converter_type' => $provider,
            'api_key' => $api_key,
            'api_provider' => $provider
        )),
        'timeout' => 70 // 70초 타임아웃
    ));
    
    if (is_wp_error($response)) {
        return new WP_Error('api_error', 'FastAPI 서버 연결 실패: ' . $response->get_error_message(), array('status' => 500));
    }
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (!$data || !isset($data['task_id'])) {
        return new WP_Error('conversion_failed', '변환 요청 실패', array('status' => 500));
    }
    
    // 결과 폴링
    $task_id = $data['task_id'];
    $max_attempts = 90; // 90초
    $poll_interval = 1; // 1초
    
    for ($i = 0; $i < $max_attempts; $i++) {
        sleep($poll_interval);
        
        $status_response = wp_remote_get("http://127.0.0.1:8000/api/v1/conversion/{$task_id}", array(
            'timeout' => 10
        ));
        
        if (!is_wp_error($status_response)) {
            $status_body = wp_remote_retrieve_body($status_response);
            $status_data = json_decode($status_body, true);
            
            if ($status_data && $status_data['status'] === 'completed') {
                // 사용량 업데이트
                newsforge_update_usage($user_ip ?? null);
                
                // Google Analytics 이벤트 트래킹
                newsforge_track_conversion_event($provider, $url);
                
                return rest_ensure_response(array(
                    'success' => true,
                    'content' => $status_data['result'],
                    'message' => '변환이 성공적으로 완료되었습니다.'
                ));
            } elseif ($status_data && $status_data['status'] === 'failed') {
                return new WP_Error('conversion_failed', $status_data['error'] ?? '변환 실패', array('status' => 500));
            }
        }
    }
    
    return new WP_Error('timeout', '변환 시간이 초과되었습니다.', array('status' => 408));
}

// 사용 통계 함수
function newsforge_get_usage_stats($request) {
    $user_id = get_current_user_id();
    
    if (!$user_id) {
        return new WP_Error('unauthorized', '로그인이 필요합니다.', array('status' => 401));
    }
    
    global $wpdb;
    $table_name = $wpdb->prefix . 'newsforge_usage';
    
    // 오늘 사용량
    $today_usage = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND DATE(created_at) = CURDATE()",
        $user_id
    ));
    
    // 이번 달 사용량
    $month_usage = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d AND YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())",
        $user_id
    ));
    
    // 전체 사용량
    $total_usage = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(*) FROM {$table_name} WHERE user_id = %d",
        $user_id
    ));
    
    return rest_ensure_response(array(
        'today' => intval($today_usage),
        'month' => intval($month_usage),
        'total' => intval($total_usage)
    ));
}

// 사용량 업데이트 함수
function newsforge_update_usage($user_ip = null) {
    global $wpdb;
    $table_name = $wpdb->prefix . 'newsforge_usage';
    
    $user_id = is_user_logged_in() ? get_current_user_id() : 0;
    $ip_address = $user_ip ?: $_SERVER['REMOTE_ADDR'];
    
    $wpdb->insert(
        $table_name,
        array(
            'user_id' => $user_id,
            'ip_address' => $ip_address,
            'created_at' => current_time('mysql')
        ),
        array('%d', '%s', '%s')
    );
    
    // 비로그인 사용자 일일 사용량 업데이트
    if (!is_user_logged_in()) {
        $usage_key = 'newsforge_usage_' . md5($ip_address . date('Y-m-d'));
        $current_usage = get_transient($usage_key) ?: 0;
        set_transient($usage_key, $current_usage + 1, DAY_IN_SECONDS);
    }
}

// Google Analytics 이벤트 트래킹
function newsforge_track_conversion_event($provider, $url) {
    if (get_theme_mod('google_analytics_id')) {
        ?>
        <script>
        if (typeof gtag !== 'undefined') {
            gtag('event', 'content_conversion', {
                'event_category': 'Service Usage',
                'event_label': '<?php echo esc_js($provider); ?>',
                'value': 1,
                'custom_map': {
                    'provider': '<?php echo esc_js($provider); ?>',
                    'source_url': '<?php echo esc_js(parse_url($url, PHP_URL_HOST)); ?>'
                }
            });
        }
        </script>
        <?php
    }
}

// 데이터베이스 테이블 생성
function newsforge_create_tables() {
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
        KEY created_at (created_at)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
}

// 테마 활성화 시 테이블 생성
function newsforge_activation() {
    newsforge_create_tables();
    
    // 기본 페이지 생성
    $pages = array(
        'premium' => '프리미엄',
        'dashboard' => '대시보드',
        'help' => '도움말',
        'about' => '회사 소개',
        'privacy' => '개인정보처리방침',
        'terms' => '이용약관'
    );
    
    foreach ($pages as $slug => $title) {
        if (!get_page_by_path($slug)) {
            wp_insert_post(array(
                'post_title' => $title,
                'post_name' => $slug,
                'post_content' => "[$slug] 페이지 내용",
                'post_status' => 'publish',
                'post_type' => 'page'
            ));
        }
    }
}
add_action('after_switch_theme', 'newsforge_activation');

// AJAX 핸들러: 사용 통계 업데이트
function newsforge_ajax_update_usage() {
    check_ajax_referer('newsforge_nonce', 'nonce');
    
    newsforge_update_usage();
    
    wp_die('success');
}
add_action('wp_ajax_update_usage_stats', 'newsforge_ajax_update_usage');
add_action('wp_ajax_nopriv_update_usage_stats', 'newsforge_ajax_update_usage');

// 프리미엄 사용자 역할 추가
function newsforge_add_premium_role() {
    add_role('premium_user', '프리미엄 회원', array(
        'read' => true,
        'premium_features' => true,
        'unlimited_conversions' => true
    ));
}
add_action('init', 'newsforge_add_premium_role');

// 프리미엄 기능 확인
function is_premium_user($user_id = null) {
    if (!$user_id) {
        $user_id = get_current_user_id();
    }
    
    if (!$user_id) {
        return false;
    }
    
    $user = get_user_by('id', $user_id);
    return $user && in_array('premium_user', $user->roles);
}

// 관리자 메뉴 추가
function newsforge_admin_menu() {
    add_menu_page(
        'NewsForge Pro',
        'NewsForge Pro',
        'manage_options',
        'newsforge-admin',
        'newsforge_admin_page',
        'dashicons-edit-page',
        30
    );
    
    add_submenu_page(
        'newsforge-admin',
        '사용 통계',
        '사용 통계',
        'manage_options',
        'newsforge-stats',
        'newsforge_stats_page'
    );
}
add_action('admin_menu', 'newsforge_admin_menu');

// 관리자 페이지
function newsforge_admin_page() {
    ?>
    <div class="wrap">
        <h1>NewsForge Pro 설정</h1>
        <p>뉴스 콘텐츠 생성 서비스 관리 페이지입니다.</p>
        
        <h2>FastAPI 서버 상태</h2>
        <div id="server-status">확인 중...</div>
        
        <h2>최근 변환 현황</h2>
        <div id="recent-conversions">로딩 중...</div>
    </div>
    
    <script>
    // FastAPI 서버 상태 확인
    fetch('http://127.0.0.1:8000/api/v1/health')
        .then(response => response.json())
        .then(data => {
            document.getElementById('server-status').innerHTML = '✅ FastAPI 서버 정상 작동';
        })
        .catch(error => {
            document.getElementById('server-status').innerHTML = '❌ FastAPI 서버 연결 실패';
        });
    </script>
    <?php
}

// 통계 페이지
function newsforge_stats_page() {
    global $wpdb;
    $table_name = $wpdb->prefix . 'newsforge_usage';
    
    // 오늘 사용량
    $today_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE DATE(created_at) = CURDATE()");
    
    // 이번 주 사용량
    $week_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE WEEK(created_at) = WEEK(CURDATE())");
    
    // 이번 달 사용량
    $month_count = $wpdb->get_var("SELECT COUNT(*) FROM {$table_name} WHERE MONTH(created_at) = MONTH(CURDATE())");
    
    ?>
    <div class="wrap">
        <h1>사용 통계</h1>
        
        <div class="notice notice-info">
            <p><strong>오늘 변환 횟수:</strong> <?php echo intval($today_count); ?>회</p>
            <p><strong>이번 주 변환 횟수:</strong> <?php echo intval($week_count); ?>회</p>
            <p><strong>이번 달 변환 횟수:</strong> <?php echo intval($month_count); ?>회</p>
        </div>
        
        <h2>최근 사용 내역</h2>
        <?php
        $recent_usage = $wpdb->get_results(
            "SELECT * FROM {$table_name} ORDER BY created_at DESC LIMIT 20",
            ARRAY_A
        );
        
        if ($recent_usage) {
            echo '<table class="wp-list-table widefat fixed striped">';
            echo '<thead><tr><th>사용자</th><th>IP 주소</th><th>시간</th></tr></thead><tbody>';
            
            foreach ($recent_usage as $usage) {
                $user = $usage['user_id'] ? get_user_by('id', $usage['user_id']) : null;
                $username = $user ? $user->display_name : '비회원';
                
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
    <?php
}

?> 