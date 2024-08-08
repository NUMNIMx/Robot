import time
import matplotlib.pyplot as plt
from robomaster import robot

states = ['foward','left','right','turnback']
l_tof = []
axis = {'x':[],'y':[]}
ad = {'left':[],'right':[]}
s = [0,0,0]

#sensors
#tof
def sub_data_handler(sub_info):
    distance = sub_info
    #print("tof1:{0}  tof2:{1}  tof3:{2}  tof4:{3}".format(distance[0], distance[1], distance[2], distance[3]))
    l_tof.append(int(distance[0]))

    state(l_tof, ad)
    #print(s)
#ad
def sub_data_handler2(sub_info):
    io,ad_data = sub_info
    #print("ad value: {0}".format(ad_data))
    ad['left'].append(float(ad_data[0]))
    ad['right'].append(float(ad_data[2]))
    
    state(l_tof, ad)
    #print(s)

#sub_pos
def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(float(x))
    axis['y'].append(float(y))

#acurator
#state

def state(tof, charp):
    min_charp = 140
    #print("tof:", tof)
    #print("charp:", charp)
    
    if len(tof) > 0:
        #print("tof[-1]:", tof[-1])
        if tof[-1] <= 310:
            s[1] = 1
            #print("Setting s[1] to 1")
        else:
            s[1] = 0
            #print("Setting s[1] to 0")
    
    if len(charp['left']) > 0:
        #print("charp['left'][-1]:", charp['left'][-1])
        if charp['left'][-1] >= min_charp:
            s[0] = 1
            #print("Setting s[0] to 1")
        else:
            s[0] = 0
            #print("Setting s[0] to 0")
    
    if len(charp['right']) > 0:
        #print("charp['right'][-1]:", charp['right'][-1])
        if charp['right'][-1] >= min_charp:
            s[2] = 1
            #print("Setting s[2] to 1")
        else:
            s[2] = 0
            #print("Setting s[2] to 0")
    
    print("Updated s:", s)

def change_state(s):
    if s[1] == 0 :
        state = states[0]
    elif s[1] == 1:
        state = states[3]
    

# def error(sub_pos,ref_x,ref_y):
#     ref_x += 0.1
#     ref_y += 0.1
#     err_x = (
#             ref_x - sub_pos['x'][-1]
#         )
#     err_y = (
#             ref_y - sub_pos['y'][-1]
#         ) 
#     return err_x,err_y

# def pid(err_x,err_y,after_t,prev_t):
#     # accumulate_x += err_x*(after_t-prev_t)
#     # accumulate_y += err_y*(after_t-prev_t)
#     # speed_x = (
#     #     (p * err_x)+ d*((err_x-prev_err_x)/(after_time-prev_time)) + i*accumulate_x
#     # )
#     # speed_y = (
#     #     (p * err_y)+ d*((err_y-prev_err_y)/(after_time-prev_time)) + i*accumulate_y
#     # )
#     pass

def forward(sub_pos,l_tof):
    ref_pos_x = sub_pos['x'][-1]
    ref_pos_y = sub_pos['y'][-1]
    # if l_tof[-1] <= 400:

def backward(sub_pos,l_tof):
    while True:
        if l_tof[-1] < 300:
            pass
            ##pid 

def left(sub_pos,charp):
    while True:
            pass
            ##pid 

def right(sub_pos,charp):
    while True:
            pass
            ##pid 




#main
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor
    
    ep_sensor_adaptor.sub_adapter(freq=5, callback=sub_data_handler2)
    ep_sensor.sub_distance(freq=5, callback=sub_data_handler)
    ep_chassis.sub_position(freq=5, callback=sub_position_handler)
    

    time.sleep(60)
    ep_sensor_adaptor.unsub_adapter()
    ep_sensor.unsub_distance()
    ep_chassis.unsub_position()
    ep_robot.close()
    #print(l_tof)
    #print(axis)
    #print(ad)