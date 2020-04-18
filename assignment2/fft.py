import argparse
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import cv2
import numpy as np
import os.path as osp
import time
from tqdm import tqdm


def parseInput():
    choice_helper = {
        1: "[1] (Default) for fast mode where ther image is converted into its FFT form and displayed",
        2: "[2] for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displyed",
        3: "[3] for compressing and saving the image",
        4: "[4] for plotting the runtime graphs for the report"
    }
    denoise_helper = {
        1: "[1] (Default) remove low frequency",
        2: "[2] remove high frequency",
        3: "[3] threshold everything",
        4: "[4] threshold low frequency",
        5: "[5] threshold high frequency"
    }
    parser = argparse.ArgumentParser("fft.py")
    parser.add_argument("-m", type=int, default=1, choices=[1, 2, 3, 4], help='; '.join(choice_helper.values()))
    parser.add_argument("image", type=str, default="moonlanding.png", metavar="image.png", nargs="?",
                        help="(optional) filename of the image we wish to take the DFT of.")
    parser.add_argument("--denoise_ratio", type=float, default=0.1, help="(optional) denoising ratio")
    parser.add_argument("--compress_ratio", type=float, default=0.9, help="(optional) compressing ratio")
    parser.add_argument("--denoise_type", type=int, default=1, choices=[1, 2, 3, 4, 5], help='; '.join(denoise_helper.values()))
    parser.add_argument("--denoise_cap", type=int, default=10000, help="(optiona) thresholding for denoise")
    parser.add_argument("--debug", action="store_false", help="run under debug mode")
    return parser.parse_args()


