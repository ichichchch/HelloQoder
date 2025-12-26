"""
BatchClip Frontend - Streamlit Application
Minimalist UI for batch video uploads and viewing results
"""

import streamlit as st
import requests
from pathlib import Path
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="BatchClip - Video Processing",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


def api_request(method: str, endpoint: str, **kwargs):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None


def format_size(size_bytes: int) -> str:
    """Format file size to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: float) -> str:
    """Format duration to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


# Sidebar navigation
st.sidebar.title("🎬 BatchClip")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📤 Upload", "📁 Assets", "⚙️ Processing", "✂️ Editor", "📊 Logs"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")

# Health check
try:
    health = requests.get("http://localhost:8000/health", timeout=2).json()
    st.sidebar.success("✅ Backend Online")
except:
    st.sidebar.error("❌ Backend Offline")


# ===== UPLOAD PAGE =====
if page == "📤 Upload":
    st.title("📤 Video Upload")
    st.markdown("Upload video files for processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Files")
        
        uploaded_files = st.file_uploader(
            "Select video files",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            accept_multiple_files=True
        )
        
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., interview, raw, project-a"
        )
        
        if st.button("🚀 Upload", type="primary", disabled=not uploaded_files):
            with st.spinner("Uploading files..."):
                for file in uploaded_files:
                    files = {"file": (file.name, file.getvalue(), file.type)}
                    data = {"tags": tags_input} if tags_input else {}
                    
                    result = api_request("POST", "/upload/single", files=files, data=data)
                    
                    if result and result.get("success"):
                        st.success(f"✅ Uploaded: {file.name}")
                        st.json(result.get("metadata", {}))
                    else:
                        st.error(f"❌ Failed to upload: {file.name}")
    
    with col2:
        st.subheader("Recent Uploads")
        
        result = api_request("GET", "/upload/list")
        if result:
            uploads = result.get("uploads", [])
            if uploads:
                for upload in uploads[:5]:
                    with st.container():
                        st.markdown(f"**{upload.get('original_filename', 'Unknown')}**")
                        st.caption(f"ID: {upload.get('asset_id', '')[:8]}...")
                        st.caption(f"Status: {upload.get('status', 'unknown')}")
                        st.markdown("---")
            else:
                st.info("No uploads yet")


# ===== ASSETS PAGE =====
elif page == "📁 Assets":
    st.title("📁 Media Assets")
    st.markdown("Browse and manage your video assets")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "uploaded", "preprocessed", "completed"]
        )
    
    # Fetch assets
    endpoint = "/assets/" if status_filter == "All" else f"/assets/?status={status_filter}"
    result = api_request("GET", endpoint)
    
    if result:
        assets = result.get("assets", [])
        st.metric("Total Assets", len(assets))
        
        if assets:
            for asset in assets:
                with st.expander(f"📹 {asset.get('original_filename', 'Unknown')} - {asset.get('asset_id', '')[:8]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Metadata**")
                        st.write(f"- Status: `{asset.get('status', 'unknown')}`")
                        st.write(f"- Size: {format_size(asset.get('size_bytes', 0))}")
                        if asset.get('duration'):
                            st.write(f"- Duration: {format_duration(asset.get('duration', 0))}")
                        if asset.get('resolution'):
                            st.write(f"- Resolution: {asset.get('resolution')}")
                    
                    with col2:
                        st.markdown("**Tags**")
                        tags = asset.get('tags', [])
                        if tags:
                            st.write(", ".join([f"`{t}`" for t in tags]))
                        else:
                            st.write("No tags")
                    
                    # Actions
                    st.markdown("**Actions**")
                    action_cols = st.columns(4)
                    
                    asset_id = asset.get('asset_id')
                    
                    with action_cols[0]:
                        if st.button("🔄 Preprocess", key=f"preprocess_{asset_id}"):
                            with st.spinner("Processing..."):
                                result = api_request(
                                    "POST",
                                    f"/processing/{asset_id}/preprocess",
                                    json={"generate_proxy": True, "split": False}
                                )
                                if result:
                                    st.success("Preprocessing complete!")
                                    st.json(result)
                    
                    with action_cols[1]:
                        if st.button("📊 Get Logs", key=f"logs_{asset_id}"):
                            logs = api_request("GET", f"/assets/{asset_id}/logs")
                            if logs:
                                st.json(logs)
                    
                    with action_cols[2]:
                        if st.button("🗑️ Delete", key=f"delete_{asset_id}"):
                            result = api_request("DELETE", f"/assets/{asset_id}")
                            if result:
                                st.success("Asset deleted!")
                                st.rerun()
        else:
            st.info("No assets found")


