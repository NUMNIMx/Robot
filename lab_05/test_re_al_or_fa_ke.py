import cv2
import numpy as np
import time
from robomaster import robot
from robomaster import camera

def display_image(image):
    cv2.imshow('Detected', image)
    # ใช้ waitKey(1) เพื่อตรวจสอบการกดปุ่ม
    key = cv2.waitKey(1)
    if key == ord('q'):  # หากกดปุ่ม 'q'
        return False
    return True

def detect_red_in_window(window):
    # แปลงภาพเป็นสี HSV
    hsv = cv2.cvtColor(window, cv2.COLOR_BGR2HSV)
    
    # กำหนดขอบเขตของสีแดงใน HSV
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # สร้างหน้ากากสำหรับสีแดง
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # หาขอบเขตของวัตถุที่ตรวจพบ
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return len(contours) > 0, cv2.countNonZero(mask)  # ถ้ามี contour ก็แปลว่าพบสีแดง และคืนค่าจำนวน pixel สีแดง

def sliding_window(image, window_size, step_size):
    max_red_area = 0
    best_box = None

    # วนลูปเลื่อนกรอบไปทั่วภาพ
    for y in range(0, image.shape[0] - window_size[1], step_size):
        for x in range(0, image.shape[1] - window_size[0], step_size):
            window = image[y:y + window_size[1], x:x + window_size[0]]
            
            # ตรวจสอบว่ามีสีแดงอยู่ในหน้าต่างหรือไม่ และตรวจสอบพื้นที่สีแดง
            found_red, red_area = detect_red_in_window(window)
            
            if found_red and red_area > max_red_area:
                max_red_area = red_area
                best_box = (x, y, window_size[0], window_size[1])

    # วาดกรอบที่ดีที่สุด (มีสีแดงมากที่สุด) ลงในภาพ
    if best_box is not None:
        x, y, w, h = best_box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return image

if __name__ == '__main__':
    # เริ่มการเชื่อมต่อกับ Robomaster
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")

    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_360P)

    try:
        while True:
            # อ่านเฟรมจากกล้อง
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            
            if frame is not None:
                # ขนาดหน้าต่างสำหรับ sliding window
                window_size = (90,180)  # ขนาด 50x50 pixels
                step_size = 20  # เลื่อนทีละ 20 pixels

                # ใช้ sliding window ในการตรวจจับและวาดเฉพาะกรอบที่ดีที่สุด
                result_image_with_red_detection = sliding_window(frame, window_size, step_size)

                # แสดงผลลัพธ์
                if not display_image(result_image_with_red_detection):
                    break

            time.sleep(0.1)  # ปรับการหน่วงเวลาเพื่อให้ได้การประมวลผลที่เหมาะสม

    except KeyboardInterrupt:
        print("Program interrupted by user")

    # หยุดสตรีมและปิดการเชื่อมต่อ
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
