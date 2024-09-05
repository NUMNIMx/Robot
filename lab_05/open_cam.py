import cv2
import numpy as np

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
    # อ่านภาพ (แทนที่ 'path_to_image.jpg' ด้วยพาธของภาพของคุณ)
    image = cv2.imread('D:\Subject\Robot Ai\Robot_group\Robot_old_too\lab_05\coke.png')
    
    # ตรวจจับกระป๋องโค้ก
    result, mask = detect_coke_can(image)
    
    # แสดงผลลัพธ์
    cv2.imshow('Original Image', image)
    cv2.imshow('Detected Coke Can', result)
    cv2.imshow('Mask', mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()