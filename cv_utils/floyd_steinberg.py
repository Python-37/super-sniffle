__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"
import random

import cv2
import numpy as np
from numba import jit


def find_closest2tone(pixel_value):
    """
    Given a pixel_value (int from 0-255), return the 0 or 255, whichever is closer
    as well as the distance from that value.
    """
    diff = abs(255 - pixel_value)
    if diff < pixel_value:
        return 255, -diff
    return 0, pixel_value


def find_closest(pixel_value, palette):
    """
    Given a palette (an array of rgb values stored as tuples or lists) and a
    pixel value (tuple or list of rgb values), return the closest color in the palette
    and the distance of each rgb value in pixel_value from that color.
    """
    error_array, total_array = [], []
    i = 0
    for color in palette:
        error_array.append([])
        for channel_index in range(len(pixel_value)):
            error_array[i].append(pixel_value[channel_index] -
                                  color[channel_index])
        total_error = 0
        for error in error_array[i]:
            total_error += abs(float(error))
        total_array.append(total_error)
        i += 1
    min_index = total_array.index(min(total_array))
    return palette[min_index], error_array[min_index]


class Steinberg:
    divisor = 16.0
    # The error diffusion values
    MR, BL, BM, BR = 7.0, 3.0, 5.0, 1.0

    def __init__(self, image):
        self.width, self.height = image.shape[:2]
        self.image = image
        self.palette = []

    def convert2_gray(self):
        """
        Convert image to gray. (For use in two-tone dithering)
        """
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def dither2tone(self):
        """
        Apply a Steinberg dither using only black and white for the palette.
        """
        self.convert2_gray()
        error_array = np.zeros((self.width, self.height))
        for y in range(self.height):
            for x in range(self.width):
                pixel_value = self.image[x, y] + error_array[x][y]
                pixel_value, error = find_closest2tone(pixel_value)
                self.image[x, y] = pixel_value
                error = float(error)
                try:
                    error_array[x + 1, y] = self.MR / self.divisor * error
                except Exception:
                    pass
                try:
                    error_array[x - 1, y + 1] = self.BL / self.divisor * error
                except Exception:
                    pass
                try:
                    error_array[x, y + 1] = self.BM / self.divisor * error
                except Exception:
                    pass
                try:
                    error_array[x + 1, y + 1] = self.BR / self.divisor * error
                except Exception:
                    pass
        return self.image

    def generate_random_palette(self, colors=8):
        """
        Given the number of colors to generate, generate a random palette of colors.
        """
        self.palette = []
        for i in range(colors):
            self.palette.append((random.randint(0,
                                                255), random.randint(0, 255),
                                 random.randint(0, 255)))

    def generate_selective_palette(self, colors=8):
        """
        Given the number of colors to generate, generate a palette of colors by taking
        random points on the original image and getting their rgb values.
        """
        self.palette = []
        for i in range(colors):
            pixel = self.image[random.randint(0, self.width - 1),
                               random.randint(0, self.height - 1)]
            self.palette.append((pixel[0], pixel[1], pixel[2]))

    def choose_palette(self, mode: str = None, num_colors: int = None):
        """
        Get the user's choice for generating a palette.
        """
        print('1. Random Palette\t2. Selective Palette')
        options = ['1', '2']
        mode = mode or input('Choice: ')
        while mode not in options:
            mode = input('Choice: ')
        num_colors = num_colors or int(input('Number of colors to generate: '))
        if mode == '1':
            self.generate_random_palette(num_colors)
        elif mode == '2':
            self.generate_selective_palette(num_colors)
        else:
            raise TypeError("invalid argument num_colors")

    def dither(self):
        """
        Apply a Steinberg dither on the class's image. The image is overwritten.
        """
        self.choose_palette()
        error_array = np.zeros((self.width, self.height, 3))
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.image[x, y]
                pixel_value = [pixel[0], pixel[1], pixel[2]]
                for i in range(len(pixel_value)):
                    pixel_value[i] += error_array[x][y][i]
                pixel_value, error = find_closest(pixel_value, self.palette)
                self.image[x, y] = pixel_value
                try:
                    for channel_index in range(len(error_array[x + 1, y])):
                        error_array[
                            x + 1,
                            y][channel_index] = self.MR / self.divisor * error[
                                channel_index]
                except Exception:
                    pass
                try:
                    for channel_index in range(len(error_array[x - 1, y + 1])):
                        error_array[
                            x - 1, y +
                            1][channel_index] = self.BL / self.divisor * error[
                                channel_index]
                except Exception:
                    pass
                try:
                    for channel_index in range(len(error_array[x, y + 1])):
                        error_array[
                            x, y +
                            1][channel_index] = self.BM / self.divisor * error[
                                channel_index]
                except Exception:
                    pass
                try:
                    for channel_index in range(len(error_array[x + 1, y + 1])):
                        error_array[
                            x + 1, y +
                            1][channel_index] = self.BR / self.divisor * error[
                                channel_index]
                except Exception:
                    pass

        return self.image


@jit(nopython=True)
def floyd_steinberg(image):
    """
    另一种 floyd steinberg 算法的实现，使用了numba，运算速度很快
    NOTE works in-place!
      :param image: dtype=float, 范围在0.0-1.0
      :return : 处理后的图片，直接会在原图上修改！
    """
    h, w = image.shape
    for y in range(h):
        for x in range(w):
            old = image[y, x]
            new = np.round(old)
            image[y, x] = new
            error = old - new
            # precomputing the constants helps
            if x + 1 < w:
                image[y, x + 1] += error * 0.4375  # right, 7 / 16
            if (y + 1 < h) and (x + 1 < w):
                image[y + 1, x + 1] += error * 0.0625  # right, down, 1 / 16
            if y + 1 < h:
                image[y + 1, x] += error * 0.3125  # down, 5 / 16
            if (x - 1 >= 0) and (y + 1 < h):
                image[y + 1, x - 1] += error * 0.1875  # left, down, 3 / 16
    return image


if __name__ == "__main__":
    from PIL import Image
    img = cv2.imread("test.jpg")
    dither = Steinberg(img)
    # res = dither.dither2tone()  # gray
    res = dither.dither()[..., ::-1]  # RGB
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # res = floyd_steinberg(img / 255) * 255
    Image.fromarray(res).show()
