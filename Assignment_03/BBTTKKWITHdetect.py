import time
import matplotlib.pyplot as plt
import keyboard
import numpy as np
from robomaster import robot
import csv
import cv2
from robomaster import robot, blaster, camera
from ultimateeiei2 import  came,find_thief,cosine_similarity_white_edges,sliding_window,find_thief_body
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

class Robomaster:
    def __init__(self):
        self.position = (1, 3)
        self.visited = []  # List to store visited cells
        self.junctions = []  #ลิส node ทางที่เป็นไปได้
        self.path_history = []
        self.last_direction = []
        self.robot_direction = DIRECTIONS2[current_index]
        self.exploration_complete = False
        self.wall = [i for i in wall]
        self.sensor_data = {}
        ep_robot = robot.Robot()
        ep_robot.initialize(conn_type="ap")
        global ep_chassis, ep_gimbal
        ep_chassis = ep_robot.chassis
        ep_sensor = ep_robot.sensor
        ep_sensor_adaptor = ep_robot.sensor_adaptor
        ep_gimbal = ep_robot.gimbal
        ep_robot.initialize(conn_type="ap", proto_type="udp")
        ep_gimbal = ep_robot.gimbal
        ep_camera = ep_robot.camera
        ep_blaster = ep_robot.blaster
        ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

        center_x = 1280 / 2
        center_y = 720 / 2

        p = 0.6 / 1.7
        accumulate_err_x = 0
        accumulate_err_y = 0
        prev_time = time.time()

        try:
            while True:
                frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
                if frame is not None:
                    result_image, circles = find_thief(frame)
                    ep_blaster.set_led(brightness=0, effect=blaster.LED_OFF)
                    
                    if circles is not None:
                        for (x, y, r) in circles:
                            err_x = center_x - x
                            err_y = center_y - y
                            after_time = time.time()
                            accumulate_err_x += err_x * (after_time - prev_time)
                            accumulate_err_y += err_y * (after_time - prev_time)

                            speed_x = p * err_x
                            speed_y = p * err_y

                            ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)
                            prev_time = after_time
                    
                        # Check if gimbal is centered on blue circle
                        if abs(center_x - x) < 10 and abs(center_y - y) < 10:  # Check if within 10 pixels of the center2
                            # Capture the current frame
                            captured_image = frame.copy()
                        
                            # Crop the image to 189x75 pixels centered at (x, y)
                            x_start = max(0, x - 95)  # 189 / 2 = 94.5, take floor
                            y_start = max(0, y - 37)  # 75 / 2 = 37.5, take floor
                            cropped_image = captured_image[y_start:y_start + 250, x_start:x_start + 189]
                            cropped_image = cv2.GaussianBlur(cropped_image, (5, 5), 0)
                            cropped_image  =  cv2.cvtColor( cropped_image, cv2.COLOR_BGR2GRAY)
                            cropped_image = cv2.Canny( cropped_image, 1, 35)
                            # Perform template matching on the cropped image
                            result_image, max_similarity = find_thief_body(cropped_image, r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assignment_03\headless_boky_man.jpg')

                            if max_similarity > 0:  # Check if match is found
                                print("Match found: True") 
                                ep_blaster.fire(times=1)
                                time.sleep(2)
                                # Print that a match was found
                            else:
                                print("Match found: False")  # Print that no match was found
                    else:
                        # Stop the gimbal if no circles are found
                        ep_gimbal.stop()  # Stop the gimbal in its current position
                    
                    if not came(result_image):
                        ep_gimbal.stop()  # Stop the gimbal when the program ends
                else:
                    ep_gimbal.stop()  # Stop the gimbal if no frame is received
        except KeyboardInterrupt:
            print("Program interrupted by user")  


        ep_robot.initialize(conn_type="ap")
 
        ep_sensor_adaptor.sub_adapter(freq=50, callback=sub_data_handler2)
        ep_sensor.sub_distance(freq=50, callback=sub_data_handler)
        ep_chassis.sub_position(freq=50, callback=sub_position_handler)
        ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()
    
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
                path_clear = False

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
        global current_index
        current_index = (current_index+1)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

    def turn_left(self):
        ep_chassis.move(x=0, y=0, z=90, z_speed=100).wait_for_completed()
        global current_index
        current_index = (current_index-1)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

    def backward(self):
        ep_chassis.move(x=0, y=0, z=-180, z_speed=100).wait_for_completed()
        global current_index
        current_index = (current_index+2)%4
        self.robot_direction = DIRECTIONS2[current_index]
        self.Move()

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

            if self.is_path_clear(direction) and new_position not in self.visited not in self.wall:
                if self.robot_direction == 'เหนือ' :
                    if direction == (1,0):
                        tdirection = (1,0)
                        data['front'] = 0
                    if direction == (0,1):
                        tdirection = (0,1)
                        data['right'] = 0
                    if direction == (-1,0):
                        tdirection = (-1,0)
                        data['back'] = 0
                    if direction == (0,-1):
                        tdirection = (0,-1)
                        data['left'] = 0
                if self.robot_direction == 'ตะวันออก' :
                    if direction == (1,0):
                        tdirection = (0,1)
                        data['right'] = 0
                    if direction == (0,1):
                        tdirection = (-1,0)
                        data['back'] = 0
                    if direction == (-1,0):
                        tdirection = (0,-1)
                        data['left'] = 0
                    if direction == (0,-1):
                        tdirection = (1,0)
                        data['front'] = 0
                if self.robot_direction == 'ใต้' :
                    if direction == (1,0):
                        tdirection = (-1,0)
                        data['back'] = 0
                    if direction == (0,1):
                        tdirection = (0,-1)
                        data['left'] = 0
                    if direction == (-1,0):
                        tdirection = (1,0)
                        data['front'] = 0
                    if direction == (0,-1):
                        tdirection = (0,1)
                        data['right'] = 0
                if self.robot_direction == 'ตะวันตก' :
                    if direction == (1,0):
                        tdirection = (0,-1)
                        data['left'] = 0
                    if direction == (0,1):
                        tdirection = (1,0)
                        data['front'] = 0
                    if direction == (-1,0):
                        tdirection = (0,1)
                        data['right'] = 0
                    if direction == (0,-1):
                        tdirection = (-1,0)
                        data['back'] = 0
                t_possible_moves.append(tdirection)
                possible_moves.append(direction)
                print(f'new_position: {new_position} and direction{direction}') 
                
            if not self.is_path_clear(direction) :
                if self.robot_direction == 'เหนือ' :
                    if direction == (1,0):
                        tdirection = (1,0)
                        data['front'] = 1
                    if direction == (0,1):
                        tdirection = (0,1)
                        data['right'] = 1
                    if direction == (-1,0):
                        tdirection = (-1,0)
                        data['back'] = 1
                    if direction == (0,-1):
                        tdirection = (0,-1)
                        data['left'] = 1
                if self.robot_direction == 'ตะวันออก' :
                    if direction == (1,0):
                        tdirection = (0,1)
                        data['right'] = 1
                    if direction == (0,1):
                        tdirection = (-1,0)
                        data['back'] = 1
                    if direction == (-1,0):
                        tdirection = (0,-1)
                        data['left'] = 1
                    if direction == (0,-1):
                        tdirection = (1,0)
                        data['front'] = 1
                if self.robot_direction == 'ใต้' :
                    if direction == (1,0):
                        tdirection = (-1,0)
                        data['back'] = 1
                    if direction == (0,1):
                        tdirection = (0,-1)
                        data['left'] = 1
                    if direction == (-1,0):
                        tdirection = (1,0)
                        data['front'] = 1
                    if direction == (0,-1):
                        tdirection = (0,1)
                        data['right'] = 1
                if self.robot_direction == 'ตะวันตก' :
                    if direction == (1,0):
                        tdirection = (0,-1)
                        data['left'] = 1
                    if direction == (0,1):
                        tdirection = (1,0)
                        data['front'] = 1
                    if direction == (-1,0):
                        tdirection = (0,1)
                        data['right'] = 1
                    if direction == (0,-1):
                        tdirection = (-1,0)
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
    