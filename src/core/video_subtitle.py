import os
import subprocess
import streamlit as st

class SubtitleVideoProcessor:
    @staticmethod
    def get_video_metadata(video_path):
        """
        Get video metadata using FFprobe.
        
        Args:
            video_path (str): Path to the video file
        
        Returns:
            dict: Video metadata including duration, width, height, codec
        """
        try:
            cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                metadata = json.loads(result.stdout)
                
                # Extract relevant video stream information
                video_stream = next((stream for stream in metadata.get('streams', []) if stream['codec_type'] == 'video'), None)
                
                if video_stream:
                    return {
                        'duration': float(metadata['format'].get('duration', 0)),
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'codec': video_stream.get('codec_name', 'unknown')
                    }
            return None
        except Exception as e:
            st.error(f"Error getting video metadata: {e}")
            return None

    @staticmethod
    def add_subtitles_to_video(video_path, srt_path, output_path):
        """
        Add subtitles to a video using FFmpeg.
        
        Args:
            video_path (str): Path to the input video
            srt_path (str): Path to the subtitle .srt file
            output_path (str): Path to save the output video with subtitles
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24'",
                '-c:a', 'copy',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                st.error(f"FFmpeg error: {result.stderr}")
                return False
        except Exception as e:
            st.error(f"Error adding subtitles: {e}")
            return False