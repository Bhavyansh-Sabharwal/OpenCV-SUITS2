import os
import cv2
import numpy as np
from flask import Flask, request, render_template, send_file
from PIL import Image
from skimage import filters, feature, segmentation
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def detect_terrain(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while preserving edges
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(blurred)
    
    # Use Canny edge detection with automatic threshold detection
    sigma = 0.33
    median = np.median(enhanced)
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    edges = cv2.Canny(enhanced, lower, upper)
    
    # Morphological operations to connect nearby edges
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area and shape
    filtered_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 50:  # Minimum area threshold
            # Calculate contour complexity
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity < 0.8:  # Non-circular shapes are more likely to be terrain features
                    filtered_contours.append(cnt)
    
    # Create result image
    result = img.copy()
    
    # Draw contours with different colors based on size
    for cnt in filtered_contours:
        area = cv2.contourArea(cnt)
        if area > 200:  # Larger features in bright red
            cv2.drawContours(result, [cnt], -1, (0, 0, 255), 2)
            # Add semi-transparent fill
            mask = np.zeros_like(img)
            cv2.drawContours(mask, [cnt], -1, (255, 255, 255), -1)
            red_mask = np.zeros_like(img)
            red_mask[mask[:,:,0] > 0] = [0, 0, 255]
            result = cv2.addWeighted(result, 1, red_mask, 0.3, 0)
        else:  # Smaller features in darker red
            cv2.drawContours(result, [cnt], -1, (0, 0, 180), 1)
    
    return result

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
        
        if file:
            # Save original image
            input_path = os.path.join(UPLOAD_FOLDER, 'input.jpg')
            file.save(input_path)
            
            # Process image
            processed_img = detect_terrain(input_path)
            
            # Save processed image
            output_path = os.path.join(UPLOAD_FOLDER, 'output.jpg')
            cv2.imwrite(output_path, processed_img)
            
            return render_template('index.html', 
                                input_image='static/uploads/input.jpg',
                                output_image='static/uploads/output.jpg')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 