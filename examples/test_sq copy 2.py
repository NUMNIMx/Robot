import pandas as pd
from robomaster import robot
import time

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง

def sub_position_handler(position_info):
    x, y, z = position_info
    global fm_x
    global fm_y
    #print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = float("{:.4f}".format(float(x)))    
    fm_y= float("{:.4f}".format(float(y)))  
    
    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์
    
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    x_val = 0.2 ; x_dif = x_val-fm_x
    y_val = 0 ; y_dif = 0
    z_val = -90
    i = 0
    
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    time.sleep(1)
    
    
    while i <= 6:
        if float(fm_x) < x_val:
            x_dif=x_val-
        if float(fm_x)> x_val:
            x_dif=x_val-v
        ep_chassis.move(x=x_dif, y=0, z=0, xy_speed=0.7).wait_for_completed()
        #ep_chassis.move(x=0, y=0, z=z_val, z_speed=45).wait_for_completed()
        i += 1
        print(fm_x,fm_y)

    ep_chassis.unsub_position()

    ep_robot.close()
    
    # สร้าง DataFrame จากข้อมูลตำแหน่งที่เก็บไว้
    df = pd.DataFrame(positions)
    
    # บันทึกเป็นไฟล์ CSV
    df.to_csv('robot_positions.csv', index=False)