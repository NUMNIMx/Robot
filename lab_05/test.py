import cv2
import numpy as np

# ฟังก์ชันคำนวณ cosine similarity
def cosine_similarity(a, b):
    a = a.flatten()
    b = b.flatten()
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)

# โหลดภาพหลักและแม่แบบ
image = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\coke_can_sources.png')
template = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\coke_can_tran.png')

# แปลงภาพและแม่แบบเป็นสีเทา
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# ขนาดของแม่แบบ
template_height, template_width = gray_template.shape

# ใช้การ Thresholding เพื่อลบพื้นหลัง
_, thresh_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)
_, thresh_template = cv2.threshold(gray_template, 100, 255, cv2.THRESH_BINARY)

# วนลูปผ่านแต่ละตำแหน่งของหน้าต่างเลื่อนในภาพ
for y in range(0, gray_image.shape[0] - template_height + 1):
    for x in range(0, gray_image.shape[1] - template_width + 1):
        # ดึงพื้นที่จากภาพที่ตรงกับขนาดของแม่แบบ
        window = thresh_image[y:y+template_height, x:x+template_width]
        
        # คำนวณ cosine similarity ระหว่างหน้าต่างกับแม่แบบ
        similarity = cosine_similarity(window, thresh_template)
        
        # กำหนด threshold สำหรับการตรวจจับ
        if similarity > 0.8:  # ปรับค่าตามความต้องการ
            # วาด rectangle รอบๆ ตำแหน่งที่ตรวจพบ
            cv2.rectangle(image, (x, y), (x + template_width, y + template_height), (0, 255, 0), 2)

# แสดงภาพผลลัพธ์
cv2.imshow('Detected Coke Can', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
