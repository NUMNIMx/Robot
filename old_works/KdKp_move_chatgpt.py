import pandas as pd
from robomaster import robot
import time

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง

def sub_position_handler(position_info):
    x, y, z = position_info

    global fm_x
    global fm_y
    print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = "{:.2f}".format(float(x))
    fm_y = "{:.2f}".format(float(y))
    print(fm_x, fm_y)

    positions.append({'x': fm_x, 'y': fm_y, 'z': z})  # เก็บตำแหน่ง x และ y ในลิสต์

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)

    ref_x = 1
    ref_y = 0
    goal_x = 0
    goal_y = 0
    count = 0

    Kp = 1
    Kd = 0.1  # ค่า Kd ที่เพิ่มเข้ามา
    previous_error_x = 0
    previous_error_y = 0
    previous_time = time.time()

    ep_chassis.move(x=ref_x, y=ref_y, z=0, xy_speed=0.6)
    time.sleep(0.1)
    
    for i in range(2):
        count = 0
        while True:
            current_time = time.time()
            delta_time = current_time - previous_time
            if delta_time == 0:
                delta_time = 0.01  # เพื่อป้องกันการหารด้วย 0
            
            # เดินไปพิกัด 1
            if float(fm_x) < 1 and count == 0:
                ref_x = 1
                error_x = float(ref_x) - float(fm_x)
                error_y = float(ref_y) - float(fm_y)
                
                derivative_x = (error_x - previous_error_x) / delta_time
                derivative_y = (error_y - previous_error_y) / delta_time

                if float(fm_x) < 1:
                    speed_x = Kp * error_x + Kd * derivative_x
                    speed_x = max(min(speed_x, 1), 0.15)
                    speed_y = Kp * error_y + Kd * derivative_y
                    
                    ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=1)
                    
                # ถอยกลับมา 1
                if float(fm_x) > 1 and count == 0:
                    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=1)
                    time.sleep(0.1)
                    
                    if float(fm_x) > 1:
                        speed_x = Kp * error_x + Kd * derivative_x
                        speed_x = max(min(speed_x, -0.15), -1)
                        speed_y = Kp * error_y + Kd * derivative_y
                        
                        ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=1)
                        
            # ถ้าเท่ากับ 1 ให้หยุด
            if float(fm_x) == 1.00 and count == 0:
                ep_chassis.drive_speed(x=0, y=0, z=0, timeout=1)
                time.sleep(2)
                count += 1
                
            # เดินไปพิกัด 0
            if float(fm_x) > 0 and count == 1:
                ref_x = 0
                error_x = float(ref_x) - float(fm_x)
                error_y = float(ref_y) - float(fm_y)
                
                derivative_x = (error_x - previous_error_x) / delta_time
                derivative_y = (error_y - previous_error_y) / delta_time
                
                if float(fm_x) > 0:
                    speed_x = Kp * error_x + Kd * derivative_x
                    speed_x = max(min(speed_x, -0.15), -1)
                    speed_y = Kp * error_y + Kd * derivative_y
                    
                    ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=1)
                    
                if float(fm_x) < 0 and count == 1:
                    ep_chassis.drive_speed(x=0, y=0, z=0, timeout=1)
                    time.sleep(0.1)
                    
                    if float(fm_x) < 0:
                        speed_x = Kp * error_x + Kd * derivative_x
                        speed_x = max(min(speed_x, 0.15), 1)
                        speed_y = Kp * error_y + Kd * derivative_y
                        
                        ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0, timeout=1)
                        
            if float(fm_x) == 0.00 and count == 1:
                ep_chassis.drive_speed(x=0, y=0, z=0, timeout=1)
                time.sleep(2)
                break
            
            previous_error_x = error_x
            previous_error_y = error_y
            previous_time = current_time

    ep_chassis.unsub_position()
    ep_robot.close()