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


from robomaster import robot
import time

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_sensor_adaptor = ep_robot.sensor_adaptor

    try:
        while True:
            # 获取传感器转接板io电平
            io_left = ep_sensor_adaptor.get_io(id=1, port=2)
            io_right = ep_sensor_adaptor.get_io(id=2, port=2)

            # Print the sensor datฟ
            print('--------------------------')
            print("ซ้าย = {0}".format(io_left))
            print("ขวา = {0}".format(io_right))
            print('--------------------------') 

            # Pause briefly between readings
            time.sleep(1)

    except KeyboardInterrupt:
        # Safely close the connection when the loop is interrupted
        print("Program interrupted. Closing robot connection.")
    
    finally:
        ep_robot.close()
