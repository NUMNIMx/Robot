import cv2
import robomaster
from robomaster import robot
from robomaster import blaster
from robomaster import camera
import time
import numpy as np

def came(image):
    cv2.imshow('Detected', image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        return False
    return True

def find_thief(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([102, 123, 113])
    upper_blue = np.array([179, 255, 255])
    lower_blue2 = np.array([94, 158, 62])
    upper_blue2 = np.array([180, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask1 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask = cv2.bitwise_or(mask, mask1)
    
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, param1=50, param2=30, minRadius=10, maxRadius=40)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)  # Draw the circle in the original image
            cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)  # Draw a rectangle at the center of the circle
    
    return image, circles

def cosine_similarity_white_edges(a, b):
    # Flatten the arrays
    a_flat = a.flatten()
    b_flat = b.flatten()

    # Create masks for white edges (255 values) only
    a_white_mask = a_flat == 255
    b_white_mask = b_flat == 255

    # Find the intersection of white masks to identify the common white pixels
    intersection_mask = a_white_mask & b_white_mask

    # Check if there are common white pixels
    if np.sum(intersection_mask) == 0:
        return 0  # No common white pixels

    # Apply the intersection mask to both arrays
    a_filtered = a_flat[a_white_mask]
    b_filtered = b_flat[b_white_mask]
    cosine = np.dot(a_filtered, b_filtered) / (np.linalg.norm(a_filtered) * np.linalg.norm(b_filtered))
    print(cosine)
    # Calculate cosine similarity using only the filtered arrays
    return cosine


def sliding_window(image, window_size, stride):
    for y in range(0, image.shape[0] - window_size[1] + 1, stride):
        for x in range(0, image.shape[1] - window_size[0] + 1, stride):
            yield (x, y, image[y:y + window_size[1], x:x + window_size[0]])
            
def find_thief_body(image, template_path, stride=10, similarity_threshold=0.8):
    # Load the template and convert it to grayscale
    template = cv2.imread(template_path)
    if template is None:
        print("Template image not found.")
        return image, 0  # Return the original image if template is not found
    template  =  cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.GaussianBlur(template, (5, 5), 0)
    template_edges = cv2.Canny(template, 1, 35)
    # Perform edge detection (Canny) on the template
    
    # Define window size based on template size
    window_size = template.shape[:2]
    
    max_similarity = 0
    best_match_location = None
    
    # Sliding window over the grayscale image
    for (x, y, window) in sliding_window(image, window_size, stride):
        # Perform edge detection on the current window
        window  =  cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
        window = cv2.GaussianBlur(window, (5, 5), 0)
        window_edges = cv2.Canny(window, 1, 35)
        
        # Calculate cosine similarity between window edges and template edges
        similarity = cosine_similarity_white_edges(window_edges, template_edges)
        
        # Check if the similarity exceeds the threshold
        if similarity > similarity_threshold and similarity > max_similarity:
            max_similarity = similarity
            best_match_location = (x, y)
    
    if best_match_location is not None:
        # Draw a rectangle around the best match found
        top_left = best_match_location
        bottom_right = (top_left[0] + window_size[1], top_left[1] + window_size[0])
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    
    return image, max_similarity


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap", proto_type="udp")
    ep_gimbal = ep_robot.gimbal
    ep_camera = ep_robot.camera
    ep_blaster = ep_robot.blaster
    ep_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)
    ep_gimbal.recenter(pitch_speed=200, yaw_speed=200).wait_for_completed()

    center_x = 1280 / 2
    center_y = 720 / 2

    p = 0.6 / 1.7
    accumulate_err_x = 0
    accumulate_err_y = 0
    prev_time = time.time()

    try:
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            if frame is not None:
                result_image, circles = find_thief(frame)
                ep_blaster.set_led(brightness=0, effect=blaster.LED_OFF)
                
                if circles is not None:
                    for (x, y, r) in circles:
                        err_x = center_x - x
                        err_y = center_y - y
                        after_time = time.time()
                        accumulate_err_x += err_x * (after_time - prev_time)
                        accumulate_err_y += err_y * (after_time - prev_time)

                        speed_x = p * err_x
                        speed_y = p * err_y

                        ep_gimbal.drive_speed(pitch_speed=speed_y, yaw_speed=-speed_x)
                        prev_time = after_time
                
                    # Check if gimbal is centered on blue circle
                    if abs(center_x - x) < 10 and abs(center_y - y) < 10:  # Check if within 10 pixels of the center2
                        # Capture the current frame
                        captured_image = frame.copy()
                    
                        # Crop the image to 189x75 pixels centered at (x, y)
                        x_start = max(0, x - 95)  # 189 / 2 = 94.5, take floor
                        y_start = max(0, y - 37)  # 75 / 2 = 37.5, take floor
                        cropped_image = captured_image[y_start:y_start + 250, x_start:x_start + 189]
                        cropped_image = cv2.GaussianBlur(cropped_image, (5, 5), 0)
                        cropped_image  =  cv2.cvtColor( cropped_image, cv2.COLOR_BGR2GRAY)
                        cropped_image = cv2.Canny( cropped_image, 1, 35)
                        # Perform template matching on the cropped image
                        result_image, max_similarity = find_thief_body(cropped_image, r'D:\Subject\Robot Ai\Robot_group\Robot_old_too\Assignment_03\headless_boky_man.jpg')

                        if max_similarity > 0:  # Check if match is found
                            print("Match found: True") 
                            ep_blaster.fire(times=1)
                            time.sleep(2)
                             # Print that a match was found
                        else:
                            print("Match found: False")  # Print that no match was found
                else:
                    # Stop the gimbal if no circles are found
                    ep_gimbal.stop()  # Stop the gimbal in its current position
                
                if not came(result_image):
                    ep_gimbal.stop()  # Stop the gimbal when the program ends
            else:
                ep_gimbal.stop()  # Stop the gimbal if no frame is received
    except KeyboardInterrupt:
        print("Program interrupted by user")  

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()