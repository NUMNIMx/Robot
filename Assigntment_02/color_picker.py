import cv2
import numpy as np

def nothing(x):
    pass

# สร้างหน้าต่างสำหรับแถบเลื่อน
cv2.namedWindow("Color Picker")

# สร้างแถบเลื่อนสำหรับแต่ละช่องของ HSV
cv2.createTrackbar("Lower-H", "Color Picker", 0, 180, nothing)
cv2.createTrackbar("Lower-S", "Color Picker", 0, 255, nothing)
cv2.createTrackbar("Lower-V", "Color Picker", 0, 255, nothing)
cv2.createTrackbar("Upper-H", "Color Picker", 180, 180, nothing)
cv2.createTrackbar("Upper-S", "Color Picker", 255, 255, nothing)
cv2.createTrackbar("Upper-V", "Color Picker", 255, 255, nothing)

# เริ่มการจับภาพจากกล้อง (หรือใช้ภาพที่บันทึกไว้)
cap = cv2.VideoCapture(0)  # ใช้ 0 สำหรับกล้องเริ่มต้น หรือเปลี่ยนเป็นชื่อไฟล์ภาพ

while True:
    # อ่านเฟรมจากกล้อง (หรือภาพ)
    _, frame = cap.read()
    
    # แปลงภาพเป็น HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
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
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # แสดงภาพ
    cv2.imshow("Original", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)
    
    # ออกจากลูปเมื่อกด 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# แสดงค่าสุดท้ายที่ได้
print(f"Lower HSV: [{l_h}, {l_s}, {l_v}]")
print(f"Upper HSV: [{u_h}, {u_s}, {u_v}]")

# ปิดทุกหน้าต่างและปล่อยทรัพยากร
cap.release()
cv2.destroyAllWindows()