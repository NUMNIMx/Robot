import cv2
import matplotlib.pyplot as plt

# Define parameters
w = 120  # Width of the sliding window
h = 120  # Height of the sliding window
steps = 60  # Step size for the sliding window

# Define sliding window
def slidingWindow(image, stepSize, windowSize):
    for y in range(0, image.shape[0] - windowSize[1] + 1, stepSize):
        for x in range(0, image.shape[1] - windowSize[0] + 1, stepSize):
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

# Load your test image
imageTest = cv2.imread(r'E:\Users\Home\Desktop\New folder (12)\Robot\lab_4_immage\coke.webp')
if imageTest is None:
    print("Error: Image not found.")
    exit()

# Prepare to visualize all sliding windows
plt.figure(figsize=(20, 10))

# Iterate over all possible positions
count = 0
for i, (x, y, _) in enumerate(slidingWindow(imageTest, stepSize=steps, windowSize=(h, w))):
    imageCopy = imageTest.copy()
    cv2.rectangle(imageCopy, (x, y), (x + w, y + h), (0, 255, 0), 2)
    plt.subplot(6, 10, count + 1)  # Adjust the subplot grid based on the number of images
    plt.imshow(imageCopy[:, :, ::-1])  # Convert BGR to RGB for display
    plt.axis('off')
    plt.title(f'Pos: ({x}, {y})')
    count += 1
    if count >= 60:  # Display the first 60 windows for visualization
        break

plt.show()
