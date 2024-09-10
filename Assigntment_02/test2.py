import cv2
import robomaster
from robomaster import robot, vision, blaster
import time
import numpy as np
from scipy.spatial.distance import cosine
import pandas as pd
import matplotlib.pyplot as plt

# Initialize global variables
count_f = 0
steady_count = 0
steady_threshold = 8

# Define DuckMarker class to encapsulate the detected object
class DuckMarker:
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

# Load the templates in RGB format
template_paths = [
    r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assigntment_02\td_0.1floor.jpg',
]
templates = [cv2.imread(path) for path in template_paths]

# Extract RGB channels from the first template (modify to use multiple templates if needed)
template_r = templates[0][:, :, 0].flatten()  # Red channel
template_g = templates[0][:, :, 1].flatten()  # Green channel
template_b = templates[0][:, :, 2].flatten()  # Blue channel

# Cosine similarity function
def cosine_similarity(vec1, vec2):
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    return np.dot(vec1_norm, vec2_norm)

# Sliding window function to scan the image
def sliding_window(image, step_size, window_size):
    for y in range(0, image.shape[0], step_size):
        for x in range(0, image.shape[1], step_size):
            window = image[y:y + window_size[1], x:x + window_size[0]]
            if window.shape[0] != window_size[1] or window.shape[1] != window_size[0]:
                continue
            yield (x, y, window)

# Object detection function
def duck_detection(img, step_size, window_size, template, template_r, template_g, template_b):
    best_score = -1
    best_box = None
    for (x, y, window) in sliding_window(img, step_size, window_size):
        window_r = window[:, :, 0].flatten()
        window_g = window[:, :, 1].flatten()
        window_b = window[:, :, 2].flatten()

        similarity_r = cosine_similarity(template_r, window_r)
        similarity_g = cosine_similarity(template_g, window_g)
        similarity_b = cosine_similarity(template_b, window_b)

        similarity = (similarity_r + similarity_g + similarity_b) / 3

        # Adjust threshold for detection if needed
        if 0.74 <= similarity <= 0.84:
            print(f"Object detected at position: ({x}, {y}) with similarity: {similarity}")
            best_score = similarity
            best_box = (x, y, template.shape[0], window.shape[1])

    if best_box is not None:
        marker = DuckMarker(
            (best_box[0] + best_box[2] / 2) / 1280,
            (best_box[1] + best_box[3] / 2) / 720,
            best_box[2] / 1280,
            best_box[3] / 720,
            best_score
        )
        return [marker], best_score
    return [], 0

# Main function
if __name__ == "__main__":
    # Initialize the robot
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster

    # Setup camera and gimbal
    center_x = 1280 / 2
    center_y = 720 / 2
    ep_camera.start_video_stream(display=False)
    ep_gimbal.sub_angle(freq=50)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    count = 0
    time.sleep(1)

    # PID controller constants
    p = 0.6 / 2.2
    i = p / (0.6 / 1.2)
    d = 0

    # Data tracking for analysis
    data_pith_yaw = []
    accumulate_x = 0
    accumulate_y = 0
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
    stop_start_time = None 
    last_marker = None

    while True:
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        markers, score = duck_detection(img, 10, templates[0].shape[:2], templates[0], template_r, template_g, template_b)

        if len(markers) != 0:
            after_time = time.time()
            x, y = markers[-1].center
            if 0.7 < score < 0.86:
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

    # Clean up
    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()
