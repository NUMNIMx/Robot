import cv2
import numpy as np

# ค่าพารามิเตอร์
f = 800  # focal length ของกล้อง (ต้องใช้ค่าที่ถูกต้องตามการทดลอง)
k_x = 1  # ค่าคงที่ตามแกน X
k_y = 1  # ค่าคงที่ตามแกน Y
coke_real_width = 6.5  # ความกว้างของกระป๋องโค้กจริง (เซนติเมตร)
coke_real_height = 12.0  # ความสูงของกระป๋องโค้กจริง (เซนติเมตร)

# โหลดภาพ
cokepic = cv2.imread(r'/Users/seaconcoding/Desktop/robottest/Robot/lab_06/coke_can_180.jpg')

# แปลงเป็น HSV และทำการ threshold เพื่อหาโค้ก
hsv = cv2.cvtColor(cokepic, cv2.COLOR_BGR2HSV)
low_red = np.array([143, 39, 0])
up_red = np.array([180, 224, 90])
mask = cv2.inRange(hsv, low_red, up_red)

# ค้นหา contours ของโค้ก
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# ตรวจสอบว่ามี contour หรือไม่
if contours:
    # หาค่า bounding box ของ contour
    x, y, w, h = cv2.boundingRect(contours[0])
    
    # คำนวณระยะทาง Z จากแกน X และแกน Y
    Z_x = (k_x * f * coke_real_width) / w
    Z_y = (k_y * f * coke_real_height) / h
    
    # คำนวณระยะทางจริงโดยใช้สูตรพีทาโกรัส
    Z = np.sqrt(Z_x**2 + Z_y**2)
    
    # แสดงผลลัพธ์
    print(f"ระยะทางจากกล้องถึงกระป๋องโค้ก (แกน X): {Z_x:.2f} cm")
    print(f"ระยะทางจากกล้องถึงกระป๋องโค้ก (แกน Y): {Z_y:.2f} cm")
    print(f"ระยะทางรวมจากกล้องถึงกระป๋องโค้ก: {Z:.2f} cm")
    
    # วาดสี่เหลี่ยมรอบโค้กในภาพ
    cv2.rectangle(cokepic, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('Detected Coke Can', cokepic)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("ไม่พบกระป๋องโค้กในภาพ")
