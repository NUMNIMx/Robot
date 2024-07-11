import pandas as pd
from robomaster import robot
import time
if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    time.sleep(1)
    ep_chassis.move(x=-1, y=0, z=0, xy_speed=0.6)
    ep_robot.close()