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
    x_val = 0.4 
    y_val = 0 ; 
    z_val = -90
    i = 0
    
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    time.sleep(1)
    
    #รอบที่ 1 จุดมุ่งหมาย x = 1.2 y = 0
    while True:
        if float(fm_x) != x_val:
            x_dif=x_val-fm_x
        if float(fm_y) != y_val:
            y_dif=y_val-fm_y
        ep_chassis.move(x=x_dif, y=y_dif, z=0, z_speed=45).wait_for_completed()
        x_val += 0.4
        i += 1
        if i == 3 :
            ep_chassis.move(x=0, y=0, z=z_val, z_speed=45).wait_for_completed()
            i = 0
            break
    
        print(fm_x,fm_y)

    ep_chassis.unsub_position()

    ep_robot.close()
    
    # สร้าง DataFrame จากข้อมูลตำแหน่งที่เก็บไว้
    df = pd.DataFrame(positions)
    
    # บันทึกเป็นไฟล์ CSV
    df.to_csv('robot_positions.csv', index=False)