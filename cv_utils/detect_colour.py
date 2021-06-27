__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import cv2
import numpy as np

red_min1 = np.array([0, 15, 5])
red_max1 = np.array([5, 255, 255])
red_min2 = np.array([160, 15, 5])
red_max2 = np.array([180, 255, 255])

green_min = np.array([40, 15, 5])
green_max = np.array([90, 255, 255])

yellow_min = np.array([8, 15, 5])
yellow_max = np.array([40, 255, 255])


def detect_colour(image, colour_min, colour_max):
    """
    将图片中特定颜色范围的部分检测出来
      :param image: HSV 颜色通道的图片
      :param colour_min: 待检测颜色范围最小值
      :param colour_max: 待检测颜色范围最大值
      :return : 将颜色范围过滤出来之后以白色为背景的图片，HSV颜色通道
    """
    zone = cv2.inRange(image, colour_min, colour_max)
    mask = zone == 255
    img = np.zeros_like(image)
    img[:] = (0, 0, 255)
    # NOTE 此处由于 mask 的 shape 与两个代表图片的数组不一致，所以不能使用
    # NOTE np.where 方法，只能使用 mask 切片的形式
    img[mask] = image[mask]
    return img


if __name__ == "__main__":
    image = cv2.imread("test.jpg", cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    result = detect_colour(image, yellow_min, yellow_max)
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    cv2.imshow("result-yellow", result)
    cv2.waitKey(0)

    result = detect_colour(image, red_min1, red_max1) + detect_colour(
        image, red_min2, red_max2)
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    cv2.imshow("result-red", result)
    cv2.waitKey(0)

    result = detect_colour(image, green_min, green_max)
    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)
    cv2.imshow("result-green", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
