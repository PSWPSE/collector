#!/usr/bin/env python3
"""
NewsForge Pro FastAPI 서버 관리 스크립트
- 포트 정리
- 서버 시작/중지
- Health check
- 자동 복구
"""

import os
import sys
import time
import signal
import subprocess
import requests
import psutil
from pathlib import Path

# 설정
BACKEND_DIR = Path(__file__).parent
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
HEALTH_URL = f"http://127.0.0.1:{SERVER_PORT}/api/v1/health"
MAX_STARTUP_TIME = 30  # 최대 30초 대기

class ServerManager:
    def __init__(self):
        self.process = None
        self.backend_dir = BACKEND_DIR
        
    def cleanup_port(self, port: int) -> bool:
        """포트를 사용하는 프로세스들을 정리합니다."""
        print(f"🧹 포트 {port} 정리 중...")
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                                print(f"  ⚠️  PID {proc.info['pid']} ({proc.info['name']}) 종료 중...")
                                proc.kill()
                                killed_count += 1
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"포트 정리 중 오류: {e}")
            
        if killed_count > 0:
            print(f"✅ {killed_count}개 프로세스 종료됨")
            time.sleep(2)  # 프로세스 종료 대기
        else:
            print("✅ 정리할 프로세스 없음")
            
        return killed_count > 0
    
    def check_health(self, timeout: int = 5) -> bool:
        """서버 health check를 수행합니다."""
        try:
            response = requests.get(HEALTH_URL, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_server(self, max_wait: int = MAX_STARTUP_TIME) -> bool:
        """서버가 준비될 때까지 대기합니다."""
        print(f"⏳ 서버 시작 대기 중 (최대 {max_wait}초)...")
        
        for i in range(max_wait):
            if self.check_health():
                print(f"✅ 서버 준비 완료! ({i+1}초 소요)")
                return True
            
            if i % 5 == 0 and i > 0:
                print(f"  대기 중... {i}/{max_wait}초")
                
            time.sleep(1)
            
        print(f"❌ 서버 시작 타임아웃 ({max_wait}초)")
        return False
    
    def start_server(self, production: bool = False) -> bool:
        """서버를 시작합니다."""
        print("🚀 NewsForge Pro 서버 시작 중...")
        
        # 1. 포트 정리
        self.cleanup_port(SERVER_PORT)
        
        # 2. 환경 변수 설정
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.backend_dir)
        
        # 3. 서버 시작 명령 구성
        if production:
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app",
                "--host", SERVER_HOST,
                "--port", str(SERVER_PORT),
                "--workers", "1"
            ]
        else:
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app.main:app",
                "--host", SERVER_HOST,
                "--port", str(SERVER_PORT),
                "--reload",
                "--reload-exclude", "*.log",
                "--reload-exclude", "*.txt",
                "--reload-exclude", "temp_*",
                "--reload-exclude", "__pycache__"
            ]
        
        # 4. 서버 시작
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.backend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            print(f"📡 서버 프로세스 시작됨 (PID: {self.process.pid})")
            
            # 5. 서버 준비 대기
            if self.wait_for_server():
                print(f"✅ FastAPI 서버가 http://{SERVER_HOST}:{SERVER_PORT}에서 실행 중")
                return True
            else:
                print("❌ 서버 시작 실패")
                self.stop_server()
                return False
                
        except Exception as e:
            print(f"❌ 서버 시작 오류: {e}")
            return False
    
    def stop_server(self):
        """서버를 중지합니다."""
        print("🛑 서버 중지 중...")
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("✅ 서버 정상 종료됨")
            except subprocess.TimeoutExpired:
                print("⚠️  강제 종료 중...")
                self.process.kill()
                self.process.wait()
                print("✅ 서버 강제 종료됨")
        
        # 포트 재정리
        self.cleanup_port(SERVER_PORT)
    
    def restart_server(self, production: bool = False) -> bool:
        """서버를 재시작합니다."""
        print("🔄 서버 재시작 중...")
        self.stop_server()
        time.sleep(2)
        return self.start_server(production)
    
    def status(self) -> dict:
        """서버 상태를 확인합니다."""
        health_ok = self.check_health()
        
        status = {
            "running": health_ok,
            "port": SERVER_PORT,
            "health_url": HEALTH_URL,
            "backend_dir": str(self.backend_dir)
        }
        
        if health_ok:
            print("✅ 서버 정상 동작 중")
        else:
            print("❌ 서버 연결 실패")
            
        return status


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NewsForge Pro 서버 관리")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "health"], 
                       help="수행할 작업")
    parser.add_argument("--production", action="store_true", 
                       help="프로덕션 모드로 실행")
    
    args = parser.parse_args()
    
    manager = ServerManager()
    
    if args.action == "start":
        success = manager.start_server(args.production)
        sys.exit(0 if success else 1)
        
    elif args.action == "stop":
        manager.stop_server()
        
    elif args.action == "restart":
        success = manager.restart_server(args.production)
        sys.exit(0 if success else 1)
        
    elif args.action == "status":
        status = manager.status()
        print(f"서버 상태: {status}")
        
    elif args.action == "health":
        if manager.check_health():
            print("✅ Health check 성공")
            sys.exit(0)
        else:
            print("❌ Health check 실패")
            sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단됨")
        manager = ServerManager()
        manager.stop_server()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1) 