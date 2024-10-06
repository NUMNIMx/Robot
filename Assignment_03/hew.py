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
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return image, circles

def find_theif_body(image, image1):
    result = cv2.absdiff(image, image1)
    edges = cv2.Canny(result, 60, 160)
    blurred = cv2.GaussianBlur(result, (5, 5), 0)
    edges = cv2.Canny(blurred, 20, 120)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    largest_area = 0
    largest_contour = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > largest_area:
            largest_area = area
            largest_contour = contour

    if largest_contour is not None:
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return edges, image1, largest_area

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

    p = 0.6 / 1.7
    i = p / (0.7 / 2)
    d = p * (0.7 / 8)

    accumulate_err_x = 0
    accumulate_err_y = 0
    prev_time = time.time()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=2)
            if frame is not None:
                result_image, circles = find_theif(frame)

                if circles is not None:  # เช็คว่ามีวงกลมหรือไม่
                    ep_blaster.set_led(brightness=32, effect=blaster.LED_ON)
                    time.sleep(1)

                    before = frame
                    after = ep_camera.read_cv2_image(strategy="newest", timeout=2)
                    edges, bounded_image, largest_area = find_theif_body(before, after)

                    if largest_area > 50:
                        ep_blaster.fire(fire_type=blaster.WATER_FIRE, times=3)
                        print(f"Firing! Largest Area: {largest_area}")
                        time.sleep(2)
                    else:
                        ep_blaster.set_led(effect=blaster.LED_OFF)
                        print(f"Area too small: {largest_area}")

                    if not came(bounded_image):
                        break

                # เช็ควงกลมเท่านั้นถ้าหากมีค่า
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

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program interrupted by user")

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
