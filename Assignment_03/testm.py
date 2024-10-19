import time
import matplotlib.pyplot as plt
import keyboard
import numpy as np
from robomaster import robot
import csv
import cv2


DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)] #หน้า ขวา ใต้ ซ้าย
DIRECTIONS2 = ['เหนือ','ตะวันออก','ใต้','ตะวันตก']
size_maze = (6,6)
wall = []
for i in range(size_maze[0]):
    wall.append((i,-1))
for i in range(size_maze[0]):
    wall.append((i,size_maze[1]))
for i in range(size_maze[1]):
    wall.append((-1,i))
for i in range(size_maze[1]):
    wall.append((size_maze[0],i))
current_index = 0
l_tof = []
s = [0, 0, 0] #กำหนดตัวเริ่มต้นตำแหน่งที่ 0 0
ad = {'left': [], 'right': []}
io = {'left': [], 'right': []}
axis = {'x': [], 'y': []}
previous_filtered_left = 0.0
previous_filtered_right = 0.0
alpha = 0.3
filtered_left_values = []
filtered_right_values = []
n=0


def sub_data_handler(sub_info):
    distance = sub_info
    l_tof.append(int(distance[0]))
    state(l_tof, ad)

def state(tof, charp):
    min_charp = 20
    if len(tof) > 0:
        if tof[-1] <= 330:
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
class Camera:
    def __init__(self):
        # Initialize the camera
        pass  # Add actual camera initialization logic here

    def capture_image(self):
        # Logic to capture an image
        print("Capturing image...")  # Replace with actual capture logic
        return "image_data"  # Return the captured image data
def sub_data_handler2(sub_info):
    global previous_filtered_left, previous_filtered_right
    io_data, ad_data = sub_info
    # io
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
        cm1 = ((vl_volt - 4.2) / -0.326) - 1.6
        ad['left'].append(cm1)

    elif vl_volt >= 0.5:
        cm1 = ((vl_volt - 2.4) / -0.1) - 2
        ad['left'].append(cm1)
    
    else:
        cm1 = 'empty'
        ad['left'].append(cm1)

def adc_r(right):
    vr_volt = ((right / 1023) * 3.1)
    if vr_volt >= 1.6:
        cm2 = ((vr_volt - 4.2) / -0.326) - 2
        ad['right'].append(cm2)
        
    elif vr_volt >= 0.5:
        cm2 = ((vr_volt - 2.4) / -0.1) - 2
        ad['right'].append(cm2)
        
    else:
        cm2 = 'empty'
        ad['right'].append(cm2)

def low_pass_filter(current_value, previous_filtered_value, alpha):
    filtered_value = current_value + (alpha) * previous_filtered_value
    return filtered_value
def find_thief(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([102, 123, 113])
    upper_blue = np.array([179, 255, 255])
    lower_blue2 = np.array([94, 158, 62])
    upper_blue2 = np.array([180, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask1 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask = cv2.bitwise_or(mask, mask1)
    
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=40)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)  # Draw the circle in the original image
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)  # Draw a rectangle at the center of the circle
    
    return image, circles


