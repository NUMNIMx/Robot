import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot

visited = []
node = []
old_node = []
n_way = 0
deadend = False
s = [0,0,0]

def go_to_node(index):
    pass
def way_to_go():
    pass
def check_tof(str):
    pass
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
    
    
    if len(node)>0 and (deadend or (len(node) < len(old_node))) :
        if deadend :
            go_to_node(-1)
            node.pop(-1)
            
    if ((s == [0,1,1] and s==[1,0,1]) or (s==[1,0,1] and s ==[1,1,0])):
        if s == [0,1,1]:
            

    # if len(node)>0 and 
    old_node = node

    