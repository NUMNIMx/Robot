import cv2
import numpy as np
import matplotlib.pyplot as plt

# ฟังก์ชันคำนวณ Cosine Similarity
def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    return np.dot(vec1_norm, vec2_norm)

# ฟังก์ชัน Sliding Window
def sliding_window(image, step_size, window_size):
    for y in range(0, image.shape[0] - window_size[1] + 1, step_size):
        for x in range(0, image.shape[1] - window_size[0] + 1, step_size):
            window = image[y:y + window_size[1], x:x + window_size[0]]
            
            # ปรับขนาดหน้าต่างให้ตรงกับขนาดแม่แบบ
            window_resized = cv2.resize(window, (window_size[1], window_size[0]))  # (width, height)
            yield (x, y, window_resized)

# ฟังก์ชัน Non-Maximum Suppression (NMS) เพื่อกรองการตรวจจับซ้ำซ้อน
def non_max_suppression(boxes, overlapThresh):
    if len(boxes) == 0:
        return []
    
    # ถ้าบาง boxes มีรูปแบบ integer ให้แปลงเป็น float
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")
    
    pick = []
    
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)
    
    while len(idxs) > 0:
        last = idxs[-1]
        pick.append(last)
        
        xx1 = np.maximum(x1[last], x1[idxs[:-1]])
        yy1 = np.maximum(y1[last], y1[idxs[:-1]])
        xx2 = np.minimum(x2[last], x2[idxs[:-1]])
        yy2 = np.minimum(y2[last], y2[idxs[:-1]])
        
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        
        overlap = (w * h) / area[idxs[:-1]]
        
        idxs = idxs[np.where(overlap <= overlapThresh)[0]]
    
    return boxes[pick].astype("int")

# โหลดเทมเพลตทั้งหมดในรูปแบบ BGR
template_paths = [
    r'E:\Users\Home\Desktop\New folder (12)\Robot\Coke_template01.jpg',
    r'E:\Users\Home\Desktop\New folder (12)\Robot\Coke_template02.jpg',
    r'E:\Users\Home\Desktop\New folder (12)\Robot\Coke_template03.jpg',
    r'E:\Users\Home\Desktop\New folder (12)\Robot\Coke_template04.jpg',
    r'E:\Users\Home\Desktop\New folder (12)\Robot\Coke_template05.jpg'
]
templates = [cv2.imread(path) for path in template_paths]

# แปลงเทมเพลตเป็นฟอร์แมต BGR และแปลงเป็นเวกเตอร์
template_vectors = []
for template in templates:
    if template is not None:
        template_r = template[:, :, 2].flatten()  # ช่องสีแดงใน BGR
        template_g = template[:, :, 1].flatten()  # ช่องสีเขียวใน BGR
        template_b = template[:, :, 0].flatten()  # ช่องสีน้ำเงินใน BGR
        template_vector = np.concatenate([template_r, template_g, template_b])
        template_vectors.append(template_vector)
    else:
        print("Error loading template.")

# ขนาดของหน้าต่างต้องเท่ากับขนาดของเทมเพลต
window_size = templates[0].shape[:2][::-1]  # (width, height)
step_size = 10  # ก้าวทีละ 10 พิกเซล

# โหลดภาพที่ต้องการตรวจจับในรูปแบบ BGR
image_path = r'E:\Users\Home\Desktop\New folder (12)\Robot\coke01.jpg'
image = cv2.imread(image_path)
if image is None:
    print("Error loading target image.")
    exit()

original_image = image.copy()

# เก็บตำแหน่งและค่าความคล้ายสำหรับการวาดกรอบ
detections = []

# ใช้ Sliding Window กับทุกเทมเพลต
for (x, y, window) in sliding_window(image, step_size, window_size):
    if window.shape[0] != window_size[1] or window.shape[1] != window_size[0]:
        continue
    
    # แปลงหน้าต่างเป็นเวกเตอร์เดียว
    window_r = window[:, :, 2].flatten()  # ช่องสีแดง
    window_g = window[:, :, 1].flatten()  # ช่องสีเขียว
    window_b = window[:, :, 0].flatten()  # ช่องสีน้ำเงิน
    window_vector = np.concatenate([window_r, window_g, window_b])
    
    # เปรียบเทียบกับทุกเทมเพลต
    for template_vector in template_vectors:
        similarity = cosine_similarity(template_vector, window_vector)
        
        if similarity > 0.75:
          detections.append([x, y, x + window_size[0], y + window_size[1], similarity])

# ถ้ามีการตรวจจับ ให้ใช้ NMS เพื่อลดการซ้ำซ้อน
if len(detections) > 0:
    boxes = np.array(detections)
    pick = non_max_suppression(boxes, overlapThresh=0.3)
    
    for (x1, y1, x2, y2, sim) in pick:
        cv2.rectangle(original_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(original_image, f"{sim:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# แสดงภาพที่มีการวาดกรอบรอบวัตถุ
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plot_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
plt.imshow(plot_image)
plt.title('Original Image')
plt.axis('off')

plt.subplot(1, 2, 2)
plot_detected = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
plt.imshow(plot_detected)
plt.title('Detected Objects')
plt.axis('off')

plt.show()
