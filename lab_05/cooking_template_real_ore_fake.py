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

def detect_red_coke_can(image):
    # แปลงภาพเป็นสี HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
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

    # ค่าตัวแปรสำหรับกรอบที่ใหญ่ที่สุด
    max_area = 0
    best_box = None

    # วาดกรอบสี่เหลี่ยมรอบ ๆ ขอบเขตที่ตรวจพบและเลือกกรอบที่ใหญ่ที่สุด
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # ตรวจสอบขนาดวัตถุขั้นต่ำ
            if area > max_area:
                max_area = area
                x, y, w, h = cv2.boundingRect(contour)
                best_box = (x, y, w, h)

    # วาดกรอบที่ใหญ่ที่สุดลงในภาพ
    if best_box is not None:
        x, y, w, h = best_box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

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
                # ตรวจจับกระป๋องโค้กสีแดง
                result_image_with_red_detection = detect_red_coke_can(frame)

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
