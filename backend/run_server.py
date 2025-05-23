import subprocess
import time
from pyngrok import ngrok, exception

# ngrok 인증 토큰 설정 및 터널 생성
def setup_ngrok(auth_token):
    try:
        ngrok.set_auth_token(auth_token)
        
        # 기존 세션 확인 및 종료
        try:
            sessions = ngrok.get_tunnels()
            if sessions:
                print("기존 ngrok 세션이 감지되었습니다. 세션을 종료합니다.")
                ngrok.kill()
        except:
            pass
        
        # ngrok 터널 생성
        http_tunnel = ngrok.connect(3000)
        public_url = http_tunnel.public_url
        print(f"\n* ngrok 터널이 생성되었습니다: {public_url}")
        print("* 이 URL을 통해 외부에서 채팅 애플리케이션에 접속할 수 있습니다.\n")
        
        return public_url
    except exception.PyngrokNgrokError as e:
        print(f"ngrok 에러: {e}")
        raise

if __name__ == "__main__":
    # FastAPI 서버 시작
    try:
        server_process = subprocess.Popen(["python", "app/app.py"])
        print("FastAPI 서버가 시작되었습니다.")

        # 서버가 시작될 때까지 대기
        time.sleep(3)  # FastAPI 서버가 포트를 점유할 시간 확보
    except Exception as e:
        print(f"에러: FastAPI 서버 시작 중 오류 발생: {e}")
        exit(1)
    
    try:
         # ngrok 인증 토큰 입력 받기
        auth_token = input("ngrok 인증 토큰을 입력하세요: ")

        # ngrok 설정
        public_url = setup_ngrok(auth_token)
        
        # 앱이 계속 실행되도록 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 종료 시 프로세스 정리
        print("\n종료 중...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)  # 우아한 종료 대기
        except subprocess.TimeoutExpired:
            server_process.kill()  # 강제 종료
        ngrok.kill()
        print("ngrok 터널 및 FastAPI 서버가 종료되었습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")
        server_process.terminate()
        ngrok.kill()
        print("ngrok 터널 및 FastAPI 서버가 종료되었습니다.")