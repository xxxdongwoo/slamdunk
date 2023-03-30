from typing import Union

from fastapi import FastAPI
import io
import json
from PIL import Image
from fastapi import File,FastAPI, Response
import torch
import cv2
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import json
import telegram
import time

bot = telegram.Bot(token='6007372301:AAEZWipCHU_oaQV7a1Kh_0Ig-ZARlPHjHjs')
chat_id =6102779631

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
#app.mount("/home/khj/slamdunk/FastAPI/static", StaticFiles(directory="static"), name="static")

cap = cv2.VideoCapture(0)

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('/home/khj/slamdunk/yolov5/', 'custom','/home/khj/slamdunk/0328_custom/exp/weights/best.pt', 
                       source='local', device='cpu', force_reload=True)
#model 변경하는 부분에서 많은 Error가 발생, local dataset을 이용시 많은 조건을 수정 필요 

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def video_show(request: Request):
    return templates.TemplateResponse("simple_gui.html",{"request": request})

async def gen_frames():
    prev_num_persons = 0 #이전 프레임에서 발견된 사람 수를 저장할 변수 초기화 
    while True:
        _, frame = cap.read()
        if not _:
            break
        else:
            results = model(frame)
            annotated_frame = results.render()
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            if results and results.pandas().xyxy[0] is not None:
                resulting_json = json.loads(results.pandas().xyxy[0].to_json(orient="records"))             
                num_persons = len([d for d in resulting_json if d["confidence"] >= 0.7 and d["name"] == "person"])
                if num_persons > 0 and num_persons != prev_num_persons:  # 사람 수가 이전 프레임과 다르면 메시지 전송
                    await bot.send_message(chat_id, text=f"사람이 {num_persons}명 확인 되었습니다. QR코드를 확인 합니다")
                    prev_num_persons = num_persons  # 이전 프레임에서 발견된 사람 수를 업데이트
                    
                    # 2분 딜레이
                    #time.sleep(120)
                    #await asyncio.sleep(120)            
                #if num_persons != prev_num_persons:
                 #   await bot.send_message(chat_id, text=f"사람이 {num_persons}명 확인 되었습니다. QR코드를 확인 합니다")
                  #  prev_num_persons = num_persons
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # print(results.pandas().xyxy[0].to_json(orient="records"))

@app.get('/video')
def video():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    # return StreamingResponse(video_streaming(), media_type="multipart/x-mixed-replace; boundary=frame")
    
# if __name__ == "__main__":
#     app.run(debug=True)


# def gen_frames():
    # while(True):
    #     ret, frame = cam.read()
    #     results= model(frame)
    #     annotation = results.render()
    #     print(results.pandas().xyxy[0].to_json(orient="records"))
    #     cv2.imshow("test", frame)
    #     cv2.waitKey(1)
        
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
