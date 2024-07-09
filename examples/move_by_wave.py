import pandas as pd
from robomaster import robot
import time
import keyboard
import matplotlib.pyplot as plt
import csv

x_pos = []  # เพิ่มลิสต์เก็บตำแหน่ง
times = []
target = []

global expect
expect = 1

def sub_position_handler(position_info):
    x, y, z = position_info
    x_pos.append(x)
    global fm_x
    global fm_y
    #print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x= "{:.2f}".format(float(x))    
    fm_y= "{:.2f}".format(float(y)) 
    
    times.append(time.time()-start)
    target.append(expect)


def toggle_target(expect):
    if expect == 1:
        return 0
    elif expect == 0:
        return 1


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    
    ref_x = 1
    ref_y = 0
    speed = 50
    slp = 1
    count = 0
    c = 0
    
    p = 150
    start = time.time()
    ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
    time.sleep(1)
    while c < 2:
        
        if float(fm_x) and count == 0:
            fm_x = float(fm_x)
            fm_y = float(fm_y)

            err_x = (
                ref_x - fm_x
            )
            err_y = (
                ref_y - fm_y
            )
            
        
            if p*err_x>=50:
                speed = p*(err_x)
            else:
                speed == 50
            print(err_x,fm_x,fm_y)
            # print(target)
            # print(len(target),len(x_pos),len(times))
            ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
            # if float(fm_y) > 0.07:
            #     speed_y = p*(err_y*50)
            #     ep_chassis.drive_wheels(w1=speed_y, w2=0, w3=0, w4=0)
            # if float(fm_y) > -0.07:
            #     speed_y = p*(err_y*50)
            #     ep_chassis.drive_wheels(w1=0, w2=speed_y, w3=0, w4=0)
            if round(float(fm_x),5)>=1.0:
                #ep_chassis.move(x=1, y=0, z=0, xy_speed=0.6).wait_for_completed()
                ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                time.sleep(2)
                expect = toggle_target(expect)
                count += 1
                
        if count == 1:
            fm_x = float(fm_x)
            err_x = (
                fm_x 
            )
            if p*(err_x)>=50:
                speed = p*(err_x)
            else:
                speed == 16
            print(err_x,fm_x,fm_y)
            # print(target)
            # print(len(target),len(x_pos),len(times))
            ep_chassis.drive_wheels(w1=-speed, w2=-speed, w3=-speed, w4=-speed)
            if round(float(fm_x),5) <= 0.0:
                #ep_chassis.move(x=0, y=0, z=0, xy_speed=0.6).wait_for_completed()
                ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                time.sleep(2)
                expect = toggle_target(expect)
                c+=1
                count -= 1
        
                    
            # if keyboard.is_pressed('q'):
            #     ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            #     print('finish')
            #     print(len(target),len(x_pos),len(times))
            #     break


    ep_chassis.unsub_position()

    ep_robot.close()
    # df = pd.read_csv('POS.csv')
    plt.figure(figsize=(6, 6))
    plt.plot(times, target)
    plt.plot(times, x_pos)
    plt.title('Robot MAP')
    plt.ylabel('X position')
    plt.xlabel('Time')
    plt.tight_layout()
    plt.show()
  
