import os
import streamlit as st
from core.subtitle_extractor import VideoSubtitleExtractor
from utils import SUPPORTED_LANGUAGES, check_gpu_availability
import time

def main():
    st.title("🎬 Video Hardcoded Subtitle Extractor")

    # Check GPU availability
    is_gpu_available = check_gpu_availability()
    st.sidebar.info(f"GPU Support: {'Available ✅' if is_gpu_available else 'Not Available ❌.'}")

    # Use environment variables or default paths
    VIDEO_INPUT_DIR = os.environ.get('VIDEO_INPUT_DIR', 'C:/video')

    # Ensure directories exist
    os.makedirs(VIDEO_INPUT_DIR, exist_ok=True)

    # Use session state to persist subtitles between button clicks
    if 'subtitles' not in st.session_state:
        st.session_state.subtitles = None
    if 'video_path' not in st.session_state:
        st.session_state.video_path = ''

    # Sidebar configuration
    st.sidebar.header("Extraction Settings")
    frame_rate = st.sidebar.slider(
        "Frame Processing Rate", 
        min_value=1, 
        max_value=30, 
        value=5,
        help="Higher rates capture more frames but increase processing time"
    )
    
    confidence_threshold = st.sidebar.slider(
        "Subtitle Confidence Threshold", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.7,
        help="Lower values include more potential subtitles, higher values are more selective"
    )

    # Language selection
    languages =  {v: k for k, v in SUPPORTED_LANGUAGES.items()}
    selected_lang = st.sidebar.selectbox(
        "Select Language",
        options=list(languages.keys()),
        index=0,
        help="Select the language of subtitles in the video"
    )
    
    # Get language code
    lang_code = languages[selected_lang]

    # List available videos in the input directory
    available_videos = [f for f in os.listdir(VIDEO_INPUT_DIR) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
    
    # Video selection dropdown
    selected_video = st.selectbox(
        "Select a Video", 
        [""] + available_videos,
        help="Select a video from the mounted videos directory"
    )

    # Determine the actual video path
    if selected_video:
        video_path = os.path.join(VIDEO_INPUT_DIR, selected_video)
    else:
        video_path = ""

    # Process button
    process_button = st.button("Process Subtitles")

    if process_button:
        if not video_path:
            st.warning("Please select a video or enter a video path.")
            return
        
        if not os.path.isfile(video_path):
            st.warning(f"The specified path '{video_path}' is not a valid file.")
            return
        
        # Create extractor with specified max concurrent frames
        extractor = VideoSubtitleExtractor(lang=lang_code, use_gpu=is_gpu_available)

        # Get video metadata
        metadata = extractor.get_video_metadata(video_path)
        
        # Display video metadata
        if metadata:
            st.sidebar.subheader("Video Details")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.sidebar.metric("Duration", f"{metadata['duration']:.2f} sec")
                st.sidebar.metric("FPS", f"{metadata['fps']:.2f}")
            with col2:
                st.sidebar.metric("Resolution", f"{metadata['width']}x{metadata['height']}")

        # Start timer
        start_time = time.time()

        # Create a progress bar
        progress_bar = st.progress(0)

        # Extract subtitles
        with st.spinner(f'Extracting subtitles from {os.path.basename(video_path)}...'):
            subtitles = extractor.extract_subtitles(
                video_path, 
                frame_rate=frame_rate,
                confidence_threshold=confidence_threshold,
                progress_bar=progress_bar  # Pass the progress bar
            )

        # Store subtitles and video path in session state
        st.session_state.subtitles = subtitles
        st.session_state.video_path = video_path

        # End timer
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Display processing time in sidebar
        st.sidebar.subheader("Processing Time")
        st.sidebar.text(f"Time taken: {processing_time:.2f} seconds")

    # Check if subtitles exist in session state
    if st.session_state.subtitles:
        # Display results
        if len(st.session_state.subtitles) > 10:
            st.subheader("🔍 Extracted First 10 Subtitles")
            subtitles = st.session_state.subtitles[:10] # Select first 10 if too many extracted subtitle
        else:
            st.subheader("🔍 Extracted Subtitles")
            subtitles = st.session_state.subtitles

        for i, subtitle in enumerate(subtitles, 1):
            # Display subtitle details
            st.text(f"{i}. {subtitle['start_time']} --> {subtitle['end_time']}")
            # Split and display each line of the subtitle
            for line in subtitle['text'].split("\n"):
                st.text(line)
            st.text("---")
        
        srt_content = ""
        for i, subtitle in enumerate(st.session_state.subtitles, 1):
            # Keep newlines for SRT format
            srt_content += f"{i}\n{subtitle['start_time']} --> {subtitle['end_time']}\n{subtitle['text']}\n\n"
        
        # Save button
        save_button = st.button("💾 Save Subtitles")
        
        if save_button:
            # Generate output filename
            output_filename = f"{os.path.splitext(os.path.basename(st.session_state.video_path))[0]}.srt"
            output_path = os.path.join(VIDEO_INPUT_DIR, output_filename)
            
            # Save to file in mounted directory
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            # Show success message
            st.success(f"Subtitles saved to {output_path}")

if __name__ == "__main__":
    main()