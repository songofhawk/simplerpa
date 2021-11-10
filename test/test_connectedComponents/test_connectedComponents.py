from cv2 import cv2

if __name__ == '__main__':
    img = cv2.imread('./img_erode.png', cv2.IMREAD_UNCHANGED)
    black_back = cv2.bitwise_not(img)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(black_back)
    print(stats)
    # num_labels, labels, stats, centroids = cv2.connectedComponentsWithStatsWithAlgorithm(img, 4, ltype=cv2.CV_16U,
    #                                                                                      ccltype=cv2.CCL_GRANA)
    # print(stats)
