import cv2
import numpy as np
import time
from robomaster import robot
from robomaster import camera

# ฟังก์ชันสำหรับคำนวณ cosine similarity
def cosine_similarity(A, B):
    A_flat = A.flatten()
    B_flat = B.flatten()
    dot_product = np.dot(A_flat, B_flat)
    norm_A = np.linalg.norm(A_flat)
    norm_B = np.linalg.norm(B_flat)
    if norm_A == 0 or norm_B == 0:  # ป้องกันการหารด้วย 0
        return 0
    return dot_product / (norm_A * norm_B)

# ฟังก์ชันสำหรับ sliding window
def sliding_window(image, template_size, stride, padding):
    padded_image = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0)
    h, w = image.shape[:2]
    th, tw = template_size

    for y in range(0, h - th + 1, stride):
        for x in range(0, w - tw + 1, stride):
            yield x, y, padded_image[y:y+th, x:x+tw]

# ฟังก์ชันสำหรับตรวจจับกระป๋องโค้กสีแดงโดยใช้ cosine similarity และ template 5 รูป
def detect_red_coke_can(image, templates, stride=4, padding=0):
    best_match_value = 0
    best_box = None

    # วนลูปผ่านทุก template
    for template in templates:
        template_h, template_w = template.shape[:2]

        # วนลูปผ่านทุก window ในภาพที่ได้จากกล้อง
        for x, y, window in sliding_window(image, (template_h, template_w), stride, padding):
            if window.shape[:2] == template.shape[:2]:
                similarity = cosine_similarity(window, template)

                # เก็บ window ที่มีค่าความเหมือนสูงสุด
                if similarity > best_match_value:
                    best_match_value = similarity
                    best_box = (x, y, template_w, template_h)

    # ถ้าพบ window ที่มีค่าความเหมือนสูงสุด
    if best_box is not None:
        x, y, w, h = best_box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return image

# ฟังก์ชันสำหรับแสดงภาพ
def display_image(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):  # หากกดปุ่ม 'q'
        return False
    return True

if __name__ == '__main__':
    # โหลด template ทั้ง 5 รูป (ปรับเส้นทางตามตำแหน่งที่เก็บไฟล์)
    template1 = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\Coke_template01.jpg')
    template2 = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\Coke_template02.jpg')
    template3 = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\Coke_template03.jpg')
    template4 = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\Coke_template04.jpg')
    template5 = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\Coke_template05.jpg')

    # สร้างลิสต์ของ template
    templates = [template1, template2, template3, template4, template5]

    # เริ่มการเชื่อมต่อกับ Robomaster
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")

    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)

    try:
        while True:
            # อ่านเฟรมจากกล้อง
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

            if frame is not None:
                # ตรวจจับกระป๋องโค้กสีแดงด้วย cosine similarity และ template 5 รูป
                result_image = detect_red_coke_can(frame, templates, stride=4, padding=10)

                # แสดงผลลัพธ์
                if not display_image(result_image):
                    break

            time.sleep(0.1)  # ปรับการหน่วงเวลาเพื่อให้ได้การประมวลผลที่เหมาะสม

    except KeyboardInterrupt:
        print("Program interrupted by user")

    # หยุดสตรีมและปิดการเชื่อมต่อ
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
