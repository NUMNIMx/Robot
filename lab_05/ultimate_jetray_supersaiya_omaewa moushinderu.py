import cv2
import numpy as np

# โหลดภาพ
image = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\lab_4_immage\captured_image1.jpg')

# แปลงภาพเป็น Grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# แปลงภาพเป็น Binary โดยใช้ Thresholding
_, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# ค้นหา Contours
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# วาด Contours ลงบนภาพต้นฉบับ
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

# แสดงผลภาพ
cv2.imshow("Contours", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
