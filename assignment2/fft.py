import argparse
import matplotlib.pyplot as plt
import cv2
import numpy as np


def parseInput():
    choice_helper = {
        1: "[1] (Default) for fast mode where ther image is converted into its FFT form and displayed",
        2: "[2] for denoising where the image is denoised by applying an FFT, truncating high frequencies and then displyed",
        3: "[3] for compressing and saving the image",
        4: "[4] for plotting the runtime graphs for the report"
    }
    parser = argparse.ArgumentParser("fft.py")
    parser.add_argument("-m", type=int, choices=[1, 2, 3, 4], default=1, help='; '.join(choice_helper.values()))
    parser.add_argument("image", type=str, default="moonlanding", metavar="somepic",
                        help="(optional) filename of the image we wish to take the DFT of.")
    return parser.parse_args()


def FFTransformer():
    def __init__(self, config):
        mode = config.m
        pic = config.image
        print("mode: ", mode)
        print("pic: ", pic)


if __name__ == '__main__':
    config = parseInput()  # Throwing exception for no reason
    FFTransformer(config)
