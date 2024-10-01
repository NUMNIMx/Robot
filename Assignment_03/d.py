import cv2
import numpy as np

# โหลดภาพทั้งสอง
image1 = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\bottleman_2_plate_led.jpg')
image2 = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\bottleman_2_plate.jpg')

result = cv2.subtract(image1, image2)

# แสดงภาพผลลัพธ์
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()

# บันทึกภาพผลลัพธ์
cv2.imwrite('result.png', result)
