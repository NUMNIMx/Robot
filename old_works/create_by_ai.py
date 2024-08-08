import pandas as pd
from robomaster import robot
import time
import keyboard
import matplotlib.pyplot as plt

x_pos = []  # List to store x positions
times = []
target = []

global expect
expect = 1

def sub_position_handler(position_info):
    x, y, z = position_info
    x_pos.append(float(x))  # Store x positions as float
    global fm_x
    global fm_y
    fm_x = float(x)
    fm_y = float(y)
    
    times.append(time.time() - start)
    target.append(expect)

def toggle_target(expect):
    return 0 if expect == 1 else 1

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    
    ep_chassis = ep_robot.chassis
    ep_chassis.sub_position(freq=50, callback=sub_position_handler)
    
    ref_x = 1
    ref_y = 0
    speed = 50
    count = 0
    c = 0
    time.sleep(1)
    
    start = time.time()
    ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
    time.sleep(1)
    while c < 2:
        while True:
            if count == 0:
                err_x = ref_x - fm_x
                speed = max(50, err_x * 100)
                print(fm_x, fm_y)
                ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
                
                if round(fm_x, 5) >= 1.0:
                    ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                    expect = toggle_target(expect)
                    count += 1
                    
            if count == 1:
                err_x = ref_x - fm_x
                speed = max(50, err_x * 80)
                print(fm_x, fm_y)
                ep_chassis.drive_wheels(w1=-speed, w2=-speed, w3=-speed, w4=-speed)
                
                if round(fm_x, 5) <= 0.0:
                    ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                    expect = toggle_target(expect)
                    count -= 1
                    
            if keyboard.is_pressed('q'):
                ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                print('finish')
                print(len(target), len(x_pos), len(times))
                break
        
        c += 1
    
    ep_chassis.unsub_position()
    ep_robot.close()

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(times, x_pos, label='X position over time')
    plt.plot(times, target, label='Target over time', linestyle='--')
    plt.title('Robot Position and Target Over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('X Position / Target')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
