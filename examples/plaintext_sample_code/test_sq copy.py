import pandas as pd
from robomaster import robot

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง

def sub_position_handler(position_info):
    x, y, z = position_info
     

    print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x= "{:.2f}".format(float(x))    
    fm_y= "{:.2f}".format(float(y))  

    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    j=0
  
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    while j < 5:
        x_val = 1.2
        y_val = 0.6
        z_val = -90
        i = 0
        
        while i < 4:
            ep_chassis.move(x=x_val, y=0, z=0, xy_speed=0.6).wait_for_completed()
            ep_chassis.move(x=0, y=0, z=z_val, z_speed=45).wait_for_completed()
            i += 1
        j+=1
        
    ep_chassis.unsub_position()
    ep_robot.close()
    
    # สร้าง DataFrame จากข้อมูลตำแหน่งที่เก็บไว้
    df = pd.DataFrame(positions)
    
    # บันทึกเป็นไฟล์ CSV
    df.to_csv('robot_positions_before.csv', index=False)