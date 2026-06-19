# By ThiruXD

import streamlit as st
import numpy as np
import io
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Import Cloudinary libraries safely
try:
    import cloudinary
    import cloudinary.uploader
    from cloudinary.utils import cloudinary_url
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

# Page Configuration
st.set_page_config(page_title="AI Photo Editor & Compressor", layout="wide")
st.title("📸 AI Photo Editor, Upscaler & Compressor")
st.sidebar.title("Controls")

# Initialize Cloudinary Configuration from Secrets if available
if CLOUDINARY_AVAILABLE and "cloudinary" in st.secrets:
    cloudinary.config(
        cloud_name = st.secrets["cloudinary"]["cloud_name"],
        api_key = st.secrets["cloudinary"]["api_key"],
        api_secret = st.secrets["cloudinary"]["api_secret"],
        secure = True
    )
    st.sidebar.success("☁️ Cloudinary API Connected!")
else:
    st.sidebar.warning("⚠️ Using Local Upscaler (Cloudinary Secrets Missing)")

# 1. FILE UPLOADER WIDGET
uploaded_file = st.sidebar.file_uploader(
    "📤 Upload an image", 
    type=["jpg", "jpeg", "png", "webp"]
)

# Initialize global working image states
if uploaded_file is not None:
    initial_img = Image.open(uploaded_file).convert("RGB")
else:
    initial_img = Image.new("RGB", (800, 500), color=(135, 206, 235))
    st.info("💡 Please upload an image using the sidebar file browser to begin editing!")

# 2. SESSION STATE MANAGEMENT
if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file:
    st.session_state.last_uploaded = uploaded_file
    st.session_state.original = initial_img.copy()
    st.session_state.transformed_base = initial_img.copy()

# Reset Button Execution
if st.sidebar.button("🔄 Reset to Original"):
    st.session_state.transformed_base = st.session_state.original.copy()
    st.rerun()

# Base working copies
img = st.session_state.transformed_base.copy()
original = st.session_state.original.copy()

# 3. FILE SIZE OPTIMIZER PANEL (NEW FEATURE)
with st.sidebar.expander("💾 File Size Compressor", expanded=True):
    st.markdown("### Compress to target size")
    target_size_kb = st.number_input("Target File Size (KB):", min_value=10, max_value=10000, value=200, step=50)
    enable_compressor = st.checkbox("Enable Intelligent Compression", value=True)

# 4. HIGH RESOLUTION UPSCALER PANEL
with st.sidebar.expander("🚀 Super Resolution Upscaler"):
    st.write(f"Current Resolution: **{img.width} x {img.height}** pixels")
    scale_factor = st.radio("Select Upscale Multiplier:", [2, 3, 4], index=0, horizontal=True)
    
    if st.button("✨ Apply High-Res Upscale"):
        new_w = img.width * scale_factor
        new_h = img.height * scale_factor
        
        if CLOUDINARY_AVAILABLE and "cloudinary" in st.secrets and uploaded_file is not None:
            with st.spinner("☁️ Uploading & Upscaling on Cloudinary Servers..."):
                try:
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=95)
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    upload_result = cloudinary.uploader.upload(img_byte_arr)
                    public_id = upload_result['public_id']
                    
                    cloud_url, _ = cloudinary_url(
                        public_id, 
                        width=new_w, 
                        height=new_h, 
                        crop="scale",
                        quality="auto:best"
                    )
                    
                    import requests
                    response = requests.get(cloud_url)
                    st.session_state.transformed_base = Image.open(io.BytesIO(response.content)).convert("RGB")
                    st.toast(f"Cloudinary upscaled successfully to {new_w}x{new_h}!", icon="☁️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Cloudinary error: {e}. Falling back to local upscaler.")
                    
        upscaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        st.session_state.transformed_base = sharpened
        st.toast(f"Locally upscaled {scale_factor}x to {new_w}x{new_h}!", icon="🎯")
        st.rerun()

# 5. TRANSFORM PANEL
with st.sidebar.expander("Transform"):
    if st.button("Rotate 90°"):
        st.session_state.transformed_base = st.session_state.transformed_base.rotate(-90, expand=True)
        st.rerun()
    if st.button("Flip Horizontal"):
        st.session_state.transformed_base = ImageOps.mirror(st.session_state.transformed_base)
        st.rerun()
    if st.button("Flip Vertical"):
        st.session_state.transformed_base = ImageOps.flip(st.session_state.transformed_base)
        st.rerun()

