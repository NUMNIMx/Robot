import cv2
import robomaster
from robomaster import robot
from robomaster import vision
from robomaster import blaster
from robomaster import camera
import time
import numpy as np
from scipy.spatial.distance import cosine
import pandas as pd
import matplotlib.pyplot as plt

def display_image(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        return False
    return True

def detect_red_coke_cans(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_cans = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Minimum object size
            x, y, w, h = cv2.boundingRect(contour)
            detected_cans.append((x, y, w, h, area))
    
    # Sort detected cans by area (largest first)
    detected_cans.sort(key=lambda x: x[4], reverse=True)
    
    # Draw bounding boxes for the top N largest detections
    N = 2  # Number of cans to detect
    for i, (x, y, w, h, _) in enumerate(detected_cans[:N]):
        color = (0, 0, 255) if i == 0 else (255, 0, 0)  # Red for largest, Blue for second largest
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Can {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    
    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            width = int(frame.shape[1]/3)
            high = int(frame.shape[0]/3)
            mask = np.zeros(frame.shape[:2], dtype="uint8")
            cv2.rectangle(mask,(width, high), (width*2, high*2+100), 255, -1)
            frame = cv2.bitwise_and(frame,frame, mask=mask)
            
            if frame is not None:
                result_image_with_red_detection = detect_red_coke_cans(frame)
                
                if not display_image(result_image_with_red_detection):
                    break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Program interrupted by user")
    
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()