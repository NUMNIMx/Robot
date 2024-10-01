import cv2
import numpy as np
import matplotlib.pyplot as plt
d120 = [30,80]
d60 = [64,166]
d180 = [20,50]
d75 = [49,125]
d100 = [36,96]
d125 = [28,73]

def kfinder(d120,d60,d180):
    kxf120 = d120[0] * (120/5.8)
    kyf120 = d120[1] * (120/14.5)
    kxf60 = d60[0] * (60/5.8)
    kyf60 = d60[1] * (60/14.5)
    kxf180= d180[0] * (180/5.8)
    kyf180 = d180[1] * (180/14.5)
    print(f'kx kxy ในระยะ 120{kxf120,kyf120}')
    print(f'kx kxy ในระยะ 180{kxf180,kyf180}')
    print(f'kx kxy ในระยะ 60{kxf60,kyf60}')
    mean_kx = (kxf120 + kxf180 +kxf60)/3
    mean_ky = (kyf120 + kyf180 +kyf60)/3
    return mean_kx, mean_ky
def zfinder(kx,ky,d75,d100,d125):
    zx75 = kx*5.8*1/d75[0]
    zx100 = kx*5.8*1/d100[0]
    zx125 = kx*5.8*1/d125[0]
    zy75 = ky*14.5*1/d75[1]
    zy100 = ky*14.5*1/d100[1]
    zy125 = ky*14.5*1/d125[1]
    zx = [zx75,zx100,zx125]
    zy = [zy75,zy100,zy125]
    print('แสดงค่า zx และ zy',zx,zy)
    return zx,zy

if __name__ == "__main__":
    kx,ky = kfinder(d120,d60,d180)
    zx,zy = zfinder(kx,ky,d75,d100,d125)
    zx2,zy2 = zfinder(kx,ky,d60,d120,d180)
    sc_zx = [1/i for i in zx]
    sc_zy = [1/i for i in zy]
    sc_zxr = [1/i for i in zx2]
    sc_zyr = [1/i for i in zy2]
    print(zx,zy)
    
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].plot(sc_zxr,[d60[0],d120[0],d180[0]],color = 'red', marker='o',label='1/zx (dx)')  # ใช้ marker='o' เพื่อแสดงจุดที่แต่ละค่า
    axs[0].plot(sc_zyr,[d60[1],d120[1],d180[1]],color = 'b', marker='x', label='1/zy (dy)')
    # เพิ่มชื่อแกนและชื่อกราฟ
    axs[0].set_title('Graph A: Scaled Measurements vs. Distance 60,120,180')
    axs[0].set_xlabel('1/Z')
    axs[0].set_ylabel('Distance')

    axs[0].legend()


    axs[1].plot(sc_zx,[d75[0],d100[0],d125[0]],color = 'red', marker='o',label='1/zx (dx) 75 100 125')  # ใช้ marker='o' เพื่อแสดงจุดที่แต่ละค่า
    axs[1].plot(sc_zy,[d75[1],d100[1],d125[1]],color = 'b', marker='x', label='1/zy (dy) 75 100 125')
    axs[1].plot(sc_zxr,[d60[0],d120[0],d180[0]],color = 'purple', marker='o',label='1/zx (dx) 60 120 180')  # ใช้ marker='o' เพื่อแสดงจุดที่แต่ละค่า
    axs[1].plot(sc_zyr,[d60[1],d120[1],d180[1]],color = 'orange', marker='x', label='1/zy (dy) 60 120 180')
    # เพิ่มชื่อแกนและชื่อกราฟ
    axs[1].set_title('Graph F: Scaled Measurements vs. Distance 60,75,80,100,125,180 ')
    axs[1].set_xlabel('1/Z')
    axs[1].set_ylabel('Distance')

    axs[1].legend()



    # แสดงกราฟ
    plt.show()
    
