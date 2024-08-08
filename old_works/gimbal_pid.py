import cv2
import robomaster
from robomaster import robot
from robomaster import vision
from robomaster import blaster
import time
import pandas as pd
import matplotlib.pyplot as plt


start =  time.time()
# คลาสสำหรับเก็บข้อมูล marker(ป้าย)
class MarkerInfo:
    # ข้อมูลจุดตรงกลางป้าย ความกว้าง ความยาว ข้อมูลป้าย
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info

    # คำนวณมุมซ้ายบนของป้ายและแปลงเป็น pixel
    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)

    # คำนวณมุมขวาล่างของป้ายและแปลงเป็น pixel
    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)

    # จุดกลางป้ายเป็น pixel
    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)

    # ข้อมูลป้าย
    @property
    def text(self):
        return self._info


markers = []


# in case that there are many detected markers
def on_detect_marker(marker_info):
    number = len(marker_info)
    markers.clear()
    for i in range(0, number):
        x, y, w, h, info = marker_info[i]
        markers.append(
            MarkerInfo(x, y, w, h, info)
        )  # x and y w h is in a range of [0 1] relative to image's size


# เก็บข้อมูลมุมของ gimbal
def sub_data_handler(angle_info):
    global list_of_data
    list_of_data = angle_info


if __name__ == "__main__":
    # initialize robot
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster
    i=1
    # the image center constants4
    
    center_x = (1280 / 2)
    center_y = 720 / 2
    

    ep_camera.start_video_stream(display=False)
    ep_gimbal.sub_angle(freq=50, callback=sub_data_handler)
    result = ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)

    # หมุน gimbal กลับไปที่ center
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    count = 0
    time.sleep(1)

    # PID controller constants
    p = 0.83/1.7
    i= p/(0.6/2)
    d = p*(0.6/8)
    # i = 0
    # d = 0

    data_pith_yaw = []
    accumulate_x = 0
    accumulate_y = 0
    # loop การทำงานของหุ่น
    prev_time = time.time()
    prev_err_x = 0
    prev_err_y = 0
    while True:
        if len(markers) != 0:  # target found
            after_time = time.time()
            x, y = markers[-1].center  # x,y here in the pixel unit
            add_time = time.time() - start
            

            err_x = (
                center_x - x
            )  # err_x = image_center in x direction - current marker center in x direction
            err_y = (
                center_y - y
            )  # err_y = image_center in y direction - current marker center in y direction
            accumulate_x += err_x*(after_time-prev_time)
            accumulate_y += err_y*(after_time-prev_time)

            if count >= 1:
                # คำนวณความเร็วในการหมุน gimbal โดยใช้ PID
                speed_x = (
                    (p * err_x)+ d*((err_x-prev_err_x)/(after_time-prev_time)) + i*accumulate_x
                )
                speed_y = (
                    (p * err_y)+ d*((err_y-prev_err_y)/(after_time-prev_time)) + i*accumulate_y
                )

                # หมุน gimbal ตามความเร็วที่คำนวณมาก
                ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)
                time.sleep(0.001)
            
                # เก็บค่ามุมของ gimbal, error x, error y, speed x, speed y
                print(add_time)
                data_pith_yaw.append(
                    list(list_of_data)
                    + [err_x, err_y, round(speed_x, 3), round(speed_y, 3), center_x, x,add_time]
                )
            
            count += 1
            

            
            # prev_time = endtimmme
            # # delt_err_x = err_x-prev_err_x
            # prev_err_x = err_x
            # # delt_err_y = err_y-prev_err_x
            # prev_err_y = err_y
            print('prev_time :',prev_time,'err_x',err_x,'abs(err_x-prev_err_x)',abs(err_x-prev_err_x),'(abs(err_y-prev_err_y)',abs(err_y-prev_err_y))
            prev_time = after_time
            # delt_err_x = err_x-prev_err_x
            prev_err_x = err_x
            # delt_err_y = err_y-prev_err_x
            prev_err_y = err_y

        else:
            # หมุนกลับ center
            ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)

        # อ่านภาพ
        img = ep_camera.read_cv2_image(strategy="newest", timeout=5)

        # วาดสี่เหลี่ยมบนภาพในตำแหน่งที่เจอป้าย
        for j in range(0, len(markers)):
            cv2.rectangle(img, markers[j].pt1, markers[j].pt2, (0, 255, 0))
            cv2.putText(
                img,
                markers[j].text,
                markers[j].center,
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                3,
            )
        # แสดงภาพ
        cv2.imshow("Markers", img)
        
        # สำหรับออกจาก loop while
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

    result = ep_vision.unsub_detect_info(name="marker")
    ep_camera.stop_video_stream()
    ep_robot.close()

    # plot error x, error y, speed x, speed y
    x_point = [i for i in range(len(data_pith_yaw))]
    y_point4 = [i[4] for i in data_pith_yaw]
    y_point5 = [i[5] for i in data_pith_yaw]
    y_point6 = [i[6] for i in data_pith_yaw]
    y_point7 = [i[7] for i in data_pith_yaw]
    y_point8 = [i[8] for i in data_pith_yaw]
    y_point9 = [i[9] for i in data_pith_yaw]
    y_point10 = [i[10] for i in data_pith_yaw]
    '''y_t = 
    x_t = [1280/2,1280/4,(1280/4)*3]'''


    plt.plot(y_point10, y_point8)
    plt.plot(y_point10, y_point9)
    # plt.plot(x_point, y_point4)
    # plt.plot(x_point, y_point5)
    # plt.plot(x_point, y_point6)
    # plt.plot(x_point, y_point7)
    plt.legend(["certer_x", "x"])
    plt.show()
    df = pd.DataFrame({"index": x_point, "center_x": y_point8, "e x": y_point4, "e y": y_point5, "u x": y_point6, "u y": y_point7, "x": y_point9})
    df.to_csv("data_0_1.csv")