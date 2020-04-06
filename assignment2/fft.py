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
        plt.subplot(1,2,1)
        plt.title('origin')
        plt.imshow(original_image)

        if self.mode == 1:
            # mode 1
            plt.show()
        elif self.mode == 2:
            # mode 2
            plt.subplot(1,2,2)
            plt.title('denoising')
            plt.imshow(original_image)
            plt.show()

        elif self.mode == 3:
            # mode 3
            print("3")
        else:
            # mode 4
            print("4")

    def dft_naive(self, original_image):
        pass

    def dft_FFT(self, original_image):
        pass

    def rev_2ddft(self, fft_image):
        row, col = fft_image.shape
        for r in range(row):
            temp = 0
            for c in range(col):
                temp = fft_image[r, c]
        pass
    
    def rowDFT(self,arr):
        arr = np.asarray(arr, dtype=float)
        N = arr.shape[0]
        n = np.arange(N)
        k = n.reshape((N, 1))
        M = np.exp(-2j * np.pi * k * n / N)
        return np.dot(M, arr)

    def rowFFT(self,arr):
        arr = np.asarray(arr, dtype=float)
        N = arr.shape[0]
        
        if N % 2 > 0:
            raise ValueError("size of x must be a power of 2")
        elif N <= 32:  # this cutoff should be optimized
            return self.rowDFT(arr)
        else:
            X_even = self.rowFFT(arr[::2])
            X_odd = self.rowFFT(arr[1::2])
            factor = np.exp(-2j * np.pi * np.arange(N) / N)
            return np.concatenate([X_even + factor[:(int)(N / 2)] * X_odd,
                                   X_even + factor[(int)(N / 2):] * X_odd])



if __name__ == '__main__':
    config = parseInput()  # Throwing exception for no reason
    try:
        fft = FFTransformer(config)
        fft.start()
        x = np.random.random(1024)
    except RuntimeError:
        raise
        exit(0)
