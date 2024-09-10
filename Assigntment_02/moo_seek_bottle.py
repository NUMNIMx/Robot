import cv2
import robomaster
from robomaster import robot, blaster, camera
import time
import numpy as np
import matplotlib.pyplot as plt

class BottleMarker:
    def __init__(self, x, y, w, h, score):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._score = score

    @property
    def pt1(self):
        return int(self._x), int(self._y)

    @property
    def pt2(self):
        return int(self._x + self._w), int(self._y + self._h)

    @property
    def center(self):
        return int(self._x + self._w / 2), int(self._y + self._h / 2)

    @property
    def text(self):
        return f"Score: {self._score:.2f}"

def detect_bottle(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define the color range for blue (cap color) detection
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 190, 190])

    mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_score = -1
    best_box = None

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        if area > 100:  # Adjust this threshold as needed
            score = area / (w * h)  # Example score based on compactness
            # Check if score is within the desired range
            if 0.74 <= score <= 0.84 and score > best_score:
                best_score = score
                best_box = (x, y, w, h)

    if best_box:
        x, y, w, h = best_box
        # Increase the height of the rectangle by a factor, e.g., 1.5 times the height
        increased_height = int(h * 4)
        # Ensure the new height doesn't go out of bounds of the image
        new_y = max(0, y - (increased_height - h) // 2)  # Centering the increase
        new_h = min(image.shape[0] - new_y, increased_height)
        cv2.rectangle(image, (x, new_y), (x + w, new_y + new_h), (0, 255, 0), 2)
        return BottleMarker(x, new_y, w, new_h, best_score), best_score
    else:
        return None, None




if __name__ == "_main_":
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_blaster = ep_robot.blaster
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal

    center_x = 1280 / 2
    center_y = 720 / 2
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.sub_angle(freq=10)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    time.sleep(1)

    p = 0.6 / 2.2
    i = p / (0.6 / 1.2)
    d = 0

    accumulate_err_x = 0
    accumulate_err_y = 0
    data_pith_yaw = []
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
    count = 0

    lst_bottle = []

    while True:
        print(count)
        img = ep_camera.read_cv2_image(strategy="newest", timeout=1)
        mask = np.zeros(img.shape[:2], dtype="uint8")
        cv2.rectangle(mask, (300, 0), (980, 600), 255, -1)
        img = cv2.bitwise_and(img, img, mask=mask)
        marker, score = detect_bottle(img)
        if marker and score:
            lst_bottle.append(score)
            after_time = time.time()
            x, y = marker.center

            err_x = center_x - x
            err_y = center_y - y
            accumulate_err_x += err_x * (after_time - prev_time)
            accumulate_err_y += err_y * (after_time - prev_time)

            if abs(prev_err_x - err_x) <= 10 and abs(prev_err_y - err_y) <= 10:
                count += 1
            else:
                count = 0
            
            if count == 10:
                # ep_blaster.fire(fire_type=blaster.INFRARED_FIRE)
                count = 0
                
            speed_x = p * err_x
            speed_y = p * err_y
            ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)

            data_pith_yaw.append([err_x, err_y, round(speed_x, 3), round(speed_y, 3), after_time - prev_time])

            prev_time = after_time
            prev_err_x = err_x
            prev_err_y = err_y

            cv2.rectangle(img, marker.pt1, marker.pt2, (0, 255, 0), 2)
            cv2.putText(img, marker.text, marker.center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            time.sleep(0.001)
        
        if len(lst_bottle) == 10:
            print(sum(lst_bottle) / len(lst_bottle))
            lst_bottle = []

        else:
            ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)

        cv2.imshow("Bottle Detection", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()