import paddleocr.tools.infer.utility as utility
import numpy as np

def init_args():
    args = utility.parse_args()
    args.use_gpu = True
    args.warmup = True
    args.det_model_dir = "weights/det"
    args.rec_model_dir = "weights/rec"
    args.rec_char_dict_path = "weights/rec/en_dict.txt"
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
                                 horizontal_ratio=0.8):
    """
    Filter bounding boxes to focus on center-bottom subtitles
    
    :param dt_boxes: List of detected bounding boxes
    :param img_height: Height of the image
    :param img_width: Width of the image
    :param vertical_ratio: Vertical region to consider for subtitles
    :param horizontal_ratio: Horizontal region to consider for subtitles
    :return: Filtered bounding boxes
    """
    filtered_boxes = []
    for box in dt_boxes:
        # Calculate box center
        box_center_y = np.mean(box[:, 1])

        # Check vertical position (bottom half or bottom third of image)
        vertical_condition = box_center_y > (img_height * vertical_ratio)
        
        # Check horizontal spread (not too wide or narrow)
        horizontal_spread = max(box[:, 0]) - min(box[:, 0])
        horizontal_condition = horizontal_spread < (img_width * horizontal_ratio)
        
        if vertical_condition and horizontal_condition:
            filtered_boxes.append(box)
    
    return filtered_boxes