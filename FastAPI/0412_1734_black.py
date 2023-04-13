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


app = FastAPI()
bridge = CvBridge()

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('../', 'custom','../0403_custom/exp/weights/best.pt', source='local', device='cpu', force_reload=True)

templates = Jinja2Templates(directory="templates")
cv2_img = np.zeros((480, 640, 3), np.uint8)

@app.get("/", response_class=HTMLResponse)
def video_show(request: Request):
    return templates.TemplateResponse("video_show.html",{"request": request})
def callback(msg):
    global cv2_img
    try:
        #print(1)
        #msg = rospy.wait_for_message("/usb_cam/image_raw", Image)
        # print(2)
        # cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
        # frame=cv2_img.copy()
        # cv2.imshow('re2', frame)
        cv2_img1 = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
        cv2_img = cv2.cvtColor(cv2_img1, cv2.COLOR_RGB2BGR)
    except CvBridgeError as e:
        print(e)
        
def gen():
    global cv2_img
    while True:
        
        print("Receiving cam images. ",datetime.now().strftime('%y-%m-%d-%H:%M:%S'))
        ##cv2.imshow("re", cv2_img)
        ##cv2.waitKey(1)
        _, img_encoded = cv2.imencode('.jpg', cv2_img)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img_encoded.tobytes() + b'\r\n')

@app.get('/video')
def video():
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")

def main():
    image_topic = "/usb_cam/image_raw"
    
    rospy.init_node('image_listener')
    
    rospy.Subscriber(image_topic, Image, callback)
    rospy.spin()
    

if __name__ == '__main__':
    # logtxext = str(input("Do you want to save the image? yes or no : "))
    # print(logtxext)
    # if logtxext == 'yes':
    #     print("if")

    main()