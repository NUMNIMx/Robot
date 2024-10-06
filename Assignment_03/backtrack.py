import time
import matplotlib.pyplot as plt
import keyboard
from robomaster import robot
import csv


DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
l_tof = []
s = [0,0,0]
ad = {'left':[],'right':[]}
io = {'left':[],'right':[]}
axis = {'x':[],'y':[]}
previous_filtered_left = 0.0
previous_filtered_right = 0.0
alpha = 0.3
filtered_left_values = []
filtered_right_values = []

def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    state(l_tof, ad)

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

def sub_data_handler2(sub_info):
    global previous_filtered_left, previous_filtered_right
    io_data, ad_data = sub_info
    #io
    io['left'].append(io_data[1])
    io['right'].append(io_data[3])
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

def adc_l(left):
    vl_volt = ((left / 1023) * 3.1)
    if vl_volt >= 1.6:
        cm1 = ((vl_volt - 4.2) / -0.326)-1.6
        ad['left'].append(cm1)

    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1)-2
        ad['left'].append(cm1)
    
    else:
        cm1 = 'empty'
        ad['left'].append(cm1)
        

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326)-2
        ad['right'].append(cm2)
        
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1)-2
        ad['right'].append(cm2)
        
    else:
        cm2 = 'empty'
        ad['right'].append(cm2)



def low_pass_filter(current_value, previous_filtered_value, alpha):
    # Apply the IIR filter
    filtered_value = current_value + (alpha) * previous_filtered_value
    return filtered_value

class Robomaster:
    def __init__(self):
        self.position = (0, 0)
        self.visited = []  # List to store visited cells
        self.junctions = []  # List to store junctions (multiple paths)
        self.path_history = []

        ep_robot = robot.Robot()
        ep_robot.initialize(conn_type="ap")
        global ep_chassis
        ep_chassis = ep_robot.chassis
        ep_sensor = ep_robot.sensor
        ep_sensor_adaptor = ep_robot.sensor_adaptor
        ep_gimbal = ep_robot.gimbal

        ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_data_handler2)
        ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
        ep_chassis.sub_position(freq=50, callback=sub_position_handler)
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    def tof_check(self,direction):
        pass
    def is_path_clear(self, direction):
        path_clear = bool
        # Implement sensor feedback to check if the path in 'direction' is clear
        # Replace with actual sensor check: True if no wall, False if blocked
        if direction == (0,1):#ทางขวา
            if s[2] == 1 :
                if io['right'] == 1 :
                    path_clear = False
                elif io['right'] == 0 :
                    tof = self.tof_check(direction)
                    if tof >= 200 :
                        path_clear = False
                    else :
                        path_clear = True

            if  s[2] == 0 :
                path_clear = True

        if direction == (0,-1):#ทางซ้าย
            if s[0] == 1 :
                if io['left'] == 1 :
                    path_clear = False
                elif io['left'] == 0 :
                    tof = self.tof_check(direction)
                    if tof >= 200 :
                        path_clear = False
                    else :
                        path_clear = True

            if  s[0] == 0 :
                path_clear = True
        
        if direction == (1,0) :
            if s[1] == 1:
                path_clear = False
            elif s[1] == 0:
                path_clear = True
        
        if direction == (-1,0):#ข้างหลัง
            if len(self.visited) < 2:
                path_clear == False
            else :
                path_clear == True
                
        return path_clear
    
    def move_in_direction(self, dx, dy):
        # Implement robot movement in the direction (dx, dy)
        # Replace this with actual movement commands for your robot
        if dy == 1:
            TurnRight()
            Move()
        if dy == -1:
            TurnLeft()
            Move()
        if dx == 1 :
            Move()
        if dx == -1 :
            Backward()
        pass

    

    def explore_maze(self):
        while True:
            x, y = self.position
            self.visited.append(self.position)  # Mark current position as visited

            # Find all valid moves based on sensor data
            possible_moves = []
            for direction in DIRECTIONS:
                dx, dy = direction
                new_position = (x + dx, y + dy)
                if self.is_path_clear(direction) and new_position not in self.visited:
                    print(direction)
                    possible_moves.append(direction)

            if len(possible_moves) > 1:
                self.junctions.append(self.position)
                self.path_history.append((dx, dy))

            if not possible_moves:
                if not self.junctions:
                    print("Maze exploration complete")
                    break  # Exploration finished: all accessible areas explored

                # Backtrack to the last junction (node with unexplored paths)
                dx, dy = self.path_history.pop()  # ดึงการเคลื่อนที่ล่าสุดออกมา
                self.move_in_direction(-dx, -dy)
                if len(self.path_history) == 0 :
                    self.position = self.junctions.pop()
                continue

            dx, dy = possible_moves[0]
            self.move_in_direction(dx, dy)
            self.position = (x + dx, y + dy)  # Update position after movement

        print(f"Explored {len(self.visited)} cells.")
def Move():
    target_distance = 0.6  # Target distance to move forward
    ep_chassis.move(x=target_distance, y=0, z=0,x_speed=0.7).wait_for_completed()
    

def TurnRight():
    ep_chassis.move(x=0, y=0, z=90,z_speed=100).wait_for_completed()
    target_distance = 0.6 
    ep_chassis.move(x=target_distance, y=0, z=0,x_speed=0.7).wait_for_completed()
def TurnLeft():
    ep_chassis.move(x=0, y=0, z=-90,z_speed=100).wait_for_completed()
    target_distance = 0.6 
    ep_chassis.move(x=target_distance, y=0, z=0,x_speed=0.7).wait_for_completed()
def Backward():
    ep_chassis.move(x=0, y=0, z=-180,z_speed=100).wait_for_completed()
    target_distance = 0.6 
    ep_chassis.move(x=target_distance, y=0, z=0,x_speed=0.7).wait_for_completed()
if __name__ == '__main__':
    robot = Robomaster()
    robot.explore_maze()
