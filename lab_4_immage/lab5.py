import cv2
import numpy as np
import matplotlib.pyplot as plt
#เทสรูป
image = r'E:\Users\Home\Desktop\New folder (12)\Robot\lab_4_immage\coke.webp'
r_image = cv2.imread(image)
#เปลี่ยนเป็นHSL
HSL_image = cv2.cvtColor(r_image,cv2.COLOR_BGR2HSV)
#เเบ่งสีค่าHSV 3 ค่า [:,:,:,]ค่าเเรกคือ องศ่่าในรูป 2กับคือคือเปแเสนความสว่างจากขาวไปดำ  3คือ ความเข้ม ของสี
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])
#inrage คือฟังชั้นเทรชโอส ก็คือง่าย if elif กำหนดค่า 
mask = cv2.inRange(HSL_image, lower_red, upper_red)
#kernel operation สร้างm5*5 ทั้งหมดเป็น1 unit 8 = 8bit 255
kernel = np.ones((5, 5), np.uint8)
cv2.imshow('image test', mask)
cv2.waitKey(0)