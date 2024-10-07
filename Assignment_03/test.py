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

def find_theif_body(image):
    # Compute the absolute difference between two frames
    result = cv2.COLOR_BAYER_BG2GRAY(image)
    blurred = cv2.GaussianBlur(result, (5, 5), 0)
    
    # Load the template image
    template = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assignment_03\bottleman_1_plate_led.jpg') 
    template = cv2.COLOR_BAYER_BG2GRAY(template)
    if template is None:
        print("Template image not found.")
        return result
    
    # Get the width and height of the template
    template_height, template_width = template.shape[:2]
    
    # Perform template matching
    match_result = cv2.matchTemplate(blurred, template, cv2.TM_CCOEFF_NORMED)
    
    # Define a threshold to consider a match valid
    threshold = 0.2
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
    
    if max_val > threshold:
        # If a match is found, draw a rectangle around the detected object
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, 'Thief Detected', (top_left[0], top_left[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
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
    i = 0 # p / (0.7 / 2)
    d = 0 # p * (0.7 / 8)

    accumulate_err_x = 0
    accumulate_err_y = 0
    prev_time = time.time()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                ep_blaster.set_led(brightness=32, effect=blaster.LED_ON)
                time.sleep(1)
                im = find_theif_body(frame)

                if not came(im):
                    break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program interrupted by user")  

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
