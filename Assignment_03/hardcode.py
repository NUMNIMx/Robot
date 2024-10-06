import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot

states = ['foward','left','right','turnback']
l_tof = []
axis = {'x':[],'y':[]}
mark_x = 0
mark_y = 0
yaw_l = [0]
ad = {'left':[0],'right':[0]}
s = [0,0,0]

point_s = [0,1] #เปลี่ยนตามที่จารวาง
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
        ep_chassis.move(x=0.6, y=0, z=0, xy_speed=0.5).wait_for_completed()
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
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

def rotation_to_move():
    ltof = ftof = rtof = None
    slide_check_nextpos()
    if s[0] == 0 :
        ep_gimbal.moveto(yaw=90, yaw_speed=200).wait_for_completed() 
        ltof = l_tof[-1]
    if s[1] == 0 :
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        ftof = l_tof[-1]
    if s[2] == 0 :
        ep_gimbal.moveto(yaw=-90, yaw_speed=200).wait_for_completed()   
        rtof = l_tof[-1]
    if sum(s) < 3:
        pass
    return check_min_distance(ltof,ftof,rtof)
        
def change_point():
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

def get_sensor_values(yaw):
    left_wall = None
    front_wall = None
    back_wall = None
    right_wall = None
    
    # sensors = [s0, s1, s2] คือ เซนเซอร์ซ้าย, หน้า, ขวา
    if yaw == 0:
        left_wall = s[0]  # เซนเซอร์ด้านซ้ายเช็คกำแพงซ้าย
        front_wall = s[1]  # เซนเซอร์ด้านหน้าเช็คกำแพงหน้า
        right_wall = s[2]   # เซนเซอร์ด้านขวาเช็คกำแพงขวา
    elif yaw == -90:
        front_wall = s[0]  # เซนเซอร์ซ้ายเช็คกำแพงหน้า
        right_wall = s[1]   # เซนเซอร์ด้านหน้าเช็คกำแพงขวา
        back_wall = s[2]  # เซนเซอร์ขวาเช็คกำแพงหลัง
    elif yaw == 90:
        front_wall = s[2]  # เซนเซอร์ขวาเช็คกำแพงหน้า
        left_wall = s[1]   # เซนเซอร์ด้านหน้าเช็คกำแพงซ้าย
        back_wall = s[0]  # เซนเซอร์ซ้ายเช็คกำแพงหลัง
    elif yaw == 180:
        back_wall = s[1]  # เซนเซอร์หน้าเช็คกำแพงหลัง
        right_wall = s[0]   # เซนเซอร์ซ้ายเช็คกำแพงขวา
        left_wall = s[2]  # เซนเซอร์ขวาเช็คกำแพงซ้าย
    else:
        raise ValueError("Yaw ไม่ถูกต้อง")
    
    values_to_return = []
    if left_wall is not None or left_wall is None :
        if left_wall is not None:
            values_to_return.append(left_wall)
        else :
            values_to_return.append(0)
    if front_wall is not None or front_wall is None:
        if left_wall is not None:
            values_to_return.append(front_wall)
        else :
            values_to_return.append(0)
    if back_wall is not None or back_wall is None:
        if left_wall is not None:
            values_to_return.append(back_wall)
        else :
            values_to_return.append(0)
    if right_wall is not None or right_wall is None:
        if left_wall is not None:
            values_to_return.append(right_wall)
        else :
            values_to_return.append(0)

    return values_to_return
    

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
    if point_s[0] == 0 or point_s[0] == 5 or point_s[1] == 0 or point_s[1] == 5: #กรณีติกรอบเขาวงกต
        if (point_s[0] == 0 or point_s[0] == 5) and (point_s[1] != 0 or point_s[1] != 5):# x ติดกรอบซ้ายขวา
            if point_s[0] == 0:# check all except left
                forward_check()
                right_check()
                back_check()
            elif point_s[0] == 5: # check all except right
                forward_check()
                left_check()
                back_check()
        elif (point_s[1] == 0 or point_s[1] == 5) and (point_s[0] != 0 or point_s[0] != 5):# y ติดกรอบซ้าย ขวา
            if point_s[1] == 0: # check all except back
                left_check()
                right_check()
                forward_check()
            elif point_s[1] == 5: # check all except forward
                left_check()
                right_check()
                back_check()
        elif (point_s[1] == 0 or point_s[1] == 5)  and (point_s[0] == 0 or point_s[0] == 5):# y ติดกรอบขวาซ้าย บนล่าง
            if point_s[0] == 0 and point_s[1] == 0: # check lower left coner
                forward_check()
                right_check()
            if point_s[0] == 0 and point_s[1] == 5: # check lower right coner
                back_check()
                right_check()
            if point_s[0] == 5 and point_s[1] == 0: # check top left coner
                left_check()
                forward_check()
            if point_s[0] == 5 and point_s[1] == 5: # check top right coner
                left_check()
                back_check()
    else: #ทุกกรณีที่ไม่ติดกรอบ เช็ค สี่ด้าน
        left_check()
        right_check()
        forward_check()
        back_check()
        
def get_data(): # ฟังก์ชันเก็บข้อมูลลงคีย์ สามารถเพิ่มได้อีกหากมีอะไรต้องการเก็บและอยากดึงข้อมูลมาใช้
    #global left_pos ; global forward_pos ; global right_pos
    left_wall =  s[0]
    forward_wall = s[1]
    right_wall = s[2]
    yaw = yaw_t
    return [left_wall,forward_wall,right_wall,yaw]

def memory_maze(point_s):
    # สร้าง tuple ของ point_s เพื่อใช้เป็นคีย์
    point_key = (point_s[0], point_s[1])

    # ตรวจสอบว่าคีย์นี้มีอยู่ใน dict_memo แล้วหรือยัง
    if point_key in dict_memo:
        print('Already have', point_key)
        return  # ถ้าพบว่ามีแล้ว ไม่เพิ่มค่าใหม่
    dict_memo[point_key] = get_sensor_values(yaw_t) , yaw_t # เพิ่มคีย์และค่าใหม่ลงใน dict_memo
    print('Added:', {point_key: dict_memo[point_key]})
            
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

def sub_attitude_info_handler(attitude_info):
    yaw, pitch, roll = attitude_info
    #print("chassis attitude: yaw:{0}, pitch:{1}, roll:{2} ".format(yaw, pitch, roll))
    yaw_l.append(float(yaw))
    yaw_t = find_closest_value(yaw_l[-1],l_z)
    print('yaw', yaw_t)
    
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
    print("Updated s:", s)
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
        
# def center_cal(adl, adr):
    # if adl <= 11 :
    #     move =  adl - 11
    #     ep_chassis.move(x=0, y=move, z=0, xy_speed=0.15).wait_for_completed()
    #     print('move complete')
    # if adr <= 11 :
    #     move = adr - 11
    #     ep_chassis.move(x=0, y=-move, z=0, xy_speed=0.15).wait_for_completed()
    #     print('move complete')
    
def find_closest_value(z, values=[-180, -90, 0, 90, 180]):
    return min(values, key=lambda x: abs(x - z))

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
    rotation_to_move()
    # while True:
    #     if s[1] == 0:
    #         pass
    #         #move_rside(l_tof, axis, s)
    #     if keyboard.is_pressed:
    #         print("Stopping the robot and exiting the loop...")
    #         break
    #     time.sleep(5)



    
    plt.figure(figsize=(10, 5))
    plt.plot(axis['y'], axis['x'], label='Path', marker='o')
    plt.title('Robot Movement Path')
    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.legend()
    plt.grid(True)
    plt.show()

