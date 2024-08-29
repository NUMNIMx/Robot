import cv2
import numpy as np

# เปิดไฟล์วิดีโอ
video_path = r'E:\Users\Home\Desktop\New folder (12)\Robot\“Coke” Zero x NewJeans.mp4'
cap = cv2.VideoCapture(video_path)

# กำหนดขอบเขตของสีแดง (สีหลักของกระป๋องโค้ก)
lower_red = np.array([0, 120, 70])
upper_red = np.array([10, 255, 255])

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # แปลงภาพจาก BGR เป็น HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # สร้าง mask สำหรับสีแดง
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    
    # เพิ่มขอบเขตสำหรับสีแดง (เช่น สีแดงเข้ม)
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    
    # รวม mask ทั้งสอง
    mask = mask1 + mask2
    
    # สร้าง Kernel สำหรับ Morphological Operations
    kernel = np.ones((5, 5), np.uint8)  # ขนาด kernel 5x5
    
    # ใช้ Erosion เพื่อลบ noise ขนาดเล็ก
    mask = cv2.erode(mask, kernel, iterations=1)
    
    # ใช้ Dilation เพื่อขยายพื้นที่ของกระป๋องโค้ก
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # หาขอบเขตของวัตถุที่ตรวจจับได้
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # วาดกรอบรอบวัตถุที่ตรวจจับได้
    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # กำหนดขนาดขั้นต่ำของวัตถุที่ต้องการตรวจจับ
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # แสดงผลลัพธ์
    cv2.imshow('Coca-Cola Detection', frame)
    
    # กด 'q' เพื่อออกจากวิดีโอ
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
