import cv2
import numpy as np

# โหลดเทมเพลตในรูปแบบ RGB
t1 = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke_template01.jpg')
t2 = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke_template02.jpg')
t3 = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke_template03.jpg')
t4 = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke_template04.jpg')
t5 = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke_template05.jpg')
templates = [t1, t2, t3, t4, t5]
# โหลดเป็น RGB และแยกเป็น 3 ช่องสี (R, G, B)
template_r = t1[:, :, 0].flatten()  # ช่องสีแดง
template_g = t1[:, :, 1].flatten()  # ช่องสีเขียว
template_b = t1[:, :, 2].flatten()  # ช่องสีน้ำเงิน

def cosine_similarity(vec1, vec2):
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    return np.dot(vec1_norm, vec2_norm)

def sliding_window(image, step_size, window_size):
    for y in range(0, image.shape[0], step_size):  # เคลื่อนตามแนวแกน Y
        for x in range(0, image.shape[1], step_size):  # เคลื่อนตามแนวแกน X
            window = image[y:y + window_size[1], x:x + window_size[0]]

            # ตรวจสอบว่าหน้าต่างที่เลือกมีขนาดพอดีกับ template หรือไม่
            if window.shape[0] != window_size[1] or window.shape[1] != window_size[0]:
                continue

            # ส่งตำแหน่ง (x, y) และเนื้อหาของหน้าต่างไปใช้
            yield (x, y, window)

# ขนาดของหน้าต่างต้องเท่ากับขนาดของเทมเพลต
window_size = t1.shape[:2]  # (ความสูง, ความกว้าง) โดยไม่รวมช่องสี
step_size = 10  # ก้าวทีละ 10 พิกเซล

# โหลดภาพที่ต้องการตรวจจับ
image = cv2.imread(r'C:\Users\MSI A15\Documents\GitHub\Robot\Robot\Coke01.jpg')
print(t1.shape)
print(image.shape)
# ใช้ Sliding Window
for (x, y, window) in sliding_window(image, step_size, window_size):
    # แยกช่องสี R, G, B จากหน้าต่างที่ได้
    window_r = window[:, :, 0].flatten()
    window_g = window[:, :, 1].flatten()
    window_b = window[:, :, 2].flatten()

    # คำนวณ Cosine Similarity สำหรับแต่ละช่องสี
    similarity_r = cosine_similarity(template_r, window_r)
    similarity_g = cosine_similarity(template_g, window_g)
    similarity_b = cosine_similarity(template_b, window_b)

    # คำนวณค่าเฉลี่ยของ Cosine Similarity จากทั้ง 3 ช่องสี
    similarity = (similarity_r + similarity_g + similarity_b) / 3
    
    # ถ้าความคล้ายสูงกว่า threshold (เช่น 0.9) แสดงว่าตรวจพบวัตถุ
    if similarity > 0.81:
        print(f"Object detected at position: ({x}, {y}) with similarity: {similarity}")

        # วาดกรอบรอบวัตถุที่ตรวจพบ
        cv2.rectangle(image, (x, y), (x + window_size[1], y + window_size[0]), (255, 0, 10), 2)

# แสดงภาพที่มีการวาดกรอบรอบวัตถุ
cv2.imshow("Detected Object", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
