import streamlit as st
import os
from subtitle_extractor import SubtitleExtractor

def main():
    st.title("Video Subtitle Extractor")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    frame_rate = st.sidebar.slider("Frame Processing Rate", 1, 30, 5)

    # File uploader
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov'])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getvalue())

        # Extract subtitles
        extractor = SubtitleExtractor()
        
        try:
            with st.spinner('Extracting subtitles...'):
                subtitles = extractor.extract_subtitles("temp_video.mp4", frame_rate)

            # Display results
            st.subheader("Extracted Subtitles")
            if subtitles:
                srt_content = ""
                for i, subtitle in enumerate(subtitles, 1):
                    # Display in both formats
                    st.text(f"{i}. {subtitle['start_time']} --> {subtitle['end_time']}")
                    st.text(subtitle['text'])
                    st.text("---")
                    
                    # Prepare SRT format
                    srt_content += f"{i}\n{subtitle['start_time']} --> {subtitle['end_time']}\n{subtitle['text']}\n\n"
                
                # Option to save subtitles
                if st.button("Save Subtitles"):
                    # Save as .srt file
                    with open("extracted_subtitles.srt", "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    st.success("Subtitles saved to extracted_subtitles.srt")
            else:
                st.warning("No subtitles found in the video.")

        finally:
            # Ensure cleanup of temporary files and resources
            if 'extractor' in locals():
                extractor.cleanup()
            # Remove the temporary video file
            os.remove("temp_video.mp4")

if __name__ == "__main__":
    main()