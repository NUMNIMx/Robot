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
    print(fm_x,fm_y)

    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    
    ref_x = 1
    ref_y = 0
    r_x = 0
    r_y = 0
    ep_chassis.move(x=ref_x, y=ref_y, z=0, xy_speed=0.6)
    
    time.sleep(1)
    
    p = 0.5

    while True:

        if fm_x != ref_x:
            err_x = (
                float(ref_x) - float(fm_x)
            )
            err_y = (
                float(ref_y) - float(fm_y)
            )
            ep_chassis.move(x=err_x, y=err_y, z=0, x_speed=p*err_x,y_speed=p*err_y).wait_for_completed()
        if fm_x <= ref_x:
            err_x = (
                 float(fm_x)- float(ref_x) 
            )
            err_y = (
                 float(fm_y)- float(ref_y) 
            )
            ep_chassis.move(x=err_x, y=err_y, z=0, x_speed=p*err_x,y_speed=p*err_y).wait_for_completed()
            
        if fm_x == ref_x:
            err1_x = (
                float(r_x) - float(fm_x)
            )
            err1_y = (
                float(r_y) - float(fm_y)
            )
            ep_chassis.move(x=err1_x, y=err1_y, z=0, x_speed=p*err_x,y_speed=p*err_y).wait_for_completed()