class FFTransformer:

    def __init__(self, config):
        self.mode = config.m
        self.image_name = config.image
        self.denosing_percentile = config.denoise_ratio
        self.compressing_percentile = config.compress_ratio
        self.debug = config.debug
        self.denosing_type = config.denoise_type
        self.denoise_cap = config.denoise_cap
        if not osp.exists(self.image_name):
            raise RuntimeError(
                "INVALID image input: {}. Please type python fft.py -h for help.".format(self.image_name))

    def to_string(self):
        return "Mode: {}, Image: {}".format(self.mode, self.image_name)

    def start(self):
        original_image = self.validify_img(cv2.imread(self.image_name, cv2.IMREAD_GRAYSCALE))

        # display original image
        plt.title("original")
        plt.imshow(original_image)
        plt.savefig("assignment2/pics/original_"+self.image_name, bbox_inches='tight')
        plt.close()

        if self.mode == 1:
            # mode 1
            fft_image = self.dft_fast2d(original_image)

            plt.title('self.fft')
            plt.imshow(np.abs(fft_image), norm=LogNorm())
            plt.savefig("assignment2/pics/self_fft_"+self.image_name, bbox_inches='tight')
            plt.close()

            fft_image = np.fft.fft2(original_image)
            plt.title('np.fft')
            plt.imshow(np.abs(fft_image), norm=LogNorm())
            plt.savefig("assignment2/pics/np_fft_"+self.image_name, bbox_inches='tight')

        elif self.mode == 2:
            # mode 2
            self.denoise(original_image, percentile=self.denosing_percentile, type=self.denosing_type, cap=self.denoise_cap)

        elif self.mode == 3:
            # mode 3
            compressed_img = self.compress(original_image, percentile=self.compressing_percentile)

            plt.title('compressing: percentile = {}'.format(self.compressing_percentile))
            plt.imshow(compressed_img.real)
            plt.savefig("assignment2/pics/compressing_{}_".format(self.compressing_percentile)+self.image_name, bbox_inches='tight')

        else:
            # mode 4
            e = 7 if self.debug else 14
            trial = 2 if self.debug else 10
            naive_time = list()
            fast_time = list()

            for p in range(5,e):
                size = 2**p
                print("##########################")
                print("Test data size: ({}, {})".format(size, size))
                print("##########################")
                temp_n_time = list()
                temp_f_time = list()
                for t in range(trial):
                    print("Trial: {}".format(t))

                    test_data = np.random.rand(size, size).astype(np.float32)

                    naive_start = time.time()
                    self.dft_naive2d(test_data)
                    n_time = time.time() - naive_start
                    print("Naive time: {}".format(n_time))
                    temp_n_time.append(n_time)

                    fast_start = time.time()
                    self.dft_fast2d(test_data)
                    f_time = time.time() - fast_start
                    print("Fast time: {}".format(f_time))
                    temp_f_time.append(f_time)

                naive_time.append(temp_n_time)
                fast_time.append(temp_f_time)

            naive_time = np.array(naive_time)
            fast_time = np.array(fast_time)

            naive_mean = naive_time.mean(axis=1)
            naive_std = naive_time.std(axis=1)

            fast_mean = fast_time.mean(axis=1)
            fast_std = fast_time.std(axis=1)

            power = np.arange(5, e)

            plt.errorbar(power, naive_mean, yerr=naive_std, label="naive")
            plt.errorbar(power, fast_mean, yerr=fast_std, label="fast")
            plt.xlabel("size of test data (power of 2)")
            plt.ylabel("runtime (second)")
            plt.xticks(power)
            plt.title("Runtime for navie FT against fast ft")
            plt.legend(loc='best')
            plt.show()

    def compress(self, image, percentile=0.25, threshold=16):

        """

            :param image: 2D numpy array
            :param percentile: compressing ratio
            :param threshold: threshold for FFT
            :return: image after compressing
        """

        fft_img = self.dft_fast2d(image, threshold=threshold)

        # filtering
        row, col = fft_img.shape

        for r in range(row):
            for c in range(col):
                if (r + c) > (row + col)*percentile:
                    fft_img[r,c] = 0

        return self.idft_fast2d(fft_img.real)

    def denoise(self, image, percentile=0.25, threshold=16, type=1, cap=10000):

        """
            Denoising API using FFT

            :param image: 2D numpy array
            :param percentile: percentile to keep
            :param threshold: threshold for FFT
            :return: imgae after denoising
        """

        fft_img = self.dft_fast2d(image, threshold=threshold)

        # filtering
        row, col = fft_img.shape

        percentile = 0.5 if percentile > 0.5 else percentile
        percentile = 0 if percentile < 0 else percentile

        if type == 1:
            denoise_type = "remove_high_freq"
            for r in tqdm(range(row)):
                for c in range(col):
                    if r < row*percentile or r > row*(1-percentile):
                        fft_img[r, c] = 0
                    if c < col*percentile or c > col*(1-percentile):
                        fft_img[r, c] = 0
            title = '{}: percentile = {}'.format(denoise_type, percentile)
            save = "assignment2/pics/denoising_{}_{}_".format(denoise_type, percentile)+self.image_name

        elif type == 2:
            denoise_type = "remove_low_freq"
            for r in tqdm(range(row)):
                for c in range(col):
                    if r > row*percentile and r < row*(1-percentile):
                        fft_img[r, c] = 0
                    if c > col*percentile and c < col*(1-percentile):
                        fft_img[r, c] = 0
            title = '{}: percentile = {}'.format(denoise_type, percentile)
            save = "assignment2/pics/denoising_{}_{}_".format(denoise_type, percentile)+self.image_name

        elif type == 3:
            denoise_type = "threshold_everything"
            for r in tqdm(range(row)):
                for c in range(col):
                    fft_img[r, c] = fft_img[r, c] if fft_img[r, c] < cap else cap
                    fft_img[r, c] = fft_img[r, c] if fft_img[r, c] > -cap else -cap
            title = '{}: cap = {}'.format(denoise_type, cap)
            save = "assignment2/pics/denoising_{}_{}_".format(denoise_type, cap)+self.image_name

        elif type == 4:
            denoise_type = "threshold_low_freq"
            for r in tqdm(range(row)):
                for c in range(col):
                    if r > row*percentile and r < row*(1-percentile):
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] < cap else cap
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] > -cap else -cap
                    if c > col*percentile and c < col*(1-percentile):
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] < cap else cap
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] > -cap else -cap
            title = '{}: percentile = {}, cap = {}'.format(denoise_type, percentile, cap)
            save = "assignment2/pics/denoising_{}_{}_{}_".format(denoise_type, percentile, cap)+self.image_name

        elif type == 5:
            denoise_type = "threshold_high_freq"
            for r in tqdm(range(row)):
                for c in range(col):
                    if r < row*percentile or r > row*(1-percentile):
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] < cap else cap
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] > -cap else -cap
                    if c < col*percentile or c > col*(1-percentile):
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] < cap else cap
                        fft_img[r, c] = fft_img[r, c] if fft_img[r, c] > -cap else -cap
            title = '{}: percentile = {}, cap = {}'.format(denoise_type, percentile, cap)
            save = "assignment2/pics/denoising_{}_{}_{}_".format(denoise_type, percentile, cap)+self.image_name

        else:
            raise NotImplemented

        plt.title(title)
        plt.imshow(np.abs(self.idft_fast2d(fft_img)))
        plt.savefig(save, bbox_inches='tight')


    def dft_naive1d(self, signal):

        """
            Naive 1D FT

            :param signal: 1D Numpy array
            :return: signal after naive FT
        """

        length = signal.shape[0]
        n = np.arange(length)
        k = n.reshape((length, 1))
        factor = np.exp(-2j * np.pi * k * n / length).astype(np.complex64)
        return np.dot(factor, signal).astype(np.complex64)

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
        odd = self.dft_fast1d(signal[1::2])
        factor = np.exp(-2j * np.pi * np.arange(length) / length).astype(np.complex64)
        return np.concatenate((even + factor[:length // 2] * odd,
                               even + factor[length // 2:] * odd), axis=0)

    def dft_naive2d(self, img):

        """
            2D naive FT

            :param img: 2D numpy array
            :return: img after naive FT
        """

        row, col = img.shape
        output = np.empty([row, col], np.complex64)

        for r in range(row):
            for c in range(col):
                sum = 0
                for n in range(col):
                    for m in range(row):
                        sum += img[m, n] * np.exp(-2j * np.pi * (float(r * m) / row + float(c * n) / col))
                output[r, c] = sum

        return output.astype(np.complex64)

    def __dft_fast2d__(self, img, threshold=16):

        """
            2D Cooley-Tukey FFT

            :param img: 2D numpy array
            :param threshold: minimum split length
            :return: img after 2D Cooley-Tukey FFT
        """
        row, col = img.shape
        if col % 2:
            raise RuntimeError("column of image must be divisible by 2. current: {}".format(col))

        if col <= threshold:
            return np.array([self.dft_naive1d(img[r, :]) for r in range(row)])

        even = self.__dft_fast2d__(img[:, ::2])
        odd = self.__dft_fast2d__(img[:, 1::2])
        factor = np.array([np.exp(-2j * np.pi * np.arange(col) / col) for r in range(row)]).astype(np.complex64)
        return np.concatenate(
            (even + np.multiply(factor[:, :col // 2], odd),
             even + np.multiply(factor[:, col // 2:], odd)), axis=1)

    def dft_fast2d(self, img, threshold=16):
        """
            API for 2D FFT

            :param img: 2D numpy array
            :param threshold: threshold: minimum split length
            :return: img after FFT
        """
        return self.__dft_fast2d__(self.__dft_fast2d__(img, threshold).T, threshold).T

    def idft_naive1d(self, ft_signal):

        """
            Inverse 1D Naive FT

            :param ft_signal: 1D numpy FT array
            :return: ft_signal after inverse 1D naive FT
        """

        length = ft_signal.shape[0]
        return ft_signal.dot(
            np.array([[np.exp(2j * np.pi * i * j / length) for i in range(length)] for j in range(length)])).astype(np.complex64)

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
        factor = np.exp(2j * np.pi * np.arange(length) / length).astype(np.complex64)
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
        output = np.empty([row, col], np.complex64)

        for r in range(row):
            for c in range(col):
                sum = 0
                for n in range(col):
                    for m in range(row):
                        sum += ft_img[m, n] * np.exp(2j * np.pi * (float(r * m) / row + float(c * n) / col))
                output[r, c] = sum / (row * col)

        return output.astype(np.complex64)

    def __idft_fast2d__(self, ft_img, threshold=16):
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

        even = self.__idft_fast2d__(ft_img[:, ::2])
        odd = self.__idft_fast2d__(ft_img[:, 1::2])
        factor = np.array([np.exp(2j * np.pi * np.arange(col) / col) for i in range(row)]).astype(np.complex64)
        return np.concatenate(
            (even + np.multiply(factor[:, :col // 2], odd), even + np.multiply(factor[:, col // 2:], odd)), axis=1)

    def idft_fast2d(self, ft_img, threshold=16):
        """
            API For inverse 2D FFT

            :param ft_img: 2D numpy array
            :param threshold: minimum split length
            :return: ft_signal after inverse 2D fast FT
        """
        row, col = ft_img.shape
        return self.__idft_fast2d__(self.__idft_fast2d__(ft_img, threshold).T, threshold).T / row / col

    def validify_img(self, img):
        """
            Validify image to make it has a shape with power of 2

            :param img: 2D numpy array
            :return: 2D numpy array w/ shape of power of 2
        """
        r_row, r_col = np.power([2,2],np.ceil(np.log2(img.shape))).astype(int)
        return cv2.resize(img, (r_col, r_row), interpolation=cv2.INTER_CUBIC)

    # def __fft_shift__(self, img):
    #     row, col = img.shape
    #     row/=2
    #     col/=2
    #     return np.concatenate(
    #         (np.concatenate(
    #             (img[int(row):, int(col):], img[int(row):, :int(col)]),
    #             axis=1),
    #          np.concatenate(
    #              (img[:int(row), int(col):], img[:int(row), :int(col)]),
    #              axis=1)),
    #         axis=0)
        


if __name__ == '__main__':
    config = parseInput()  # Throwing exception for no reason
    try:
        fft = FFTransformer(config)
        fft.start()
    except RuntimeError:
        raise
        exit(0)
