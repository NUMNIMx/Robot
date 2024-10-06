point_s = [0,0]
dict_memo = {}

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
    return [left_wall,forward_wall,right_wall]

def memory_maze(n, point_s):
    # สร้าง tuple ของ point_s เพื่อใช้เป็นคีย์
    point_key = (point_s[0], point_s[1])

    # ตรวจสอบว่าคีย์นี้มีอยู่ใน dict_memo แล้วหรือยัง
    if point_key in dict_memo:
        print('Already have', point_key)
        return  # ถ้าพบว่ามีแล้ว ไม่เพิ่มค่าใหม่
    dict_memo[point_key] = get_data()  # เพิ่มคีย์และค่าใหม่ลงใน dict_memo
    print('Added:', {point_key: dict_memo[point_key]})