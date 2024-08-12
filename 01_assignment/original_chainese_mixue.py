import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot

states = ['foward','left','right','turnback']
l_tof = []
axis = {'x':[],'y':[]}
ad = {'left':[0],'right':[0]}
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
# volt_to_cm = {
#     3.0: 2,
#     2.95: 3,
#     2.8: 4,
#     2.6: 5,
#     2.2: 6,
#     1.8: 8,
#     1.4: 12,
#     1.0: 18,
#     0.8: 22,
#     0.6: 28,
#     0.4: 34,
#     0.2: 38
# }

# def convert_volt_to_cm(volt):
#     # หาค่า cm ที่สอดคล้องกับ volt โดยการหาใกล้เคียงที่สุดใน dictionary
#     closest_volt = min(volt_to_cm.keys(), key=lambda k: abs(k - volt))
#     return volt_to_cm[closest_volt]
#sensors
#tof
def adc_l(left):
    vl_volt = ((left / 1023) * 3.1)
    if vl_volt >= 1.6:
        cm1 = ((vl_volt - 4.2) / -0.326)-1.6
        ad['left'].append(cm1)
        print('cmL = ',cm1)
    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1)-2
        ad['left'].append(cm1)
        print('cmL = ',cm1)
    else:
        cm1 = 'empty'
        ad['left'].append(cm1)
        print('cmL = ',cm1)

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326)-2
        ad['right'].append(cm2)
        print('cmR = ',cm2)
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1)-2
        ad['right'].append(cm2)
        print('cmR = ',cm2)
    else:
        cm2 = 'empty'
        ad['right'].append(cm2)
        print('cmR = ',cm2)


def low_pass_filter(current_value, previous_filtered_value, alpha):
    # Apply the IIR filter
    filtered_value = current_value + (alpha) * previous_filtered_value
    return filtered_value

def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    state(l_tof, ad)

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
    adc_r(filtered_right)
    adc_l(filtered_left)
    state(l_tof, ad)

def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(float(x))
    axis['y'].append(float(y))

def state(tof, charp):
    min_charp = 20
    if len(tof) > 0:
        if tof[-1] <= 250:
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

def change_state(s):
    if s[1] == 0 :
            state = states[0]
    elif s[1] == 1 :
        if s[0] == 0 :
            state = states[1]
        elif s[0] == 1 :
            if s[2] == 0 :
                state = states[2]
            elif s[2] == 1 :
                state = states[3]
    print(state)

def center_cal(adl, adr):
    if abs(adl - adr) >= 2:
        if adl > adr or adl < adr:
            print("hello")
            center=(adl + adr)/2
            move = (center-adl)/100
            print('move = ',move)
            print('center = ',center)
            if move >= 1.5 :
                ep_chassis.move(x=0, y=move, z=0, xy_speed=0.7)
            else:
                ep_chassis.move(x=0, y=move*2.2, z=0, xy_speed=0.7)
            print('move complete')
            time.sleep(3)
        else:
            print("Boom")

def center_reset(adl,adr):
    move = 0 
    if adl <= 5 :
        move = (adl - 5)/100
        if abs(move) <= 0.15 :
            ep_chassis.move(x=0, y=0.05, z=0, xy_speed=0.1)
            print('move complete')
        else:
            ep_chassis.move(x=0, y=move, z=0, xy_speed=0.1)
            print('move complete')
        time.sleep(3)
    if adr <= 5 :
        move = (adr - 5)/100
        if abs(move) <= 0.15 :
            ep_chassis.move(x=0, y=-0.05, z=0, xy_speed=0.1)
            print('move complete')
        else:
            ep_chassis.move(x=0, y=move, z=0, xy_speed=0.1)
            print('move complete')
        time.sleep(3)
# def center_cal(adl, adr):
#     if adl <= 11 :
#         move =  adl - 11
#         ep_chassis.move(x=0, y=move, z=0, xy_speed=0.15).wait_for_completed()
#         print('move complete')
#     if adr <= 11 :
#         move = adr - 11
#         ep_chassis.move(x=0, y=-move, z=0, xy_speed=0.15).wait_for_completed()
#         print('move complete')

