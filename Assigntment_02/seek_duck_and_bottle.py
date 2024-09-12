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
lst_x = []
def sub_position_handler(position_info):
    x, y, z  = position_info
    
    global fm_x
    global fm_y
    #print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = float("{:.4f}".format(float(x)))    
    fm_y= float("{:.4f}".format(float(y)))
    lst_x.append(fm_x)

def display_image(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        ep_chassis.move(x=-1.2, y=0, z=0, xy_speed=0.7).wait_for_completed()
        return False
    return True

def detect_yellow_chickens(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # ปรับช่วงสีให้เหมาะสมกับสีเหลืองของตุ๊กตาไก่
    lower_yellow = np.array([31, 132, 0])
    upper_yellow = np.array([42, 255, 241])
    lower_yellow2 = np.array([0,184,90])
    upper_yellow2 = np.array([93,255,255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask2 = cv2.inRange(hsv, lower_yellow2, upper_yellow2)
    contours, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chickens = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # ขนาดขั้นต่ำของวัตถุ
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y, w, h+10, area))
    
    # เรียงลำดับตามขนาดพื้นที่ (ใหญ่สุดก่อน)
    detected_chickens.sort(key=lambda x: x[4], reverse=True)
    
    # วาดกรอบสี่เหลี่ยมรอบตุ๊กตาไก่ที่ตรวจพบ N ตัวแรก
    N = 1  # ตรวจจับเพียงแค่ตุ๊กตาไก่ตัวเดียว
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255)  # สีเหลืองอ่อนสำหรับตัวใหญ่สุด
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

def detect_blue_bottles(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # ปรับช่วงสีให้เหมาะสมกับสีน้ำเงินของขวดน้ำ
    lower_blue = np.array([102, 123, 113])
    upper_blue = np.array([179, 255, 255])
    lower_blue2 = np.array([94, 158, 62])
    upper_blue2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask1 = cv2.inRange(hsv,lower_blue2,upper_blue2)
    mask=cv2.bitwise_or(mask,mask1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_bottles = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:  # ขนาดขั้นต่ำของวัตถุ 
            x, y, w, h = cv2.boundingRect(contour)
            print(lst_x[-1])
            if lst_x[-1] < 0.6:
                detected_bottles.append((x-5, y-40, w+10, h*5, area))
            
            if lst_x[-1] >=0.6 and lst_x[-1] < 0.9:
                detected_bottles.append((x-10, y-68, w+20, h+109, area))
            if  lst_x[-1] >= 0.9 :
                detected_bottles.append((x-10, y-104, w+20, h+179, area))
            
        
            # detected_bottles.append((x-8, y-25, w+10, h*5, area))
    
    # เรียงลำดับตามขนาดพื้นที่ (ใหญ่สุดก่อน)
    detected_bottles.sort(key=lambda x: x[4], reverse=True)
    
    # วาดกรอบสี่เหลี่ยมรอบขวดน้ำที่ตรวจพบ N ขวดแรก
    N = 1  # ตรวจจับเพียงแค่ขวดน้ำขวดเดียว
    for i, (x, y, w, h, _) in enumerate(detected_bottles[:N]):
        color = (255, 0, 0)  # สีน้ำเงินสำหรับขวดใหญ่สุด
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Bottle {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_chassis = ep_robot.chassis
    ep_gimbal = ep_robot.gimbal
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    ep_chassis.move(x=1.2, y=0, z=0, xy_speed=0.6)
    
    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            width = int(frame.shape[1]/3)
            high = int(frame.shape[0]/3)
            mask = np.zeros(frame.shape[:2], dtype="uint8")
            cv2.rectangle(mask,(width, high), (width*2, high*2+100), 255, -1)
            frame = cv2.bitwise_and(frame,frame, mask=mask)
            
            if frame is not None:
                # ตรวจจับตุ๊กตาไก่
                result_image_with_yellow_detection = detect_yellow_chickens(frame)
                # ตรวจจับขวดน้ำ
                result_image_with_bottle_detection = detect_blue_bottles(result_image_with_yellow_detection)
                
                if not display_image(result_image_with_bottle_detection):
                    break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Program interrupted by user")
    ep_chassis.unsub_position()
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
