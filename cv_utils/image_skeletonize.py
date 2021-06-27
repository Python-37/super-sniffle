#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import barry_as_FLUFL
"""将图像内容骨架化"""
__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import time

import cv2
import numpy as np


class Refine:
    MAP_ARRAY = np.asarray([
        0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,
        1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1,
        1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1,
        1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0,
        1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0
    ])

    def three_element_add(self, image):
        array0 = image[:]
        array1 = np.append(image[1:], np.array([0]))
        array2 = np.append(image[2:], np.array([0, 0]))
        arr_sum = array0 + array1 + array2
        return arr_sum[:-2]

    def v_thin(self, image, array):
        flag = True
        height, width = image.shape[:2]
        for i in range(1, height):
            M_all = self.three_element_add(image[i])
            for j in range(1, width):
                if not flag:
                    flag = True
                else:
                    M = M_all[j - 1] if j < width - 1 else 1
                    if image[i, j] == 0 and M != 0:
                        a = np.zeros(9)
                        if height - 1 > i and width - 1 > j:
                            kernel = image[i - 1:i + 2, j - 1:j + 2]
                            a = np.where(kernel == 255, 1, 0)
                            a = a.reshape(1, -1)[0]
                        NUM = np.array([1, 2, 4, 8, 0, 16, 32, 64, 128])
                        sum_arr = int(np.sum(a * NUM))
                        image[i, j] = array[sum_arr] * 255
                        if array[sum_arr] == 1:
                            flag = False
        return image

    def h_thin(self, image, array):
        height, width = image.shape[:2]
        flag = True
        for j in range(1, width):
            M_all = self.three_element_add(image[:, j])
            for i in range(1, height):
                if not flag:
                    flag = True
                else:
                    M = M_all[i - 1] if i < height - 1 else 1
                    if image[i, j] == 0 and M != 0:
                        a = np.zeros(9)
                        if height - 1 > i and width - 1 > j:
                            kernel = image[i - 1:i + 2, j - 1:j + 2]
                            a = np.where(kernel == 255, 1, 0)
                            a = a.reshape(1, -1)[0]
                        NUM = np.array([1, 2, 4, 8, 0, 16, 32, 64, 128])
                        sum_arr = int(np.sum(a * NUM))
                        image[i, j] = array[sum_arr] * 255
                        if array[sum_arr] == 1:
                            flag = False
        return image

    def __call__(self, binary, map_array=None, num: int = 2) -> np.ndarray:
        """
        :param map_array: 不知道是啥
        :param num: 骨架化程度，这个数越大则骨架化越明显
        """
        map_array = map_array or self.MAP_ARRAY
        binary_image = binary.copy()
        image = cv2.copyMakeBorder(binary_image,
                                   1,
                                   0,
                                   1,
                                   0,
                                   cv2.BORDER_CONSTANT,
                                   value=0)
        for _ in range(num):
            self.v_thin(image, map_array)
            self.h_thin(image, map_array)
        return image


if __name__ == '__main__':
    image = cv2.imread(r'test.jpg', 0)
    ret, binary = cv2.threshold(image, 70, 255, cv2.THRESH_BINARY)

    # from skimage import morphology
    # skeleton0 = morphology.skeletonize(binary / 255)
    # skeleton = skeleton0.astype(np.uint8) * 255

    t1 = time.time()
    result = Refine()(binary, num=2)
    t2 = time.time()

    print('cost time:', t2 - t1)
    cv2.imshow('image', image)
    cv2.imshow('binary', binary)
    cv2.imshow('xi hua', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
