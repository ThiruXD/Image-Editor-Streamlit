# Image Editor Using Pillow and Streamlit

## Project Overview

This project is a web-based Photo Editor built using Pillow (PIL) and Streamlit. It allows users to upload images and apply various image processing operations through an interactive and user-friendly interface.

The application demonstrates the practical use of digital image processing techniques for image enhancement, filtering, transformation, and editing. By combining Pillow's robust image manipulation capabilities with Streamlit's intuitive web framework, the project provides a simple yet effective, real-time image editing solution that runs seamlessly in local and cloud environments.

---

## Objective

The primary objective of this project is to develop an interactive photo editing application that enables users to perform basic image processing tasks without requiring advanced technical knowledge.

The application aims to:

- Enhance image quality
- Apply non-destructive image filters
- Perform geometric image transformations
- Provide real-time image previews
- Create an easy-to-use editing experience

---

## Features

- Dynamic Image Upload Functionality
- Real-Time Sliders for Transient Adjustments
- Linear/Non-Compounding Filter Modification
- Grayscale Conversion & Blending
- Interactive Image Resizing
- Image Rotation (90-degree steps)
- Image Flipping (Horizontal & Vertical)
- Gaussian Blur Effects
- Visual Contour and Edge Detection Filters
- Brightness and Contrast Scaling
- Real-Time Side-by-Side Preview Layout
- Buffered Native File Downloader

---

## Technologies Used

- Python
- Streamlit
- Pillow (PIL)
- NumPy
- io (Standard library memory buffering)

---

## System Workflow

1. User drops an image into the sidebar file uploader.
2. The system sets up stateful memory storage variables.
3. Destructive mutations (rotations, flips, edge art styles) modify a hidden base canvas.
4. Linear changes (sliders for blur, contrast, brightness, zoom) are rendered dynamically on top.
5. The processed result renders immediately side-by-side with the original image.
6. The user down-streams the raw matrix as a localized standard JPG download.

---

## Image Processing Operations

### Image Enhancement
- Brightness Adjustment
- Contrast Adjustment
- Kernel Sharpening

### Image Transformation
- Geometric Resizing
- Multi-Axis Rotation (expand canvas borders)
- Mirror/Flip Actions
- Focal Point Center-Zoom Scaling

### Filtering & Artistic Transitions
- Grayscale Blending Intensity Slider
- Safe Linear Gaussian Blur
- Warm Temperature Overlay Matrix
- Canny-Style Edge Detection
- Vector Outline Contour Sketching
- Posterized Cartoon Emulation

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Gayathri-7095/photo-editor-opencv-streamlit.git
```

Navigate to the project directory:

```bash
cd photo-editor-opencv-streamlit
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

After execution, open the local URL displayed in the terminal:

```text
http://localhost:8501
```

Upload an image and start editing using the available tools.

---

## Example Use Cases

* Photo enhancement
* Basic image editing
* Lightweight browser-based adjustments
* Educational learning projects
* Image preprocessing workflows

---

## Results

The application successfully performs various image editing and processing operations through a simple web interface. Users can upload images, apply modifications, preview results instantly, and download edited images.

The project demonstrates the integration of Digital Image Processing and Web Application Development to create an interactive, cloud-compatible image editing platform.

---

## Key Learnings

* Stateful Web Session Management (`st.session_state`)
* Linear vs. Compounding Matrix Mutations
* Pixel-Level Image Transformations via Pillow
* Streamlit Layout Grid Architecture
* UI/UX Design Optimization for Media Processing
* In-Memory Media File Buffering (`io.BytesIO`)

---

## Future Enhancements

* Dynamic Object Background Removal
* Face Detection Layer Integration
* Multi-Step History Undos
* Custom Canvas Text Overlay Watermarking
* Batch Structural Image Processing
* Local Color Range Extraction Filters

---

## Credits
- ThiruXD
- Gemini AI
