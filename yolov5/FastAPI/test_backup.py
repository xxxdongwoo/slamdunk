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
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', device='cpu', force_reload=True)

while(True):
    ret, frame = cam.read()
    results= model(frame)
    annotation = results.render()
#img = 'https://ultralytics.com/images/zidane.jpg'
#results = model(img)
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