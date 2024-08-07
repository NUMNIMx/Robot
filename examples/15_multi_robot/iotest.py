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

import robomaster
from robomaster import robot
import time

def sub_data_handler(sub_info):
    io_data, ad_data = sub_info
    print("io value: {0}, ad value: {1}".format(io_data, ad_data))
    if io_data[0] == 1:
        ep_chassis.drive_speed(x=0.5)  # Move forward with a speed of 0.5 m/s
    else:
        ep_chassis.drive_speed(x=0)  # Stop the robot

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor_adaptor
    ep_sensor.sub_adapter(freq=5, callback=sub_data_handler)
    
    try:
        time.sleep(60)  # Keep the program running for 60 seconds
    finally:
        ep_sensor.unsub_adapter()
        ep_robot.close()
