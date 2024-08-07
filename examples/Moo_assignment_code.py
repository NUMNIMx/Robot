import robomaster
from robomaster import robot
import time
import keyboard

axis_x = []
axis_y = []
lst_adap = []
lst_tof = []
lst_io = []
f_way = []
all_p_data = []
dict_w = {}
speed = 13
direc = None
current_x = None
current_y = None

def calculator_adc(s_l, s_r):
    res = []
    volt_l = (s_l/1023)*3.1
    volt_r = (s_r/1023)*3.1
    sensor = [volt_l, volt_r]
    for i in sensor:
        if i >= 1.6:
            cm = (i-4.2)/-0.326
            res.append(cm)
        elif i >= 0.8:
            cm = (i-2.4)/-0.1
            res.append(cm)
        else:
            res.append('g')
    return res

def recenter(axis_x, axis_y, vector):
    if axis_x and axis_y is None:
        return None
    return 

def find_data(axis_x, axis_y, lst_adap, lst_tof, lst_io):
    if axis_x and axis_y and lst_adap and lst_tof and lst_io:
        data = list(add_data(axis_x, axis_y, lst_adap, lst_tof, lst_io))
        print(data)
        state, parts, deg, wall = list(state_robot(data))
    else:
        print('Robot not ready')
    return state, parts, deg, wall

def find_direction(parts, deg, wall):
    p_data = []
    all_parts = []
    dict_w = {}
    for i in range(len(deg)) :
        angle = deg[i]
        ep_gimbal.moveto(yaw= angle, yaw_speed= 100).wait_for_completed()
        time.sleep(0.5)
        tof = lst_tof[-1]
        dict_w[parts[i]] = tof

    max_dis = max(dict_w, key = dict_w.get)
    rotation(max_dis)
    p_data.append(dict_w)
    print(dict_w)
    p_data.append([axis_x[-1], axis_y[-1]])
    p_data.append(wall)
    print('point data : {}'.format(p_data))
    return p_data

def rotation(vector):
    if vector == 'l':
        ep_chasis.move(x=0, y=0, z=90, z_speed=45).wait_for_completed()
    if vector == 'r' :
        ep_chasis.move(x=0, y=0, z=-90, z_speed=45).wait_for_completed()
    if vector == 'b' :
        ep_chasis.move(x=0, y=0, z=180, z_speed=45).wait_for_completed()
        

def sub_gimbal(angle_info):
    global list_of_data
    list_of_data = angle_info

def state_robot(data):
    state = ['finding', 'backing']
    parts = []
    deg = []
    wall = []
    if data is None:
        print('Sensor not ready')
        return None

    if data[0] < 180:
        parts.append('l')
        deg.append(-90)
    else:
        wall.append('l')

    if data[1] < 200:
        parts.append('r')
        deg.append(90)
    else:
        wall.append('r')

    if data[2] > 400:
        parts.append('f')
        deg.append(0)
    else:
        wall.append('f')

    if data[3] == 0:
        parts.append('b')
        deg.append(180)
    else:
        wall.append('b')
    if parts:
        if parts[0] == 'b':
            return state[1], parts, deg, wall
        else:
            return state[0], parts, deg, wall
    else:
        return state[0], parts, deg, wall

def move_wheels(state, parts, deg):
    if state == 'finding':
        if len(parts) > 1:
            ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
            for i in len(deg) :
                ep_gimbal.moveto(yaw= i, yaw_speed= 100).wait_for_completed()
                print('i can go : {}'.format(i))

def add_data(axis_x, axis_y, lst_adap, lst_tof, lst_io):
    pos = [axis_x[-1], axis_y[-1]]
    forward_sensor = lst_tof[-1]
    current_adap = lst_adap[-1]
    right_sensor = current_adap[1]
    left_sensor = current_adap[2]
    back_sensor = lst_io[-1]
    distance_x = axis_x[-1] - axis_x[0]
    distance_y = axis_y[-1] - axis_y[0]
    return left_sensor, right_sensor, forward_sensor, back_sensor

def sub_position_handler(position_info):
    x, y, z = position_info
    axis_x.append(x); axis_y.append(y)
    # print(axis_x)

def sub_data_handler(distance):
    lst_tof.append(distance[0])
    # print("tof1:{0}  tof2:{1}  tof3:{2}  tof4:{3}".format(distance[0], distance[1], distance[2], distance[3]))

def sub_adapter(sub_adaptor):
    io_data, adap = sub_adaptor
    lst_adap.append(adap)
    lst_io.append(io_data[0])
    # print('info left : {} | right : {} | back : {}'.format(info[1], info[2], info[0]))

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chasis = ep_robot.chassis
    ep_gimbal = ep_robot.gimbal
    ep_sensor = ep_robot.sensor
    ep_sensor_adaptor = ep_robot.sensor_adaptor

    #Gimbal
    ep_gimbal.sub_angle(freq=50, callback=sub_gimbal)
    #TOF
    ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
    #ADP
    ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_adapter)
    #chasis
    ep_chasis.sub_position(freq=50, callback=sub_position_handler)
    time.sleep(1)

    data = None
    state = None
    parts = None
    deg = None
    wall = None
    target = None

    while True:
        print(all_p_data)
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        if state is None:
            state, parts, deg, wall = list(find_data(axis_x, axis_y, lst_adap, lst_tof, lst_io))
            # print(parts)
            if len(parts) == 1 and parts[0] is 'b':
                ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

                if len(parts) > 1:
                    for i in range(len(parts)):
                        if parts[i] == 'b':
                            del parts[i]
                            del deg[i]
                    all_p_data.append(find_direction(parts, deg, wall))
                    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
                
        if lst_tof[-1] > 300:
            ep_chasis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
        else :
            state = None
            ep_chasis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            time.sleep(0.5)

    while state == 'backing':
        pass

    ep_sensor.unsub_distance
    ep_chasis.unsub_position()
    ep_sensor_adaptor.unsub_adapter()
    ep_robot.close()
