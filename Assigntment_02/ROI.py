import cv2

# อ่านภาพ
image = cv2.imread('/Users/seaconcoding/Desktop/robottest/Robot/lab_4_immage/a5_2.1floor.jpg')

# เลือก ROI
roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)

# ตัดภาพเฉพาะส่วนที่สนใจ
roi_cropped = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
cv2.imwrite('2.jpg', roi_cropped)
# แสดงภาพที่ตัดออกมา
cv2.imshow("Cropped ROI", roi_cropped)
cv2.waitKey(0)
cv2.destroyAllWindows()
