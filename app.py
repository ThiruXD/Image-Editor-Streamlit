import streamlit as st
import numpy as np
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Page Configuration
st.set_page_config(page_title="Photo Editor", layout="wide")
st.title("📸 AI Photo Editor")
st.sidebar.title("Controls")

# 1. FILE UPLOADER WIDGET
uploaded_file = st.sidebar.file_uploader(
    "📤 Upload an image", 
    type=["jpg", "jpeg", "png", "webp"]
)

# Initialize global working image states
if uploaded_file is not None:
    # Read the user's uploaded file natively
    initial_img = Image.open(uploaded_file).convert("RGB")
else:
    # Friendly fallback banner informing user to add a file
    initial_img = Image.new("RGB", (800, 500), color=(135, 206, 235))
    st.info("💡 Please upload an image using the sidebar file browser to begin editing!")

# 2. SESSION STATE MANAGEMENT
# Detect if a completely new image file was dropped in to reset the working cache
if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file:
    st.session_state.last_uploaded = uploaded_file
    st.session_state.original = initial_img.copy()
    st.session_state.edited = initial_img.copy()

# Master working image variables
img = st.session_state.edited.copy()
original = st.session_state.original.copy()

# Reset Button Execution
if st.sidebar.button("🔄 Reset to Original"):
    st.session_state.edited = st.session_state.original.copy()
    st.rerun()

# 3. IMAGE ADJUSTMENTS PANEL
with st.sidebar.expander("Adjustments"):
    # Pre-populate dimensions based on active configuration specs
    w = st.slider("Width", 100, 2000, img.size[0])
    h = st.slider("Height", 100, 2000, img.size[1])
    b = st.slider("Brightness", 0.1, 3.0, 1.0)  # Pillow scale factor: 1.0 is neutral
    c = st.slider("Contrast", 0.1, 3.0, 1.0)

# Process base modifications
if img.size != (w, h):
    img = img.resize((w, h), Image.Resampling.LANCZOS)
img = ImageEnhance.Brightness(img).enhance(b)
img = ImageEnhance.Contrast(img).enhance(c)

# 4. FILTERS (SLIDERS) PANEL
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
        warm_tint = Image.new("RGB", img.size, (255, 125, 0))
        img = Image.blend(img, warm_tint, (warm_val / 300.0))

# 5. ADVANCED EFFECTS PANEL
with st.sidebar.expander("Advanced Effects"):

    if st.button("Edge Detection"):
        img = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")

    if st.button("Cartoon"):
        edges = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")
        posterized = ImageOps.posterize(img, 3)
        img = Image.blend(posterized, edges, 0.2)

    if st.button("Sketch"):
        img = ImageOps.grayscale(img).filter(ImageFilter.CONTOUR).convert("RGB")

# 6. PORTRAIT MODE PANEL
with st.sidebar.expander("Portrait Mode (AI alternative)"):
    if st.button("Apply Background Blur"):
        # Uniform artistic bokeh emulation fallback style for server execution
        img = img.filter(ImageFilter.GaussianBlur(radius=12))

# 7. TRANSFORM PANEL
with st.sidebar.expander("Transform"):

    if st.button("Rotate 90°"):
        img = img.rotate(-90, expand=True)

    if st.button("Flip Horizontal"):
        img = ImageOps.mirror(img)

    if st.button("Flip Vertical"):
        img = ImageOps.flip(img)

# 8. ZOOM PANEL
with st.sidebar.expander("Zoom"):
    zoom = st.slider("Zoom Center", 1, 3, 1)

    if zoom > 1:
        w_, h_ = img.size
        cx, cy = w_ // 2, h_ // 2
        nw, nh = w_ // zoom, h_ // zoom
        img = img.crop((cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2))
        img = img.resize((w_, h_), Image.Resampling.LANCZOS)

# 9. DISPLAY RENDER INTERFACE
col1, col2 = st.columns(2)

with col1:
    st.subheader("Original Image")
    st.image(original, use_container_width=True)

with col2:
    st.subheader("Edited Image")
    st.image(img, use_container_width=True)

# Commit changes into browser memory tracking variables
st.session_state.edited = img.copy()

# 10. NATIVE BUFFER DOWNLOAD SYSTEM
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=95)

st.download_button(
    label="⬇️ Download Image (JPG)",
    data=buffer.getvalue(),
    file_name="edited.jpg",
    mime="image/jpeg"
)
