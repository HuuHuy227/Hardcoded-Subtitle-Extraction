import os
import tempfile
import subprocess
import cv2
import numpy as np
from typing import List, Optional, Generator

class VideoFrameExtractor:
    def __init__(self, max_frames_in_memory: int = 100):
        """
        Initialize video frame extractor
        
        :param max_frames_in_memory: Maximum number of frames to keep in memory at once
        """
        self.max_frames_in_memory = max_frames_in_memory
        self.temp_dir = tempfile.mkdtemp(prefix='video_frames_')

    def check_ffmpeg_availability(self) -> bool:
        """
        Check if FFmpeg is available in the system
        """
        try:
            subprocess.run(['ffmpeg', '-version'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def extract_frames(self, video_path: str, frame_rate: int = 1) -> Generator[np.ndarray, None, None]:
        """
        Extract frames from video with memory-efficient generator
        
        :param video_path: Path to the input video file
        :param frame_rate: Number of frames to extract per second
        :return: Generator of frame arrays
        """
        # Use FFmpeg if available, otherwise fallback to OpenCV
        extractor = (
            self._extract_frames_with_ffmpeg 
            if self.check_ffmpeg_availability() 
            else self._extract_frames_with_opencv
        )
        
        yield from extractor(video_path, frame_rate)

    def _extract_frames_with_ffmpeg(self, video_path: str, frame_rate: int = 1) -> Generator[np.ndarray, None, None]:
        """
        Extract frames using FFmpeg
        
        :param video_path: Path to the input video file
        :param frame_rate: Number of frames to extract per second
        :return: Generator of frame arrays
        """
        try:
            # Construct output pattern for frames
            output_pattern = os.path.join(self.temp_dir, 'frame_%05d.jpg')
            
            # FFmpeg command to extract frames
            subprocess.run([
                'ffmpeg', 
                '-i', video_path, 
                '-vf', f'fps={frame_rate}', 
                '-q:v', '2', 
                output_pattern
            ], check=True)
            
            # Sort and yield frames
            frame_files = sorted([
                os.path.join(self.temp_dir, f) 
                for f in os.listdir(self.temp_dir) 
                if f.startswith('frame_') and f.endswith('.jpg')
            ])
            
            for frame_path in frame_files:
                frame = cv2.imread(frame_path)
                yield frame
                
                # Optional: remove frame file after yielding to save disk space
                os.remove(frame_path)
        
        except Exception as e:
            print(f"FFmpeg frame extraction error: {e}")

    def _extract_frames_with_opencv(self, video_path: str, frame_rate: int = 1) -> Generator[np.ndarray, None, None]:
        """
        Extract frames using OpenCV
        
        :param video_path: Path to the input video file
        :param frame_rate: Number of frames to extract per second
        :return: Generator of frame arrays
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            success, frame = cap.read()
            if not success:
                break

            if frame_count % frame_rate == 0:
                yield frame

            frame_count += 1

        cap.release()

    def get_video_metadata(self, video_path: str) -> Optional[dict]:
        """
        Get video metadata
        
        :param video_path: Path to the input video file
        :return: Dictionary with video metadata or None
        """
        try:
            cap = cv2.VideoCapture(video_path)
            return {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            }
        except Exception as e:
            print(f"Error getting video metadata: {e}")
            return None
        finally:
            cap.release() if 'cap' in locals() else None

    def cleanup(self):
        """
        Clean up temporary directory with enhanced error handling
        """
        try:
            import shutil
            import os
            
            # Print diagnostic information
            print(f"Attempting to clean up temp directory: {self.temp_dir}")
            print(f"Temp directory exists: {os.path.exists(self.temp_dir)}")
            
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("Temporary directory successfully removed")
        except PermissionError:
            print(f"Permission denied when trying to remove {self.temp_dir}")
        except FileNotFoundError:
            print(f"Temporary directory not found: {self.temp_dir}")
        except Exception as e:
            print(f"Unexpected error cleaning up temporary directory: {e}")
            print(f"Error type: {type(e).__name__}")

    def __del__(self):
        """
        Ensure cleanup when object is garbage collected
        """
        self.cleanup()