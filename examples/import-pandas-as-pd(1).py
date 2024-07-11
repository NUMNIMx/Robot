import pandas as pd
from robomaster import robot
import time

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง
delta_time_all = []
def sub_position_handler(position_info):
    x, y, z = position_info
    global start_time
    global fm_x
    global fm_y
    print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x= "{:.2f}".format(float(x))    
    fm_y= "{:.2f}".format(float(y))
    end_time = time.time() - start_time  
    delta_time = float('{:.05f}'.format(end_time))

    print(fm_x,fm_y)
    delta_time_all.append(delta_time)
    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=5, callback=sub_position_handler)
    
    ref_x = 1
    ref_y = 0
    goal_x = 0
    goal_y = 0
    count = 0
    
    ep_chassis.move(x=ref_x, y=ref_y, z=0, xy_speed=0.6)
    time.sleep(0.1)
    p = 1
    for i in range(2):
        count = 0
        while True:
                #เดินไปพิกัด 1 
                if float(fm_x) < 1 and count == 0: 
                    ref_x = 1
                    err_x = (
                        float(ref_x) - float(fm_x)
                    )

                    err_y = (
                        float(ref_y) - float(fm_y)
                    )
                    if float(fm_x) < 1:
                        speed_x = (
                            (p*err_x)
                        )
                        if speed_x < 0.15 :
                                speed_x = 0.15
                        if speed_x > 1 :
                                speed_x = 1
                        speed_y = (
                            (p*err_y)
                        )
                        
                        ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0,timeout=1)
                    #ถอยกลับมา 1  
                    if float(fm_x) > 1 and count == 0:
                        ep_chassis.drive_speed(x=0, y=0, z=0,timeout=1)
                        time.sleep(0.1)
                        
                        if float(fm_x) > 1:
                            speed_x = (
                                (p*err_x)
                            )
                            if speed_x > -0.15 :
                                speed_x = -0.15
                            if speed_x < -1 :
                                speed_x = -1
                            speed_y = (
                                (p*err_y)
                            )
                            ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0,timeout=1)
                #ถ้าเท่ากับ 1 ให้หยุด
                if float(fm_x) == 1 and count == 0:
                    ep_chassis.drive_speed(x=0, y=0, z=0,timeout=1)
                    time.sleep(2)
                    count += 1
                #เดินไปพิกัด 0
                if float(fm_x) > 0 and count == 1:
                    ref_x = 0  
                    err_x = (
                        float(ref_x) - float(fm_x)
                    )

                    err_y = (
                        float(ref_y) - float(fm_y)
                    )
                    if float(fm_x) > 0:
                        speed_x = (
                            (p*err_x)
                        )
                        if speed_x > -0.15 :
                            speed_x = -0.15
                        if speed_x < -1 :
                            speed_x = -1
                        speed_y = (
                            (p*err_y)
                        )
                        
                        ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0,timeout=1)

                    if float(fm_x) < 0 and count == 1:
                        ep_chassis.drive_speed(x=0, y=0, z=0,timeout=1)
                        time.sleep(0.1)
                        
                        if float(fm_x) < 0:
                            speed_x = (
                                (p*err_x)
                            )
                            if speed_x < 0.15 :
                                speed_x = 0.15
                            if speed_x > 1 :
                                speed_x = 1
                            speed_y = (
                                (p*err_y)
                            )
                            ep_chassis.drive_speed(x=speed_x, y=speed_y, z=0,timeout=1)

                if float(fm_x) == 0 and count == 1: 
                    ep_chassis.drive_speed(x=0, y=0, z=0,timeout=1)
                    time.sleep(2)
                    break

    
    ep_chassis.unsub_position()
    ep_robot.close()                

       # else:
       #     ep_chassis.drive_speed(x=0, y=0, z=0, timeout=5)
        #    ep_chassis.unsub_position()
         #   ep_robot.close()
          #  break

