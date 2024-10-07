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

# Detect blue circles (optimized)
def find_theif(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    lower_blue2 = np.array([94, 147, 104])
    upper_blue2= np.array([180, 229, 187])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask=cv2.bitwise_or(mask,mask2)
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)  # Smaller kernel for performance
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=1, maxRadius=30)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw the circle and center
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return image, circles

# Detect yellow chickens (optimized)
def detect_yellow_chickens(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Range for yellow color (adjusted)
    lower_yellow = np.array([29,222,83])
    upper_yellow = np.array([83,255,255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    blurred = cv2.GaussianBlur(mask, (3, 3), 0)
    contours, _ = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chickens = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Filter out small objects
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y, w, h, area))
    
    detected_chickens.sort(key=lambda x: x[4], reverse=True)  # Sort by area
    
    N = 1  # Detect only the largest chicken
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255)  # Yellow color for chicken
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image


# Thread for handling camera frames
def camera_thread(ep_camera, ep_gimbal, ep_blaster):
    center_x = 640 / 2  # Adjusted for resized frame
    center_y = 360 / 2
    p = 0.6 / 1.7

    frame_skip = 2  # Process every second frameq
    frame_count = 0

    try:
        while True:
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                frame = cv2.resize(frame, (640, 360))  # Resize for faster processing
                
                # Crop the frame using a mask
                width = int(frame.shape[1] / 3)
                height = int(frame.shape[0] / 3)
                left_margin = 100
                right_margin = 100

                mask = np.zeros(frame.shape[:2], dtype="uint8")
                cv2.rectangle(mask, 
                            (width - left_margin, height), 
                            (width * 2 + right_margin, height * 2 + 250), 
                            255, -1)

                frame = cv2.bitwise_and(frame, frame, mask=mask)
                
                # Detect blue circle (theif) and yellow chickens
                

                result_image, circles = find_theif(frame)
                
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

# Main function
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster

    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    # Start camera thread
    t1 = threading.Thread(target=camera_thread, args=(ep_camera, ep_gimbal, ep_blaster))
    t1.start()
    t1.join()

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
