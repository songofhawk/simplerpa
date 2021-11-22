import argparse
import simplerpa.aircv as ac
import cv2
import numpy as np
from simplerpa.core.data.Action import Action
from simplerpa.core.action.ActionImage import ActionImage


def sobel(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # img_original = gray / 255   # 归一化
    # 分别求X,Y方向的梯度
    grad_X = cv2.Sobel(gray, -1, 1, 0)
    grad_Y = cv2.Sobel(gray, -1, 0, 1)
    # 求梯度图像
    grad = cv2.addWeighted(grad_X, 0.5, grad_Y, 0.5, 0)
    return grad


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--src", default='book_cover_rotated.jpg', help="path for the object image")
    parser.add_argument("--temp", default='book_cover.jpg', help="path for image containing the object")
    args = parser.parse_args()

    img_src = cv2.imread(args.src)
    img_temp = cv2.imread(args.temp)

    img_src_sobel = sobel(img_src)
    cv2.imwrite('img_src_soble.png', img_src_sobel)
    img_temp_sobel = sobel(img_temp)
    cv2.imwrite('img_temp_soble.png', img_temp_sobel)

    # 载入灰度原图，并且归一化

    result_list = ActionImage.find_all_template(img_src_sobel, img_temp_sobel, 0.8, auto_scale=(0.8, 1.9))
    # 最终证明用特征点的方法查找logo类图标的效果不好，可能由于图像简单，特征点太少，无法匹配
    for index, result in enumerate(result_list):
        rect = result['rectangle']
        # print('result-{}: confidence-{}, scale-{}, priority-{}， {}'.format(index,
        #                                                                    result.confidence if result is not None else None,
        #                                                                    result.scale,
        #                                                                    result.priority if hasattr(
        #                                                                        result,
        #                                                                        'priority') else None,
        #                                                                    rect if result is not None else None))
        cv2.rectangle(img_src, rect[0], rect[3], (0, 0, 220), 2)

    cv2.imwrite('result.png', img_src)



