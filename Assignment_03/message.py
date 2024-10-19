import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot
import numpy as np


states = ['foward','left','right','turnback']
l_tof = []
axis = {'x':[],'y':[]}
yaw_l = [0]
ad = {'left':[0],'right':[0]}
io_data = {'left':[],'right':[]}
sensor = [0,0,0]

mark_x = 0
mark_y = 0
max_grid_og_x = int(input("Max grid X: "))
max_grid_og_y = int(input("Max grid y: "))
max_grid_x = max_grid_og_x-1
max_grid_y = max_grid_og_y-1
end_ep = max_grid_og_x*max_grid_og_y
point_x = int(input('x: '))
point_y = int(input('y: '))
point_s = [point_x,point_y] #เปลี่ยนตามที่จารวาง
dict_memo = {}


speed = 30
time_values = [0]
start_time = time.time()
previous_filtered_left = 0.0
previous_filtered_right = 0.0
alpha = 0.3
filtered_left_values = []
filtered_right_values = []
time_plot_values = []
l_z = [-180,-90,0,90,180]
yaw_t = int()
#sensors
#tof

def check_min_distance(ltof,ftof,rtof):
    # สมมติว่า ltof, ftof, rtof ถูกกำหนดค่าแล้วก่อนหน้านี้
    distances = {'left': ltof, 'front': ftof, 'right': rtof}
    
    # หาค่าที่น้อยที่สุด
    min_direction = min(distances, key=distances.get)
    
    # ดำเนินการตามทิศทางที่มีค่าต่ำที่สุด
    if min_direction == 'left':
        print("Move to the left")
        # เพิ่มการเคลื่อนไหวไปทางซ้าย เช่น:
        ep_chassis.move(x=0, y=0, z=90, z_speed=50).wait_for_completed()
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        ep_chassis.move(x=0.6, y=0, z=0, xy_speed=0.5).wait_for_completed()
        change_point()
        memory_maze(point_s)
    
    elif min_direction == 'front':
        print("Move to the front")
        # เพิ่มการเคลื่อนไหวไปข้างหน้า เช่น:
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        ep_chassis.move(x=0.6, y=0, z=0, xy_speed=0.5).wait_for_completed()
        
        change_point()
        memory_maze(point_s)
    
    elif min_direction == 'right':
        print("Move to the right")
        # เพิ่มการเคลื่อนไหวไปทางขวา เช่น:
        ep_chassis.move(x=0, y=0, z=-90, z_speed=50).wait_for_completed()
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        ep_chassis.move(x=0.6, y=0, z=0, xy_speed=0.5).wait_for_completed()
        change_point()
        memory_maze(point_s)

def memo_soy(point_soy):
    global route
    route = []
    
    
        
def change_point(): #map
    global mark_x, mark_y  # Assuming you're using these variables globally
    # Check if robot has moved approximately 60 cm on the x-axis
    if 0.58 < axis['x'][-1] - mark_x < 0.62:  # If moved around 60 cm on the x-axis
        point_s[0] += 1  # Increase x-axis position
        mark_x = axis['x'][-1]  # Update mark_x to the latest position


    if 0.58 < axis['y'][-1] - mark_y < 0.62:
        point_s[1] += 1  # Increase y-axis position
        mark_y = axis['y'][-1]
        
    if -0.62 < axis['x'][-1] - mark_x < -0.58:
        point_s[0] -= 1  # Decrease x-axis position
        mark_x = axis['x'][-1]

    if -0.62 < axis['y'][-1] - mark_y < -0.58:
        point_s[1] -= 1  # Decrease y-axis position
        mark_y = axis['y'][-1]


