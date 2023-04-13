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
import webbrowser

bot = telegram.Bot(token='6007372301:AAEZWipCHU_oaQV7a1Kh_0Ig-ZARlPHjHjs')
chat_id =6102779631

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
#app.mount("/home/khj/slamdunk/FastAPI/static", StaticFiles(directory="static"), name="static")

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 해상도 설정
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 100)  # FPS 설정

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('/home/yun/yolov5/', 'custom','/home/yun/yolov5/0407_best/exp/weights/best.pt', 
                       source='local', device='cpu', force_reload=True)
# model = torch.hub.load('/home/yun/yolov5/', 'custom','/home/yun/yolov5/0403_custom/exp/weights/best.pt', 
                    #    source='local', device='cpu', force_reload=True)
#model 변경하는 부분에서 많은 Error가 발생, local dataset을 이용시 많은 조건을 수정 필요 

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def video_show(request: Request):
    return templates.TemplateResponse("simple_gui.html",{"request": request})
async def gen_frames():
    pre_num_persons = 0 # 이전 비디오에서 발견된 사람 수를 저장할 변수 초기화
    pre_num_smoke = 0   # 이전 비디오에서 발견된 연기 수를 저장할 변수 초기화
    pre_num_fire = 0    # 이전 비디오에서 발견된 불 수를 저장할 변수 초기화
    frame_num = 0       # 이전 비디오 개수 저장할 변수 초기화 
    #print("SLAMDUNK 경비 순찰 시작합니다")
    #bot.send_message(chat_id, text="SLAMDUNK 경비 순찰 시작합니다\n")
    async def print_message(frame_num):
        message =""
        nonlocal pre_num_persons, pre_num_fire, pre_num_smoke
        #if frame_num == 0: # 프레임 번호가 0일때만 "SLAMDUNK 경비 순찰 시작합니다" 메시지 전송
        #    await bot.send_message(chat_id, text="SLAMDUNK 경비 순찰 시작합니다")
        if frame_num % 3000 == 0: # 대략적으로 5분에 한번 문자오는듯 ,현재 프레임 번호가 3000 배수일때 문자전송
            message = "SLAMDUNK 경비 순찰 중 입니다.\n"
        # 이전 프레임 ,객체의 개수가 바뀌어야만 문자알림 전송, 안그러면 많은 문자가 중복되어 쌓이게 됨,
        # 같은 객체를 인식하고 반복적으로 문자를 보내는것을 막기위함 
        if num_persons != pre_num_persons or num_smoke != pre_num_smoke or num_fire != pre_num_fire:
            if num_persons > 0 and num_persons != pre_num_persons == 0:
                message += f"사람이 {num_persons}명 확인 되었습니다.\nQR코드를 확인 합니다.\n"
                webbrowser.open("https://webqr.com/index.html")
                pre_num_persons = num_persons
            if num_smoke > 0 and num_smoke != pre_num_smoke:
                message += f"연기가 {num_smoke}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"
                pre_num_smoke = num_smoke
            if num_fire > 0 and num_fire != pre_num_fire:
                message += f"화재가 {num_fire}곳 에서 발견 되었습니다.\n지금 바로 확인 바랍니다\n"
                pre_num_fire = num_fire

        if message:
            await bot.send_message(chat_id, text=message)

    while True:   
        _, frame = cap.read()
        print(frame)
        frame_num += 1
        if not _:
            break
        else:
            results = model(frame)
            annotated_frame = results.render()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            if results and results.pandas().xyxy[0] is not None:
                resulting_json = json.loads(results.pandas().xyxy[0].to_json(orient="records"))
                num_persons = len([d for d in resulting_json if d["confidence"] >= 0.75 and d["name"] == "person"]) #사람은 기준점 75%를 넘어야 문자
                num_smoke = len([d for d in resulting_json if d["name"] == "smoke"]) # 연기는 기준점없이 문자 알람
                num_fire = len([d for d in resulting_json if d["name"] == "fire"])  # 불 도 기준점 없이 문자 알람 

                await print_message(frame_num)

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





#if num_persons > 0 and num_persons != pre_num_persons:  # 사람 수가 이전 비디오와 다르면 메시지 전송
#                    await bot.send_message(chat_id, text=f"사람이 {num_persons}명 확인 되었습니다. QR코드를 확인 합니다")
#                    pre_num_persons = num_persons  # 이전 비디오에서 발견된 사람 수를 업데이트
#                    print(results.pandas().head())
