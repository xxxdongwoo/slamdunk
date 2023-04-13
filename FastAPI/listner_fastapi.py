import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from datetime import datetime
import rospy
import numpy as np

app = FastAPI()
bridge = CvBridge()

@app.post('/image')
def image(image: bytes):
    np_img = np.frombuffer(image, dtype=np.uint8)
    cv2_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    return StreamingResponse(gen_frames(cv2_img), media_type="multipart/x-mixed-replace; boundary=frame")

def gen_frames(cv2_img):
    while True:
        print("Receiving cam images. ",datetime.now().strftime('%y-%m-%d-%H:%M:%S'))
        # Process the image here
        annotated_cv_image = cv2_img # Placeholder for now

        ret, buffer = cv2.imencode('.jpg', annotated_cv_image)
        cv_image = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv_image + b'\r\n')
        
        # Send the image to some other endpoint
        # requests.post("http://localhost:8000/image", data=cv_image, headers={"Content-Type": "image/jpeg"})
        # print(results.pandas().xyxy[0].to_json(orient="records"))

if __name__ == "__main__":
    # Subscribe to USB_CAM/IMAGE_RAW topic
    rospy.init_node("camera_subscriber")
    rospy.Subscriber("USB_CAM/IMAGE_RAW", Image, gen_frames)
 
