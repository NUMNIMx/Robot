import cv2
import robomaster
from robomaster import robot
from robomaster import blaster
from robomaster import camera
import time
import numpy as np
import threading

# Show the processed image
def came(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        return False
    return True

# Detect blue circles
def find_theif(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([102, 123, 113])
    upper_blue = np.array([179, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    blurred = cv2.GaussianBlur(mask, (3, 3), 0)  # Smaller kernel
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=40, minRadius=20, maxRadius=100)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return image, circles

# Detect yellow chickens
def detect_yellow_chickens(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([31, 132, 0])
    upper_yellow = np.array([42, 255, 241])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chickens = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y, w, h, area))
    
    detected_chickens.sort(key=lambda x: x[4], reverse=True)
    N = 1
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255)
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image

# Find object using template matching
def find_theif_body(image, image1):
    result = cv2.absdiff(image, image1)
    blurred = cv2.GaussianBlur(result, (3, 3), 0)  # Smaller kernel
    template = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assignment_03\tem_match.png') 
    
    if template is None:
        print("Template image not found.")
        return result
    
    template_height, template_width = template.shape[:2]
    match_result = cv2.matchTemplate(blurred, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
    
    if max_val > threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, 'Thief Detected', (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return image

# Thread for handling camera frames
def camera_thread(ep_camera, ep_gimbal, ep_blaster):
    center_x = 640 / 2  # Updated for resized frame
    center_y = 360 / 2
    p = 0.6 / 2.2

    try:
        frame_skip = 2  # Process every 2nd frame
        frame_count = 0

        while True:
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue
            
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                frame = cv2.resize(frame, (640, 360))  # Resize frame for faster processing
                
                result_image, circles = find_theif(frame)
                result_image = detect_yellow_chickens(result_image)

                if circles is not None:
                    for (x, y, r) in circles:
                        err_x = center_x - x
                        err_y = center_y - y

                        speed_x = p * err_x
                        speed_y = p * err_y

                        ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)

                if not came(result_image):
                    break
                
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program interrupted by user")  

# Main logic
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster

    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    t1 = threading.Thread(target=camera_thread, args=(ep_camera, ep_gimbal, ep_blaster))
    t1.start()

    t1.join()

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
