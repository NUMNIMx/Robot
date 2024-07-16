import pandas as pd
from robomaster import robot
import time

positions = []  # เพิ่มลิสต์เก็บตำแหน่ง
list_attitude = []
list_imu = []
list_esc = []
lst_time = []
list_tof = []
c_time = time.time()
    
#attitude
def sub_attitude_info_handler(attitude_info):
    yaw, pitch, roll = attitude_info
    
    end = time.time()-c_time
    print("chassis attitude: yaw:{0}, pitch:{1}, roll:{2} ".format(yaw, pitch, roll))
    list_attitude.append("yaw:{0}, pitch:{1}, roll:{2} ".format(yaw, pitch, roll))
    lst_time.append("seacound:{0}".format(end))
#position
def sub_position_handler(position_info):
    x, y, z = position_info
    global fm_x
    global fm_y
    #print("chassis position: x:{0}, y:{1}, z:{2}".format(x, y, z))
    fm_x = float("{:.4f}".format(float(x)))    
    fm_y= float("{:.4f}".format(float(y)))  
    
    positions.append({'x': fm_x, 'y': fm_y,'z':z})#เก็บตำแหน่งx และ y ในลิสต์
#imu
def sub_imu_info_handler(imu_info):
    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = imu_info
    print("chassis imu: acc_x:{0}, acc_y:{1}, acc_z:{2}, gyro_x:{3}, gyro_y:{4}, gyro_z:{5}".format(
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z))
    list_imu.append("acc_x:{0}, acc_y:{1}, acc_z:{2}, gyro_x:{3}, gyro_y:{4}, gyro_z:{5}".format(
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z))
#esc
def sub_esc_info_handler(esc_info):
    speed, angle, timestamp, state = esc_info
    print("chassis esc: speed:{0}, angle:{1}, timestamp:{2}, state:{3}".format(speed, angle, timestamp, state))
    list_esc.append("speed:{0}, angle:{1}, timestamp:{2}, state:{3}".format(speed, angle, timestamp, state))

#tof
def sub_data_handler(sub_info):
    distance = sub_info
    print("tof1:{0}  tof2:{1}  tof3:{2}  tof4:{3}".format(distance[0], distance[1], distance[2], distance[3]))
    list_tof.append("tof1:{0}".format(distance[0]))

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_sensor = ep_robot.sensor
    ep_chassis = ep_robot.chassis
    ep_gimbal = ep_robot.gimbal
    previous_time = time.time()
    j = 0
    ep_sensor.sub_distance(freq=10, callback=sub_data_handler)
    ep_chassis.sub_esc(freq=10, callback=sub_esc_info_handler)
    ep_chassis.sub_imu(freq=10, callback=sub_imu_info_handler)
    ep_chassis.sub_attitude(freq=10, callback=sub_attitude_info_handler)
    ep_chassis.sub_position(freq=10, callback=sub_position_handler)
    time.sleep(1)
    while j<3:
        
        x_val = 0.2 ; x_val2 = 0.6 ; x_val3 = 0.4 ; x_val4 = 0
        y_val = 0 ; y_val2 = 0.2 ; y_val3 = 0.6 ; y_val4 = 0.4
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
            x_val += 0.2
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
            y_val2 += 0.2
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
            x_val3 -= 0.2
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
            y_val4 -= 0.2
    
    
            print(fm_x,fm_y)
            i += 1
            if i == 3 :
                ep_chassis.move(x=0, y=0, z=z_val, z_speed=150).wait_for_completed()
                i = 0
                break
        ep_gimbal.recenter(pitch_speed=300, yaw_speed=300).wait_for_completed()

        j+=1
    end_time=time.time()
    now_time= end_time-previous_time
    print(now_time)
    ep_sensor.unsub_distance()
    ep_chassis.unsub_esc()
    ep_chassis.unsub_imu()
    ep_chassis.unsub_attitude()
    ep_chassis.unsub_position()
    

    ep_robot.close()
    
    # สร้าง DataFrame จากข้อมูลตำแหน่งที่เก็บไว้
    df1 = pd.DataFrame(positions)
    df2 = pd.DataFrame(list_attitude)
    df3 = pd.DataFrame(list_esc)
    df4 = pd.DataFrame(list_imu)
    df5 = pd.DataFrame(list_tof)
    df6 = pd.DataFrame(lst_time)
    
    # บันทึกเป็นไฟล์ CSV
    df1.to_csv('robot_positions.csv', index=False)
    df2.to_csv('robot_attitude.csv', index=False)
    df3.to_csv('robot_esc.csv', index=False)
    df4.to_csv('robot_imu.csv', index=False)
    df5.to_csv('robot_tof.csv', index=False)
    df6.to_csv("timme.csv",index=False)


