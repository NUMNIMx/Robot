import pandas as pd
from robomaster import robot
import time

positions = []  # List to store positions

def sub_position_handler(position_info):
    x, y, z = position_info

    global fm_x
    global fm_y
    print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = "{:.2f}".format(float(x))    
    fm_y = "{:.2f}".format(float(y))  
    print(fm_x, fm_y)

    positions.append({'x': fm_x, 'y': fm_y, 'z': z})  # Store positions in the list

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    
    ref_x_forward = 1
    ref_y = 0
    ref_x_backward = 0
    
    p = 0.5
    move_forward = True
    
    try:
        while True:
            if move_forward:
                ep_chassis.move(x=ref_x_forward, y=ref_y, z=0, xy_speed=0.8).wait_for_completed()
                move_forward = False
            else:
                ep_chassis.move(x=ref_x_backward, y=ref_y, z=0, xy_speed=0.8).wait_for_completed()
                move_forward = True

            time.sleep(1)
            
            err_x = float(ref_x_forward) - float(fm_x) if move_forward else float(fm_x) - float(ref_x_backward)
            err_y = float(ref_y) - float(fm_y)
            
            speed_x = p * err_x
            speed_y = p * err_y
            
            ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=5)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        ep_chassis.unsub_position()
        ep_robot.close()
