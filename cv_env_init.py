"""
图像处理算法测试介面的作用域包含的内容
包括自动补全、文档、OpenCV、numpy等必要包、函数等
"""
import pydoc  # noqa
import rlcompleter

import cv2  # noqa
import numpy as np  # noqa

completer = rlcompleter.Completer(globals())
img = None
_ = None


def complete(code_str: str) -> list:
    i = 0
    res = []
    while True:
        try:
            buff = completer.complete(code_str, i)
        except Exception:
            break
        else:
            if buff is None:
                break
            res.append(buff)
            i += 1
    return res
