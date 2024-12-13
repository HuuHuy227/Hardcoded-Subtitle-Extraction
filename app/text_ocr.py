import os
import cv2
import copy
import numpy as np
from PIL import Image
from paddleocr.ppocr.utils.logging import get_logger
import paddleocr.tools.infer.utility as utility
import paddleocr.tools.infer.predict_det as predict_det
import paddleocr.tools.infer.predict_rec as predict_rec
from utils import sorted_boxes, filter_center_bottom_bboxes

# from paddleocr.ppocr.utils.utility import get_image_file_list, check_and_read

logger = get_logger()

class TextOcr(object):
    def __init__(self, args) -> None:
        self.args = args
        self.text_detector = predict_det.TextDetector(args)
        self.text_recognizer = predict_rec.TextRecognizer(args)
        self.crop_image_res_index = 0
        # self.pad = args.padding_value

    def draw_crop_rec_res(self, output_dir, img_crop_list):
        os.makedirs(output_dir, exist_ok=True)
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite(
                os.path.join(
                    output_dir, f"mg_crop_{bno+self.crop_image_res_index}.jpg"
                ),
                img_crop_list[bno],
            )
        self.crop_image_res_index += bbox_num

    def get_rotate_crop_image(self, img, points):
        """
        img_height, img_width = img.shape[0:2]
        left = int(np.min(points[:, 0]))
        right = int(np.max(points[:, 0]))
        top = int(np.min(points[:, 1]))
        bottom = int(np.max(points[:, 1]))
        img_crop = img[top:bottom, left:right, :].copy()
        points[:, 0] = points[:, 0] - left
        points[:, 1] = points[:, 1] - top
        """
        assert len(points) == 4, "shape of points must be 4*2"
        img_crop_width = int(
            max(
                np.linalg.norm(points[0] - points[1]), np.linalg.norm(points[2] - points[3])
            )
        )
        img_crop_height = int(
            max(
                np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2])
            )
        )
        pts_std = np.float32(
            [
                [0, 0],
                [img_crop_width, 0],
                [img_crop_width, img_crop_height],
                [0, img_crop_height],
            ]
        )
        M = cv2.getPerspectiveTransform(points, pts_std)
        dst_img = cv2.warpPerspective(
            img,
            M,
            (img_crop_width, img_crop_height),
            borderMode=cv2.BORDER_REPLICATE,
            flags=cv2.INTER_CUBIC,
        )
        dst_img_height, dst_img_width = dst_img.shape[0:2]
        if dst_img_height * 1.0 / dst_img_width >= 1.5:
            dst_img = np.rot90(dst_img)
        return dst_img

    def get_minarea_rect_crop(self, img, points):
        bounding_box = cv2.minAreaRect(np.array(points).astype(np.int32))
        points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

        index_a, index_b, index_c, index_d = 0, 1, 2, 3
        if points[1][1] > points[0][1]:
            index_a = 0
            index_d = 1
        else:
            index_a = 1
            index_d = 0
        if points[3][1] > points[2][1]:
            index_b = 2
            index_c = 3
        else:
            index_b = 3
            index_c = 2

        box = [points[index_a], points[index_b], points[index_c], points[index_d]]
        crop_img = self.get_rotate_crop_image(img, np.array(box))
        return crop_img
    
    def __call__(self, img):
        # time_dict = {"det": 0, "rec": 0, "cls": 0, "all": 0}
        if isinstance(img, str):
            img = Image.open(img).convert('RGB')
            img = np.array(img)

        if img is None:
            logger.debug("no valid image provided")
            return None, None
        
        h, w = img.shape[:2]
        # start = time.time()
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        print(len(dt_boxes))
        # Filter boxes for center-bottom subtitles
        dt_boxes = sorted_boxes(dt_boxes)
        dt_boxes = filter_center_bottom_bboxes(dt_boxes, h, w)   

        # time_dict["det"] = elapse

        if not dt_boxes:
            logger.debug("no dt_boxes found, elapsed : {}".format(elapse))
            # end = time.time()
            # time_dict["all"] = end - start
            return None, None #, time_dict
        else:
            logger.debug(
                "dt_boxes num : {}, elapsed : {}".format(len(dt_boxes), elapse)
            )
        img_crop_list = []

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            if self.args.det_box_type == "quad":
                img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            else:
                img_crop = self.get_minarea_rect_crop(ori_im, tmp_box)
                
            # Ignore all vertical box
            if img_crop.shape[1] > img_crop.shape[0]: # Width > Height
                img_crop_list.append(img_crop)

        if len(img_crop_list) > 1000:
            logger.debug(
                f"rec crops num: {len(img_crop_list)}, time and memory cost may be large."
            )
            
        rec_res, elapse = self.text_recognizer(img_crop_list)
        assert len(rec_res) <= len(dt_boxes)
        # time_dict["rec"] = elapse
        logger.debug("rec_res num  : {}, elapsed : {}".format(len(rec_res), elapse))
    
        # end = time.time()
        # time_dict["all"] = end - start
        
        return dt_boxes, rec_res #filter_boxes, filter_rec_res

if __name__ == "__main__":
    args = utility.parse_args()
    path = "C:/Subtitle-Extraction/image.png"
    # path = "./weights/reg"
    args.use_gpu = False
    args.det_model_dir = "weights/det"
    args.rec_model_dir = "weights/rec"
    args.rec_char_dict_path = "weights/rec/en_dict.txt"
    # args.rec_char_dict_path
    # args.page_num = 1
    args.warmup = True
    # print(args)
    text_sys = TextOcr(args)

    logger.debug("warmup 5 times")
    if args.warmup:
        img = np.random.uniform(0, 255, [640, 640, 3]).astype(np.uint8)
        for i in range(5):
            res = text_sys(img)

    img = Image.open(path).convert('RGB')
    res = text_sys(np.array(img))
    print(res)
    


