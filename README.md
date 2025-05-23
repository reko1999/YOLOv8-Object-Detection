# YOLOv8-Object-Detection
YOLOv8 기반 실시간 객체 인식 웹 서비스

## 개요
모바일 카메라로 촬영한 영상을 YOLOv8 모델로 실시간 객체 인식, 웹 UI에 결과를 표시. FastAPI와 React 기반, ngrok으로 외부 접근.

## 설치
1. Python 3.8 이상.
3. YOLOv8 모델: `yolo task=detect mode=predict model=yolov8n.pt`.
4. ngrok 설치 및 인증 토큰 설정.

## 실행
1. FastAPI: `python app.py`.
2. ngrok: `python run_server.py`.
3. 공개 URL로 접속.

## API 사용법
- **엔드포인트**: `/api/detect`
- **메서드**: POST
- **요청**: FormData `image` 필드에 JPEG 이미지.
- **응답**: JSON (객체 정보, base64 이미지).
