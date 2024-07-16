import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV files
df_positions = pd.read_csv('robot_positions.csv')
df_attitude = pd.read_csv('robot_attitude.csv')
df_esc = pd.read_csv('robot_esc.csv')
df_imu = pd.read_csv('robot_imu.csv')
df_tof = pd.read_csv('robot_tof.csv')
df_time = pd.read_csv('timme.csv')

# Plotting robot_positions.csv vs timme.csv
plt.figure(figsize=(10, 6))
plt.plot(df_time, df_positions['x'], label='x position')
plt.plot(df_time, df_positions['y'], label='y position')
plt.plot(df_time, df_positions['z'], label='z position')
plt.xlabel('Time (s)')
plt.ylabel('Position')
plt.title('Robot Positions Over Time')
plt.legend()
plt.show()

# Plotting robot_attitude.csv vs timme.csv
plt.figure(figsize=(10, 6))
plt.plot(df_time, df_attitude, label='Attitude (Yaw, Pitch, Roll)')
plt.xlabel('Time (s)')
plt.ylabel('Attitude')
plt.title('Robot Attitude Over Time')
plt.legend()
plt.show()

# Plotting robot_esc.csv vs timme.csv
plt.figure(figsize=(10, 6))
plt.plot(df_time, df_esc, label='ESC (Speed, Angle, Timestamp, State)')
plt.xlabel('Time (s)')
plt.ylabel('ESC')
plt.title('Robot ESC Over Time')
plt.legend()
plt.show()

# Plotting robot_imu.csv vs timme.csv
plt.figure(figsize=(10, 6))
plt.plot(df_time, df_imu, label='IMU (Acc_x, Acc_y, Acc_z, Gyro_x, Gyro_y, Gyro_z)')
plt.xlabel('Time (s)')
plt.ylabel('IMU')
plt.title('Robot IMU Over Time')
plt.legend()
plt.show()

# Plotting timme.csv vs timme.csv
plt.figure(figsize=(10, 6))
plt.plot(df_time, df_time, label='Time')
plt.xlabel('Time (s)')
plt.ylabel('Time')
plt.title('Time Over Time')
plt.legend()
plt.show()
