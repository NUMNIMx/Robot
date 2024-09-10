import cv2
import robomaster
from robomaster import robot
from robomaster import camera
import numpy as np
import time
from queue import Empty

def nothing(x):
    pass

# สร้างหน้าต่างสำหรับแถบเลื่อน
cv2.namedWindow("Color Picker")

# สร้างแถบเลื่อนสำหรับแต่ละช่องของ HSV
cv2.createTrackbar("Lower-H", "Color Picker", 0, 180, nothing)
cv2.createTrackbar("Lower-S", "Color Picker", 120, 255, nothing)
cv2.createTrackbar("Lower-V", "Color Picker", 110, 255, nothing)
cv2.createTrackbar("Upper-H", "Color Picker", 89, 180, nothing)
cv2.createTrackbar("Upper-S", "Color Picker", 255, 255, nothing)
cv2.createTrackbar("Upper-V", "Color Picker", 255, 255, nothing)

def detect_yellow_chickens(image, lower_yellow, upper_yellow):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_chickens = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # ขนาดขั้นต่ำของวัตถุ
            x, y, w, h = cv2.boundingRect(contour)
            detected_chickens.append((x, y, w, h, area))
    
    # เรียงลำดับตามขนาดพื้นที่ (ใหญ่สุดก่อน)
    detected_chickens.sort(key=lambda x: x[4], reverse=True)
    
    # วาดกรอบสี่เหลี่ยมรอบตุ๊กตาไก่ที่ตรวจพบ N ตัวแรก
    N = 2  # จำนวนตุ๊กตาไก่ที่ต้องการตรวจจับ
    for i, (x, y, w, h, _) in enumerate(detected_chickens[:N]):
        color = (0, 255, 255) if i == 0 else (255, 255, 0)  # สีเหลืองอ่อนสำหรับตัวใหญ่สุด, สีเหลืองเข้มสำหรับตัวที่สอง
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, f'Chicken {i+1}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return image, mask

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_camera = ep_robot.camera
    
    # ตรวจสอบการเชื่อมต่อ
    if not ep_camera.is_connected:
        print("กล้องไม่ได้เชื่อมต่อ กรุณาตรวจสอบการเชื่อมต่อของคุณ")
        ep_robot.close()
        exit()
    
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    
    # รอให้สตรีมวิดีโอเริ่มต้น
    time.sleep(2)

    try:
        while True:
            try:
                frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
                if frame is None:
                    print("ไม่สามารถอ่านเฟรมได้ ลองอีกครั้ง...")
                    continue
            except Empty:
                print("ไม่ได้รับเฟรมภายในเวลาที่กำหนด ลองอีกครั้ง...")
                continue
            
            # รับค่าจากแถบเลื่อน
            l_h = cv2.getTrackbarPos("Lower-H", "Color Picker")
            l_s = cv2.getTrackbarPos("Lower-S", "Color Picker")
            l_v = cv2.getTrackbarPos("Lower-V", "Color Picker")
            u_h = cv2.getTrackbarPos("Upper-H", "Color Picker")
            u_s = cv2.getTrackbarPos("Upper-S", "Color Picker")
            u_v = cv2.getTrackbarPos("Upper-V", "Color Picker")
            
            # กำหนดช่วงสี
            lower_yellow = np.array([l_h, l_s, l_v])
            upper_yellow = np.array([u_h, u_s, u_v])
            
            result_image, mask = detect_yellow_chickens(frame, lower_yellow, upper_yellow)
            
            # แสดงภาพ
            cv2.imshow("Original", frame)
            cv2.imshow("Mask", mask)
            cv2.imshow("Result", result_image)
            
            # ออกจากลูปเมื่อกด 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("โปรแกรมถูกหยุดโดยผู้ใช้")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {str(e)}")
    finally:
        # แสดงค่าสุดท้ายที่ได้
        print(f"Lower HSV: [{l_h}, {l_s}, {l_v}]")
        print(f"Upper HSV: [{u_h}, {u_s}, {u_v}]")
        
        # ปิดการเชื่อมต่อและปล่อยทรัพยากร
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()