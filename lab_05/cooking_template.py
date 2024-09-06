import cv2

# โหลดภาพหลักและภาพเทมเพลต
image = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\coke01.jpg')
template = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\lab_05\coke.png')
(h_t, w_t) = template.shape[:2]

# แปลงภาพหลักเป็นเทา (สำหรับการค้นหาแบบเทมเพลต)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# ทำ Template Matching
result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)

# หาตำแหน่งที่ดีที่สุด
(min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)

# กำหนดค่าพื้นฐานของพื้นที่ที่มีการจับคู่
(startX, startY) = max_loc
(endX, endY) = (startX + w_t, startY + h_t)

# วาดกรอบสี่เหลี่ยมล้อมรอบเทมเพลต
cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

# แสดงภาพที่มีกรอบสี่เหลี่ยม
cv2.imshow('Detected', image)
cv2.waitKey(0)
cv2.destroyAllWindows()