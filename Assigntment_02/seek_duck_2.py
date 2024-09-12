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

def detect_yellow_chickens(image):
    # Define region of interest (ROI) - focus on lower half of the image
    height, width = image.shape[:2]
    roi = image[height//2:, :]  # Take the lower half of the image

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Adjust color range for yellow chicken toys
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chickens = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Adjust minimum area as needed
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y + height//2, w, h, area))  # Adjust y-coordinate
    
    # Sort by area (largest first)
    detected_chickens.sort(key=lambda x: x[4], reverse=True)
    
    # Draw bounding boxes for the N largest detected chickens
    N = 2  # Number of chickens to detect
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255) if i == 0 else (255, 255, 0)  # Light yellow for largest, dark yellow for second
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
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
            if frame is not None:
                result_image = detect_yellow_chickens(frame)
                
                if not display_image(result_image):
                    break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Program interrupted by user")
    
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()