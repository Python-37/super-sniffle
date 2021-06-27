"""用于计算图像中某个点围绕另一点旋转指定角度的座标
NOTE 值得注意的是，opencv中图片的座标和数学意义上的座标系不一致，所以放在
NOTE 平面直角座标系中顺时针和逆时针的结果是相反的，无需在此处纠结
"""
__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import importlib
import inspect
from functools import wraps

import numpy as np
from numpy import pi

try:
    util_classes = importlib.import_module("..utils", __package__)
    DecoratorBaseClass = util_classes.utils.DecoratorBaseClass
except (ImportError, TypeError):
    from utils.utils import DecoratorBaseClass


def collinear_point_by_distance(point1: np.ndarray, point2: np.ndarray,
                                distance: float):
    """给定一个点 point1，计算这个点在与 point2 共线方向上与 point2
    距离为 point1 与 point2 距离乘 distance 的点座标
    """
    return point2 + (point1 - point2) * distance


def whether_counterclockwise(func):
    """装饰器，为 rotate_point 添加按照逆时针方向旋转的功能
    rotate_point 函数调用时指定 counterclockwise 具名参数为True
    则按照逆时针方向旋转
    """
    @wraps(func)
    def inner(*args, counterclockwise=False, **kwargs):
        nonlocal sig
        if counterclockwise:
            func_arguments = sig.bind(*args, **kwargs).arguments
            angle = func_arguments["angle"]
            args = args[:2] + (-angle, )
        res = func(*args, **kwargs)
        return res

    sig = inspect.signature(func)
    parms = list(sig.parameters.values())
    parms.append(
        inspect.Parameter("counterclockwise",
                          inspect.Parameter.KEYWORD_ONLY,
                          default=False))
    inner.__signature__ = sig.replace(parameters=parms)
    return inner


class WhetherCounterclockwise(DecoratorBaseClass):
    """
    装饰器类，跟上面的 whether_counterclockwise 等效，只不过看起来更高级一点
    检视被装饰函数（rotate_point）的帮助讯息可以使用 help(self) ，要检视更多
    内容可以使用 vars(self) 和 dir(self)
    """
    def __init__(self, func):
        super().__init__(func)
        self.sig = inspect.signature(func)
        parms = list(self.sig.parameters.values())
        parms.append(
            inspect.Parameter("counterclockwise",
                              inspect.Parameter.KEYWORD_ONLY,
                              default=False))
        self.__signature__ = self.sig.replace(parameters=parms)

    def __call__(self, *args, counterclockwise=False, **kwargs):
        if counterclockwise:
            func_arguments = self.sig.bind(*args, **kwargs).arguments
            angle = func_arguments["angle"]
            args = args[:2] + (-angle, )
        res = self.__wrapped__(*args, **kwargs)
        return res


# @whether_counterclockwise
@WhetherCounterclockwise
def rotate_point(center_point, src_point, angle, *, use_degree=True):
    """
    将一个点绕另一个点旋转自定义角度
      :param center_point: 绕这个点旋转
      :param src_point: 将这个点进行旋转
      :param angle: 旋转这个角度
      :param counterclockwise: 布林值，装饰器中添加的参数，是否逆时针旋转
      :param use_degree: 强制具名参数，默认为True，即使用角度，如果指定为
                         False，则 angle 参数需要使用弧度
    """
    if use_degree:
        angle = np.deg2rad(angle)
    center_x, center_y = np.asarray(center_point)
    src_x, src_y = np.asarray(src_point)
    result_x = (src_x - center_x) * np.cos(angle) - (
        src_y - center_y) * np.sin(angle) + center_x
    result_y = (src_y - center_y) * np.cos(angle) + (
        src_x - center_x) * np.sin(angle) + center_y
    return result_x, result_y


if __name__ == '__main__':
    import time
    from itertools import cycle

    import cv2

    # 用于前景提取，时钟变化时可以提取运动的表针的mask
    bg_detect_MOG = cv2.createBackgroundSubtractorMOG2()
    bg_detect_KNN = cv2.createBackgroundSubtractorKNN(history=5)

    mirrorwise = False
    raw_point = np.array([500, 200], dtype=np.int32)
    center_point = np.asarray((500, 400), dtype=np.int32)
    img = np.full((800, 1000, 3), 255, np.uint8)
    # 将1到12的数字放到表盘上
    for text, deg in enumerate(np.arange(pi / 6, (2 + 1.5e-1) * pi, pi / 6),
                               start=1):
        dst_point = rotate_point(center_point,
                                 raw_point,
                                 deg,
                                 counterclockwise=mirrorwise,
                                 use_degree=False)
        cv2.circle(img, (int(dst_point[0]), int(dst_point[1])),
                   radius=2,
                   color=(255, 0, 0),
                   thickness=10)
        cv2.putText(img,
                    str(text), (int(dst_point[0]), int(dst_point[1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0),
                    thickness=2,
                    lineType=2)
    cv2.circle(img,
               tuple(center_point.tolist()),
               radius=2,
               color=(0, 255, 0),
               thickness=10)

    while True:
        img1 = img.copy()
        current_time = time.time() + 28800  # UTC+8 时间
        # 分别计算时针分针秒针角度
        second_degree, minute_degree, hour_degree = map(
            lambda item: divmod((item[0] % item[1]) / item[2], 360)[1],
            zip(cycle((current_time, )), (60, 3600, 86400),
                (pow(6, -1), 10, 120)))
        # 以下代码等效
        # second_degree = (current_time % 60) * 6
        # minute_degree = (current_time % 3600) / 10
        # hour_degree = ((current_time % 86400) % 43200) / 120
        for deg, text, line_length, line_colour in \
            zip(
                (second_degree, minute_degree, hour_degree),
                ("s", "m", "h"),
                (.9, .7, .5),
                ((255, 62, 150), (255, 99, 71), (255, 165, 0))
                ):
            # 计算表盘中点正上方点旋转后的座标
            dst_point = rotate_point(center_point,
                                     raw_point,
                                     deg,
                                     counterclockwise=mirrorwise,
                                     use_degree=True)
            # 上一步座标乘一个长度参数，表示三个表针，得到最终的表针座标
            dst_point = tuple(
                collinear_point_by_distance(np.asarray(dst_point),
                                            center_point, line_length).astype(
                                                np.int32).tolist())
            img1 = cv2.line(img1, (int(center_point[0]), int(center_point[1])),
                            dst_point, line_colour[::-1], 5)
            img1 = cv2.circle(img1,
                              tuple(np.asarray(dst_point, np.int32).tolist()),
                              radius=2,
                              color=(*reversed(line_colour), ),
                              thickness=10)
            img1 = cv2.putText(img1.copy(),
                               text, (int(dst_point[0]), int(dst_point[1])),
                               cv2.FONT_HERSHEY_SIMPLEX,
                               1,
                               color=(*reversed(line_colour), ),
                               thickness=2,
                               lineType=2)
        bg_mask_MOG = bg_detect_MOG.apply(img1)
        bg_mask_KNN = bg_detect_KNN.apply(img1)

        cv2.imshow("Masked MOG", bg_mask_MOG)
        cv2.imshow("Masked KNN", bg_mask_KNN)
        cv2.imshow("Clock", img1)
        key = cv2.waitKey(1)
        if key == ord("q") or key == 27:
            break
        time.sleep(.3)
    cv2.destroyAllWindows()
