import cv2
import numpy as np
import matplotlib.pyplot as plt
#เทสรูป
image = r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\lab_4_immage\coke.webp'
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
#ใช้kernel ในการกำจัด noise ทำให้ภาพเบลอเพื่อความสมูท erode ของ cv2เหมือนเป้นการค่อยๆลด อาจใช้คำสั่ง cv2.filter2D
mask = cv2.erode(mask, kernel, iterations=1)
mask = cv2.dilate(mask, kernel, iterations=1)
#เเปลง mask ให้เป็ย binary im 
# แปลง mask เป็นภาพไบนารี
binary_image = (mask > 0).astype(np.uint8)
plt.subplot(1,2,1)
plot_image = cv2.cvtColor(r_image,cv2.COLOR_BGR2RGB)
plt.imshow(plot_image)
plt.axis('off')

plt.subplot(1, 2, 2)
plt.title('Binary Image (Green = 1, Others = 0)')
plt.imshow(binary_image, cmap='gray')
plt.axis('off')
plt.show()