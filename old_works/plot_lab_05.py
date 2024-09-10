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

count_f = 0
steady_count = 0
steady_threshold = 3  # Number of frames to check for steadiness

# Class to hold marker information
class MarkerInfo:
    def __init__(self, x, y, w, h, score):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._score = score

    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)

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

    anchor_boxes = [(45, 85)]
    best_score = -1
    best_box = None
    stride = 12

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
    # Initialize robot
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
    p = 0.65
    i = 0
    d = 0

    data_pith_yaw = []
    accumulate_x = 0
    accumulate_y = 0
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
    stop_start_time = None 
    last_marker = None

    error_x_list = []
    error_y_list = []

    while True:
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        markers, score = detect_coke_can(img)

        if len(markers) != 0:  # Target found
            after_time = time.time()
            x, y = markers[-1].center
            if 0.7 < score < 0.85:
                if last_marker and last_marker.pt1 == markers[-1].pt1 and last_marker.pt2 == markers[-1].pt2:
                    steady_count += 1
                else:
                    steady_count = 0

                last_marker = markers[-1]
                print(f"Steady Count: {steady_count}")

                if steady_count >= steady_threshold:
                    ep_blaster.fire(fire_type=blaster.INFRARED_FIRE, times=1)
                    steady_count = 0
                    

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

                # Store error values for plotting
                error_x_list.append(err_x)
                error_y_list.append(err_y)

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

    # Plot the error values
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(error_x_list, label='Error X')
    plt.title('PID Controller Error')
    plt.xlabel('Frame')
    plt.ylabel('Error X')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(error_y_list, label='Error Y')
    plt.xlabel('Frame')
    plt.ylabel('Error Y')
    plt.legend()

    plt.tight_layout()
    plt.show()
