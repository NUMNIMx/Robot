import cv2
import numpy as np

# โหลดภาพต้นฉบับและภาพที่เป็น template
source_image = cv2.imread('source_image.jpg')
template = cv2.imread('template_image.jpg')

# ขนาดของ template
(tH, tW) = template.shape[:2]

# ทำ Template Matching โดยใช้ cv2.matchTemplate
result = cv2.matchTemplate(source_image, template, cv2.TM_CCOEFF_NORMED)

# กำหนดค่าความคล้าย (threshold) เพื่อหาจุดที่ตรงกัน
threshold = 0.8
locations = np.where(result >= threshold)

# วาดกรอบสี่เหลี่ยมล้อมรอบ template ที่พบ
for pt in zip(*locations[::-1]):
    cv2.rectangle(source_image, pt, (pt[0] + tW, pt[1] + tH), (0, 255, 0), 2)

# แสดงผลลัพธ์
cv2.imshow('Detected', source_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
