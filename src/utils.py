import paddleocr.tools.infer.utility as utility
import numpy as np
from typing import Dict, Tuple
import os

SUPPORTED_LANGUAGES: Dict[str, str] = {
    'en': 'English',
    'zh': 'Chinese (Simplied)', 
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
}

def get_language_paths(lang: str) -> Tuple[str, str]:
    """
    Get model and dictionary paths for specified language
    
    Args:
        lang: Language code ('en', 'zh', etc)
        
    Returns:
        Tuple of (model_dir_path, dict_path)
        
    Raises:
        ValueError: If language not supported
    """
    if lang not in SUPPORTED_LANGUAGES:
        supported = ', '.join(SUPPORTED_LANGUAGES.keys())
        raise ValueError(f"Language '{lang}' not supported. Use one of: {supported}")
        
    base_path = "weights"
    model_dir = os.path.join(base_path, "rec", lang)
    dict_path = os.path.join(model_dir, f"{lang}_dict.txt")


    # Validate paths exist
    if not os.path.exists(model_dir):
        raise ValueError(f"Model directory not found: {model_dir}")
    if not os.path.exists(dict_path):
        raise ValueError(f"Dictionary file not found: {dict_path}")
        
    return model_dir, dict_path

def init_args(lang: str = "en", use_gpu: bool = False):
    args = utility.parse_args()
    args.use_gpu = use_gpu # Use this base on your environment
    args.warmup = True

    model_dir, dict_path = get_language_paths(lang)
    args.det_model_dir = "weights/det"
    args.rec_model_dir = model_dir
    args.rec_char_dict_path = dict_path
    return args

def sorted_boxes(dt_boxes):
    """
    Sort detected text boxes from top to bottom, left to right
    """
    sorted_boxes = sorted(dt_boxes, key=lambda x: (
        np.mean(x[:, 1]),  # Sort by vertical position
        np.mean(x[:, 0])   # Then by horizontal position
    ))
    return sorted_boxes

def filter_center_bottom_bboxes(dt_boxes, img_height, img_width,
                              vertical_ratio=0.6,
                              horizontal_ratio=0.8,
                              min_width_ratio=0.1,
                              max_height_ratio=0.15):
    """
    Enhanced filter for subtitle bounding boxes
    """
    filtered_boxes = []
    for box in dt_boxes:
        # Box dimensions
        box_height = max(box[:, 1]) - min(box[:, 1])
        box_width = max(box[:, 0]) - min(box[:, 0])
        box_center_y = np.mean(box[:, 1])
        
        # Filter conditions
        vertical_condition = box_center_y > (img_height * vertical_ratio)
        width_condition = (box_width < img_width * horizontal_ratio and 
                         box_width > img_width * min_width_ratio)
        height_condition = box_height < img_height * max_height_ratio
        
        if vertical_condition and width_condition and height_condition:
            filtered_boxes.append(box)
    
    return filtered_boxes