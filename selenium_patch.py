import re

# web_extractor.py 파일 패치
with open('extractors/single/web_extractor.py', 'r') as f:
    content = f.read()

# Selenium 설정 개선
old_setup = '''    def setup_selenium(self) -> None:
        """Selenium 웹드라이버 설정"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self.ua.random}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)'''

new_setup = '''    def setup_selenium(self) -> None:
        """Selenium 웹드라이버 설정"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--page-load-strategy=eager')
        options.add_argument(f'user-agent={self.ua.random}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(15)
        self.driver.implicitly_wait(10)'''

content = content.replace(old_setup, new_setup)

# WebDriverWait 시간 단축
content = re.sub(r'WebDriverWait\(self\.driver, 20\)', 'WebDriverWait(self.driver, 10)', content)

with open('extractors/single/web_extractor.py', 'w') as f:
    f.write(content)

print("Selenium 설정 최적화 완료")
