import cv2
import numpy as np
import os
import time

# Record the start time
start_time = time.time()
print('Running cloth mask')

def get_cloth_mask(image_path):
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros_like(image)

    cv2.drawContours(mask, contours, -1, (255, 255, 255), -1)

    return mask

def process_images(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = os.listdir(input_folder)
    image_files = [f for f in image_files if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    for image_file in image_files:
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, image_file)

        cloth_mask = get_cloth_mask(input_path)

        cv2.imwrite(output_path, cloth_mask)

        print(f"Cloth mask saved at: {output_path}")

input_folder = "SD-VITON/dataroot/test/cloth"
output_folder = "SD-VITON/dataroot/test/cloth-mask"
process_images(input_folder, output_folder)
# Record the end time
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time

# Print the execution time in seconds
print("Done with cloth mask.\nExecution time: {:.4f} seconds".format(execution_time))
print('----------------------------------------------------------------------------------------')