import cv2
import numpy as np
import time

def nothing(x):
    pass

# สร้างหน้าต่างสำหรับแถบเลื่อน
cv2.namedWindow("Color Picker")

# รอให้หน้าต่างถูกสร้าง
time.sleep(1)

# สร้างแถบเลื่อนสำหรับแต่ละช่องของ HSV
cv2.createTrackbar("Lower-H", "Color Picker", 0, 180, nothing)
cv2.createTrackbar("Lower-S", "Color Picker", 0, 255, nothing)
cv2.createTrackbar("Lower-V", "Color Picker", 0, 255, nothing)
cv2.createTrackbar("Upper-H", "Color Picker", 180, 180, nothing)
cv2.createTrackbar("Upper-S", "Color Picker", 255, 255, nothing)
cv2.createTrackbar("Upper-V", "Color Picker", 255, 255, nothing)


image_path = r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\boky_man32.jpg'

frame = cv2.imread(image_path)

if frame is None:
    print("ไม่สามารถอ่านรูปภาพได้ กรุณาตรวจสอบพาธของไฟล์")
    exit()

while True:
    # สร้างสำเนาของรูปภาพเพื่อไม่ให้กระทบกับภาพต้นฉบับ
    frame_copy = frame.copy()

    # แปลงภาพเป็น HSV
    hsv = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2HSV)

    # รับค่าจากแถบเลื่อน
    l_h = cv2.getTrackbarPos("Lower-H", "Color Picker")
    l_s = cv2.getTrackbarPos("Lower-S", "Color Picker")
    l_v = cv2.getTrackbarPos("Lower-V", "Color Picker")
    u_h = cv2.getTrackbarPos("Upper-H", "Color Picker")
    u_s = cv2.getTrackbarPos("Upper-S", "Color Picker")
    u_v = cv2.getTrackbarPos("Upper-V", "Color Picker")

    # กำหนดช่วงสี
    lower_range = np.array([l_h, l_s, l_v])
    upper_range = np.array([u_h, u_s, u_v])

    # สร้างมาสก์
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # ใช้มาสก์กับภาพต้นฉบับ
    result = cv2.bitwise_and(frame_copy, frame_copy, mask=mask)

    # แสดงภาพ
    cv2.imshow("Original", frame_copy)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    # ออกจากลูปเมื่อกด 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# แสดงค่าสุดท้ายที่ได้
print(f"Lower HSV: [{l_h}, {l_s}, {l_v}]")
print(f"Upper HSV: [{u_h}, {u_s}, {u_v}]")

# ปิดทุกหน้าต่าง
cv2.destroyAllWindows()