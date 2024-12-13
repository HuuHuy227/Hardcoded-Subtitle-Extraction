import paddleocr.tools.infer.utility as utility

def init_args():
    args = utility.parse_args()
    args.use_gpu = False
    args.det_model_dir = "weights/det"
    args.rec_model_dir = "weights/rec"
    args.rec_char_dict_path = "weights/rec/en_dict.txt"
    return args

def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        for j in range(i, -1, -1):
            if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and (
                _boxes[j + 1][0][0] < _boxes[j][0][0]
            ):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes

def filter_center_bottom_bboxes(bboxes, img_height, img_width, center_ratio=0.5, bottom_ratio=0.2):
    """
    Filters bounding boxes to select those in the center-bottom region of the frame.

    Args:
        bboxes (list): List of bounding boxes with coordinates [x1, y1, x2, y2, x3, y3, x4, y4].
        img_height (int): Height of the image.
        img_width (int): Width of the image.
        center_ratio (float): Proportion of the image width considered as the center.
        bottom_ratio (float): Proportion of the image height considered as the bottom.

    Returns:
        list: Filtered bounding boxes in the center-bottom region.
    """
    center_x_min = (1 - center_ratio) / 2 * img_width
    center_x_max = (1 + center_ratio) / 2 * img_width
    bottom_y_min = (1 - bottom_ratio) * img_height

    filtered_bboxes = []
    for bbox in bboxes:
        # Calculate the bounding box center
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        bbox_center_x = sum(x_coords) / 4
        bbox_center_y = sum(y_coords) / 4

        # Check if the center is within the center-bottom region
        if center_x_min <= bbox_center_x <= center_x_max and bbox_center_y >= bottom_y_min:
            filtered_bboxes.append(bbox)

    return filtered_bboxes

# import numpy as np

# def sorted_boxes(dt_boxes):
#     """
#     Sort detected text boxes from top to bottom, left to right
#     """
#     sorted_boxes = sorted(dt_boxes, key=lambda x: (
#         np.mean(x[:, 1]),  # Sort by vertical position
#         np.mean(x[:, 0])   # Then by horizontal position
#     ))
#     return sorted_boxes

# def filter_center_bottom_bboxes(dt_boxes, img_height, img_width, 
#                                  vertical_ratio=0.6, 
#                                  horizontal_ratio=0.8):
#     """
#     Filter bounding boxes to focus on center-bottom subtitles
    
#     :param dt_boxes: List of detected bounding boxes
#     :param img_height: Height of the image
#     :param img_width: Width of the image
#     :param vertical_ratio: Vertical region to consider for subtitles
#     :param horizontal_ratio: Horizontal region to consider for subtitles
#     :return: Filtered bounding boxes
#     """
#     filtered_boxes = []
#     for box in dt_boxes:
#         # Calculate box center
#         box_center_y = np.mean(box[:, 1])

#         # Check vertical position (bottom half or bottom third of image)
#         vertical_condition = box_center_y > (img_height * vertical_ratio)
        
#         # Check horizontal spread (not too wide or narrow)
#         horizontal_spread = max(box[:, 0]) - min(box[:, 0])
#         horizontal_condition = horizontal_spread < (img_width * horizontal_ratio)
        
#         if vertical_condition and horizontal_condition:
#             filtered_boxes.append(box)
    
#     return filtered_boxes