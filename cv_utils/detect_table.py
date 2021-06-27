__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

from typing import Tuple

import cv2


def detect_table(image,
                 row_w: int = 50,
                 row_h: int = 1,
                 col_w: int = 1,
                 col_h: int = 50,
                 black_background: bool = False) -> Tuple:
    """
    用于将图片中表格的边框（包括内部边框）去除
      :param row_w: 横线横向长度
      :param row_h: 横线纵向长度
      :param col_w: 竖线横向长度
      :param col_h: 竖线纵向长度
      :param black_background: 是否是黑色背景图片
      :return : 原始图像的复制、检测出来的横线、检测出来的竖线、
                检测出来的表格和去除表格的结果
    """
    img = image.copy()
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (row_w, row_h))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (col_w, col_h))
    # 原始图像是白色背景黑色前景，此处如果进行了转换，下面的运算也需要进行调整
    if black_background:
        row_img = cv2.erode(img, kernel1)
        col_img = cv2.erode(img, kernel2)
        table_img = col_img | row_img
        result_img = img ^ (col_img | row_img)
    else:
        row_img = cv2.dilate(img, kernel1)
        col_img = cv2.dilate(img, kernel2)
        table_img = col_img & row_img
        result_img = ~img ^ (col_img & row_img)
    return img, row_img, col_img, table_img, result_img


if __name__ == "__main__":
    img = cv2.imread("test.jpg", cv2.IMREAD_GRAYSCALE)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)

    # img, row_img, col_img, table_img, result_img = detect_table(
    #     img, 80, 1, 1, 30, black_background=False)
    img, row_img, col_img, table_img, result_img = detect_table(
        ~img, 80, 1, 1, 30, black_background=True)
    cv2.imshow("原始图像", img)
    cv2.imshow("检测出来的横线", row_img)
    cv2.imshow("检测出来的竖线", col_img)
    cv2.imshow("检测出来的表格", table_img)
    cv2.imshow("去除表格后的图片", result_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
