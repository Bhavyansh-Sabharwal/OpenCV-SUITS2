# SUITS Terrain Detector

A web application that uses OpenCV to detect and highlight uneven terrain and holes in ground images.

## Features
- Upload images through a modern web interface
- Automatic detection of terrain irregularities using OpenCV
- Real-time processing and visualization
- Highlighted results with red boundaries around detected terrain features

## Setup

1. Install the required dependencies:
```bash
pip install flask opencv-python numpy Pillow scikit-image
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage
1. Click the "Choose Image" button to select an image
2. The application will automatically process the image and display both the original and processed versions
3. Detected terrain features will be highlighted in red

## Technical Details
The application uses:
- Flask for the web framework
- OpenCV for image processing
- Edge detection and contour finding for terrain analysis
- Semi-transparent overlays for highlighting detected areas 