def move_rside(l_tof,axis,s):
    while True:
        if keyboard.is_pressed('q'):
            print("Exiting loop...")
            break
        if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'):
            # center_cal(ad['left'][-1], ad['right'][-1]) 
            center_reset(ad['left'][-1], ad['right'][-1])
        if s[1]==0:
            ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
        if ad['right'][-1] == 'empty' and s[1]== 0 and (ad['left'][-1] != 'empty' or ad['left'][-1] == 'empty') :#(s[2]==0 and s[0]==1 and s[1]== 0)
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            time.sleep(0.5)
            ep_chassis.move(x=0.15, y=0, z=0, xy_speed=0.5).wait_for_completed()
            ep_chassis.move(x=0, y=0, z=-88, z_speed=120).wait_for_completed()
            ep_gimbal.recenter(pitch_speed=150, yaw_speed=150).wait_for_completed()
            ep_chassis.move(x=0.5, y=0, z=0, xy_speed=0.7).wait_for_completed()
            time.sleep(0.5)
        if ad['right'][-1] == 'empty' and s[1] == 1 and (ad['left'][-1] != 'empty' or ad['left'][-1] == 'empty') :#(s[2]==0 and s[0]==1 and s[1]== 1) :
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            time.sleep(0.5)
            ep_chassis.move(x=0, y=0, z=-88, z_speed=120).wait_for_completed()
            ep_gimbal.recenter(pitch_speed=150, yaw_speed=150).wait_for_completed()
            ep_chassis.move(x=0.55, y=0, z=0, xy_speed=0.7).wait_for_completed()
            time.sleep(0.5)
        if ad['right'][-1] != 'empty' and s[1] == 1 and ad['left'][-1] == 'empty':#(s[0] == 0 and s[1]==1 and s[2]==1)
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            time.sleep(0.5)
            ep_chassis.move(x=0, y=0, z=90, z_speed=120).wait_for_completed()
            ep_gimbal.recenter(pitch_speed=150, yaw_speed=150).wait_for_completed()
            time.sleep(0.5)
        if ad['right'][-1] != 'empty' and s[1] == 1 and ad['left'][-1] != 'empty':#s[0] == 1 and s[1] == 1 and s[2] == 1
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            time.sleep(0.5)
            ep_chassis.move(x=0, y=0, z=180, z_speed=100).wait_for_completed()
            ep_gimbal.recenter(pitch_speed=150, yaw_speed=150).wait_for_completed()
            time.sleep(0.5)
def move_forward(l_tof, axis, s):
    lst_c_pos = {'x_c': [], 'y_c': []}
    if s[1] == 0:
        ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
        #print(l_tof[-1])

        if l_tof[-1] <= 290:
            ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            s[1] = 1
            #print(lst_c_pos)

def turnleft():
    ep_chassis.move(x=0, y=0, z=90, xy_speed=0.7).wait_for_completed()
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

def turnright():
    ep_chassis.move(x=0, y=0, z=-90, xy_speed=0.7).wait_for_completed()
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

def turnback():
    ep_chassis.move(x=0, y=0, z=180, xy_speed=0.7).wait_for_completed()
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

if __name__ == '__main__':
    i=0
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_gimbal = ep_robot.gimbal
    ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_data_handler2)
    ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    time.sleep(1)

    while i != 1:
        if keyboard.is_pressed('q'):
            print("Exiting loop...")
            i = 1
        if s[1] == 0:
            move_rside(l_tof,axis,s)

    
    plt.figure(figsize=(10, 5))
    plt.plot(axis['y'], axis['x'], label='Path', marker='o')
    plt.title('Robot Movement Path')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.legend()
    plt.grid(True)
    plt.show()

    ep_sensor_adaptor.unsub_adapter()
    ep_sensor.unsub_distance()
    ep_chassis.unsub_position()
    ep_robot.close()