class Robomaster:
    def __init__(self):
        self.position = (0, 2)
        self.visited = []
        self.junctions = []
        self.path_history = []
        self.last_direction = []
        self.robot_direction = DIRECTIONS2[0]  # Initialize with the first direction
        self.exploration_complete = False
        self.wall = []  # Initialize wall data as required
        self.sensor_data = {}
        ep_robot = robot.Robot()
        ep_robot.initialize(conn_type="ap", proto_type="udp")
        global ep_chassis, ep_gimbal
        ep_chassis = ep_robot.chassis
        ep_sensor = ep_robot.sensor
        ep_sensor_adaptor = ep_robot.sensor_adaptor
        ep_gimbal = ep_robot.gimbal

        ep_sensor_adaptor.sub_adapter(freq=50, callback=self.sub_data_handler2)
        ep_sensor.sub_distance(freq=50, callback=self.sub_data_handler)
        ep_chassis.sub_position(freq=50, callback=self.sub_position_handler)
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

        self.camera = Camera()  
        self.camera.initialize() 
    def plot_maze(self):
        # Get the grid size based on the sensor data keys
        max_x = max(key[0] for key in self.sensor_data.keys())
        max_y = max(key[1] for key in self.sensor_data.keys())

        # Create the plot
        fig, ax = plt.subplots(figsize=(5, 5))

        # Loop through each cell in the sensor_data
        for (y, x), walls in self.sensor_data.items():
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
                
            if (x[0] for x in self.sensor_data.keys()) and (y[1] for y in self.sensor_data.keys()):
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
    
    def tof_check(self, direction):
        tof = 0
        if direction == (0, 1): #ขวา
            ep_gimbal.moveto(pitch=0, yaw=90, yaw_speed=200).wait_for_completed()
            time.sleep(0.4)
            tof = l_tof[-1]
        if direction == (0, -1): #ซ้าย
            ep_gimbal.moveto(pitch=0, yaw=-90, yaw_speed=200).wait_for_completed()  
            time.sleep(0.4)  
            tof = l_tof[-1]
        if direction == (-1,0): #ล่าง
            ep_gimbal.moveto(pitch=0, yaw=-180, yaw_speed=200).wait_for_completed()
            time.sleep(0.4)
            tof = l_tof[-1]
        
        return tof      

    def is_path_clear(self, direction):
        path_clear = bool
    
        if direction == (0, 1):  # Right
            if s[2] == 1:
                if io['right'][-1] == 0:
                    path_clear = False
                elif io['right'][-1] == 1:
                    tof = self.tof_check(direction)
                    time.sleep(0.4)
                    if tof <= 300:
                        path_clear = False
            if s[2] == 0 :
                path_clear = True

        if direction == (0, -1):  # Left
            if s[0] == 1:
                if io['left'][-1] == 0:
                    path_clear = False
                elif io['left'][-1] == 1:
                    tof = self.tof_check(direction)
                    time.sleep(0.4)
                    if tof <= 300:
                        path_clear = False
            if s[0] == 0 and io['left'] == 1:
                path_clear = True

        if direction == (1, 0):  # Forward
            if s[1] == 1:
                path_clear = False
            if s[1] == 0:
                path_clear = True
        if direction == (-1, 0):  # Backward
            if len(self.visited) < 2 :
                tof = self.tof_check(direction)
                time.sleep(0.4)
                if tof <= 350 :
                    path_clear = False
                else :
                    path_clear = True
            else :
                path_clear = True

        return path_clear
    
    def move_in_direction(self, dx, dy):
        if dy == 1:
            self.turn_right()
        if dy == -1:
            self.turn_left()
        if dx == 1 :
            self.Move()
        if dx == -1 :
            self.backward()

    def center_reset(self,adl,adr):
        move = 0 
        if adl <= 6 :
            move = (adl -6)/100
            if abs(move) <= 0.15 :
                ep_chassis.move(x=0, y=0.15, z=0, xy_speed=0.1).wait_for_completed()
                
            else:
                ep_chassis.move(x=0, y=move, z=0, xy_speed=0.1).wait_for_completed()
                
            time.sleep(4)
        if adr <= 6 :
            move = (adr - 6)/100
            if abs(move) <= 0.15 :
                ep_chassis.move(x=0, y=-0.15, z=0, xy_speed=0.1).wait_for_completed()
                
            else:
                ep_chassis.move(x=0, y=-move, z=0, xy_speed=0.1).wait_for_completed()
            time.sleep(4)

    def Move(self):
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
        target_distance = 0.6  # Target distance to move forward
        ep_chassis.move(x=target_distance, y=0, z=0, xy_speed=0.6).wait_for_completed()
        ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()

        time.sleep(1)
        self.explore_step()

    def turn_right(self):
        ep_chassis.move(x=0, y=0, z=-90, z_speed=100).wait_for_completed()
        self.center_re()
        global current_index
        current_index = (current_index+1)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

    def turn_left(self):
        ep_chassis.move(x=0, y=0, z=90, z_speed=100).wait_for_completed()
        self.center_re()
        global current_index
        current_index = (current_index-1)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

    def backward(self):
        ep_chassis.move(x=0, y=0, z=-180, z_speed=100).wait_for_completed()
        self.center_re()
        global current_index
        current_index = (current_index+2)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

    def center_re(self):
        if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'):    
            print(ad['left'][-1],ad['right'][-1])
            self.center_reset(ad['left'][-1],ad['right'][-1])

    def explore_step(self):
        global n
        if self.exploration_complete:
            return
        if (ad['left'][-1] != 'empty' and ad['right'][-1] != 'empty'):    
            print(ad['left'][-1],ad['right'][-1])
            self.center_reset(ad['left'][-1],ad['right'][-1])
        x, y = self.position
        self.visited.append(self.position)
        print(f'visited{self.visited}')
        print(f'robot direct :{self.robot_direction}')
        t_possible_moves = []
        possible_moves = []
        not_possoble = []
        sensor_data = {}
        data = {}
        for direction in DIRECTIONS:
            dx, dy = direction
            if direction in [(1,0),(-1,0),(0,1),(0,-1)] :
                if self.robot_direction == 'เหนือ':
                    new_position = (x + dx, y + dy)
                if  self.robot_direction == 'ใต้':
                    new_position = (x - dx, y - dy)
                   
                if self.robot_direction == 'ตะวันออก':
                    new_position = (x - dy, y + dx)
                if self.robot_direction == 'ตะวันตก':
                    new_position = (x + dy, y - dx )

            if self.is_path_clear(direction) and new_position not in self.visited and new_position not in self.wall:
                if self.robot_direction == 'เหนือ' :
                    if direction == (1,0):
                        tdirection = (1,0)
                    if direction == (0,1):
                        tdirection = (0,1)
                    if direction == (-1,0):
                        tdirection = (-1,0)
                    if direction == (0,-1):
                        tdirection = (0,-1)
                if self.robot_direction == 'ตะวันออก' :
                    if direction == (1,0):
                        tdirection = (0,1)
                    if direction == (0,1):
                        tdirection = (-1,0)
                    if direction == (-1,0):
                        tdirection = (0,-1)
                    if direction == (0,-1):
                        tdirection = (1,0)
                if self.robot_direction == 'ใต้' :
                    if direction == (1,0):
                        tdirection = (-1,0)
                    if direction == (0,1):
                        tdirection = (0,-1)
                    if direction == (-1,0):
                        tdirection = (1,0)
                    if direction == (0,-1):
                        tdirection = (0,1)
                if self.robot_direction == 'ตะวันตก' :
                    if direction == (1,0):
                        tdirection = (0,-1)
                    if direction == (0,1):
                        tdirection = (1,0)
                    if direction == (-1,0):
                        tdirection = (0,1)
                    if direction == (0,-1):
                        tdirection = (-1,0)
                t_possible_moves.append(tdirection)
                possible_moves.append(direction)
                print(f'new_position: {new_position} and direction{direction}') 
            if self.is_path_clear(direction): 
                if self.robot_direction == 'เหนือ' :
                    if direction == (1,0):
                        data['front'] = 0
                    if direction == (0,1):
                        data['right'] = 0
                    if direction == (-1,0):

                        data['back'] = 0
                    if direction == (0,-1):

                        data['left'] = 0
                if self.robot_direction == 'ตะวันออก' :
                    if direction == (1,0):
                        data['right'] = 0
                    if direction == (0,1):

                        data['back'] = 0
                    if direction == (-1,0):

                        data['left'] = 0
                    if direction == (0,-1):
                        data['front'] = 0
                if self.robot_direction == 'ใต้' :
                    if direction == (1,0):

                        data['back'] = 0
                    if direction == (0,1):

                        data['left'] = 0
                    if direction == (-1,0):
                        data['front'] = 0
                    if direction == (0,-1):
                        data['right'] = 0
                if self.robot_direction == 'ตะวันตก' :
                    if direction == (1,0):

                        data['left'] = 0
                    if direction == (0,1):
                        data['front'] = 0
                    if direction == (-1,0):
                        data['right'] = 0
                    if direction == (0,-1):

                        data['back'] = 0
            if not self.is_path_clear(direction) :
                if self.robot_direction == 'เหนือ' :
                    if direction == (1,0):
                        data['front'] = 1
                    if direction == (0,1):
                        data['right'] = 1
                    if direction == (-1,0):

                        data['back'] = 1
                    if direction == (0,-1):

                        data['left'] = 1
                if self.robot_direction == 'ตะวันออก' :
                    if direction == (1,0):
                        data['right'] = 1
                    if direction == (0,1):

                        data['back'] = 1
                    if direction == (-1,0):

                        data['left'] = 1
                    if direction == (0,-1):
                        data['front'] = 1
                if self.robot_direction == 'ใต้' :
                    if direction == (1,0):

                        data['back'] = 1
                    if direction == (0,1):

                        data['left'] = 1
                    if direction == (-1,0):
                        data['front'] = 1
                    if direction == (0,-1):
                        data['right'] = 1
                if self.robot_direction == 'ตะวันตก' :
                    if direction == (1,0):

                        data['left'] = 1
                    if direction == (0,1):
                        data['front'] = 1
                    if direction == (-1,0):
                        data['right'] = 1
                    if direction == (0,-1):

                        data['back'] = 1
                
        if len(possible_moves) > 1:
            self.junctions.append(self.position)
            print(f'junction :{self.junctions}')
        
        if not possible_moves:
            if not self.junctions:
                print("Maze exploration complete")
                self.exploration_complete = True
                return
            
            dx, dy = self.path_history.pop()
            if len(self.path_history) == 0:
                self.junctions.pop()
            if self.robot_direction == 'เหนือ' :
                if (dx, dy) == (1,0):
                    tdirection = (1,0)
                if (dx, dy) == (0,1):
                    tdirection = (0,1)
                if (dx, dy) == (-1,0):
                    tdirection = (-1,0)
                if (dx, dy) == (0,-1):
                    tdirection = (0,-1)
            if self.robot_direction == 'ตะวันออก' :
                if (dx, dy) == (1,0):
                    tdirection = (0,1)
                if (dx, dy) == (0,1):
                    tdirection = (-1,0)
                if (dx, dy) == (-1,0):
                    tdirection = (0,-1)
                if (dx, dy) == (0,-1):
                    tdirection = (1,0)
            if self.robot_direction == 'ใต้' :
                if (dx, dy) == (1,0):
                    tdirection = (-1,0)
                if (dx, dy) == (0,1):
                    tdirection = (0,-1)
                if (dx, dy) == (-1,0):
                    tdirection = (1,0)
                if (dx, dy) == (0,-1):
                    tdirection = (0,1)
            if self.robot_direction == 'ตะวันตก' :
                if (dx, dy) == (1,0):
                    tdirection = (0,-1)
                if (dx, dy) == (0,1):
                    tdirection = (1,0)
                if (dx, dy) == (-1,0):
                    tdirection = (0,1)
                if (dx, dy) == (0,-1):
                    tdirection = (-1,0)
            tx, ty = tdirection
            self.position = (x-tx,y-ty)
            print(f'backtrack to node : {self.position}')
            self.move_in_direction(-dx, -dy)

            return
                

        dx, dy = possible_moves[0]
        tx, ty = t_possible_moves[0]
        if len(self.junctions)>0:
            self.path_history.append((dx,dy))
            print(f'history:{self.path_history}')
        self.position = (x + tx, y + ty)
        self.sensor_data[(x + tx, y + ty)] = data
        print(self.sensor_data)
        self.move_in_direction(dx, dy)

    def explore_maze(self):
        self.explore_step()
        time.sleep(0.1)  # Initial exploration step
        while not self.exploration_complete:
            time.sleep(0.1)  # Small delay to prevent busy-waiting

if __name__ == '__main__':
    robot = Robomaster()
    robot.explore_maze()
    robot.plot_maze()