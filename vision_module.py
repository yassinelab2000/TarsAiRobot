'''
This module handles camera operations
Copyright (c) 2025 Yassine Labiade
Licensed under the MIT License.
'''

import cv2 #OpenCV 
import datetime
import os
import time

def capture_image():
    cam = cv2.VideoCapture(0) #opens the default camera
    ret, frame = cam.read() #ret is a boolean if true cam is working is false it is Camera error, frame is an array of RGBA channels (its the picture itsself)
    if not ret:
        cam.release()
        return None, "Camera error"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tars_vision_{timestamp}.jpg"
    filepath = os.path.join("snapshots", filename)
    os.makedirs("snapshots", exist_ok=True)
    cv2.imwrite(filepath, frame)
    cam.release() #close camera

    return filepath, f"I've taken a picture: {filename}"

'''
If you are trying to run this file separately, on Windows the file will work. 
However, on a Raspberry Pi, it most likely won’t. 
I will need to add the capture_and_save_image() function,
probably in another file. This function will have to use rpicam-still exclusively,
as it is specifically designed for Raspberry Pi Camera Modules like the OV5647.
This ensures full compatibility and eliminates fallback delays or failures !!
'''
# TEST SECTION 
if __name__ == "__main__":
    print("Testing camera module")
    print("Taking a picture in 3 seconds)")
    
    time.sleep(3)  
    
    filepath, message = capture_image()
    
    if filepath:
        print(f"SUCCESS: {message}")
        print(f"Saved at: {filepath}")
    else:
        print(f"FAILED: {message}")