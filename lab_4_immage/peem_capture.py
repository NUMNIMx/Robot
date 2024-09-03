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
def save_scv(ep_camera):
    f = ep_camera.read_cv2_image(strategy="newest") 
    cv2.imwrite('a5_0.1floor.jpg', f)
    print("capture complete")


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")

    ep_camera = ep_robot.camera

    # 显示十秒图传
    start = time.time()
    ep_camera.start_video_stream(display=True, resolution=camera.STREAM_360P)
    end = time.time()
    print(end-start)
    time.sleep(3)
    save_scv(ep_camera)
    
    ep_camera.stop_video_stream()
    ep_robot.close()
