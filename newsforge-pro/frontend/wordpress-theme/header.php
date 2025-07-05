<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- AdSense 태그 (사이트 전체) -->
    <?php if (get_theme_mod('adsense_publisher_id')): ?>
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=<?php echo get_theme_mod('adsense_publisher_id'); ?>" crossorigin="anonymous"></script>
    <?php endif; ?>
    
    <!-- Google Analytics -->
    <?php if (get_theme_mod('google_analytics_id')): ?>
        <script async src="https://www.googletagmanager.com/gtag/js?id=<?php echo get_theme_mod('google_analytics_id'); ?>"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '<?php echo get_theme_mod('google_analytics_id'); ?>');
        </script>
    <?php endif; ?>
    
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
    <div class="container">
        <div class="site-branding">
            <?php if (has_custom_logo()): ?>
                <div class="site-logo">
                    <?php the_custom_logo(); ?>
                </div>
            <?php endif; ?>
            
            <a href="<?php echo esc_url(home_url('/')); ?>" class="site-title">
                🚀 NewsForge Pro
                <span style="font-size: 0.6em; color: #6b7280;">Beta</span>
            </a>
        </div>
        
        <nav class="main-navigation">
            <div class="nav-links">
                <?php if (is_user_logged_in()): ?>
                    <a href="/dashboard" class="nav-link">대시보드</a>
                    <a href="/premium" class="nav-link">프리미엄</a>
                    <a href="<?php echo wp_logout_url(home_url()); ?>" class="nav-link">로그아웃</a>
                <?php else: ?>
                    <a href="/wp-login.php" class="nav-link">로그인</a>
                    <a href="/wp-login.php?action=register" class="nav-link premium-btn">회원가입</a>
                <?php endif; ?>
            </div>
        </nav>
    </div>
</header>

<main id="main" class="site-main"> 