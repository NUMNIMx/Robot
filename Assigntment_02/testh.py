import cv2
import numpy as np

# โหลดภาพหลักและภาพ template
image = cv2.imread('/Users/seaconcoding/Desktop/robottest/Robot/lab_4_immage/a5_0floor.jpg')
template = cv2.imread('/Users/seaconcoding/Desktop/robottest/Robot/Assigntment_02/kk/2.1.jpg')

# แปลงภาพทั้งสองเป็นขาวดำเพื่อให้การจับคู่เร็วขึ้น (สามารถข้ามขั้นตอนนี้ได้ถ้าไม่ต้องการ)
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# ขนาดของ template
w, h = template_gray.shape[::-1]

# ใช้ template matching
res = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

# หาค่าที่ตรงกับมากที่สุด
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

# ตำแหน่งของวัตถุที่พบ
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)

# วาดกรอบสี่เหลี่ยมรอบๆ วัตถุที่พบ
cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

# แสดงผลภาพ
cv2.imshow('Detected Chicken', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
