import simplerpa.aircv as ac
from cv2 import cv2

image_origin = cv2.imread('seg_course_menu_small.png')
image_template = cv2.imread('seg_sharp.png')

match_result = ac.find_all_template(image_origin, image_template, 0.8)
rect = match_result['rectangle']
img_result = image_origin.copy()
cv2.rectangle(img_result, (rect[0][0], rect[0][1]), (rect[3][0], rect[3][1]), (0, 0, 220), 2)
cv2.imwrite('result.png',img_result)
