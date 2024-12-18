from text_ocr import TextOcr
from paddleocr import draw_ocr
from utils import init_args
import numpy as np
from PIL import Image

args = init_args()
ocr = TextOcr(args)

img_path = 'C:/Subtitle-Extraction/image.png'
result = ocr(img_path)
print(result)
# for idx in range(len(result)):
#     res = result[idx]
#     for line in res:
#         print(line)

# draw result
from PIL import Image
# result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result[0]]
txts = [line[0] for line in result[1]]
scores = [line[1] for line in result[1]]
im_show = draw_ocr(image, boxes, txts, scores, font_path='C:/Subtitle-Extraction/simfang.ttf')
im_show = Image.fromarray(im_show)
im_show.save('result.jpg')


