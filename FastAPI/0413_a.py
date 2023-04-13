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
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse

from datetime import datetime
import rospy
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import threading

app = FastAPI()
bridge = CvBridge()

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('../', 'custom','../0403_custom/exp/weights/best.pt', source='local', device='cpu', force_reload=True)

templates = Jinja2Templates(directory="templates")
cv2_img = np.zeros((480, 640, 3), np.uint8)

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
def callback(msg):
    
    global cv2_img
    try:
        #msg = rospy.wait_for_message("/usb_cam/image_raw", Image)
        #cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
        cv2_img1 = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
        cv2_img = cv2.cvtColor(cv2_img1, cv2.COLOR_RGB2BGR)
        #frame=cv2_img.copy()
        #cv2.imshow('re2', frame)
    except CvBridgeError as e:
        print(e)
image_topic = "/usb_cam/image_raw"
    
threading.Thread(target=lambda: rospy.init_node('image_listener', disable_signals=True)).start()
    
rospy.Subscriber(image_topic, Image, callback)   
def gen():
    global cv2_img
    while True:
        
        print("Receiving cam images. ",datetime.now().strftime('%y-%m-%d-%H:%M:%S'))
        
        _, img_encoded = cv2.imencode('.jpg', cv2_img)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

@app.get('/video')
def video():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

#def main():
    
    #rospy.spin()
    

#if __name__ == '__main__':
    # logtxext = str(input("Do you want to save the image? yes or no : "))
    # print(logtxext)
    # if logtxext == 'yes':
    #     print("if")

    #main()