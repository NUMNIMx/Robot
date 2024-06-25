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
    j = 0
   
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    time.sleep(1)
    while j<2:
        x_val = 0.4 ; x_val2 = 1.2 ; x_val3 = 0.8 ; x_val4 = 0
        y_val = 0 ; y_val2 = 0.4 ; y_val3 = 1.2 ; y_val4 = 0.8
        z_val = -90
        i = 0 
        y_dif=0
        x_dif=0
        #รอบที่ 1 จุดมุ่งหมาย x = 1.2 y = 0
        while True:
            if float(fm_x) != x_val:
                x_dif=x_val-fm_x
            if float(fm_y) != y_val:
                y_dif=y_val-fm_y
            ep_chassis.move(x=x_dif, y=y_dif, z=0, xy_speed=6).wait_for_completed()
            x_val += 0.4
            print(fm_x,fm_y)
            i += 1
            if i == 3 :
                ep_chassis.move(x=0, y=0, z=z_val, z_speed=150).wait_for_completed()
                i = 0
                break
        #รอบที่ 2 x should be 1.2 y should be 1.2
        while True:
            if float(fm_x) != x_val2:
                x_dif=x_val2-fm_x
            if float(fm_y) != y_val2:
                y_dif=y_val2-fm_y
            ep_chassis.move(x=y_dif, y=-(x_dif), z=0, xy_speed=6).wait_for_completed()
            y_val2 += 0.4
            print(fm_x,fm_y)
            i += 1
            if i == 3 :
                ep_chassis.move(x=0, y=0, z=z_val, z_speed=150).wait_for_completed()
                i = 0
                break
        #รอบที่ 3
        while True :
            if float(fm_x) != x_val3:
                x_dif=x_val3-fm_x
            if float(fm_y) != y_val3:
                y_dif=y_val3-fm_y
            ep_chassis.move(x=-(x_dif), y=-(y_dif), z=0, xy_speed=6).wait_for_completed()
            x_val3 -= 0.4
            print(fm_x,fm_y)
            i += 1
            if i == 3 :
                ep_chassis.move(x=0, y=0, z=z_val, z_speed=150).wait_for_completed()
                i = 0
                break
        #รอบที่ 4
        while True:
            if float(fm_x) != x_val4:
                x_dif=x_val4-fm_x
            if float(fm_y) != y_val4:
                y_dif=y_val4-fm_y
            ep_chassis.move(x=-(y_dif), y=x_dif, z=0, xy_speed=6).wait_for_completed()
            y_val4 -= 0.4
            print(fm_x,fm_y)
            i += 1
            if i == 3 :
                ep_chassis.move(x=0, y=0, z=z_val, z_speed=150).wait_for_completed()
                i = 0
                break
        j+=1

    ep_chassis.unsub_position()

    ep_robot.close()
    
    # สร้าง DataFrame จากข้อมูลตำแหน่งที่เก็บไว้
    df = pd.DataFrame(positions)
    
    # บันทึกเป็นไฟล์ CSV
    df.to_csv('robot_positions.csv', index=False)