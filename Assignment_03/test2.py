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

def find_theif_body(image):
    # Since the input is already an edge-detected grayscale image, no need to convert to grayscale again

    # Load the template image and convert it to grayscale
    template = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assignment_03\boky_man_match_clear.jpg') 
    if template is None:
        print("Template image not found.")
        return image  # Return original image if template is not found
    
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.Canny(frame, 100, 200)
    # Get the width and height of the template
    template_height, template_width = template_gray.shape[:2]
    
    # Perform template matching
    match_result = cv2.matchTemplate(image, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Define a threshold to consider a match valid
    threshold = 0.5
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)

    # Draw a rectangle around the found template location
    if max_val >= threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)  # Draw rectangle on original image
    
    return image


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                ep_blaster.set_led(brightness=32, effect=blaster.LED_ON)
                time.sleep(1)
                frame  =  cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(frame, 100, 200)
                # Process frame using edge detection and template matching
                im = find_theif_body(edges)

                if not came(im):
                    break
                
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program interrupted by user")  

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
