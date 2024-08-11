import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot

states = ['foward','left','right','turnback']
l_tof = []
axis = {'x':[],'y':[]}
ad = {'left':[0],'right':[0]}
s = [0,0,0]
speed = 15
time_values = [0]
start_time = time.time()

# สร้างฟิลเตอร์ Low-Pass สำหรับเซ็นเซอร์แต่ละตัว
class LowPassFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.filtered_value = None

    def filter(self, value):
        if self.filtered_value is None:
            self.filtered_value = value
        else:
            self.filtered_value = self.alpha * value + (1 - self.alpha) * self.filtered_value
        return self.filtered_value

left_filter = LowPassFilter(alpha=0.1)
right_filter = LowPassFilter(alpha=0.1)

def adc_l(left):
    vl_volt = ((left / 1023) * 3.1)
    if vl_volt >= 1.6:
        cm1 = ((vl_volt - 4.2) / -0.326) - 1.6
    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1) - 2
    else:
        cm1 = 'empty'

    if cm1 != 'empty':
        cm1 = left_filter.filter(cm1)
        ad['left'].append(cm1)
    else:
        ad['left'].append(cm1)
    
    print('cmL = ', cm1)

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326) - 2
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1) - 2
    else:
        cm2 = 'empty'

    if cm2 != 'empty':
        cm2 = right_filter.filter(cm2)
        ad['right'].append(cm2)
    else:
        ad['right'].append(cm2)
    
    print('cmR = ', cm2)

def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    state(l_tof, ad)

def sub_data_handler2(sub_info):
    io, ad_data = sub_info
    adc_l(float(ad_data[0]))
    adc_r(float(ad_data[2]))
    end_time = time.time() - start_time
    time_values.append(end_time)
    state(l_tof, ad)

def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(float(x))
    axis['y'].append(float(y))

def state(tof, charp):
    min_charp = 20
    if len(tof) > 0:
        if tof[-1] <= 290:
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
    # print("Updated s:", s)

def change_state(s):
    if s[1] == 0:
        state = states[0]
    elif s[1] == 1:
        if s[0] == 0:
            state = states[1]
        elif s[0] == 1:
            if s[2] == 0:
                state = states[2]
            elif s[2] == 1:
                state = states[3]
    print(state)

def center_cal(adl, adr):
    if adl > adr or adl < adr:
        print("hello")
        center = (adl + adr) / 2
        move = (center - adl) / 100
        print('move = ', move)
        print('center = ', center)
        if move >= 1.5:
            ep_chassis.move(x=0, y=move, z=0, xy_speed=0.7)
        else:
            ep_chassis.move(x=0, y=move * 2.2, z=0, xy_speed=0.7)
        print('move complete')
        time.sleep(3)
    else:
        print("Boom")

def center_cal2(adl, adr):
    if adl < 12:
        ep_chassis.move(x=0, y=0.3, z=0, xy_speed=0.15)
        print('move complete')
        time.sleep(3)
    if adr < 12:
        ep_chassis.move(x=0, y=-0.3, z=0, xy_speed=0.15)
        print('move complete')

def move_forward(l_tof, axis, s):
    lst_c_pos = {'x_c': [], 'y_c': []}
    while s[1] == 0:
        if s[1] == 0:
            ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
            print(l_tof[-1])

            if l_tof[-1] <= 290:
                ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                lst_c_pos['x_c'].append(axis['x'][-1])
                lst_c_pos['y_c'].append(axis['y'][-1])
                print(lst_c_pos)
                break

def maze_runner(s):
    l_s = 0
    r_s = 0
    if s[0] == 0 and s[2] == 0 and s[1] == 1:
        if l_s == r_s:
            r_s += 1
            ep_chassis.move(x=0, y=0, z=-90, xy_speed=0.7)
        elif l_s > r_s:
            r_s += 1
            ep_chassis.move(x=0, y=0, z=90, xy_speed=0.7)
        elif l_s < r_s:
            l_s += 1
            ep_chassis.move(x=0, y=0, z=-90, xy_speed=0.7)

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
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_gimbal = ep_robot.gimbal
    ep_sensor_adaptor.sub_adapter(freq=5, callback=sub_data_handler2)
    ep_sensor.sub_distance(freq=5, callback=sub_data_handler)
    ep_chassis.sub_position(freq=5, callback=sub_position_handler)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    while True:
        print(s)
        if s[0] == 1 and s[1] == 1 and s[2] == 1:
            turnback()
            move_forward(l_tof, axis, s)
        if s[0] == 1 and s[1] == 1 and s[2] == 0:
            turnright()
            move_forward(l_tof, axis, s)
        if s[0] == 1 and s[1] == 0 and s[2] == 1:
            move_forward(l_tof, axis, s)
        elif s[0] == 1 and s[1] == 0 and s[2] == 0:
            turnright()
            move_forward(l_tof, axis, s)
        if s[0] == 0 and s[1] == 1 and s[2] == 1:
            turnleft()
            move_forward(l_tof, axis, s)
        if s[0] == 0 and s[1] == 0 and s[2] == 1:
            turnleft()
            move_forward(l_tof, axis, s)

        # if s[1] == 0:
        #     if s[0] == 1 and s[2] == 1:
        #         move_forward(l_tof, axis, s)
        #     if s[0] == 1 and s[2] == 0:
        #         turnright()
        #         move_forward(l_tof, axis, s)
        #     if s[2] == 1 and s[0] == 0:
        #         turnleft()
        #         move_forward(l_tof, axis, s)
        
        # if s[0] == 0:
        #     if s[1] == 1 and s[2] == 1:
        #         turnleft()
        #         move_forward(l_tof, axis, s)
        #     if s[2] == 0 and s[1] == 1:
        #         maze_runner(s)
                
        # if s[0] == 0 and s[1]==0  and s[2] == 1:
        #     turnleft()
        #     move_forward(l_tof, axis, s)
        # if s[0] == 1 and s[1]==0  and s[2] == 0:
        #     turnright()
        #     move_forward(l_tof, axis, s)
        # if s[0] == 0 and s[1] == 0 and s[2] == 1:
        #     maze_runner(s)
        
        else:
            turnback()

        if keyboard.is_pressed('q'):
            print("Exiting loop...")
            break
        
    ep_sensor_adaptor.unsub_adapter()
    ep_sensor.unsub_distance()
    ep_chassis.unsub_position()
    ep_robot.close()
