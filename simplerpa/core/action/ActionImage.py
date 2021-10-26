import os
import time

import numpy as np
from cnocr import CnOcr
from cv2 import cv2
import aircv as ac
# 话说网易游戏家也有个aircv，功能类似， 还提供了find_sift方法，使用sift算法查找，以后可以试试
# https://github.com/NetEaseGame/aircv
from simplerpa.core.data.ScreenRect import ScreenRect
from simplerpa.objtyping.objtyping import DataObject


class ActionImage:
    """
    图像处理操作类

    """
    cnocr = CnOcr()

    @classmethod
    def pil_to_cv(cls, pil_image):
        """
        把Pillow(PIL)格式的图片，转换成opencv格式的图片。
        两者的差别在于，首先PIL支持更丰富的图片表达方式，不一定使用RGB表达，还可以用HSV或者其他形式；
        但opencv一定用红绿蓝三原色组合，而且还别出心裁地使用了BGR这个顺序，而不是通常的RGB。

        Args:
            pil_image: PIL格式的图片

        Returns:
            opencv格式的图片
        """
        img_tmp = pil_image.convert('RGB')
        cv_rgb = np.array(img_tmp)
        return cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)

    @classmethod
    def load_from_file(cls, image_path):
        """
        从文件中读取图片，返回opencv格式的变量
        Args:
            image_path (str): 图片路径，暂时仅支持8位颜色深度

        Returns:
            opencv格式的图片变量
        """
        return cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)

    @classmethod
    def ocr(cls, cv_image, rect=None):
        """
        从指定图片的特定位置中提取文本字符串
        Args:
            cv_image (numpy): 图片变量，要求是opencv格式的
            rect: 图片中的位置

        Returns:

        """
        if rect is not None:
            cv_image = cv_image[rect.top:rect.bottom, rect.left:rect.right]
        cv_image_gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        img_high_contrast = cls.grayscale_linear_transformation(cv_image_gray, 0, 255)

        res_chars = cls.cnocr.ocr_for_single_line(img_high_contrast)

        if len(res_chars) == 0:
            return ''
        else:
            result = ''.join(list(map(str, res_chars)))

            return result

    @staticmethod
    def grayscale_linear_transformation(img_gray, new_min, new_max):
        if img_gray is None:
            return None
        old_max = img_gray.max()
        old_min = img_gray.min()
        if old_min == old_max:
            return img_gray
        scale_ratio = (new_max - new_min) / (old_max - old_min)
        img_gray_new = (img_gray - old_min) * scale_ratio + new_min
        return img_gray_new.astype(np.uint8)

    @classmethod
    def find_all_template(cls, image_current, image_template, min_confidence):
        match_results = ac.find_all_template(image_current, image_template, min_confidence)
        if match_results is None:
            return None
        res_list = []
        for match_result in match_results:
            res = cls._change_result(match_result)
            res_list.append(res)
        return res_list

    @classmethod
    def find_one_template(cls, image_source, image_template, min_confidence=0.5):
        match_result = ac.find_template(image_source, image_template, min_confidence)
        res = cls._change_result(match_result)
        return res

    @classmethod
    def _change_result(cls, match_result):
        if match_result is None:
            return None
        rect_array = match_result['rectangle']
        res = DataObject()
        res.confidence = match_result['confidence']
        res.rect = ScreenRect(rect_array[0][0], rect_array[3][0], rect_array[0][1], rect_array[3][1])
        return res

    @classmethod
    def log_image(cls, name, image, debug=True):
        if not debug:
            return
        path_root = 'log'
        if not os.path.exists(path_root):
            os.makedirs(path_root)
        timestamp = time.time()
        cv2.imwrite('{}/{}_{}.png'.format(path_root, name, timestamp), image)

    def find_rect(self, image_source, rect, color, find_all=True):
        return self.sliding_window(image_source, rect, lambda image_block: self._match_color(image_block, color),
                                   find_all)

    @staticmethod
    def sliding_window(image_source, win_rect, handler, find_all=True, step_x=4, step_y=4):
        rows, cols = image_source.shape
        win_width = win_rect.x
        win_height = win_rect.y
        results = []
        for row in range(0, rows, step_y):
            for col in range(0, cols, step_x):
                image_block = image_source[row:row + win_height, col:col + win_width]
                passed, res = handler(image_block, row, col)
                if passed:
                    result = DataObject()
                    result.handle_res = res
                    result.top = row,
                    result.left = col
                    if find_all:
                        results.append(result)
                    else:
                        return result
        return results

    @staticmethod
    def _match_color(image, color):
        r, g, b = color
        image_r = image[:, :, 2]
        image_g = image[:, :, 1]
        image_b = image[:, :, 0]
        r_match = np.all(image_r == r)
        g_match = np.all(image_g == g)
        b_match = np.all(image_b == b)
        return r_match and g_match and b_match, None
