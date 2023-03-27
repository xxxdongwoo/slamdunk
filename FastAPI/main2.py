from typing import Union

from fastapi import FastAPI

#Install requirements 
# pip install -r https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
# pip install python-multipart

#Import section
import io
import json
from PIL import Image
from fastapi import File,FastAPI
import torch
import cv2

cam = cv2.VideoCapture(0)


# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)
model = torch.hub.load('../', 'custom','../0322_custom/exp/weights/best.pt', source='local', device='cpu', force_reload=True)

while(True):
    ret, frame = cam.read()
    results= model(frame)
    annotation = results.render()
    print(results.pandas().xyxy[0].to_json(orient="records"))
    cv2.imshow("test", frame)
    cv2.waitKey(1)
    
#create your API
app = FastAPI()

#Set up your API and integrate your ML model 
@app.post("/objectdetection/")
async def get_body(file: bytes = File(...)):
    input_image =Image.open(io.BytesIO(file)).convert("RGB")
    results = model(input_image)
    results_json = json.loads(results.pandas().xyxy[0].to_json(orient="records"))
    return {"result": results_json}

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}