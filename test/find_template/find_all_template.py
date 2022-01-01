import time

import cv2

from top_k import top_k


def _to_gray(image):
    channel = 1 if len(image.shape) == 2 else image.shape[2]
    if channel == 1:
        # if the image is gray, then keep it
        image_gray = image
    elif channel == 3:
        # if it's colorful, then convert it to gray
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif channel == 4:
        # if it's colorful with transparent channel, then convert it to gray
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else:
        raise RuntimeError('im_search have {} channel, which is unexpected!'.format(channel))
    return image_gray


def find_all_template_v1(im_source, im_template, threshold=0.5, maxcnt=0, edge=False, debug=False):
    """
    用 cv2.templateFind 方法, 在im_source中查找im_search的匹配位置，源图和

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_template(string): 需要查找的图片
        threshold: 阈值，当匹配度小于该阈值的时候，就忽略掉
        maxcnt: 最大查找数量, 缺省为0, 即不限
        edge: 是否做边缘提取后再匹配

    Returns:
        A tuple of found [(point, score), ...]

    Raises:
        IOError: when file read error
    """

    if debug:
        start_time = time.time()
    gray_template = _to_gray(im_template)
    gray_source = _to_gray(im_source)
    if debug:
        print("to_gray time: {}".format(time.time() - start_time))

    # 边界提取(来实现背景去除的功能)
    if edge:
        if debug:
            start_time = time.time()
        gray_template = cv2.Canny(gray_template, 100, 200)
        gray_source = cv2.Canny(gray_source, 100, 200)
        if debug:
            print("Canny time: {}".format(time.time() - start_time))

    if debug:
        start_time = time.time()
    res = cv2.matchTemplate(gray_source, gray_template, cv2.TM_CCOEFF_NORMED)
    if debug:
        print("matchTemplate time: {}".format(time.time() - start_time))

    if debug:
        start_time = time.time()
    w, h = im_template.shape[1], im_template.shape[0]
    sw, sh = im_source.shape[1], im_source.shape[0]

    result = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        if max_val < threshold:
            break

        left = top_left[0]
        top = top_left[1]
        middle_point = (left + w / 2, top + h / 2)
        result.append(dict(
            result=middle_point,
            rectangle=(top_left, (left, top + h), (left + w, top),
                       (left + w, top + h)),
            confidence=max_val
        ))
        if maxcnt and len(result) >= maxcnt:
            break
        # 用最小值填充当前结果的周边区域，避免下次找到重叠的结果
        x1 = left - w + 1 if left - w + 1 > 0 else 0
        x2 = left + w - 1 if left + w - 1 < sw else sw
        y1 = top - h + 1 if top - h + 1 > 0 else 0
        y2 = top + h - 1 if top + h - 1 < sh else sh
        res[y1:y2, x1:x2] = -1000

    if debug:
        print("find max time: {}".format(time.time() - start_time))

    return result


def find_all_template_v2(im_source, im_search, threshold=0.5, maxcnt=100, rgb=False, bgremove=False):
    '''
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_search(string): 需要查找的图片
        threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

    Returns:
        A tuple of found [(point, score), ...]

    Raises:
        IOError: when file read error
    '''
    # method = cv2.TM_CCORR_NORMED
    # method = cv2.TM_SQDIFF_NORMED
    method = cv2.TM_CCOEFF_NORMED

    if rgb:
        s_bgr = cv2.split(im_search)  # Blue Green Red
        i_bgr = cv2.split(im_source)
        weight = (0.3, 0.3, 0.4)
        resbgr = [0, 0, 0]
        for i in range(3):  # bgr
            resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], method)
        res = resbgr[0] * weight[0] + resbgr[1] * weight[1] + resbgr[2] * weight[2]
    else:
        start_time = time.time()
        channel = 1 if len(im_search.shape) == 2 else im_search.shape[2]
        if channel == 1:
            # if the image is gray, then keep it
            s_gray = im_search
        elif channel == 3:
            # if it's colorful, then convert it to gray
            s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
        elif channel == 4:
            # if it's colorful with transparent channel, then convert it to gray
            s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGRA2GRAY)
        else:
            raise RuntimeError('im_search have {} channel, which is unexpected!'.format(channel))

        channel = 1 if len(im_source.shape) == 2 else im_source.shape[2]
        if channel == 1:
            # if the image is gray, then keep it
            i_gray = im_source
        elif channel == 3:
            # if it's colorful, then convert it to gray
            i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
        elif channel == 4:
            # if it's colorful with transparent channel, then convert it to gray
            i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGRA2GRAY)
        else:
            raise RuntimeError('im_source have {} channel, which is unexpected!'.format(channel))
        print("cvtColor time: {}".format(time.time() - start_time))

        # 边界提取(来实现背景去除的功能)
        if bgremove:
            s_gray = cv2.Canny(s_gray, 100, 200)
            i_gray = cv2.Canny(i_gray, 100, 200)

        start_time = time.time()
        res = cv2.matchTemplate(i_gray, s_gray, method)
        print("matchTemplate time: {}".format(time.time() - start_time))

    w, h = im_search.shape[1], im_search.shape[0]

    start_time = time.time()

    rows, cols = top_k(res, maxcnt)
    result = []
    # flatten = rows.flatten()
    for index in range(rows.size):
        row = rows[index]
        col = cols[index]
        val = res[row][col]
        if val < threshold:
            break
        middle_point = (col + h / 2, row + w / 2)
        result.append(dict(
            result=middle_point,
            rectangle=((col, row), (col, row + h), (col + w, row),
                       (col + w, row + h)),
            confidence=val
        ))
        if maxcnt and len(result) >= maxcnt:
            break
    # floodfill the already found area
    print("find max time: {}".format(time.time() - start_time))

    return result
