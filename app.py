import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

st.set_page_config(page_title="Photo Editor", layout="wide")

st.title("📸 AI Photo Editor")

st.sidebar.title("Controls")

# Load initial image using Pillow natively
try:
    # Fallback to demo image or your hardcoded path
    initial_img = Image.open(r"C:\Users\gayat\Downloads\kitten.webp")
except Exception:
    # If the local local path fails on cloud, create a dummy placeholder image
    initial_img = Image.new("RGB", (600, 400), color=(135, 206, 235))

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

# Portrait Face Blur alternative via Pillow
def apply_portrait_blur(pil_img):
    # Standard fallback blur since cascade XML is missing natively
    return pil_img.filter(ImageFilter.GaussianBlur(radius=15))

# Adjustments
with st.sidebar.expander("Adjustments"):
    w = st.slider("Width", 100, 1000, img.size[0])
    h = st.slider("Height", 100, 1000, img.size[1])
    b = st.slider("Brightness", 0.5, 2.0, 1.0)  # Pillow uses factor scaling (1.0 is default)
    c = st.slider("Contrast", 0.5, 3.0, 1.0)

# Apply basic size, brightness, and contrast transforms
img = img.resize((w, h))
img = ImageEnhance.Brightness(img).enhance(b)
img = ImageEnhance.Contrast(img).enhance(c)

# Filters
with st.sidebar.expander("Filters (Sliders)"):

    blur_val = st.slider("Blur", 0, 25, 0)
    if blur_val > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_val))

    sharp_val = st.slider("Sharpen", 0, 5, 0)
    if sharp_val > 0:
        for _ in range(sharp_val):
            img = img.filter(ImageFilter.SHARPEN)

    gray_val = st.slider("Grayscale Intensity", 0, 100, 0)
    if gray_val > 0:
        gray_img = ImageOps.grayscale(img).convert("RGB")
        img = Image.blend(img, gray_img, gray_val / 100.0)

    warm_val = st.slider("Warm Effect", 0, 50, 0)
    if warm_val > 0:
        # Blend with an orange/red tint layer to emulate warmth
        warm_tint = Image.new("RGB", img.size, (255, 125, 0))
        img = Image.blend(img, warm_tint, (warm_val / 300.0))

# Advanced Effects
with st.sidebar.expander("Advanced Effects"):

    if st.button("Edge Detection"):
        img = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")

    if st.button("Cartoon"):
        # Emulate cartoon via posterization and edge blending
        edges = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")
        posterized = ImageOps.posterize(img, 3)
        img = Image.blend(posterized, edges, 0.2)

    if st.button("Sketch"):
        # True grayscale edge sketch conversion
        img = ImageOps.grayscale(img).filter(ImageFilter.CONTOUR).convert("RGB")

# Portrait mode
with st.sidebar.expander("Portrait Mode (AI)"):
    if st.button("Apply Background Blur"):
        img = apply_portrait_blur(img)

# Transform
with st.sidebar.expander("Transform"):

    if st.button("Rotate 90°"):
        img = img.rotate(-90, expand=True)

    if st.button("Flip Horizontal"):
        img = ImageOps.mirror(img)

    if st.button("Flip Vertical"):
        img = ImageOps.flip(img)

# Zoom
with st.sidebar.expander("Zoom"):
    zoom = st.slider("Zoom Center", 1, 3, 1)

    if zoom > 1:
        w_, h_ = img.size
        cx, cy = w_ // 2, h_ // 2
        nw, nh = w_ // zoom, h_ // zoom
        img = img.crop((cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2))
        img = img.resize((w_, h_))

# Display Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Image")
    st.image(original)

with col2:
    st.subheader("Edited Image")
    st.image(img)

# Save edited state
st.session_state.edited = img.copy()

# Natively download using Pillow stream buffers
import io
buffer = io.BytesIO()
img.save(buffer, format="JPEG")

st.download_button(
    "⬇️ Download Image (JPG)",
    data=buffer.getvalue(),
    file_name="edited.jpg",
    mime="image/jpeg"
)
