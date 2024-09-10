import cv2
import robomaster
from robomaster import robot
from robomaster import vision
from robomaster import blaster
import time
import numpy as np
from scipy.spatial.distance import cosine
import pandas as pd
import matplotlib.pyplot as plt

# คลาสสำหรับเก็บข้อมูล marker(ป้าย)
class MarkerInfo:
    # ข้อมูลจุดตรงกลางป้าย ความกว้าง ความยาว ข้อมูลป้าย
    def __init__(self, x, y, w, h, score):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._score = score

    # คำนวณมุมซ้ายบนของป้ายและแปลงเป็น pixel
    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

    # คำนวณมุมขวาล่างของป้ายและแปลงเป็น pixel
    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

    # จุดกลางป้ายเป็น pixel
    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)

    # ข้อมูลคะแนนป้าย
    @property
    def text(self):
        return f"Score: {self._score:.2f}"


def detect_coke_can(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([0, 100, 100])
    upper_red2 = np.array([10, 255, 255])

    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1)

    anchor_boxes = [(25, 65)]
    best_score = -1
    best_box = None
    stride = 20

    for (box_w, box_h) in anchor_boxes:
        for y in range(0, mask.shape[0] - box_h, stride):
            for x in range(0, mask.shape[1] - box_w, stride):
                window = mask[y:y+box_h, x:x+box_w]
                window_vector = window.flatten()
                target_vector = np.ones_like(window_vector)

                window_norm = np.linalg.norm(window_vector)
                target_norm = np.linalg.norm(target_vector)
                if window_norm == 0 or target_norm == 0:
                    continue

                similarity = 1 - cosine(window_vector / window_norm, target_vector / target_norm)

                if 0.72 < similarity < 0.85 and similarity > best_score:
                    best_score = similarity
                    best_box = (x, y, box_w, box_h)

    if best_box is not None:
        marker = MarkerInfo(
            (best_box[0] + best_box[2] / 2) / 1280,
            (best_box[1] + best_box[3] / 2) / 720,
            best_box[2] / 1280,
            best_box[3] / 720,
            best_score
        )
        return [marker], best_score
    else:
        return [], 0

if __name__ == "__main__":
    # initialize robot
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster

    center_x = 1280 / 2
    center_y = 720 / 2

    ep_camera.start_video_stream(display=False)
    ep_gimbal.sub_angle(freq=50)

    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    count = 0
    time.sleep(1)

    # PID controller constants
    p = 0.83 / 2.2
    i = 0#p / (0.6 / 2)
    d = 0#p * (0.6 / 8)

    data_pith_yaw = []
    accumulate_x = 0
    accumulate_y = 0
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
   
    while True:
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        markers, score = detect_coke_can(img)

        if len(markers) != 0:  # target found
            
            after_time = time.time()
            x, y = markers[-1].center
              # Reset the timer if no target found
            err_x = center_x - x
            err_y = center_y - y
            accumulate_x += err_x * (after_time - prev_time)
            accumulate_y += err_y * (after_time - prev_time)

            if count >= 1:
                speed_x = (p * err_x) + d * ((err_x - prev_err_x) / (after_time - prev_time)) + i * accumulate_x
                speed_y = (p * err_y) + d * ((err_y - prev_err_y) / (after_time - prev_time)) + i * accumulate_y

                ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)
                time.sleep(0.001)

                data_pith_yaw.append([err_x, err_y, round(speed_x, 3), round(speed_y, 3), center_x, x])

            count += 1
            prev_time = after_time
            prev_err_x = err_x
            prev_err_y = err_y

        else:
            ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)

        for marker in markers:
            cv2.rectangle(img, marker.pt1, marker.pt2, (0, 255, 0))
            cv2.putText(img, marker.text, marker.center, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.imshow("Markers", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()

