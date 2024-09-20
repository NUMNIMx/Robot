import cv2

# ฟังก์ชันแสดงภาพพร้อมการซูมและเลื่อน
def display_image(window_name, image, scale, x_offset, y_offset):
    height, width = image.shape[:2]
    new_size = (int(width * scale), int(height * scale))
    resized_image = cv2.resize(image, new_size)

    # กำหนดขอบเขตของการเลื่อนเฟรมภาพ
    x_offset = min(max(0, x_offset), new_size[0] - width)
    y_offset = min(max(0, y_offset), new_size[1] - height)

    # ตัดภาพเพื่อแสดงส่วนที่เลื่อน
    cropped_image = resized_image[y_offset:y_offset + height, x_offset:x_offset + width]
    cv2.imshow(window_name, cropped_image)

def main():
    image = cv2.imread(r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\lab06\coke_can_120_c.jpg')

    scale = 1.0  # ขนาดเริ่มต้น
    scale_step = 0.1  # ขั้นตอนการซูม
    min_scale = 0.5  # ขนาดเล็กสุด
    max_scale = 3.0  # ขนาดใหญ่สุด

    x_offset, y_offset = 0, 0  # ค่าการเลื่อนเริ่มต้น
    pan_step = 50  # ขั้นตอนการเลื่อนแต่ละครั้ง

    window_name = "Select Object"
    cv2.namedWindow(window_name)

    while True:
        display_image(window_name, image, scale, x_offset, y_offset)

        key = cv2.waitKey(0)

        if key == ord('+'):  # กด + เพื่อซูมเข้า
            scale = min(scale + scale_step, max_scale)
        elif key == ord('-'):  # กด - เพื่อซูมออก
            scale = max(scale - scale_step, min_scale)
        elif key == ord('q'):  # กด q เพื่อออกจากโปรแกรม
            break
        elif key == ord('a'):  # เลื่อนซ้าย
            x_offset -= pan_step
        elif key == ord('d'):  # เลื่อนขวา
            x_offset += pan_step
        elif key == ord('w'):  # เลื่อนขึ้น
            y_offset -= pan_step
        elif key == ord('s'):  # เลื่อนลง
            y_offset += pan_step
        elif key == ord('r'):  # กด r เพื่อเลือก ROI และเซฟภาพ
            roi = cv2.selectROI(window_name, image, fromCenter=False, showCrosshair=True)
            x, y, w, h = roi
            if w > 0 and h > 0:
                object_template = image[y:y+h, x:x+w]
                filename = 'coke_can_1.jpg'  # ตั้งชื่อไฟล์เป็น coke_can_1 หรือ coke_can_2 ตามที่ต้องการ
                cv2.imwrite(filename, object_template)
                print(f'Saved {filename}')

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
