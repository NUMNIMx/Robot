import pandas as pd
from robomaster import robot
import time

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง

def sub_position_handler(position_info):
    x, y, z = position_info
     
    global fm_x
    global fm_y
    print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x= "{:.2f}".format(float(x))    
    fm_y= "{:.2f}".format(float(y))  

    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    
    ref_x = 0.6
    ref_y = 0
    ep_chassis.move(x=ref_x, y=ref_y, z=0, xy_speed=0.6).wait_for_completed()
    
    time.sleep(1)
    
    p = 0.5

    while True:

        if fm_x <= 1:
            err_x = (
                ref_x - fm_x
            )

            err_y = (
                ref_y - fm_y
            )
            if fm_x >= 0:
                speed_x = (
                    (p*err_x)
                )
                speed_y = (
                    (p*err_y)
                )
                ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=5)
        else:
            ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
