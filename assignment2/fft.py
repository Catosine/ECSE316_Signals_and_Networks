import argparse
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os.path as osp


def parseInput():
    choice_helper = {
        1: "[1] (Default) for fast mode where ther image is converted into its FFT form and displayed",
        2: "[2] for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displyed",
        3: "[3] for compressing and saving the image",
        4: "[4] for plotting the runtime graphs for the report"
    }
    parser = argparse.ArgumentParser("fft.py")
    parser.add_argument("-m", type=int, default=1, choices=[1, 2, 3, 4], help='; '.join(choice_helper.values()))
    parser.add_argument("image", type=str, default="moonlanding.png", metavar="image.png", nargs="?",
                        help="(optional) filename of the image we wish to take the DFT of.")
    return parser.parse_args()


class FFTransformer:

    def __init__(self, config):
        self.mode = config.m
        self.image_name = config.image
        if not osp.exists(self.image_name):
            raise RuntimeError(
                "INVALID image input: {}. Please type python fft.py -h for help.".format(self.image_name))

    def to_string(self):
        return "Mode: {}, Image: {}".format(self.mode, self.image_name)

    def start(self):
        original_image = cv2.imread(self.image_name, cv2.IMREAD_UNCHANGED)

        # display original image
        plt.subplot(1, 2, 1)
        plt.title('origin')
        plt.imshow(original_image)

        if self.mode == 1:
            # mode 1
            plt.show()

        elif self.mode == 2:
            # mode 2
            plt.subplot(1, 2, 2)
            plt.title('denoising')
            plt.imshow(original_image)
            plt.show()

        elif self.mode == 3:
            # mode 3
            print("3")

        else:
            # mode 4
            print("4")

    def dft_naive1d(self, signal):

        """
            Naive 1D FT

            :param signal: 1D Numpy array
            :return: signal after naive FT
        """

        length = signal.shape[0]
        n = np.arange(length)
        k = n.reshape((length, 1))
        factor = np.exp(-2j * np.pi * k * n / length)
        return np.dot(factor, signal)

    def dft_fast1d(self, signal, threshold=16):

        """
            1D Cooley-Tukey FFT

            :param signal: 1D numpy array
            :param threshold: minimum split length
            :return: signal after FFT
        """

        length = signal.shape[0]
        if length % 2:
            raise RuntimeError("length of signal must be divisible by 2")

        if length <= threshold:
            # Should call naive 1D FT
            return self.dft_naive1d(signal)

        even = self.dft_fast1d(signal[0::2])
        odd = self.dft_fast1d(signal[0::2])
        factor = np.exp(-2j * np.pi * np.arange(length) / length)
        return np.concatenate((even + factor[:length // 2] * odd,
                               even + factor[length // 2:] * odd), axis=0)

    def dft_naive2d(self, img):

        """
            2D naive FT

            :param img: 2D numpy array
            :return: img after naive FT
        """

        row, col = img.shape
        output = np.empty([row, col], np.complex)

        for r in range(row):
            for c in range(col):
                sum = 0
                for n in range(col):
                    for m in range(row):
                        sum += img[m, n] * np.exp(-2j * np.pi * (float(r * m) / row + float(c * n) / col))
                output[r, c] = sum

        return output

    def dft_fast2d(self, img, threshold=16):

        """
            2D Cooley-Tukey FFT

            :param img: 2D numpy array
            :param threshold: minimum split length
            :return: img after 2D Cooley-Tukey FFT
        """
        row, col = img.shape
        if col % 2:
            raise RuntimeError("column of image must be divisible by 2")

        if col <= threshold:
            return np.array([self.dft_naive1d(img[r, :]) for r in range(row)])

        even = self.dft_fast2d(img[:, ::2])
        odd = self.dft_fast2d(img[:, 1::2])
        factor = np.array([np.exp(-2j * np.pi * np.arange(col) / col) for r in range(row)])
        return np.concatenate(
            (even + np.multiply(factor[:, :col // 2], odd),
             even + np.multiply(factor[:, col // 2:], odd)), axis=1)

    def idft_naive1d(self, ft_signal):

        """
            Inverse 1D Naive FT

            :param ft_signal: 1D numpy FT array
            :return: ft_signal after inverse 1D naive FT
        """

        length = ft_signal.shape[0]
        return ft_signal.dot(
            np.array([[np.exp(2j * np.pi * i * j / length) for i in range(length)] for j in range(length)]))

    def idft_fast1d(self, ft_signal, threshold=16):

        """
            Inverse 1D FFT

            :param ft_signal: 1D numpy FT array
            :param threshold: minimum split length
            :return: ft_signal after inverse 1D naive FT
        """

        length = ft_signal.shape[0]

        if length % 2:
            raise RuntimeError("length of signal must be divisible by 2")

        if length <= threshold:
            return self.idft_naive1d(ft_signal)

        even = self.idft_fast1d(ft_signal[::2])
        odd = self.idft_fast1d(ft_signal[1::2])
        factor = np.exp(2j * np.pi * np.arange(length) / length)
        return np.concatenate((even + factor[:length // 2] * odd,
                               even + factor[length // 2:] * odd), axis=0)

    def idft_naive2d(self, ft_img):
        # not sure if correct

        """
            Inverse 2D Naive FT

            :param ft_img: 2D numpy FT array
            :return: ft_signal after inverse 2D naive FT
        """

        row, col = ft_img.shape
        output = np.empty([row, col], np.complex)

        for r in range(row):
            for c in range(col):
                sum = 0
                for n in range(col):
                    for m in range(row):
                        sum += ft_img[m, n] * np.exp(2j * np.pi * (float(r * m) / row + float(c * n) / col))
                output[r, c] = sum / (row * col)

        return output

    def idft_fast2d(self, ft_img, threshold=16):
        """
            Inverse 2D Fast FT

            :param ft_img: 2D numpy FT array
            :param threshold: minimum split length
            :return: ft_signal after inverse 2D fast FT
        """

        row, col = ft_img.shape

        if col % 2:
            raise RuntimeError("column of image must be divisible by 2")

        if col <= threshold:
            return np.array([self.idft_naive1d(ft_img[i, :]) for i in range(row)])

        even = self.idft_fast2d(ft_img[:, ::2])
        odd = self.idft_fast2d(ft_img[:, 1::2])
        factor = np.array([np.exp(2j * np.pi * np.arange(col) / col) for i in range(row)])
        return np.concatenate(
            (even + np.multiply(factor[:, :col // 2], odd), even + np.multiply(factor[:, col // 2:], odd)), axis=1)


if __name__ == '__main__':
    config = parseInput()  # Throwing exception for no reason
    try:
        fft = FFTransformer(config)
        fft.start()
    except RuntimeError:
        raise
        exit(0)
