import time
import matplotlib.pyplot as plt
from robomaster import robot

l_tof = []
axis = {'x':[],'y':[]}
#sensors
#tof
def sub_data_handler(sub_info):
    distance = sub_info
    print("tof1:{0}  tof2:{1}  tof3:{2}  tof4:{3}".format(distance[0], distance[1], distance[2], distance[3]))
    l_tof.append(int(distance[0]))
#sub_pos
def sub_position_handler(position_info):
    x, y, z = position_info
    axis['x'].append(float(x))
    axis['y'].append(float(y))


#
#acurator
def chasing(sub_pos,tof):
    pass
#main
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_sensor.sub_distance(freq=5, callback=sub_data_handler)
    ep_chassis.sub_position(freq=5, callback=sub_position_handler)
    ep_chassis.move(x=0.6, y=0, z=0, xy_speed=0.7)
    time.sleep(10)
    ep_sensor.unsub_distance()
    ep_chassis.unsub_position()
    ep_robot.close()
    print(l_tof)
    print(axis)