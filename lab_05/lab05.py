import cv2
import numpy as np
from robomaster import robot
from robomaster import camera
import time

def create_anchor_boxes():
    # Define anchor boxes (example sizes, adjust as needed)
    return [(30, 60), (45, 90), (60, 120)]

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def sliding_window(image, window_size, stride):
    for y in range(0, image.shape[0] - window_size[1] + 1, stride):
        for x in range(0, image.shape[1] - window_size[0] + 1, stride):
            yield (x, y, image[y:y + window_size[1], x:x + window_size[0]])

def detect_coke_can(image):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define range of red color in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # Threshold the HSV image to get only red colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # Setup anchor boxes
    anchor_boxes = create_anchor_boxes()
    
    # Prepare a template of a Coke can (you should replace this with an actual template)
    template = np.ones((60, 30), dtype=np.uint8) * 255  # Example template
    
    max_similarity = 0
    best_box = None
    
    # Sliding window with cosine similarity
    for (x, y, window) in sliding_window(mask, (30, 60), stride=10):
        for anchor_box in anchor_boxes:
            resized_window = cv2.resize(window, anchor_box)
            similarity = cosine_similarity(resized_window.flatten(), template.flatten())
            if similarity > max_similarity:
                max_similarity = similarity
                best_box = (x, y, anchor_box[0], anchor_box[1])
    
    return best_box, max_similarity

def main():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal

    ep_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)

    target_found_time = None
    while True:
        img = ep_camera.read_cv2_image()
        if img is None:
            continue

        best_box, similarity = detect_coke_can(img)

        if best_box and similarity > 0.8:  # Adjust threshold as needed
            x, y, w, h = best_box
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Calculate center of the bounding box
            center_x = x + w // 2
            center_y = y + h // 2

            # Calculate offset from image center
            offset_x = center_x - img.shape[1] // 2
            offset_y = center_y - img.shape[0] // 2

            # Move gimbal to track the can (adjust parameters as needed)
            ep_gimbal.move(pitch=-offset_y * 0.1, yaw=offset_x * 0.1).wait_for_completed()

            if target_found_time is None:
                target_found_time = time.time()
            elif time.time() - target_found_time > 2:
                # Fire laser after 2 seconds of tracking
                print("Target locked for 2 seconds - would fire laser here")
                # Add code here to fire the laser
                target_found_time = None  # Reset timer
        else:
            target_found_time = None

        cv2.imshow("ROBOMASTER Coke Can Tracking", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    ep_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()