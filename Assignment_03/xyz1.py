import cv2
import robomaster
from robomaster import robot
from robomaster import blaster
from robomaster import camera
import time
import numpy as np

def came(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        return False
    return True

def find_theif(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([102, 123, 113])
    upper_blue = np.array([179, 255, 255])
    lower_blue2 = np.array([94, 158, 62])
    upper_blue2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask1 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask = cv2.bitwise_or(mask, mask1)
    
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=200)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw the circle in the original image
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            # Draw a rectangle at the center of the circle
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return image, circles

def detect_yellow_chickens(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
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
        if area > 100:  # Minimum size of the object
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y, w, h+10, area))
    
    detected_chickens.sort(key=lambda x: x[4], reverse=True)
    
    # Draw rectangle around the first N detected chickens
    N = 1  # Detect only the largest chicken
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

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

    p = 0.6 / 2.2
    i = 0
    d = 0

    accumulate_err_x = 0
    accumulate_err_y = 0
    prev_time = time.time()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                # Detect blue circles and yellow chickens
                result_image, circles = find_theif(frame)
                result_image = detect_yellow_chickens(result_image)
                
                ep_blaster.set_led(brightness=32, effect=blaster.LED_ON)
                
                if circles is not None:
                    for (x, y, r) in circles:
                        err_x = center_x - x
                        err_y = center_y - y
                        after_time = time.time()
                        accumulate_err_x += err_x * (after_time - prev_time)
                        accumulate_err_y += err_y * (after_time - prev_time)

                        speed_x = p * err_x
                        speed_y = p * err_y

                        ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)

                        prev_time = after_time

                if not came(result_image):
                    break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program interrupted by user")  

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