def get_sensor_values(yaw, sensor):  # รับค่าจาก yaw และ s (เซนเซอร์)
    sensor = state()
    left_wall = None
    front_wall = None
    back_wall = None
    right_wall = None
    print('in def',sensor)
    # กำหนดการเช็คกำแพงตามค่า yaw
    # sensors = [s0, s1, s2] คือ เซนเซอร์ซ้าย, หน้า, ขวา
    if yaw == 0:
        left_wall = sensor[0]  # เซนเซอร์ด้านซ้ายเช็คกำแพงซ้าย
        front_wall = sensor[1]  # เซนเซอร์ด้านหน้าเช็คกำแพงหน้า
        right_wall = sensor[2]  # เซนเซอร์ด้านขวาเช็คกำแพงขวา
    elif yaw == -90:
        front_wall = sensor[0]  # เซนเซอร์ซ้ายเช็คกำแพงหน้า
        right_wall = sensor[1]  # เซนเซอร์หน้าเช็คกำแพงขวา
        back_wall = sensor[2]  # เซนเซอร์ขวาเช็คกำแพงหลัง
    elif yaw == 90:
        back_wall = sensor[0]  # เซนเซอร์ซ้ายเช็คกำแพงหลัง
        left_wall = sensor[1]  # เซนเซอร์ด้านหน้าเช็คกำแพงซ้าย
        front_wall = sensor[2]  # เซนเซอร์ขวาเช็คกำแพงหน้า
    elif yaw == 180:
        right_wall = sensor[0]  # เซนเซอร์ซ้ายเช็คกำแพงขวา
        back_wall = sensor[1]  # เซนเซอร์หน้าเช็คกำแพงหลัง
        left_wall = sensor[2]  # เซนเซอร์ขวาเช็คกำแพงซ้าย
    else:
        raise ValueError("Yaw ไม่ถูกต้อง")

    # เก็บค่าผลลัพธ์เป็นดิก โดยค่าเริ่มต้นเป็น 0 สำหรับทุกทิศทาง
    values_to_return = {
        'left': 0,
        'front': 0,
        'back': 0,
        'right': 0
    }
    
    # เก็บค่าเซนเซอร์ตามทิศทางที่ตรวจพบ
    if left_wall is not None:
        values_to_return['left'] = left_wall
        
    if front_wall is not None:
        values_to_return['front'] = front_wall
        
    if back_wall is not None:
        values_to_return['back'] = back_wall
        
    if right_wall is not None:
        values_to_return['right'] = right_wall

    return values_to_return

 
def check_mintof(sensor):
    sensor = state()
    ltof = ftof = rtof = None
    slide_check_nextpos()
    if sensor[0] == 0 :
        ep_gimbal.moveto(yaw=90, yaw_speed=200).wait_for_completed() 
        ltof = l_tof[-1]
    if sensor[1] == 0 :
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        ftof = l_tof[-1]
    if sensor[2] == 0 :
        ep_gimbal.moveto(yaw=-90, yaw_speed=200).wait_for_completed()   
        rtof = l_tof[-1]
    # if sum(s) < 3:
    #     mee_soy = point_s
    #     return memo_soy(mee_soy) 
    return check_min_distance(ltof,ftof,rtof)