# ===== PROCESSING PAGE =====
elif page == "⚙️ Processing":
    st.title("⚙️ Video Processing")
    st.markdown("Preprocess videos for editing")
    
    # Get available assets
    result = api_request("GET", "/assets/")
    assets = result.get("assets", []) if result else []
    
    if not assets:
        st.warning("No assets available. Please upload videos first.")
    else:
        # Asset selection
        asset_options = {
            f"{a.get('original_filename', 'Unknown')} ({a.get('asset_id', '')[:8]})": a.get('asset_id')
            for a in assets
        }
        
        selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
        asset_id = asset_options.get(selected_asset)
        
        st.markdown("---")
        
        # Processing options
        st.subheader("Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            generate_proxy = st.checkbox("Generate Proxy", value=True)
            proxy_resolution = st.slider(
                "Proxy Resolution",
                min_value=360,
                max_value=1080,
                value=720,
                step=90,
                disabled=not generate_proxy
            )
        
        with col2:
            split_video = st.checkbox("Split Video", value=False)
            segment_duration = st.slider(
                "Segment Duration (seconds)",
                min_value=10,
                max_value=300,
                value=60,
                step=10,
                disabled=not split_video
            )
        
        if st.button("🚀 Start Processing", type="primary"):
            with st.spinner("Processing video..."):
                result = api_request(
                    "POST",
                    f"/processing/{asset_id}/preprocess",
                    json={
                        "generate_proxy": generate_proxy,
                        "split": split_video,
                        "proxy_resolution": proxy_resolution if generate_proxy else None,
                        "segment_duration": segment_duration if split_video else None
                    }
                )
                
                if result:
                    st.success("Processing complete!")
                    st.json(result)
        
        # Quick actions
        st.markdown("---")
        st.subheader("Quick Actions")
        
        quick_cols = st.columns(3)
        
        with quick_cols[0]:
            if st.button("📊 Extract Metadata"):
                with st.spinner("Extracting..."):
                    result = api_request("POST", f"/processing/{asset_id}/metadata")
                    if result:
                        st.json(result)
        
        with quick_cols[1]:
            if st.button("🎞️ Generate Proxy Only"):
                with st.spinner("Generating..."):
                    result = api_request("POST", f"/processing/{asset_id}/proxy")
                    if result:
                        st.json(result)
        
        with quick_cols[2]:
            if st.button("✂️ Split Video Only"):
                with st.spinner("Splitting..."):
                    result = api_request("POST", f"/processing/{asset_id}/split")
                    if result:
                        st.json(result)


# ===== EDITOR PAGE =====
elif page == "✂️ Editor":
    st.title("✂️ Video Editor")
    st.markdown("Cut and edit videos using rules")
    
    # Get available assets
    result = api_request("GET", "/assets/")
    assets = result.get("assets", []) if result else []
    
    if not assets:
        st.warning("No assets available. Please upload videos first.")
    else:
        # Asset selection
        asset_options = {
            f"{a.get('original_filename', 'Unknown')} ({a.get('asset_id', '')[:8]})": a
            for a in assets
        }
        
        selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
        asset = asset_options.get(selected_asset, {})
        asset_id = asset.get('asset_id')
        
        # Show asset info
        duration = asset.get('duration', 0)
        if duration:
            st.info(f"Video Duration: {format_duration(duration)}")
        
        st.markdown("---")
        
        # Edit mode tabs
        edit_mode = st.tabs(["🎯 Extract Clip", "✂️ Rough Cut", "🤖 Auto Rough Cut"])
        
        # Extract Clip
        with edit_mode[0]:
            st.subheader("Extract Clip")
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.number_input(
                    "Start Time (seconds)",
                    min_value=0.0,
                    max_value=float(duration) if duration else 3600.0,
                    value=0.0,
                    step=0.5
                )
            
            with col2:
                end_time = st.number_input(
                    "End Time (seconds)",
                    min_value=0.0,
                    max_value=float(duration) if duration else 3600.0,
                    value=min(10.0, float(duration) if duration else 10.0),
                    step=0.5
                )
            
            output_name = st.text_input("Output Filename (optional)")
            
            if st.button("🎬 Extract Clip", type="primary"):
                if end_time <= start_time:
                    st.error("End time must be greater than start time")
                else:
                    with st.spinner("Extracting clip..."):
                        result = api_request(
                            "POST",
                            f"/editor/{asset_id}/clip",
                            json={
                                "start_time": start_time,
                                "end_time": end_time,
                                "output_name": output_name if output_name else None
                            }
                        )
                        if result:
                            st.success("Clip extracted!")
                            st.json(result)
        
        # Rough Cut
        with edit_mode[1]:
            st.subheader("Rough Cut")
            st.markdown("Define multiple segments to keep and concatenate")
            
            # Dynamic segment inputs
            if 'segments' not in st.session_state:
                st.session_state.segments = [{"start": 0.0, "end": 10.0}]
            
            for i, seg in enumerate(st.session_state.segments):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.session_state.segments[i]["start"] = st.number_input(
                        f"Segment {i+1} Start",
                        min_value=0.0,
                        value=seg["start"],
                        step=0.5,
                        key=f"seg_start_{i}"
                    )
                with col2:
                    st.session_state.segments[i]["end"] = st.number_input(
                        f"Segment {i+1} End",
                        min_value=0.0,
                        value=seg["end"],
                        step=0.5,
                        key=f"seg_end_{i}"
                    )
                with col3:
                    if st.button("🗑️", key=f"del_seg_{i}"):
                        st.session_state.segments.pop(i)
                        st.rerun()
            
            if st.button("➕ Add Segment"):
                last_end = st.session_state.segments[-1]["end"] if st.session_state.segments else 0
                st.session_state.segments.append({"start": last_end, "end": last_end + 10})
                st.rerun()
            
            if st.button("🎬 Create Rough Cut", type="primary"):
                cuts = [[s["start"], s["end"]] for s in st.session_state.segments]
                with st.spinner("Creating rough cut..."):
                    result = api_request(
                        "POST",
                        f"/editor/{asset_id}/rough-cut",
                        json={"cuts": cuts}
                    )
                    if result:
                        st.success("Rough cut created!")
                        st.json(result)
        
        # Auto Rough Cut
        with edit_mode[2]:
            st.subheader("Auto Rough Cut")
            st.markdown("Automatically keep intro and outro")
            
            col1, col2 = st.columns(2)
            
            with col1:
                intro_seconds = st.number_input(
                    "Keep Intro (seconds)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5
                )
            
            with col2:
                outro_seconds = st.number_input(
                    "Keep Outro (seconds)",
                    min_value=0.0,
                    value=5.0,
                    step=0.5
                )
            
            if st.button("🤖 Auto Rough Cut", type="primary"):
                with st.spinner("Creating auto rough cut..."):
                    result = api_request(
                        "POST",
                        f"/editor/{asset_id}/auto-rough-cut",
                        json={
                            "keep_intro_seconds": intro_seconds,
                            "keep_outro_seconds": outro_seconds
                        }
                    )
                    if result:
                        st.success("Auto rough cut created!")
                        st.json(result)


# ===== LOGS PAGE =====
elif page == "📊 Logs":
    st.title("📊 Processing Logs")
    st.markdown("View processing history and logs")
    
    # Get available assets
    result = api_request("GET", "/assets/")
    assets = result.get("assets", []) if result else []
    
    if not assets:
        st.warning("No assets available.")
    else:
        # Asset selection
        asset_options = {
            f"{a.get('original_filename', 'Unknown')} ({a.get('asset_id', '')[:8]})": a.get('asset_id')
            for a in assets
        }
        
        selected_asset = st.selectbox("Select Asset", list(asset_options.keys()))
        asset_id = asset_options.get(selected_asset)
        
        if st.button("🔄 Refresh Logs"):
            st.rerun()
        
        # Fetch logs
        logs_result = api_request("GET", f"/assets/{asset_id}/logs")
        
        if logs_result:
            logs = logs_result.get("logs", [])
            
            if logs:
                st.metric("Total Log Entries", len(logs))
                
                for log in reversed(logs):  # Show newest first
                    event = log.get("event", "unknown")
                    timestamp = log.get("timestamp", "")
                    
                    # Color code events
                    if "complete" in event:
                        icon = "✅"
                    elif "failed" in event:
                        icon = "❌"
                    elif "start" in event:
                        icon = "🔄"
                    else:
                        icon = "📝"
                    
                    with st.expander(f"{icon} {event} - {timestamp}"):
                        st.json(log)
            else:
                st.info("No logs available for this asset")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("BatchClip v0.1.0")
st.sidebar.markdown("Powered by FFmpeg")
