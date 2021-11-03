import os
import time
from typing import Tuple

import numpy as np
from cnocr import CnOcr
from cv2 import cv2
import aircv as ac
# 话说网易游戏家也有个aircv，功能类似， 还提供了find_sift方法，使用sift算法查找，以后可以试试
# https://github.com/NetEaseGame/aircv
from simplerpa.core.data.ScreenRect import ScreenRect, Vector
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
        if not isinstance(cv_image, np.ndarray):
            raise TypeError('cv_image should be a ndarray from numpy, but got a {}'.format(type(cv_image)))

        if rect is not None:
            cv_image = cv_image[rect.top:rect.bottom, rect.left:rect.right]
        cls.log_image('ocr', cv_image, True)
        cv_image_gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        img_high_contrast = cls.grayscale_linear_transformation(cv_image_gray, 0, 255)

        res_chars = cls.cnocr.ocr_for_single_line(img_high_contrast)

        if len(res_chars) == 0:
            print('ocr result: ')
            return ''
        else:
            result = ''.join(list(map(str, res_chars[0])))
            print('ocr result: {}'.format(result))
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
    def find_all_template(cls, image_current, image_template, min_confidence, auto_scale: Tuple[float, float] = None,
                          scale: float = 1):
        width = image_template.shape[1]
        height = image_template.shape[0]
        if scale == 1:
            resized = image_template
        else:
            resized = cv2.resize(image_template, (int(width * scale), int(height * scale)),
                                 interpolation=cv2.INTER_CUBIC)

        match_results = ac.find_all_template(image_current, resized, min_confidence)

        if match_results is None or len(match_results) == 0:
            if auto_scale is None:
                return None
            else:
                scale_min = auto_scale[0]
                scale_max = auto_scale[1]
                for scale in np.arange(scale_min, scale_max, 0.1):
                    resized = cv2.resize(image_template, (int(width * scale), int(height * scale)),
                                         interpolation=cv2.INTER_CUBIC)
                    match_results = ac.find_all_template(image_current, resized, min_confidence)
                    # print("try resize template to match: {}".format(scale))
                    if match_results is not None and len(match_results) > 0:
                        break
        res_list = []
        for match_result in match_results:
            res = cls._change_result(match_result, scale if auto_scale else None)
            res_list.append(res)
        return res_list

    # 这个方法没用了，因为实际上ac.find_template方法，其实也是调用了find_all_template,然后返回第一个结果而已
    # @classmethod
    # def find_one_template(cls, image_source, image_template, min_confidence=0.5,
    #                       auto_scale: Tuple[float, float] = None):
    #     match_result = cls.find_all_template(image_source, image_template, min_confidence, auto_scale)
    #     return match_result[0] if match_result else None

    @classmethod
    def _change_result(cls, match_result, scale=None):
        if match_result is None:
            return None
        rect_array = match_result['rectangle']
        res = DataObject()
        res.confidence = match_result['confidence']
        res.rect = ScreenRect(rect_array[0][0], rect_array[3][0], rect_array[0][1], rect_array[3][1])
        res.scale = scale
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

    @classmethod
    def find_rect(cls, image_source, rect, color, find_all=True, debug=False):
        return cls.sliding_window(image_source, rect,
                                  lambda image_block, top, left: cls._match_color(image_block, color),
                                  find_all=find_all,
                                  debug=debug)

    @staticmethod
    def sliding_window(image_source, win_rect, handler, find_all=True, step_x=1, step_y=1, debug=False, overlap=False):
        rows, cols, _ = image_source.shape
        win_width = win_rect.x
        win_height = win_rect.y
        results = []

        row = 0
        skip_y = 0
        while row < rows:
            top = row
            bottom = row + win_height
            if bottom > rows:
                break
            col = 0
            skip_x = 0
            while col < cols:
                left = col
                right = col + win_width
                if right > cols:
                    break
                image_block = image_source[top:bottom, left:right]
                if debug:
                    ActionImage.log_image('block-row{}-col{}'.format(row, col), image_block, debug=debug)
                passed, res = handler(image_block, top, left)
                if passed:
                    result = DataObject()
                    result.handle_res = res
                    res_rect = ScreenRect(left, right, top, bottom)
                    result.rect = res_rect
                    results.append(result)
                    if find_all:
                        skip_x = win_width
                        skip_y = win_height
                    else:
                        return results
                if skip_x > 0:
                    col = col + skip_x
                    skip_x = 0
                else:
                    col = col + step_x

            if skip_y > 0:
                row = row + skip_y
                skip_y = 0
            else:
                row = row + step_y
        return results

    @staticmethod
    def _match_color(image, color):
        img_sum = np.sum(image, axis=2)
        r, g, b = color
        color_sum = r + g + b

        if np.all(img_sum == color_sum):
            # 求和通过，说明大致匹配，再详细考察具体内容
            image_r = image[:, :, 2]
            image_g = image[:, :, 1]
            image_b = image[:, :, 0]
            r_match = np.all(image_r == r)
            g_match = np.all(image_g == g)
            b_match = np.all(image_b == b)
            passed = r_match and g_match and b_match
            return passed, None
        else:
            return False, None

    @classmethod
    def get_color(cls, image, point: Vector):
        pixel = image[point.y, point.x]
        b, g, r = pixel
        return r, g, b

    @classmethod
    def get_color_sim(cls, image, color, point: Vector):
        r, g, b = cls.get_color(image, point)
        diff = abs(color[0] - r) + abs(color[1] - g) + abs(color[2] - b)
        similarity = 1 - diff / (255 + 255 + 255)
        return similarity
