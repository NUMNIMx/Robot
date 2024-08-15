import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot

axis = {'x':[],'y':[]}
ad = {'left':[0],'right':[0]}
l_tof = []
s = [0,0,0]
speed = 30
time_values = [0]
start_time = time.time()
previous_filtered_left = 0.0
previous_filtered_right = 0.0
alpha = 0.3
filtered_left_values = []
filtered_right_values = []
time_plot_values = []

def adc_l(left):
    vl_volt = ((left / 1023) * 3.1)
    if vl_volt >= 1.6:
        cm1 = ((vl_volt - 4.2) / -0.326)-1.6
        ad['left'].append(cm1)
        # print('cmL = ',cm1)
    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1)-2
        ad['left'].append(cm1)
        # print('cmL = ',cm1)
    else:
        cm1 = 'empty'
        ad['left'].append(cm1)
        # print('cmL = ',cm1)

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326)-2
        ad['right'].append(cm2)
        # print('cmR = ',cm2)
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1)-2
        ad['right'].append(cm2)
        # print('cmR = ',cm2)
    else:
        cm2 = 'empty'
        ad['right'].append(cm2)
        # print('cmR = ',cm2)

def sub_data_handler2(sub_info):
    global previous_filtered_left, previous_filtered_right
    io, ad_data = sub_info
    
    # Raw sensor readings
    raw_left = float(ad_data[0])
    raw_right = float(ad_data[2])

    # Apply the low-pass filter
    filtered_left = low_pass_filter(raw_left, previous_filtered_left, alpha)
    filtered_right = low_pass_filter(raw_right, previous_filtered_right, alpha)

    # Update the previous filtered values
    previous_filtered_left = filtered_left
    previous_filtered_right = filtered_right

    # Store the filtered values for plotting
    filtered_left_values.append(filtered_left)
    filtered_right_values.append(filtered_right)

    # Calculate time for plotting
    end_time = time.time() - start_time
    time_plot_values.append(end_time)

    # Update the state with filtered values
    # ad['left'].append(filtered_left)
    # ad['right'].append(filtered_right)
    adc_r(raw_right)
    adc_l(raw_left)
    state(l_tof, ad)

def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(round(float(x), 3))
    axis['y'].append(round(float(y), 3))

def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    state(l_tof, ad)

def state(tof, charp):
    min_charp = 20
    if len(tof) > 0:
        if tof[-1] <= 200:
            s[1] = 1
        else:
            s[1] = 0
    
    if len(charp['left']) > 0:
        if charp['left'][-1] == 'empty':
            s[0] = 0
        if charp['left'][-1] <= min_charp:
            s[0] = 1
        else:
            s[0] = 0
    
    if len(charp['right']) > 0:
        if charp['right'][-1] == 'empty':
            s[2] = 0
        if charp['right'][-1] <= min_charp:
            s[2] = 1
        else:
            s[2] = 0

    
    #print("Updated s:", s)
    # change_state(s)
def low_pass_filter(current_value, previous_filtered_value, alpha):
    # Apply the IIR filter
    filtered_value = current_value + (alpha) * previous_filtered_value
    return filtered_value

def center_reset(adl,adr):
    move = 0 
    if adl <= 9 :
        move = (adl - 9)/100
        if abs(move) <= 0.15 :
            ep_chassis.move(x=0, y=0.05, z=0, xy_speed=0.1)
            print('move complete')
        else:
            ep_chassis.move(x=0, y=move, z=0, xy_speed=0.1)
            print('move complete')
        time.sleep(3)
    if adr <= 5 :
        move = (adr - 9)/100
        if abs(move) <= 0.15 :
            ep_chassis.move(x=0, y=-0.05, z=0, xy_speed=0.1)
            print('move complete')
        else:
            ep_chassis.move(x=0, y=move, z=0, xy_speed=0.1)
            print('move complete')
        time.sleep(3)
    
def plot_ss_tof(l_tof):
    plt.figure(figsize=(8, 4))
    plt.plot(time_plot_values, l_tof , label='tof Sensor ', color='red')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (cm)')
    plt.title('tof Sensor')
    plt.legend()
    plt.grid(True)
    plt.show()
def plot_ss_tof(adl):
    plt.figure(figsize=(8, 4))
    plt.plot(time_plot_values, adl, label='sharp_left Sensor ', color='green')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (cm)')
    plt.title('sharp_left Sensor')
    plt.legend()
    plt.grid(True)
    plt.show()
def plot_ss_tof(adr):
    plt.figure(figsize=(8, 4))
    plt.plot(time_plot_values, adr , label='sharp_right Sensor ', color='blue')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (cm)')
    plt.title('sharp_right Sensor')
    plt.legend()
    plt.grid(True)
    plt.show()
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_gimbal = ep_robot.gimbal
    ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
    ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_data_handler2)
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    
    p = 1
    # i = p/(0.6/2)
    # d = p*(0.6/8)
    # p = 0
    i = 0
    d = 0
    speed = 30
    count = 0
    time.sleep(1)
    target_x = axis['x'][0]
    accumulate_x = 0
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
    move_speed = 0
    end = 0
    I = 0
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    time.sleep(1)
    while I != 1:
        if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'): 
            center_reset(ad['left'][-1], ad['right'][-1])
        ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
        if s[1] == 1:
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            I += 1
    ep_chassis.move(x=0, y=0, z=-180,z_speed=100).wait_for_completed()
    time.sleep(1)
    print(target_x)
    while end != 1:
        now_x = axis['x'][-1]
        after_time = time.time()
        err_x = abs(target_x-now_x)
        accumulate_x += err_x*(after_time-prev_time)
        if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'): 
            center_reset(ad['left'][-1], ad['right'][-1])
        if count >= 1:
            speed_x = (
                (p * err_x)+ d*((err_x-prev_err_x)/(after_time-prev_time)) + i*accumulate_x
            )
            move_speed = (speed_x)*100
            time.sleep(0.001)
            if move_speed > 60:
                move_speed = 60
            elif move_speed < 15 and move_speed > 0:
                move_speed = 15
            elif move_speed > -15 and move_speed < 0:
                move_speed = -15
            elif move_speed < -60:
                move_speed = -60
            ep_chassis.drive_wheels(w1=move_speed, w2=move_speed, w3=move_speed, w4=move_speed)
        if abs(err_x) < 0.05:
            ep_chassis.drive_speed(x=0, y=0, z=0)
            end = 1
            
            
        count += 1
        time.sleep(0.2)
        print('target',target_x)
        print(now_x)
        print('prev time = ',prev_time)
        print('time = ',after_time)
        print('move_speed = ',move_speed)
        print('err_x = ',err_x)

    
    time.sleep(0.01)
    prev_time = after_time
    prev_err_x = err_x
    time.sleep(0.01)
    

    ep_sensor_adaptor.unsub_adapter()
    ep_sensor.unsub_distance()
    ep_chassis.unsub_position()
    ep_robot.close()