import matplotlib.pyplot as plt
import csv 

X = []
time = []



with open('Conect.csv', 'r') as csvfile:
    lines = csv.reader(csvfile)
    next(lines)  # Skip the header row
    for row in lines:
        if row:  # Check if the row is not empty
            X.append(float(row[0]))
            time.append(float(row[1]))
plt.figure(figsize=(6,6))
plt.plot(time, X)
plt.ylabel('X Position')
plt.xlabel('time Position')
plt.title('Robot Path')
plt.grid(True)
plt.axis('equal')  # This ensures the aspect ratio is 1:1
plt.show()