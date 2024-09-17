import pandas as pd
import matplotlib.pyplot as plt

# อ่านไฟล์ CSV โดยใช้ raw string
df = pd.read_csv(r"C:\Users\ItsPe\Downloads\ml.csv")

# สร้างฟังก์ชันสำหรับกำหนดค่า x
def assign_x_values(y_values):
    x_values = [5]  # เริ่มต้นที่ 5
    for i in range(1, len(y_values)):
        if y_values[i] != y_values[i-1]:
            x_values.append(x_values[-1] + 5)
        else:
            x_values.append(x_values[-1])
    return x_values

# สร้างค่า x สำหรับแต่ละชุดข้อมูล
x_train = assign_x_values(df['train'])
x_test = assign_x_values(df['test'])
x_train_real = assign_x_values(df['train_real'])

# สร้างกราฟ 2D
plt.figure(figsize=(12, 6))

# พล็อตข้อมูลทั้ง 3 ชุด
plt.plot(x_train, df['train'], label='Train', marker='o')
plt.plot(x_test, df['test'], label='Test', marker='s')
plt.plot(x_train_real, df['train_real'], label='Train Real', marker='^')

# ตั้งค่าชื่อแกน
plt.xlabel('Layer size')
plt.ylabel('Percent')

# ตั้งชื่อกราฟ
plt.title('Plot of Train, Test, and Train Real')

# แสดง legend
plt.legend()

# แสดงเส้นตาราง
plt.grid(True)

# ปรับขอบเขตของแกน y ให้เริ่มจาก 70
plt.ylim(bottom=70)

# ปรับขอบเขตของแกน x
plt.xlim(left=0)

# แสดงกราฟ
plt.tight_layout()
plt.show()