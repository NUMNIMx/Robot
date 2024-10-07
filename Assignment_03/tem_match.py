import cv2
import numpy as np

# โหลดภาพต้นฉบับและภาพแทมเพลต
img = cv2.imread('image.jpg', 0)  # ภาพต้นฉบับ (ภาพที่จะค้นหา)
template = cv2.imread('template.jpg', 0)  # ภาพแทมเพลต
w, h = template.shape[::-1]  # ขนาดของภาพแทมเพลต

# ใช้ Template Matching
result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

# กำหนดค่าความคล้ายคลึงที่ต้องการ (Threshold)
threshold = 0.8
loc = np.where(result >= threshold)

# ล้อมกรอบวัตถุที่ตรวจจับได้
for pt in zip(*loc[::-1]):
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

# แสดงผล
cv2.imshow('Detected', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
