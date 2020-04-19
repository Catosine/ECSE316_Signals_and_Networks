# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 18:09:19 2020

@author: zhouh
"""
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import cv2
import numpy as np

n_mean = [0.,      
0.00110013,
0.01776717,
0.27381959,
4.53530351,
71.9670761
] 
n_std = [
0.         ,
0.00059572 ,
0.00251474 ,
0.0376833 ,
0.35126841,
3.19783165] 

f_mean = [
1.98054314e-04,
2.99191475e-04 ,
6.83760643e-04 ,
1.09386444e-03,
4.99062538e-03 ,
2.00727224e-02 ,
7.52313137e-02 ,
3.05864573e-01,
1.37216852e+00,
5.54712843,
23.5468519,
96.3020439,
405.394364
]
f_std = [
0.00079226,
 0.00091405 ,
0.0008956  ,
0.00060017 ,
0.00126925 ,
0.0036289,
 0.01077943 ,
0.00933547 ,
0.14737561,
0.52379514,
2.85624341,
8.58681349,
38.62819134
]

n_mean = np.array(n_mean)
n_std = np.array(n_std)
f_mean = np.array(f_mean)
f_std = np.array(f_std)
power = np.arange(1, 14)
plt.errorbar(power, n_mean, yerr=n_std, label="naive")
plt.errorbar(power, f_mean, yerr=f_std, label="fast")
plt.xlabel("size of test data (power of 2)")
plt.ylabel("runtime (second)")
plt.xticks(power)
plt.title("Runtime for navie FT against fast ft")
plt.legend(loc='best')
plt.savefig("assignment2/pics/runtime.png", bbox_inches='tight')
plt.close()

