from core.text_ocr import TextOcr
from paddleocr import draw_ocr
from utils import init_args
import numpy as np
from PIL import Image, ImageDraw

# Function to draw bounding boxes with different colors
# def draw_bboxes_comparison(image, boxes):
#     draw_image = image.copy()
#     draw = ImageDraw.Draw(draw_image)
    
#     # Ensure boxes is a list and handle numpy arrays
#     if isinstance(boxes, np.ndarray):
#         boxes = [boxes]
#     elif not isinstance(boxes, list):
#         raise ValueError("boxes must be a numpy array or list of arrays")
        
#     for bbox in boxes:
#         if bbox.size == 0:  # Skip empty arrays
#             continue
#         if bbox.ndim == 1:  # Handle scalar arrays
#             continue
            
#         # Convert coordinates to integer tuples
#         points = [(int(x), int(y)) for x, y in bbox]
#         draw.polygon(points, outline="red", width=2)
    
#     return draw_image

args = init_args(lang = 'zh')
ocr = TextOcr(args)

img_path = 'C:/huy/Subtitle-Extraction/image2.png' 
result = ocr(img_path)
print(result)

# draw result
from PIL import Image
# result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result[0]]
txts = [line[0] for line in result[1]]
scores = [line[1] for line in result[1]]
im_show = draw_ocr(image, boxes, txts, scores, font_path='assets/simfang.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')





# import paddle
# paddle.set_device('cpu')

# paddle.utils.run_check()
