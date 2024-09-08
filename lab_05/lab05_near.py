import cv2
import robomaster
from robomaster import robot
from robomaster import vision
from robomaster import blaster
import time
import pandas as pd

start = time.time()

# Class for storing marker information
class MarkerInfo:
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info

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
        return self._info

markers = []

def on_detect_marker(marker_info):
    global markers
    number = len(marker_info)
    markers.clear()
    for i in range(number):
        x, y, w, h, info = marker_info[i]
        markers.append(MarkerInfo(x, y, w, h, info))

def sub_data_handler(angle_info):
    global list_of_data
    list_of_data = angle_info

if __name__ == "__main__":
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster

    center_x = (1280 / 2)
    center_y = 720 / 2

    ep_camera.start_video_stream(display=False)
    ep_gimbal.sub_angle(freq=50, callback=sub_data_handler)
    result = ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)
    
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    time.sleep(1)

    # PID controller constants
    p = 0.83 / 1.7
    i = p / (0.6 / 2)
    d = p * (0.6 / 8)

    data_pith_yaw = []
    accumulate_x = 0
    accumulate_y = 0

    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0

    while True:
        if markers:
            after_time = time.time()
            x, y = markers[-1].center

            err_x = center_x - x
            err_y = center_y - y
            dt = after_time - prev_time

            accumulate_x += err_x * dt
            accumulate_y += err_y * dt

            if dt > 0:
                speed_x = p * err_x + d * (err_x - prev_err_x) / dt + i * accumulate_x
                speed_y = p * err_y + d * (err_y - prev_err_y) / dt + i * accumulate_y

                ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)
                time.sleep(0.001)

                data_pith_yaw.append(
                    list(list_of_data) + [err_x, err_y, round(speed_x, 3), round(speed_y, 3), center_x, x, time.time() - start]
                )

            prev_time = after_time
            prev_err_x = err_x
            prev_err_y = err_y

        else:
            ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)

        img = ep_camera.read_cv2_image(strategy="newest", timeout=5)

        for marker in markers:
            cv2.rectangle(img, marker.pt1, marker.pt2, (0, 255, 0))
            cv2.putText(img, marker.text, marker.center, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.imshow("Markers", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

    result = ep_vision.unsub_detect_info(name="marker")
    ep_camera.stop_video_stream()
    ep_robot.close()
