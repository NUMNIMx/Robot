import cv2
import robomaster
from robomaster import robot
from robomaster import blaster
from robomaster import camera
import time
import numpy as np

# ฟังก์ชันแสดงผลภาพ
def came(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        return False
    return True

# ฟังก์ชันตรวจจับวงกลมสีฟ้า
def find_theif(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([94, 80, 2])
    upper_blue = np.array([126, 255, 255])
    
    # Create mask for blue color
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=40)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # วาดวงกลมที่ตรวจพบ
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            # วาดจุดตรงกลางวงกลม
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return image, circles

# ฟังก์ชันคำนวณข้อผิดพลาด PID
def pid_control(center_x, center_y, x, y, p, i, d, accumulate_err_x, accumulate_err_y, prev_time):
    err_x = center_x - x
    err_y = center_y - y
    
    after_time = time.time()
    dt = after_time - prev_time

    accumulate_err_x += err_x * dt
    accumulate_err_y += err_y * dt

    speed_x = p * err_x + i * accumulate_err_x + d * (err_x / dt)
    speed_y = p * err_y + i * accumulate_err_y + d * (err_y / dt)

    return speed_x, speed_y, accumulate_err_x, accumulate_err_y, after_time

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    center_x = 1280 / 2
    center_y = 720 / 2

    # ค่า PID เริ่มต้น
    p = 0.6 / 2.2
    i = p / (0.7 / 2)  # ค่า I เริ่มต้น
    d = p * (0.7 / 8)  # ค่า D เริ่มต้น

    accumulate_err_x = 0
    accumulate_err_y = 0
    prev_time = time.time()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                ep_blaster.set_led(brightness=32, effect=blaster.LED_ON)
                time.sleep(1)
                before = frame
                after = ep_camera.read_cv2_image(strategy="newest", timeout=2)
                
                # ตรวจจับวงกลมสีฟ้า
                result_image, circles = find_theif(after)

                # ถ้าตรวจพบวงกลม
                if circles is not None:
                    for (x, y, r) in circles:
                        # ใช้ PID ควบคุม gimbal ให้ตามตำแหน่งวงกลม
                        speed_x, speed_y, accumulate_err_x, accumulate_err_y, prev_time = pid_control(
                            center_x, center_y, x, y, p, i, d, accumulate_err_x, accumulate_err_y, prev_time
                        )
                        
                        # ปรับความเร็ว gimbal
                        ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)

                if not came(result_image):
                    break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program interrupted by user")  

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
