import matplotlib.pyplot as plt
import csv 

X = []
Y = []

with open('robot_positions.csv', 'r') as csvfile:
    lines = csv.reader(csvfile)
    next(lines)  # Skip the header row
    for row in lines:
        if row:  # Check if the row is not empty
            X.append(float(row[0]))
            Y.append(float(row[1]))

plt.plot(X, Y)
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.title('Robot Path')
plt.grid(True)
plt.axis('equal')  # This ensures the aspect ratio is 1:1
plt.show()