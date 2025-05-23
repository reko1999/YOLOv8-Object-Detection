import './App.css';
import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [cameraMode, setCameraMode] = useState('environment'); // 기본값은 후면 카메라
  const [isStreaming, setIsStreaming] = useState(false);
  const [detectedObjects, setDetectedObjects] = useState([]);
  const [processedImage, setProcessedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  
  // 카메라 시작
  const startCamera = async () => {
      try {
          if (streamRef.current) {
              streamRef.current.getTracks().forEach(track => track.stop());
          }
          
          const constraints = {
              video: {
                  facingMode: cameraMode,
                  width: { ideal: 640 },
                  height: { ideal: 480 }
              },
              audio: false
          };
          
          const stream = await navigator.mediaDevices.getUserMedia(constraints);
          streamRef.current = stream;
          
          if (videoRef.current) {
              videoRef.current.srcObject = stream;
              videoRef.current.play();
              setIsStreaming(true);
              setErrorMessage(null);
              startDetectionInterval();
          }
      } catch (err) {
          console.error("카메라 접근 오류:", err);
          setErrorMessage(`카메라 접근 오류: ${err.message}`);
          setIsStreaming(false);
      }
  };
  
  // 카메라 중지
  const stopCamera = () => {
      if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
      }
      
      if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
      }
      
      setIsStreaming(false);
      setDetectedObjects([]);
      setProcessedImage(null);
  };
  
  // 카메라 모드 변경
  const toggleCameraMode = () => {
      const newMode = cameraMode === 'environment' ? 'user' : 'environment';
      setCameraMode(newMode);
      
      if (isStreaming) {
          stopCamera();
          setTimeout(startCamera, 300); // 잠시 대기 후 재시작
      }
  };
  
  // 주기적 객체 감지 시작
  const startDetectionInterval = () => {
      if (intervalRef.current) {
          clearInterval(intervalRef.current);
      }
      
      intervalRef.current = setInterval(() => {
          detectObjects();
      }, 10000); // 10초마다 객체 감지
  };
  
  // 이미지 캡처 및 객체 감지
  const detectObjects = async () => {
      if (!videoRef.current || !isStreaming || isProcessing) return;
      
      setIsProcessing(true);
      
      try {
          // 캔버스에 비디오 프레임 캡처
          const video = videoRef.current;
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // 이미지를 Blob으로 변환
          const blob = await new Promise(resolve => {
              canvas.toBlob(resolve, 'image/jpeg', 0.8);
          });
          
          // FormData 생성
          const formData = new FormData();
          formData.append('image', blob, 'capture.jpg');
          
          // API 요청
          const response = await fetch('/api/detect', {
              method: 'POST',
              body: formData,
          });
          
          if (!response.ok) {
              throw new Error(`HTTP 오류: ${response.status}`);
          }
          
          const data = await response.json();
          setDetectedObjects(data.detected_objects);
          setProcessedImage(data.processed_image);
          setErrorMessage(null);
      } catch (err) {
          console.error("객체 감지 오류:", err);
          setErrorMessage(`객체 감지 오류: ${err.message}`);
      } finally {
          setIsProcessing(false);
      }
  };
  
  // 마운트 시 이벤트 리스너 설정
  useEffect(() => {
      // 컴포넌트 언마운트 시 정리
      return () => {
          stopCamera();
      };
  }, []);
  
  return (
      <div>
          <h1>YOLOv8 모바일 객체 인식</h1>
          
          <div id="controls">
              {!isStreaming ? (
                  <button onClick={startCamera} disabled={isProcessing}>
                      카메라 시작
                  </button>
              ) : (
                  <button onClick={stopCamera} disabled={isProcessing}>
                      카메라 중지
                  </button>
              )}
              
              <button onClick={toggleCameraMode} disabled={isProcessing}>
                  {cameraMode === 'environment' ? '전면 카메라로 전환' : '후면 카메라로 전환'}
              </button>
              
              {isStreaming && (
                  <button onClick={detectObjects} disabled={isProcessing}>
                      지금 감지하기
                  </button>
              )}
          </div>
          
          {errorMessage && (
              <div className="status" style={{ color: 'red' }}>
                  {errorMessage}
              </div>
          )}
          
          <div id="video-container">
              <video ref={videoRef} width="640" height="480" autoPlay playsInline muted></video>
              <canvas ref={canvasRef} id="canvas-overlay"></canvas>
          </div>
          
          {isProcessing && (
              <div className="loading">처리 중...</div>
          )}
          
          {processedImage && (
              <div>
                  <h2>감지된 이미지</h2>
                  <img id="result-image" src={processedImage} alt="감지된 객체" />
              </div>
          )}
          
          <div id="detection-results">
              <h2>감지된 객체</h2>
              {detectedObjects.length > 0 ? (
                  <div>
                      <p><strong>감지된 객체 수:</strong> {detectedObjects.length}</p>
                      {detectedObjects.map((obj, index) => (
                          <div key={index} className="object-item">
                              <strong>{obj.class}</strong> (신뢰도: {obj.confidence.toFixed(2)})
                              <br />
                              <small>위치: x1={obj.bbox[0]}, y1={obj.bbox[1]}, x2={obj.bbox[2]}, y2={obj.bbox[3]}</small>
                          </div>
                      ))}
                  </div>
              ) : (
                  <p>감지된 객체가 없습니다.</p>
              )}
          </div>
          
          <div className="status">
              {isStreaming ? '카메라가 활성화되었습니다. 10초마다 자동으로 객체를 감지합니다.' : '카메라가 비활성화되었습니다.'}
          </div>
      </div>
  );
}

export default App;
