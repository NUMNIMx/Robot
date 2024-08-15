import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('axis_data.csv')

# Create the plot
plt.figure(figsize=(10, 8))
plt.plot(df['X'], df['Y'], label='Robot Path', marker='o', markersize=2, linewidth=1)

# Customize the plot
plt.title('Robot Movement Path')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.legend()
plt.grid(True)

# Add start and end markers
plt.plot(df['X'].iloc[0], df['Y'].iloc[0], color='green', marker='o', markersize=10, label='Start')
plt.plot(df['X'].iloc[-1], df['Y'].iloc[-1], color='red', marker='o', markersize=10, label='End')

# Update legend
plt.legend()

# Show the plot
plt.show()