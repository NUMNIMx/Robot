import cv2
import numpy as np
from robomaster import robot

def process_image(image):
    # แปลง RGB เป็น HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # กำหนดช่วงของสีแดงใน HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # กำหนดเกณฑ์ภาพ HSV เพื่อให้ได้เฉพาะสีแดง
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # ทำ Bitwise-AND ระหว่าง mask และภาพต้นฉบับ
    result = cv2.bitwise_and(image, image, mask=mask)
    
    return result

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    
    ep_camera.start_video_stream(display=False)
    
    while True:
        img = ep_camera.read_cv2_image()
        if img is None:
            continue
        
        processed_img = process_image(img)
        
        cv2.imshow("Original", img)
        cv2.imshow("Processed", processed_img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()