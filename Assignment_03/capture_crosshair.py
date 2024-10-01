# -*-coding:utf-8-*-
# Copyright (c) 2020 DJI.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cv2
import time
from robomaster import robot
from robomaster import camera
from robomaster import blaster

def draw_crosshair(frame):
    """Draw a crosshair at the center of the frame."""
    height, width = frame.shape[:2]
    # Define the center of the frame
    center_x, center_y = width // 2, height // 2
    # Draw horizontal and vertical lines for the crosshair
    color = (0, 255, 0)  # Green crosshair
    thickness = 2
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), color, thickness)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), color, thickness)

def save_scv(ep_camera):
    """Save an image from the camera feed."""
    frame = ep_camera.read_cv2_image(strategy="newest") 
    cv2.imwrite('bottleman_3_plate.jpg', frame)
    print("Capture complete.")

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster
    ep_gimbal = ep_robot.gimbal

    # Show video stream for 10 seconds
    start = time.time()
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    # ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    ep_gimbal.moveto(pitch=-5, yaw=0 ,pitch_speed=35, yaw_speed=0).wait_for_completed()
    while True:
        # Get the latest frame from the camera
        frame = ep_camera.read_cv2_image(strategy="newest")
        ep_blaster.set_led(brightness=0, effect=blaster.LED_ON)
        time.sleep(1)
        if frame is not None:
            # Draw the crosshair on the frame
            draw_crosshair(frame)
            # Display the frame with the crosshair
            cv2.imshow("RoboMaster Video Stream", frame)
            
            # Press 'q' to exit the video stream display
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    end = time.time()
    print(f"Video streaming duration: {end - start} seconds")
    
    save_scv(ep_camera)
    ep_blaster.set_led(brightness=0, effect=blaster.LED_OFF)
    
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
