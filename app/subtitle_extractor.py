import os
import tempfile
import subprocess
import difflib
import cv2

from text_ocr import TextOcr
from utils import init_args

class SubtitleExtractor:
    def __init__(self, max_frames_in_memory: int = 100):
        """
        Initialize SubtitleExtractor
        
        :param max_frames_in_memory: Maximum number of frames to keep in memory at once
        """
        # Initialize PaddleOCR arguments
        self.args = init_args()
        self.args.warmup = True
        
        # Initialize OCR system
        self.text_sys = TextOcr(self.args)
        
        # Track previous subtitles for quality comparison
        self.previous_subtitles = []
        
        # Temporary directory for frame management
        self.temp_dir = tempfile.mkdtemp(prefix='video_subtitles_')
        
        # Maximum frames to keep in memory
        self.max_frames_in_memory = max_frames_in_memory

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

    def extract_frames(self, video_path: str, frame_rate: int = 1):
        """
        Extract frames from video with memory-efficient approach
        
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

    def _extract_frames_with_ffmpeg(self, video_path: str, frame_rate: int = 1):
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
                
                # Remove frame file after yielding to save disk space
                os.remove(frame_path)
        
        except Exception as e:
            print(f"FFmpeg frame extraction error: {e}")

    def _extract_frames_with_opencv(self, video_path: str, frame_rate: int = 1):
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

    def get_video_metadata(self, video_path: str):
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

    def _compute_similarity(self, str1: str, str2: str) -> float:
        """
        Compute similarity between two strings
        
        :param str1: First string
        :param str2: Second string
        :return: Similarity score (0-1)
        """
        # Remove spaces and convert to lowercase for comparison
        clean_str1 = str1.replace(' ', '').lower()
        clean_str2 = str2.replace(' ', '').lower()
        
        # Use SequenceMatcher to compute similarity
        return difflib.SequenceMatcher(None, clean_str1, clean_str2).ratio()

    def _select_best_subtitle(self, subtitles: list) -> str:
        """
        Select the best subtitle based on multiple criteria
        
        :param subtitles: List of subtitle candidates with recognition results
        :return: Best subtitle
        """
        if not subtitles:
            return ""
        
        # If subtitles are tuples of (text, confidence), extract text with highest confidence
        if isinstance(subtitles[0], tuple):
            # Sort subtitles by:
            # 1. Confidence score (descending)
            # 2. Length of subtitle text (descending)
            def subtitle_score(subtitle):
                text, confidence = subtitle
                return (
                    confidence,  # Primary sorting by confidence
                    len(text.strip()),  # Secondary sorting by text length
                    -len(text.replace(' ', ''))  # Tertiary sorting to prefer more substantive text
                )
            
            # Get the best subtitle
            best_subtitle_tuple = max(subtitles, key=subtitle_score)
            return best_subtitle_tuple[0]
        
        # If subtitles are just strings, fall back to previous logic
        # Prioritize longer subtitles
        best_subtitle = max(subtitles, key=len)
        
        # Remove duplicates with high similarity
        filtered_subtitles = []
        for subtitle in subtitles:
            is_unique = all(
                self._compute_similarity(subtitle, prev) < 0.8 
                for prev in filtered_subtitles
            )
            if is_unique:
                filtered_subtitles.append(subtitle)
        
        return max(filtered_subtitles, key=len) if filtered_subtitles else best_subtitle

    def extract_subtitles(self, video_path: str, frame_rate: int = 1) -> list:
        """
        Extract subtitles from video
        
        :param video_path: Path to the video file
        :param frame_rate: Number of frames to skip between each processed frame
        :return: List of extracted subtitles with timestamps
        """
        # Get video metadata
        metadata = self.get_video_metadata(video_path)
        fps = metadata['fps'] if metadata else 1
        
        subtitles = []

        for idx, frame in enumerate(self.extract_frames(video_path, frame_rate)):
            # Process frame
            _, rec_res = self.text_sys(frame)
            
            if rec_res:
                # Extract unique, non-empty subtitles with their confidence scores
                current_frame_subtitles = [
                    (res[0], res[1])  # (text, confidence)
                    for res in rec_res 
                    if res[0].strip()  # Non-empty text
                ]
                
                # If we have subtitles in this frame
                if current_frame_subtitles:
                    # Select the best subtitle
                    best_subtitle = self._select_best_subtitle(current_frame_subtitles)
                    
                    # Calculate timestamp
                    current_time = (idx * frame_rate) / fps
                    start_time = self._format_timestamp(current_time)
                    end_time = self._format_timestamp(current_time + 3)  # Assume 3-second duration
                    
                    # Add subtitle if it's sufficiently different from previous ones
                    if best_subtitle and not self._is_too_similar(best_subtitle):
                        subtitles.append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'text': best_subtitle
                        })
                        self.previous_subtitles.append(best_subtitle)

        return subtitles

    def _is_too_similar(self, subtitle: str, similarity_threshold: float = 0.8) -> bool:
        """
        Check if the subtitle is too similar to previous subtitles
        
        :param subtitle: Current subtitle
        :param similarity_threshold: Similarity threshold
        :return: True if too similar, False otherwise
        """
        for prev_subtitle in self.previous_subtitles:
            if self._compute_similarity(subtitle, prev_subtitle) > similarity_threshold:
                return True
        return False

    def _format_timestamp(self, seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millisecs = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millisecs:03d}"

    def cleanup(self):
        """
        Clean up temporary directory
        """
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temporary directory: {e}")

    def __del__(self):
        """
        Ensure cleanup when object is garbage collected
        """
        self.cleanup()

