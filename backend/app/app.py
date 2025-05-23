from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import cv2
from ultralytics import YOLO
import os
import base64
from PIL import Image
from io import BytesIO
import pathlib

# FastAPI 앱 생성
app = FastAPI()

# CORS 미들웨어 설정 (모든 오리진 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="./www/static"), name="static")
templates = Jinja2Templates(directory="./www")

# YOLOv8 모델 로드
model = YOLO("yolov8n.pt")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/info")
async def api_info():
    return {"message": "YOLOv8 Object Detection API"}

@app.post("/api/detect")
async def detect_objects(image: UploadFile = File(...)):
    # 이미지 읽기
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # YOLOv8로 객체 감지
    results = model(img)
    result = results[0]
    
    # 결과 처리
    detected_objects = []
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = result.names[cls_id]
        
        detected_objects.append({
            "class": cls_name,
            "confidence": round(conf, 2),
            "bbox": [x1, y1, x2, y2]
        })
    
    # 바운딩 박스가 있는 이미지 생성
    for obj in detected_objects:
        x1, y1, x2, y2 = obj["bbox"]
        cls_name = obj["class"]
        conf = obj["confidence"]
        
        # 바운딩 박스 그리기
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 레이블 텍스트
        label = f"{cls_name} {conf:.2f}"
        
        # 텍스트 배경
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
        
        # 텍스트 추가
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # 이미지를 base64로 인코딩
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "detected_objects": detected_objects,
        "processed_image": f"data:image/jpeg;base64,{img_base64}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

# # FastAPI 서버를 별도 스레드에서 실행
# def run_fastapi():
#     uvicorn.run(app, host="0.0.0.0", port=3000, reload=False)

# # ngrok 인증 토큰 설정 및 터널 생성
# def setup_ngrok(auth_token):
#     ngrok.set_auth_token(auth_token)
    
#     # ngrok 터널 생성 (포트 3000에 바인딩)
#     http_tunnel = ngrok.connect(3000)
#     public_url = http_tunnel.public_url
#     print(f"\n* ngrok 터널이 생성되었습니다: {public_url}")
#     print("* 이 URL을 통해 외부에서 채팅 애플리케이션에 접속할 수 있습니다.\n")
    
#     return public_url

# if __name__ == "__main__":
#     # ngrok 인증 토큰 입력 받기
#     auth_token = input("ngrok 인증 토큰을 입력하세요: ")
    
#     # FastAPI 서버를 스레드로 실행
#     fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
#     fastapi_thread.start()
    
#     # FastAPI 서버가 시작될 때까지 약간 대기
#     time.sleep(2)  # 서버 시작을 보장하기 위해 2초 대기
    
#     # ngrok 설정
#     public_url = setup_ngrok(auth_token)
    
#     try:
#         # 메인 스레드 대기
#         fastapi_thread.join()
#     except KeyboardInterrupt:
#         # 종료 시 ngrok 터널 정리
#         ngrok.kill()
#         print("\nngrok 터널 및 FastAPI 서버가 종료되었습니다.")