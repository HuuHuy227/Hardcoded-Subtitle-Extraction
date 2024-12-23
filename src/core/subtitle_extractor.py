import cv2
import difflib
import os
import re

from utils import init_args
from .text_ocr import TextOcr
from typing import List, Optional, Dict

class VideoSubtitleExtractor:
    def __init__(self, lang: str = "en", use_gpu: bool = False) -> None:
        """
        Initialize video subtitle extractor with memory-efficient processing
        
        :param lang: Language code for subtitle extraction
        """
        self.args = init_args(lang, use_gpu)
        self.args.warmup = True
        
        self.text_sys = TextOcr(self.args)
        self.previous_subtitles = []
        self.line_separator = " | "  # Separator for multiple lines in output

    def extract_subtitles(self, video_path: str, frame_rate: int = 1, 
                           confidence_threshold: float = 0.5, 
                           subtitle_disappear_threshold: int = 10,  # Increased threshold
                           progress_bar=None) -> List[Dict]:
        """
        Extract subtitles from video with precise timing and memory efficiency
        
        :param video_path: Path to the video file
        :param frame_rate: Number of frames to skip between each processed frame
        :param confidence_threshold: Minimum confidence for subtitle recognition
        :param subtitle_disappear_threshold: Number of consecutive frames without subtitle
        :param progress_bar: Streamlit progress bar object
        :return: List of extracted subtitles with precise timestamps
        """
        # Open video capture
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame skip
        frame_skip = max(1, int(fps // frame_rate))
        
        # Subtitle tracking variables
        subtitles = []
        current_subtitle = None
        frames_without_subtitle = 0
        frame_count = 0
        last_subtitle_frame = -1
        last_valid_subtitle_frame = -1

        try:
            while True:
                # Read frame
                success, frame = cap.read()
                
                # Break if no more frames
                if not success:
                    break
                
                # Process frame at specified rate
                if frame_count % frame_skip == 0:
                    # Perform OCR
                    _, rec_res = self.text_sys(frame)
                    
                    if rec_res:
                        # Group subtitles from the same frame
                        frame_subtitles = []
                        current_group = []
                        current_confidence = 0.0
                        
                        for text, conf in rec_res:
                            if conf >= confidence_threshold and text.strip():
                                current_group.append(text.strip())
                                current_confidence = max(current_confidence, conf)
                        
                        if current_group:
                            # Join multiple lines with newline
                            combined_text = "\n".join(current_group)
                            frame_subtitles.append((combined_text, current_confidence))
                        
                        if frame_subtitles:
                            best_subtitle = max(frame_subtitles, key=lambda x: (x[1], len(x[0])))[0]
                            
                            # Check subtitle uniqueness
                            is_unique = all(
                                self._compute_similarity(best_subtitle, prev) < 0.8 
                                for prev in self.previous_subtitles[-10:]  # Only compare with last 10 subtitles
                            )
                            
                            if is_unique:
                                # Close previous subtitle if exists
                                if current_subtitle:
                                    current_subtitle['end_time'] = self._format_timestamp(
                                        last_valid_subtitle_frame / fps
                                    )
                                    subtitles.append(current_subtitle)
                                
                                # Start new subtitle
                                current_subtitle = {
                                    'start_time': self._format_timestamp(frame_count / fps),
                                    'end_time': None,
                                    'text': best_subtitle
                                }
                                
                                frames_without_subtitle = 0
                                # last_subtitle_frame = frame_count
                                last_valid_subtitle_frame = frame_count
                                self.previous_subtitles.append(best_subtitle)
                            
                            # Update last valid subtitle frame
                            last_valid_subtitle_frame = frame_count
                            frames_without_subtitle = 0
                                
                    else:
                        frames_without_subtitle += 1
                    
                    # Check if subtitle should be considered disappeared
                    if current_subtitle and frames_without_subtitle >= subtitle_disappear_threshold:
                        # Use the last frame where subtitle was definitely visible
                        current_subtitle['end_time'] = self._format_timestamp(
                            last_valid_subtitle_frame / fps
                        )
                        subtitles.append(current_subtitle)
                        current_subtitle = None
                
                # Update progress bar
                if progress_bar and frame_count % max(1, total_frames // 100) == 0:
                    progress_bar.progress(int(frame_count / total_frames * 100))
                
                frame_count += 1
                
                # Stop if all frames processed
                if frame_count >= total_frames:
                    break
            
            # Handle last subtitle if exists
            if current_subtitle:
                current_subtitle['end_time'] = self._format_timestamp(
                    last_valid_subtitle_frame / fps
                )
                subtitles.append(current_subtitle)
        
        finally:
            cap.release()
        
        return subtitles

    def _compute_similarity(self, str1: str, str2: str) -> float:
        """
        Compute similarity between two strings, handling multiline text
        """
        # Normalize both strings
        clean_str1 = self._normalize_text(str1)
        clean_str2 = self._normalize_text(str2)
        
        # Remove spaces and convert to lowercase for comparison
        clean_str1 = clean_str1.replace(' ', '').lower()
        clean_str2 = clean_str2.replace(' ', '').lower()
        
        return difflib.SequenceMatcher(None, clean_str1, clean_str2).ratio()

    def _normalize_text(self, text: str) -> str:
        """
        Normalize subtitle text by handling multiline and cleaning up spaces
        
        :param text: Raw subtitle text
        :return: Normalized text
        """
        # Split text by common line separators
        lines = re.split(r'[\n\r]+', text)
        
        # Clean each line
        cleaned_lines = []
        for line in lines:
            # Remove extra spaces and trim
            line = ' '.join(line.split())
            if line:
                cleaned_lines.append(line)
        
        # Join lines with newline
        return "\n".join(cleaned_lines)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millisecs = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millisecs:03d}"

    def get_video_metadata(self, video_path: str) -> Optional[dict]:
        """
        Get video metadata efficiently
        
        :param video_path: Path to the input video file
        :return: Dictionary with video metadata or None
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            metadata = {
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
            }
            
            return metadata
        except Exception as e:
            return None
        finally:
            cap.release()