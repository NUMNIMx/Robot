import cv2
import numpy as np

# โหลดภาพ
image = cv2.imread('/Users/seaconcoding/Desktop/robottest/Robot/lab_4_immage/a5_0floor.jpg')

# แปลงภาพจาก BGR เป็น HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# ช่วงสีที่ต้องการเก็บ (HSV)
lower_color1 = np.array([0, 184, 90])
upper_color1 = np.array([93, 255, 255])
lower_color2 = np.array([102, 123, 133])
upper_color2 = np.array([179, 255, 255])

# สร้าง mask สำหรับสีในช่วงที่กำหนด
mask1 = cv2.inRange(hsv_image, lower_color1, upper_color1)
mask2 = cv2.inRange(hsv_image, lower_color2, upper_color2)

# รวม mask ทั้งสอง
combined_mask = cv2.bitwise_or(mask1, mask2)

# ลบ noise ด้วยการทำ opening และ closing
kernel = np.ones((5, 5), np.uint8)  # กำหนดขนาด kernel สามารถปรับขนาดได้ตามต้องการ

# Opening: erosion ตามด้วย dilation เพื่อลบ noise ขนาดเล็ก
opening = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

# Closing: dilation ตามด้วย erosion เพื่อลบช่องว่างเล็กๆ ภายในวัตถุ
clean_mask = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

# สร้างภาพที่เป็นสีดำทั้งหมด
result = np.zeros_like(image)

# ใช้ mask ที่ทำความสะอาดแล้ว เพื่อเก็บเฉพาะส่วนที่ตรงกับช่วงสีที่ต้องการในภาพ
result[clean_mask > 0] = image[clean_mask > 0]

# แสดงผลภาพ
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
