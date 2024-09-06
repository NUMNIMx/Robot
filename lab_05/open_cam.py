import cv2
import numpy as np
from robomaster import robot
from robomaster import camera

def detect_coke_can(image):
    # แปลง BGR เป็น HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # กำหนดช่วงของสีแดงใน HSV สำหรับกระป๋องโค้ก
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # สร้าง mask สำหรับช่วงสีแดงทั้งสองช่วง
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    
    # รวม mask ทั้งสอง
    mask = cv2.bitwise_or(mask1, mask2)
    
    # ใช้ morphological operations เพื่อลดนอยส์
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # ใช้ mask กับภาพต้นฉบับ
    result = cv2.bitwise_and(image, image, mask=mask)
    
    return result, mask

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    
    ep_camera.start_video_stream(display=True,resolution=camera.STREAM_720P)
    
    while True:
        img = ep_camera.read_cv2_image()
        if img is None:
            continue
        
        processed_img, mask = detect_coke_can(img)
        
        # หา contours ของวัตถุที่ตรวจพบ
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # วาดกรอบรอบวัตถุที่ตรวจพบ (ถ้ามี)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cv2.imshow("Original", img)
        cv2.imshow("Processed", processed_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
   
if __name__ == "__main__":
    main()