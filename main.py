from core.extractor import WebExtractor
import sys

def main():
    if len(sys.argv) != 2:
        print("사용법: python main.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        # Requests 방식으로만 추출 실행
        extractor = WebExtractor(use_selenium=False)
        data = extractor.extract_data(url)
        extractor.close()
        
        if data['success']:
            print("추출 성공!")
        else:
            print(f"추출 실패: {data.get('error', '알 수 없는 오류')}")
            
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 