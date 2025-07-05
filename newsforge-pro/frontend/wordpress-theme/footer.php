</main>

<footer class="site-footer">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h4>NewsForge Pro</h4>
                <p>AI 기반 뉴스 콘텐츠 생성 서비스</p>
                <p>뉴스 기사를 체계적인 콘텐츠로 변환하세요</p>
            </div>
            
            <div class="footer-section">
                <h4>서비스</h4>
                <ul>
                    <li><a href="/">콘텐츠 생성</a></li>
                    <li><a href="/premium">프리미엄</a></li>
                    <li><a href="/api">API 문서</a></li>
                    <li><a href="/help">도움말</a></li>
                </ul>
            </div>
            
            <div class="footer-section">
                <h4>회사</h4>
                <ul>
                    <li><a href="/about">회사 소개</a></li>
                    <li><a href="/privacy">개인정보처리방침</a></li>
                    <li><a href="/terms">이용약관</a></li>
                    <li><a href="/contact">문의하기</a></li>
                </ul>
            </div>
            
            <div class="footer-section">
                <h4>연락처</h4>
                <p>Email: support@newsforge.pro</p>
                <p>대한민국 서울특별시</p>
                <div class="social-links">
                    <a href="#" class="social-link">Twitter</a>
                    <a href="#" class="social-link">LinkedIn</a>
                    <a href="#" class="social-link">GitHub</a>
                </div>
            </div>
        </div>
        
        <div class="footer-bottom">
            <p>&copy; <?php echo date('Y'); ?> NewsForge Pro. All rights reserved.</p>
            <p>Powered by AI • Made with ❤️</p>
        </div>
    </div>
</footer>

<style>
.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.footer-section h4 {
    color: #ffffff;
    margin-bottom: 1rem;
    font-size: 1.125rem;
    font-weight: 600;
}

.footer-section ul {
    list-style: none;
    padding: 0;
}

.footer-section ul li {
    margin-bottom: 0.5rem;
}

.footer-section a {
    color: #d1d5db;
    text-decoration: none;
    transition: color 0.2s;
}

.footer-section a:hover {
    color: #ffffff;
}

.footer-bottom {
    border-top: 1px solid #374151;
    padding-top: 2rem;
    text-align: center;
    color: #9ca3af;
    font-size: 0.875rem;
}

.social-links {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.social-link {
    color: #d1d5db;
    text-decoration: none;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.social-link:hover {
    background-color: #374151;
    color: #ffffff;
}

.nav-links {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.nav-link {
    color: #4b5563;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.2s;
}

.nav-link:hover {
    color: #1f2937;
    background-color: #f3f4f6;
}

.site-branding {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.site-header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@media (max-width: 768px) {
    .footer-content {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .site-header .container {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav-links {
        flex-wrap: wrap;
        justify-content: center;
    }
}
</style>

<?php wp_footer(); ?>
</body>
</html> 