import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Photo Editor", layout="wide")

st.title("📸 AI Photo Editor")

st.sidebar.title("Controls")

# Load initial image
initial_img = cv2.imread(r"C:\Users\gayat\Downloads\kitten.webp")

if initial_img is None:
    st.error("Image not found")
    st.stop()

# Session state setup
if "original" not in st.session_state:
    st.session_state.original = initial_img.copy()

if "edited" not in st.session_state:
    st.session_state.edited = initial_img.copy()

# Reset button
if st.sidebar.button("🔄 Reset to Original"):
    st.session_state.edited = st.session_state.original.copy()
    st.rerun()

img = st.session_state.edited.copy()
original = st.session_state.original.copy()

# Face blur function
def face_blur(img):
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        if face_cascade.empty():
            return img

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return img

        blurred = cv2.GaussianBlur(img, (51,51), 0)

        for (x,y,w,h) in faces:
            blurred[y:y+h, x:x+w] = img[y:y+h, x:x+w]

        return blurred
    except:
        return img

# Adjustments
with st.sidebar.expander("Adjustments"):
    w = st.slider("Width",100,1000,img.shape[1])
    h = st.slider("Height",100,1000,img.shape[0])
    b = st.slider("Brightness",-100,100,0)
    c = st.slider("Contrast",0.5,3.0,1.0)

img = cv2.resize(img,(w,h))
img = cv2.convertScaleAbs(img, alpha=c, beta=b)

# Filters
with st.sidebar.expander("Filters (Sliders)"):

    blur_val = st.slider("Blur", 0, 25, 0)
    if blur_val > 0:
        k = blur_val if blur_val % 2 == 1 else blur_val + 1
        img = cv2.GaussianBlur(img, (k, k), 0)

    sharp_val = st.slider("Sharpen", 0, 5, 0)
    if sharp_val > 0:
        kernel = np.array([[0,-1,0],[-1,5+sharp_val,-1],[0,-1,0]])
        img = cv2.filter2D(img, -1, kernel)

    gray_val = st.slider("Grayscale Intensity", 0, 100, 0)
    if gray_val > 0:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        img = cv2.addWeighted(img, 1 - gray_val/100, gray, gray_val/100, 0)

    warm_val = st.slider("Warm Effect", 0, 50, 0)
    if warm_val > 0:
        img = cv2.add(img, np.array([0, warm_val//2, warm_val], dtype="uint8"))

# Advanced Effects
with st.sidebar.expander("Advanced Effects"):

    if st.button("Edge Detection"):
        edges = cv2.Canny(img,100,200)
        img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    if st.button("Cartoon"):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray,5)
        edges = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,9,9)
        color = cv2.bilateralFilter(img,9,250,250)
        img = cv2.bitwise_and(color, color, mask=edges)

    if st.button("Sketch"):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv,(21,21),0)
        inv_blur = 255 - blur
        sketch = cv2.divide(gray, inv_blur, scale=256.0)
        img = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

# Portrait mode
with st.sidebar.expander("Portrait Mode (AI)"):
    if st.button("Apply Background Blur"):
        img = face_blur(img)

# Transform
with st.sidebar.expander("Transform"):

    if st.button("Rotate 90°"):
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    if st.button("Flip Horizontal"):
        img = cv2.flip(img,1)

    if st.button("Flip Vertical"):
        img = cv2.flip(img,0)

# Zoom
with st.sidebar.expander("Zoom"):
    zoom = st.slider("Zoom Center",1,3,1)

    if zoom > 1:
        h_, w_ = img.shape[:2]
        cx, cy = w_//2, h_//2
        nw, nh = w_//zoom, h_//zoom
        img = img[cy-nh//2:cy+nh//2, cx-nw//2:cx+nw//2]
        img = cv2.resize(img,(w_,h_))

# Display (RGB only for UI)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Image")
    st.image(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))

with col2:
    st.subheader("Edited Image")
    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

# Save edited state
st.session_state.edited = img.copy()

# ✅ DOWNLOAD WITHOUT COLOR CHANGE (BGR 그대로)
_, buffer = cv2.imencode(".jpg", img)

st.download_button(
    "⬇️ Download Image (JPG)",
    data=buffer.tobytes(),
    file_name="edited.jpg",
    mime="image/jpeg"
)