def forward_cango(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    f_pos = (point_s[0]+1,point_s[1])
    if f_pos in dict_memo:
        print('Already have', f_pos)
        return 

def right_cango(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    r_pos = (point_s[0],point_s[1]+1)
    if r_pos in dict_memo:
        print('Already have', r_pos)
        return 
    
def left_cango(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    l_pos = (point_s[0],point_s[1]-1)
    if l_pos in dict_memo:
        print('Already have', l_pos)
        return 
    
def back_cango(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    b_pos = (point_s[0]-1,point_s[1])
    if b_pos in dict_memo:
        print('Already have', b_pos)
        return 

def Move():
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        target_distance = 0.6  # Target distance to move forward
        ep_chassis.move(x=target_distance, y=0, z=0, xy_speed=0.6).wait_for_completed()
        ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()

        time.sleep(1)
        change_point()
        memory_maze(point_s)
        

def turn_right():
    ep_chassis.move(x=0, y=0, z=-90, z_speed=100).wait_for_completed()
    Move()

def turn_left():
    ep_chassis.move(x=0, y=0, z=90, z_speed=100).wait_for_completed()
    Move()

def backward():
    ep_chassis.move(x=0, y=0, z=-180, z_speed=100).wait_for_completed()
    Move()
  
def move():
    sensor = state()
    if point_s[0] == 0 or point_s[0] == max_grid_x or point_s[1] == 0 or point_s[1] == max_grid_y: #กรณีติกรอบเขาวงกต
        if (point_s[0] == 0 or point_s[0] == max_grid_x) and (point_s[1] != 0 or point_s[1] != max_grid_y):# x ติดกรอบซ้ายขวา
            if yaw_t == 0 :
                if point_s[0] == 0:# check all except left
                    sensor[0] = 1
                    return check_mintof(sensor)
                    # if s[2] == 0:
                    #     turn_right()
                    # if s[1]==0 and s[2]==1:
                    #     Move()
                elif point_s[0] == max_grid_x: # cango all except right
                    sensor[2] = 1
                    return check_mintof(sensor)
                    # if s[2] == 0:
                    #     turn_left()
                    # if s[1]==0 and s[2]==1:
                    #     Move()
            if yaw_t == 90 :
                if point_s[0] == 0:# check all except left
                    sensor[1] = 1
                    return check_mintof(sensor)
                # elif point_s[0] == max_grid_x: # cango all except right
                #     pass
            if yaw_t == -90 :
                if point_s[0] == max_grid_x: # cango all except right
                    sensor[1] = 1
                    return check_mintof(sensor)
            if yaw_t == 180 :
                if point_s[0] == 0:# check all except left
                    sensor[2] = 1
                    return check_mintof(sensor)
                elif point_s[0] == max_grid_x: # cango all except right
                    sensor[0] = 1
                    return check_mintof(sensor)
                
        elif (point_s[1] == 0 or point_s[1] == max_grid_y) and (point_s[0] != 0 or point_s[0] != max_grid_x):# y ติดกรอบซ้าย ขวา
            if yaw_t == 0 :
                if point_s[1] == 0:# check all except back
                    return check_mintof(sensor)
                elif point_s[1] == max_grid_y: # cango all except front 
                    sensor[1] = 1
                    return check_mintof(sensor)
            if yaw_t == 90 :
                if point_s[1] == 0:# check all except back
                    sensor[0] = 1
                    return check_mintof(sensor)
                elif point_s[1] == max_grid_y: # cango all except front 
                    sensor[2] = 1
                    return check_mintof(sensor)
            if yaw_t == -90 :
                if point_s[1] == 0:# check all except back
                    sensor[2] = 1
                    return check_mintof(sensor)
                elif point_s[1] == max_grid_y: # cango all except front 
                    sensor[0] = 1
                    return check_mintof(sensor)
            if yaw_t == 180 :
                if point_s[1] == 0:# check all except back
                    sensor[1] = 1
                    return check_mintof(sensor)
                elif point_s[1] == max_grid_y: # cango all except front 
                    return check_mintof(sensor)
                
        elif (point_s[1] == 0 or point_s[1] == max_grid_y)  and (point_s[0] == 0 or point_s[0] == max_grid_x):# y ติดกรอบขวาซ้าย บนล่าง
            if point_s[0] == 0 and point_s[1] == 0: # cango lower left coner
                if yaw_t == 0 :
                    sensor[0] = 1
                    return check_mintof(sensor)
                if yaw_t == 90 :
                    sensor[0] = 1
                    sensor[1] = 1
                    return check_mintof(sensor)
                if yaw_t == -90 :
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == 180 :
                    sensor[1] = 1
                    sensor[2] = 1
                    return check_mintof(sensor)
            if point_s[0] == 0 and point_s[1] == max_grid_y: # cango lower right coner
                if yaw_t == 0 :
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == 90 :
                    sensor[1] = 1
                    return check_mintof(sensor)
                if yaw_t == -90 :
                    sensor[1] = 1
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == 180 :
                    sensor[1] = 1
                    sensor[0] = 1
                    return check_mintof(sensor)
            if point_s[0] == max_grid_x and point_s[1] == 0: # cango top left coner
                if yaw_t == 0 :
                    sensor[1] = 1
                    sensor[0] = 1
                    return check_mintof(sensor)
                if yaw_t == 90 :
                    sensor[1] = 1
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == -90 :
                    sensor[1] = 1
                    return check_mintof(sensor)
                if yaw_t == 180 :
                    sensor[2] = 1
                    return check_mintof(sensor)
            if point_s[0] == max_grid_x and point_s[1] == max_grid_y: # cango top right coner
                if yaw_t == 0 :
                    sensor[1] = 1
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == 90 :
                    sensor[2] = 1
                    return check_mintof(sensor)
                if yaw_t == -90 :
                    sensor[1] = 1
                    sensor[0] = 1
                    return check_mintof(sensor)
                if yaw_t == 180 :
                    sensor[0] = 1
                    return check_mintof(sensor)
    else: #ทุกกรณีที่ไม่ติดกรอบ เช็ค สี่ด้าน
        if yaw_t == 0 or yaw_t == 90 or yaw_t == -90 or yaw_t == 180 :
            return check_mintof(sensor)


def forward_check(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    f_pos = (point_s[0]+1,point_s[1])
    if f_pos in dict_memo:
        print('Already have', f_pos)
        return 

def right_check(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    r_pos = (point_s[0],point_s[1]+1)
    if r_pos in dict_memo:
        print('Already have', r_pos)
        return 
    
def left_check(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    l_pos = (point_s[0],point_s[1]-1)
    if l_pos in dict_memo:
        print('Already have', l_pos)
        return 
    
def back_check(): # ไม่รู้ว่าจะใส่อะไรใน return เมื่อพบว่าเคยมีใน dict_memo
    b_pos = (point_s[0]-1,point_s[1])
    if b_pos in dict_memo:
        print('Already have', b_pos)
        return 
    
def slide_check_nextpos():
    if point_s[0] == 0 or point_s[0] == max_grid_x or point_s[1] == 0 or point_s[1] == max_grid_y: #กรณีติกรอบเขาวงกต
        if (point_s[0] == 0 or point_s[0] == max_grid_x) and (point_s[1] != 0 or point_s[1] != max_grid_y):# x ติดกรอบซ้ายขวา
            if point_s[0] == 0:# check all except left
                forward_check()
                right_check()
                back_check()
            elif point_s[0] == max_grid_x: # check all except right
                forward_check()
                left_check()
                back_check()
        elif (point_s[1] == 0 or point_s[1] == max_grid_y) and (point_s[0] != 0 or point_s[0] != max_grid_x):# y ติดกรอบซ้าย ขวา
            if point_s[1] == 0: # check all except back
                left_check()
                right_check()
                forward_check()
            elif point_s[1] == max_grid_y: # check all except forward
                left_check()
                right_check()
                back_check()
        elif (point_s[1] == 0 or point_s[1] == max_grid_y)  and (point_s[0] == 0 or point_s[0] == max_grid_x):# y ติดกรอบขวาซ้าย บนล่าง
            if point_s[0] == 0 and point_s[1] == 0: # check lower left coner
                forward_check()
                right_check()
            if point_s[0] == 0 and point_s[1] == max_grid_y: # check lower right coner
                back_check()
                right_check()
            if point_s[0] == max_grid_x and point_s[1] == 0: # check top left coner
                left_check()
                forward_check()
            if point_s[0] == max_grid_x and point_s[1] == max_grid_y: # check top right coner
                left_check()
                back_check()
    else: #ทุกกรณีที่ไม่ติดกรอบ เช็ค สี่ด้าน
        left_check()
        right_check()
        forward_check()
        back_check()
        
        
# def get_data(): # ฟังก์ชันเก็บข้อมูลลงคีย์ สามารถเพิ่มได้อีกหากมีอะไรต้องการเก็บและอยากดึงข้อมูลมาใช้
#     #global left_pos ; global forward_pos ; global right_pos
#     left_wall =  sensor[0]
#     forward_wall = sensor[1]
#     right_wall = sensor[2]
#     yaw = yaw_t
#     return [left_wall,forward_wall,right_wall,yaw]

def memory_maze(point_s): #map
    # สร้าง tuple ของ point_s เพื่อใช้เป็นคีย์
    point_key = (point_s[0], point_s[1])

    # ตรวจสอบว่าคีย์นี้มีอยู่ใน dict_memo แล้วหรือยัง
    if point_key in dict_memo:
        print('Already have', point_key)
        return  # ถ้าพบว่ามีแล้ว ไม่เพิ่มค่าใหม่
    dict_memo[point_key] = get_sensor_values(yaw_t,sensor) # เพิ่มคีย์และค่าใหม่ลงใน dict_memo
    print('Added:', {point_key: dict_memo[point_key]})
        
        

          
def adc_l(left):
    vl_volt = ((left / 1023) * 3.1)
    if vl_volt >= 1.6:
        cm1 = ((vl_volt - 4.2) / -0.326)-1.6
        ad['left'].append(cm1)
        #print('cmL = ',cm1)
    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1)-2
        ad['left'].append(cm1)
        #print('cmL = ',cm1)
    else:
        cm1 = 'empty'
        ad['left'].append(cm1)
        #print('cmL = ',cm1)

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    #print("\n",
    #      right, vr_volt,
    #      '\n')
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326)-2
        ad['right'].append(cm2)
        #print('123cmR = ',cm2)
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1)-2
        ad['right'].append(cm2)
        #print('312313cmR = ',cm2)
    else:
        cm2 = 'empty'
        ad['right'].append(cm2)
        #print('cmR = ',cm2)

def low_pass_filter(current_value, previous_filtered_value, alpha):
    # Apply the IIR filter
    filtered_value = current_value + (alpha) * previous_filtered_value
    return filtered_value

def find_closest_value(z, values=[-180, -90, 0, 90, 180]):
    return min(values, key=lambda x: abs(x - z))

def sub_attitude_info_handler(attitude_info):
    yaw, pitch, roll = attitude_info
    #print("chassis attitude: yaw:{0}, pitch:{1}, roll:{2} ".format(yaw, pitch, roll))
    yaw_l.append(float(yaw))
    yaw_t = find_closest_value(yaw_l[-1],l_z)
    #print('yaw', yaw_t)
    
def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    # print(l_tof[-1])
def sub_data_handler2(sub_info):
    global previous_filtered_left, previous_filtered_right
    io, ad_data = sub_info
    
    io_data['left'].append(io[1])
    io_data['right'].append(io[3])
    
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
    

def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(float(x))
    axis['y'].append(float(y))

def state():
    min_charp = 20
    print(io_data['left'][-1],io_data['right'])
    if len(l_tof) > 0:
        if l_tof[-1] <= 250:
            sensor[1] = 1
        else:
            sensor[1] = 0
    
    if len(io_data['left']) > 0 :
        # if charp['left'][-1] == 'empty' :
        #     sensor[0] = 0
        if sum([int(io_data['left'][i]) for i in range(-10, 0)]) >= 5:

            sensor[0] = 0
        elif sum([int(io_data['left'][i]) for i in range(-10, 0)]) == 0:
            sensor[0] = 1
        else:
            sensor[0] = 1
        
    
    if len(io_data['right']) > 0:
        # if charp['right'][-1] == 'empty':
        #     sensor[2] = 0
        # if charp['right'][-1] <= min_charp and io_data['right'][-1] == 1:
        #     sensor[2] = 1
        # elif io_data['right'][-1] == 0:
        #     sensor[2] = 0
        if sum([int(io_data['right'][i]) for i in range(-10, 0)]) >= 5:
            sensor[2] = 0
        elif sum([int(io_data['right'][i]) for i in range(-10, 0)]) == 0:
            sensor[2] = 1
        else:
            sensor[2] = 1
    #print("Updated s:", s)
    # change_state(s)
    return sensor
def change_state(s):
    if sensor[1] == 0 :
            state = states[0]
    elif sensor[1] == 1 :
        if sensor[0] == 0 :
            state = states[1]
        elif sensor[0] == 1 :
            if sensor[2] == 0 :
                state = states[2]
            elif sensor[2] == 1 :
                state = states[3]
    #print(state)

def center_cal(adl, adr):
    if abs(adl - adr) >= 2:
        if adl > adr or adl < adr:
            #print("hello")
            center=(adl + adr)/2
            move = (center-adl)/100
            #print('move = ',move)
            #print('center = ',center)
            if move >= 1.5 :
                ep_chassis.move(x=0, y=move, z=0, xy_speed=0.7)
            else:
                ep_chassis.move(x=0, y=move*2.2, z=0, xy_speed=0.7)
            #print('move complete')
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
        

def check_yaw(yaw_t):
    move = 0
    if yaw_l[-1] > 0:
        if yaw_l[-1]<yaw_t:
            move = yaw_l[-1] - yaw_t
            ep_chassis.move(x=0, y=0, z=move,z_speed=120).wait_for_completed()
        if yaw_l[-1]>yaw_t:
            move = yaw_l[-1] - yaw_t
            ep_chassis.move(x=0, y=0, z=move,z_speed=120).wait_for_completed()
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

def plot_maze(sensor_data):
    # Get the grid size based on the sensor data keys
    max_x = max(key[0] for key in sensor_data.keys())
    max_y = max(key[1] for key in sensor_data.keys())

    # Create the plot
    fig, ax = plt.subplots(figsize=(5, 5))

    # Loop through each cell in the sensor_data
    for (y, x), walls in sensor_data.items():
        # Plot the left wall if walls['left'] == 1
        if walls['left'] == 1:
            ax.plot([x, x], [y, y+1], color="red", linewidth=2)

        # Plot the front wall if walls['front'] == 1 (top wall)
        if walls['front'] == 1:
            ax.plot([x, x+1], [y+1, y+1], color="red", linewidth=2)

        # Plot the right wall if walls['right'] == 1
        if walls['right'] == 1:
            ax.plot([x+1, x+1], [y, y+1], color="red", linewidth=2)

        # Plot the back wall if walls['back'] == 1 (bottom wall)
        if walls['back'] == 1:
            ax.plot([x, x+1], [y, y], color="red", linewidth=2)
            
        if (x[0] for x in sensor_data.keys()) and (y[1] for y in sensor_data.keys()):
            ax.text(x + 0.5, y + 0.5, 'v', color="blue", fontsize=12, ha='center', va='center')

    # Set the grid and limits
    ax.set_xticks(np.arange(0, max_x+2, 1))
    ax.set_yticks(np.arange(0, max_y+2, 1))
    ax.grid(True)

    # Set equal scaling for both axes, no need to invert the y-axis
    ax.set_aspect('equal')

    # Set the axis limits and flip the direction of the y-axis
    plt.ylim(0, max_y + 1)
    plt.xlim(0, max_x + 1)
    
    # Show the plot
    plt.show()

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_gimbal = ep_robot.gimbal
    ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_data_handler2)
    ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    ep_chassis.sub_attitude(freq=50, callback=sub_attitude_info_handler)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    time.sleep(1)
    get_sensor_values(yaw_t,sensor)
    print(io_data['left'][-1],io_data['right'][-1])
    print(l_tof[-1])
    ss = state()
    print('state', ss)
    memory_maze(point_s)
    print(dict_memo)
    
    # while len(dict_memo) < end_ep:
    #     move()
    #     if keyboard.press('q'):
    #         plot_maze(dict_memo)
    #         break
    # while True:
    #     if s[1] == 0:
    #         pass
    #         #move_rside(l_tof, axis, s)
    #     if keyboard.is_pressed:
    #         print("Stopping the robot and exiting the loop...")
    #         break
    #     time.sleep(5)
    # time.sleep(20)
    # ep_sensor_adaptor.unsub_adapter()
    # ep_sensor.unsub_distance()
    # ep_chassis.unsub_position()
    # ep_robot.close()

    
    plt.figure(figsize=(10, 5))
    plt.plot(axis['y'], axis['x'], label='Path', marker='o')
    plt.title('Robot Movement Path')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.legend()
    plt.grid(True)
    plt.show()


# def check_pos():
    
    # l_wallf,f_wall,r_wall = check_walls()
    # if l_wall == 0 : # 0 = Have wall, 1 = No wall
        
    # if f_wall == 0 :    
    
    # if r_wall == 0 :
    
    # if l_wall == 1 : # 0 = Have wall, 1 = No wall
        
    # if f_wall == 1 :    
    
    # if r_wall == 1 :
    # pass
 #       
# Example usage
# yaw = 90  # หรือค่า yaw ที่ได้จากการคำนวณ
# sensors = [s0, s1, s2]  # ค่าจากเซนเซอร์ทั้งสามตัว
# front, back, tof = get_sensor_values(yaw, sensors)
# print(f"เซนเซอร์ด้านหน้า: {front}, เซนเซอร์ด้านหลัง: {back}, TOF เซนเซอร์: {tof}")
 

# def adjust_angle(yaw):
#     target_yaw = 0
#     correction = yaw
#     if -135 < yaw <= -45:
#         target_yaw = -90
#         ep_chassis.move(x=0, y=0, z=correction-target_yaw, z_speed=20).wait_for_completed()  
#     elif 45 < yaw < 135:
#         target_yaw = 90
#         ep_chassis.move(x=0, y=0, z=correction-target_yaw, z_speed=20).wait_for_completed()
#     elif -45 < yaw <= 45:
#         target_yaw = 0
#         ep_chassis.move(x=0, y=0, z=correction, z_speed=20).wait_for_completed()
#     elif -180 <= yaw < -135 :
#         target_yaw = -180
#         ep_chassis.move(x=0, y=0, z=correction-target_yaw, z_speed=20).wait_for_completed() 
#     elif 135 < yaw <= 180:
#         target_yaw = 180
#         ep_chassis.move(x=0, y=0, z=correction-target_yaw, z_speed=20).wait_for_completed()
            
# def move_ass3(): #คราวๆ
#     if axis['x'][-1] - mark_x > 0.58 and axis['x'][-1] - mark_x < 0.62 : #mark_x  ตำแหน่งล่าสุดที่จัดเก็บข้อมูล
#         pass

    
# ต้องมีค่าอยู่ใน dict_memo ก่อน หนึ่งตำแหน่ง
# def memory_maze():  #เก่า
#     dict_memo_a = {}
#     for d in dict_memo:
#         if (point_s[0],point_s[1]) in d.keys():
#             pass
#         else:
#             left_pos,forward_pos,right_pos = check_pos()
#             dict_memo_a[(point_s[0],point_s[1])] = [left_pos,forward_pos,right_pos,yaw_t]
#             #list[0-2] เก็บเป็นลิสต์ [left,{'left':เคยไป/ไม่เคยไป}] เป็นต้น ในขั้นแรกจะเป็นไม่เคยไปทั้งหมด จนกว่าจะเลือกเส้นทางจึงเปลี่ยนเป็นเคยไป ก่อน
#             # เปลี่ยนเป็นเช็คแค่มีกำแพงหรือไม่หก็พอ และ ใช้การสไลด์ตัว (x,y) แทน เช่น หากเดินไปข้างหน้า ให้ x+1 left y-1 right+1 เพื่อทำการเช็คว่าทางนั้นเคยมาหรือยัง
#             #list[3] เก็บค่าตำแหน่งการหมุนของตัวหุ่น (เนื่องจากหากเรากลับมาที่เดิมเราจะได้หมุนหัวให้ตรงจากจุดที่มา)
#             dict_memo.append(dict_memo_a)
            
            
# def center_cal(adl, adr):
    # if adl <= 11 :
    #     move =  adl - 11
    #     ep_chassis.move(x=0, y=move, z=0, xy_speed=0.15).wait_for_completed()
    #     print('move complete')
    # if adr <= 11 :
    #     move = adr - 11
    #     ep_chassis.move(x=0, y=-move, z=0, xy_speed=0.15).wait_for_completed()
    #     print('move complete')
    

# def move_rside(l_tof,axis,s):
    
#     while True:
        
#         if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'):
#             # center_cal(ad['left'][-1], ad['right'][-1]) 
#             center_reset(ad['left'][-1], ad['right'][-1])
#         if s[1]==0:
#             ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
#         if ad['right'][-1] == 'empty' and s[1]== 0 and (ad['left'][-1] != 'empty' or ad['left'][-1] == 'empty') :#(s[2]==0 and s[0]==1 and s[1]== 0)
#             ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
#             time.sleep(0.5)
#             ep_chassis.move(x=0.15, y=0, z=0, xy_speed=0.5).wait_for_completed()
#             ep_chassis.move(x=0, y=0, z=-89.5, z_speed=120).wait_for_completed()
#             if abs(yaw_l[-1]-yaw_t) >= 1 :
#                 check_yaw(yaw_t)
#             ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
#             ep_chassis.move(x=0.5, y=0, z=0, xy_speed=0.7).wait_for_completed()
#             time.sleep(0.5)
#         if ad['right'][-1] == 'empty' and s[1] == 1 and (ad['left'][-1] != 'empty' or ad['left'][-1] == 'empty') :#(s[2]==0 and s[0]==1 and s[1]== 1) :
#             ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
#             time.sleep(0.5)
#             ep_chassis.move(x=0, y=0, z=-89.5, z_speed=120).wait_for_completed()
#             if abs(yaw_l[-1]-yaw_t) >= 1 :
#                 check_yaw(yaw_t)
#             ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
#             ep_chassis.move(x=0.55, y=0, z=0, xy_speed=0.7).wait_for_completed()
#             time.sleep(0.5)
#         if ad['right'][-1] != 'empty' and s[1] == 1 and ad['left'][-1] == 'empty':#(s[0] == 0 and s[1]==1 and s[2]==1)
#             ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
#             time.sleep(0.5)
#             ep_chassis.move(x=0, y=0, z=90, z_speed=120).wait_for_completed()
#             if abs(yaw_l[-1]-yaw_t) >= 1 :
#                 check_yaw(yaw_t)
#             ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
#             time.sleep(0.5)
#         if ad['right'][-1] != 'empty' and s[1] == 1 and ad['left'][-1] != 'empty':#s[0] == 1 and s[1] == 1 and s[2] == 1
#             ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
#             time.sleep(0.5)
#             ep_chassis.move(x=0, y=0, z=180, z_speed=120).wait_for_completed()
#             if abs(yaw_l[-1]-yaw_t) >= 1 :
#                 check_yaw(yaw_t)
#             ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
#             time.sleep(0.5)
#         if keyboard.is_pressed('q'):
#             ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)  # Stop the robot
#             ep_sensor_adaptor.unsub_adapter()
#             ep_sensor.unsub_distance()
#             ep_chassis.unsub_position()
#             ep_robot.close()
#             break