# 6. ADVANCED EFFECTS PANEL
with st.sidebar.expander("Advanced Effects & Portrait"):
    if st.button("Edge Detection"):
        st.session_state.transformed_base = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")
        st.rerun()
    if st.button("Cartoon"):
        edges = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES).convert("RGB")
        posterized = ImageOps.posterize(img, 3)
        st.session_state.transformed_base = Image.blend(posterized, edges, 0.2)
        st.rerun()
    if st.button("Sketch"):
        st.session_state.transformed_base = ImageOps.grayscale(img).filter(ImageFilter.CONTOUR).convert("RGB")
        st.rerun()
    if st.button("Apply Background Blur"):
        st.session_state.transformed_base = img.filter(ImageFilter.GaussianBlur(radius=12))
        st.rerun()

# 7. IMAGE ADJUSTMENTS PANEL
with st.sidebar.expander("Adjustments"):
    w = st.slider("Width Override", 100, 4000, img.size[0])
    h = st.slider("Height Override", 100, 4000, img.size[1])
    b = st.slider("Brightness", 0.1, 3.0, 1.0)
    c = st.slider("Contrast", 0.1, 3.0, 1.0)

# 8. FILTERS PANEL
with st.sidebar.expander("Filters (Sliders)"):
    blur_val = st.slider("Blur", 0, 25, 0)
    sharp_val = st.slider("Sharpen Intensity", 0, 5, 0)
    gray_val = st.slider("Grayscale Intensity", 0, 100, 0)
    warm_val = st.slider("Warm Effect", 0, 50, 0)

# 9. ZOOM PANEL
with st.sidebar.expander("Zoom"):
    zoom = st.slider("Zoom Center", 1, 3, 1)

# --- APPLY SLIDERS SEQUENTIALLY ON THE CLEAN BASE ---
if img.size != (w, h):
    img = img.resize((w, h), Image.Resampling.LANCZOS)

img = ImageEnhance.Brightness(img).enhance(b)
img = ImageEnhance.Contrast(img).enhance(c)

if blur_val > 0:
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_val))

if sharp_val > 0:
    for _ in range(sharp_val):
        img = img.filter(ImageFilter.SHARPEN)

if gray_val > 0:
    gray_img = ImageOps.grayscale(img).convert("RGB")
    img = Image.blend(img, gray_img, gray_val / 100.0)

if warm_val > 0:
    warm_tint = Image.new("RGB", img.size, (255, 125, 0))
    img = Image.blend(img, warm_tint, (warm_val / 300.0))

if zoom > 1:
    w_, h_ = img.size
    cx, cy = w_ // 2, h_ // 2
    nw, nh = w_ // zoom, h_ // zoom
    img = img.crop((cx - nw // 2, cy - nh // 2, cx + nw // 2, cy + nh // 2))
    img = img.resize((w_, h_), Image.Resampling.LANCZOS)

# 10. INTELLIGENT COMPRESSION ENGINE LOOP
buffer = io.BytesIO()

if enable_compressor:
    # Target size converted to bytes
    target_bytes = target_size_kb * 1024
    quality = 95
    
    # Loop downwards from high quality to find the target footprint size
    while quality > 10:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        if len(buffer.getvalue()) <= target_bytes:
            break
        quality -= 5  # Step down quality if file size is still too large
        
    final_size_kb = len(buffer.getvalue()) / 1024
    st.sidebar.info(f"⚡ Compressed to **{final_size_kb:.1f} KB** (Quality: {quality}%)")
else:
    img.save(buffer, format="JPEG", quality=95)

# 11. DISPLAY RENDER INTERFACE
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Original ({original.width}x{original.height})")
    st.image(original, use_container_width=True)

with col2:
    st.subheader(f"Edited / Compressed ({img.width}x{img.height})")
    st.image(img, use_container_width=True)

# By ThiruXD
st.download_button(
    label=f"⬇️ Download Optimized Image ({len(buffer.getvalue())/1024:.1f} KB)",
    data=buffer.getvalue(),
    file_name="compressed_image.jpg",
    mime="image/jpeg"
)
