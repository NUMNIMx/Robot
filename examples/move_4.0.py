import pandas as pd
from robomaster import robot
import timeit
import time
import matplotlib.pyplot as plt
start = time.time() 
positions = []  # เพิ่มลิสต์เก็บตำแหน่ง
def sub_position_handler(position_info):
    x, y, z  = position_info
    
    global fm_x
    global fm_y
    #print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = float("{:.4f}".format(float(x)))    
    fm_y= float("{:.4f}".format(float(y)))
    positions.append({'x': fm_x, 'time': round((time.time()-start),2) ,'V': fm_x/round((time.time()-start),2)})
    #เก็บตำแหน่งx และ y ในลิ


if __name__ == '__main__':
    
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    x_val = 4
    y_val = 0.6
    z_val = -90
    i = 0
    
    ep_chassis.move(x=x_val, y=0, z=0, xy_speed=0.7).wait_for_completed()
    
    # T =end -start
    # V = fm_x/T
    # time.sleep(1)
    # print(start,end)
    # print('Time=',T)
    # print('S=',fm_x)
    # print("V=",V)
    # a = V/T
    # print('A=',a)
    # plt.figure(figsize=(6,6))
    # plt.plot(X, Y)
        # ep_chassis.move(x=0, y=0, z=z_val, z_speed=45).wait_for_completed()
        # i += 1
    # 前进 0.5米
    
    # 后退 0.5米
    #ep_chassis.move(x=-x_val, y=0, z=0, xy_speed=0.1).wait_for_completed()

    # 左移 0.6米
    #ep_chassis.move(x=0, y=-y_val, z=0, xy_speed=0.1).wait_for_completed()

    # 右移 0.6米
    #ep_chassis.move(x=0, y=y_val, z=0, xy_speed=0.1).wait_for_completed()

    # 左转 90度
    # 右转 90度
    #ep_chassis.move(x=0, y=0, z=-z_val, z_speed=45).wait_for_completed()
    ep_chassis.unsub_position()
    ep_robot.close()
    df = pd.DataFrame(positions)
    
    # บันทึกเป็นไฟล์ CSV
    df.to_csv('time_x.csv', index=False)