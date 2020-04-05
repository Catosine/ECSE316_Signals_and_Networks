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
    
    def rowdft_naive(arr):
        N = arr.size
        #e^(2ipi/N)
        factor = np.exp(2j*np.pi/N) 
        # array of e^(n*2ipi/N)
        factor_arr = np.array([(factor**index) for index in range(N)])
        # array of sum a*e^(kn2ipi/N)
        res = np.array([sum(arr*(factor_arr**k)) for k in range(N)])
        
        return res


if __name__ == '__main__':
    config = parseInput()  # Throwing exception for no reason
    try:
        fft = FFTransformer(config)
        fft.start()
    except RuntimeError:
        raise
        exit(0)
