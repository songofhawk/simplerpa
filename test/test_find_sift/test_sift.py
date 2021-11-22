import argparse
import simplerpa.aircv as ac
import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--src", default='book_cover_rotated.jpg', help="path for the object image")
    parser.add_argument("--dest", default='book_cover.jpg', help="path for image containing the object")
    args = parser.parse_args()

    img1 = cv2.imread(args.src)
    img2 = cv2.imread(args.dest)


    # MIN_MATCHES = 30
    #
    # orb = cv2.ORB_create(nfeatures=500)
    # kp1, des1 = orb.detectAndCompute(img1, None)
    # kp2, des2 = orb.detectAndCompute(img2, None)
    #
    # index_params = dict(algorithm=6,
    #                     table_number=6,
    #                     key_size=12,
    #                     multi_probe_level=2)
    # search_params = {}
    # flann = cv2.FlannBasedMatcher(index_params, search_params)
    # matches = flann.knnMatch(des1, des2, k=2)


    result_list = ac.find_all_sift(img1, img2, 4, 1)
    # 最终证明用特征点的方法查找logo类图标的效果不好，可能由于图像简单，特征点太少，无法匹配
    for index, result in enumerate(result_list):
        rect = result['rectangle']
        print('result-{}: result-{}, rectangle-{}, confidence-{}'.format(index,
                                                                           result['result'],
                                                                           rect,
                                                                           result['confidence']))
        cv2.rectangle(img1, result['lt'], result['br'], (0, 0, 220), 2)

    cv2.imwrite('result.png', img1)



