from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astropy.table import Table
# from matplotlib import cm
# from astropy.visualization import astropy_mpl_style
# from astropy.utils.data import get_pkg_data_filename
# from matplotlib.colors import LogNorm
# import matplotlib.colors as colors

from astroscrappy import detect_cosmics
from astropy.nddata import CCDData
from ccdproc import Combiner
import ccdproc
import astropy.units as u
from astropy.utils.misc import isiterable
from astropy.visualization import astropy_mpl_style

import skimage.io

import os
import sys
import argparse
import astropy.io.fits as pyfits
import skimage.morphology as morph
import skimage.exposure as skie
from scipy.ndimage import median_filter

from scipy.ndimage import gaussian_filter
from skimage import data # might not be needed
from skimage import img_as_float
from skimage.morphology import reconstruction
from scipy import ndimage

from skimage.feature import blob_dog, blob_log, blob_doh
# from scipy.stats import mode

import draco

directory = 'C:/Users/mucep/Offline/2018-12-04+05'
star = 'DYPEG'
filename = 'FstarLum'

header, data = draco.get_im('', filename)

def checkdir(directory):
    dirlist = os.listdir(directory)
    bias = [s for s in dirlist if 'BIAS.FIT' in s]
    flats = [s for s in dirlist if 'FLAT.FIT' in s]
    lights = [s for s in dirlist if (np.invert('FLAT.FIT' in s)) and (np.invert('BIAS.FIT' in s)) and ('.FIT' in s) ]
    # [s for s in dirlist if 'BIAS.FIT' in s]
    print('\ndirlist: ', len(dirlist))
    print('\nbias\': ', len(bias))
    print('\nflats: ', len(flats))
    print('\nlights: ', len(lights))
    print('\ntotal: ', len(lights) + len(flats) + len(bias))

    return bias, flats, lights


def get_series(directory, imlist):
    os.chdir(directory)
    file_string = imlist[0]
    temp = fits.getdata(file_string)
    temp_size = temp.shape
    # print(temp_size)

    reduc_file = np.zeros((temp_size[0], temp_size[1], len(imlist)))

    for i in range(1, len(imlist)):
        file_string = imlist[i]
        reduc_file[:, :, i] = fits.getdata(file_string)

    return reduc_file

def starSeeker(data):
    # mf = median_filter(data, size=10)
    # data = draco.imarith(data, '-', mf)
    limg = np.arcsinh(data)
    limg = limg / limg.max()
    low = np.percentile(limg, 10)
    high = np.percentile(limg, 99.5)
    opt_img  = skie.exposure.rescale_intensity(limg, in_range=(low,high))
    lm = morph.local_maxima(opt_img)
    x1, y1 = np.where(lm.T == True)
    v = limg[(y1,x1)]
    lim = 0.85
    x2, y2 = x1[v > lim], y1[v > lim]

    return x2, y2, opt_img



def starSeeker2(data):
    mf = median_filter(data, size= 15)
    datamf = data - mf
    limg = np.arcsinh(datamf)
    limg = limg / limg.max()
    low = np.percentile(limg, 1)
    high = np.percentile(limg, 99.5)
    opt_img  = skie.exposure.rescale_intensity(limg, in_range=(low,high))


    stars =  blob_log(opt_img, max_sigma=25, min_sigma = 5, num_sigma=10, threshold=.2)
    # stars =  blob_dog(opt_img, max_sigma=30, threshold=.2)
    # Compute radii in the 3rd column.
    stars[:, 2] = stars[:, 2] * np.sqrt(2)

    y2, x2, r = stars[:, 0], stars[:, 1], stars[:, 2]

    limg = np.arcsinh(data)
    limg = limg / limg.max()
    low = np.percentile(limg, 0.1)
    high = np.percentile(limg, 99.5)
    opt_img  = skie.exposure.rescale_intensity(limg, in_range=(low,high))

    return x2, y2, r, opt_img

def plt_stars(data, x, y, r):
    plt.style.use(astropy_mpl_style)
    plt.figure()
    plt.imshow(data, cmap='viridis', vmin=0)
    plt.colorbar()
    plt.grid(False)
    
    for i in range(len(x)):
        circlei=plt.Circle((x[i],y[i]), r[i], edgecolor='r', alpha = 0.5)
        plt.gcf().gca().add_artist(circlei)

    plt.show()


bias_list, flats_list, lights_list = checkdir(directory)
lights = get_series(directory, lights_list)

print('\nStarting star identification...')
x, y, r, opt_img = starSeeker2(lights[:, :, 10])
# x, y, r, opt_img = starSeeker2(data)
print('\nNumber of stars: ', len(x))
print('\nStarting ploting...\n')
plt_stars(opt_img, x, y, r)


