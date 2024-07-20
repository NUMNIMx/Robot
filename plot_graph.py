import pandas as pd
import matplotlib.pyplot as plt

# Read the timme.csv file
time_data = pd.read_csv('timme.csv', sep=':', header=None, names=['label', 'time'])
time_data['time'] = time_data['time'].astype(float)

# Read the other CSV files
robot_positions = pd.read_csv('robot_positions.csv')
atti_fix = pd.read_csv('robot_attitude.csv')
esc_fix = pd.read_csv('robot_esc.csv')
imu_fix = pd.read_csv('robot_imu.csv')
robot_tof = pd.read_csv('robot_tof.csv', sep=':', header=None, names=['label', 'tof'])

# Clean and convert tof data
robot_tof['tof'] = pd.to_numeric(robot_tof['tof'], errors='coerce')
robot_tof = robot_tof.dropna()
robot_tof['tof'] = robot_tof['tof'].astype(int)

# Ensure time_data and other data have the same length
min_length = min(len(time_data), len(robot_positions), len(atti_fix), len(esc_fix), len(imu_fix), len(robot_tof))
time_data = time_data[:min_length]
robot_positions = robot_positions[:min_length]
atti_fix = atti_fix[:min_length]
esc_fix = esc_fix[:min_length]
imu_fix = imu_fix[:min_length]
robot_tof = robot_tof[:min_length]

# Verify the TOF data
print(robot_tof.head())

# Create subplots
fig, axs = plt.subplots(5, 1, figsize=(10, 15))

# Plot the data
axs[0].plot(time_data['time'], robot_positions['x'], label='Robot X Position')
axs[0].plot(time_data['time'], robot_positions['y'], label='Robot Y Position')
axs[0].plot(time_data['time'], robot_positions['z'], label='Robot Z Position')
axs[0].set_title('Positions')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Position')
axs[0].legend()

axs[1].plot(time_data['time'], atti_fix['yaw'], label='Yaw')
axs[1].plot(time_data['time'], atti_fix['pitch'], label='Pitch')
axs[1].plot(time_data['time'], atti_fix['roll'], label='Roll')
axs[1].set_title('Attitude')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Angle (degrees)')
axs[1].legend()

axs[2].plot(time_data['time'], esc_fix['speed'].apply(eval).apply(lambda x: x[0]), label='Speed 1')
axs[2].plot(time_data['time'], esc_fix['speed'].apply(eval).apply(lambda x: x[1]), label='Speed 2')
axs[2].plot(time_data['time'], esc_fix['speed'].apply(eval).apply(lambda x: x[2]), label='Speed 3')
axs[2].plot(time_data['time'], esc_fix['speed'].apply(eval).apply(lambda x: x[3]), label='Speed 4')
axs[2].set_title('ESC Speeds')
axs[2].set_xlabel('Time (s)')
axs[2].set_ylabel('Speed')
axs[2].legend()

axs[3].plot(time_data['time'], imu_fix['acc_x'], label='Acc X')
axs[3].plot(time_data['time'], imu_fix['acc_y'], label='Acc Y')
axs[3].plot(time_data['time'], imu_fix['acc_z'], label='Acc Z')
axs[3].plot(time_data['time'], imu_fix['gyro_x'], label='Gyro X')
axs[3].plot(time_data['time'], imu_fix['gyro_y'], label='Gyro Y')
axs[3].plot(time_data['time'], imu_fix['gyro_z'], label='Gyro Z')
axs[3].set_title('IMU')
axs[3].set_xlabel('Time (s)')
axs[3].set_ylabel('Acceleration / Gyro')
axs[3].legend()

axs[4].plot(time_data['time'], robot_tof['tof'], label='TOF')
axs[4].set_title('Robot TOF')
axs[4].set_xlabel('Time (s)')
axs[4].set_ylabel('TOF Distance')
axs[4].legend()

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(hspace=2)

plt.show()
