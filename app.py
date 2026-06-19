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
st.set_page_config(page_title="AI Photo Editor & Cloudinary Upscaler", layout="wide")
st.title("📸 AI Photo Editor & High-Res Upscaler")
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

# 3. CLOUDINARY / LOCAL SUPER RESOLUTION UPSCALER PANEL
with st.sidebar.expander("🚀 Super Resolution Upscaler", expanded=True):
    st.write(f"Current Resolution: **{img.width} x {img.height}** pixels")
    
    # Cloudinary provides excellent AI structural enlargement or standard resizing
    scale_factor = st.radio("Select Upscale Multiplier:", [2, 3, 4], index=0, horizontal=True)
    
    if st.button("✨ Apply High-Res Upscale"):
        new_w = img.width * scale_factor
        new_h = img.height * scale_factor
        
        # Check if we should use Cloudinary cloud servers
        if CLOUDINARY_AVAILABLE and "cloudinary" in st.secrets and uploaded_file is not None:
            with st.spinner("☁️ Uploading & Upscaling on Cloudinary Servers..."):
                try:
                    # Convert active working image canvas to byte stream matrix for upload
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=95)
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Send image to Cloudinary storage cloud
                    upload_result = cloudinary.uploader.upload(img_byte_arr)
                    public_id = upload_result['public_id']
                    
                    # Generate an engineered URL performing a clean upscaling transformation via Cloudinary cloud pipeline
                    # 'dpr_auto' combined with explicit width scaling utilizes their high-end resizing layer
                    cloud_url, _ = cloudinary_url(
                        public_id, 
                        width=new_w, 
                        height=new_h, 
                        crop="scale",
                        quality="auto:best"
                    )
                    
                    # Fetch down-stream processed image results back into memory arrays
                    import requests
                    response = requests.get(cloud_url)
                    st.session_state.transformed_base = Image.open(io.BytesIO(response.content)).convert("RGB")
                    
                    st.toast(f"Cloudinary upscaled successfully to {new_w}x{new_h}!", icon="☁️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Cloudinary error encountered: {e}. Falling back to local upscaler.")
                    
        # Local Fallback Routine (runs if credentials are missing or cloud transaction hits a snag)
        # High-quality mathematical Lanczos smoothing stretch + Unsharp Mask crisp refinement
        upscaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        
        st.session_state.transformed_base = sharpened
        st.toast(f"Locally upscaled {scale_factor}x to {new_w}x{new_h}!", icon="🎯")
        st.rerun()

# 4. TRANSFORM PANEL (Permanent canvas structural changes)
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

# 5. ADVANCED EFFECTS PANEL (Permanent filter changes)
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

# 6. IMAGE ADJUSTMENTS PANEL (Transient Sliders - Runs dynamically on rerun)
with st.sidebar.expander("Adjustments"):
    w = st.slider("Width Override", 100, 4000, img.size[0])
    h = st.slider("Height Override", 100, 4000, img.size[1])
    b = st.slider("Brightness", 0.1, 3.0, 1.0)
    c = st.slider("Contrast", 0.1, 3.0, 1.0)

# 7. FILTERS PANEL (Transient Sliders - Runs dynamically on rerun)
with st.sidebar.expander("Filters (Sliders)"):
    blur_val = st.slider("Blur", 0, 25, 0)
    sharp_val = st.slider("Sharpen Intensity", 0, 5, 0)
    gray_val = st.slider("Grayscale Intensity", 0, 100, 0)
    warm_val = st.slider("Warm Effect", 0, 50, 0)

# 8. ZOOM PANEL (Transient Sliders - Runs dynamically on rerun)
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

# 9. DISPLAY RENDER INTERFACE
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Original ({original.width}x{original.height})")
    st.image(original, use_container_width=True)

with col2:
    st.subheader(f"Edited / Upscaled ({img.width}x{img.height})")
    st.image(img, use_container_width=True)

# 10. NATIVE BUFFER DOWNLOAD SYSTEM
buffer = io.BytesIO()
img.save(buffer, format="JPEG", quality=98)

# By ThiruXD
st.download_button(
    label="⬇️ Download High-Res Image (JPG)",
    data=buffer.getvalue(),
    file_name="edited_highres.jpg",
    mime="image/jpeg"
)
