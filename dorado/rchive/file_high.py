import os
import datetime
from astropy.nddata import CCDData
from astropy.io import fits
import astropy.units as u
import numpy as np

__all__ = ['mkwrkdir', 'get_night', 'checkdir', 'get_series', 'write_series', 'get_im', 'file_string']

def mkwrkdir(datadir):
        """
        mkwrkdir creates standard data processing working directories.
        
        Parameters
        ----------
        datadir: string
                Path to data directory to make working folder.

        Returns
        -------
        None
        """
        # night, expath = ''
        stardir = os.getcwd()

        path = datadir # + night + '/' + expath # + '/'
        os.chdir(path)
        os.mkdir(path + '/wrk')
        path = path + '/wrk'
        os.mkdir(path + '/bias')
        os.mkdir(path + '/flats')
        os.mkdir(path + '/lights')
        os.mkdir(path + '/calibrated')
        os.mkdir(path + '/aligned')
        # os.mkdir(path + '/stars')
        # os.mkdir(path + '/results')

        os.chdir(stardir)

def get_night():
        """
        get_night obtains a timestring for the most recent(previous) night.

        Parameters
        ----------
        None

        Returns
        -------
        night: string
                Timestring for the most recent night.
        """
        # currently does not support first/last of the month
        date = datetime.date.today()
        year = date.year
        month = date.month
        date2 = date.day
        date1 = date2 - 1
        night = str(year) + '-' + str(month) + '-' + str(date1) + '+' + str(date2)
        return night

def checkdir(directory):
        """
        checkdir returns lists

        Parameters
        ----------
        directory: string
                Path to data directory to make working folder.

        Returns
        -------
        bias, flats, lights: arrays
                Arrays containing the filestrings for the bias, flats, and lights.
        """ 
        path = directory # + '/' + night + '/' + expath
        print(path)
        dirlist = os.listdir(path)
        bias = [s for s in dirlist if 'BIAS' in s]
        if len(bias)==0:
                bias = [s for s in dirlist if 'Bias' in s]
        if len(bias)==0:
                bias = [s for s in dirlist if 'Bias' in s]
        flats = [s for s in dirlist if 'FLAT' in s]
        if len(flats)==0:
                flats = [s for s in dirlist if 'FlatField' in s]
        lights = [s for s in dirlist if (np.invert('FLAT' in s)) and (np.invert('Flat' in s)) and (np.invert('BIAS' in s)) and (np.invert('Bias' in s)) and ('.FIT' in s) ]
        if len(lights)==0:
                lights = [s for s in dirlist if (np.invert('FLAT' in s)) and (np.invert('Flat' in s)) and (np.invert('BIAS' in s)) and (np.invert('Bias' in s)) and ('.fit' in s) ]
        if len(lights)==0:
                lights = [s for s in dirlist if (np.invert('FLAT' in s)) and (np.invert('Flat' in s)) and (np.invert('BIAS' in s)) and (np.invert('Bias' in s)) and ('.fits' in s) ]
        if len(lights)==0:
                lights = [s for s in dirlist if (np.invert('FLAT' in s)) and (np.invert('Flat' in s)) and (np.invert('BIAS' in s)) and (np.invert('Bias' in s)) and ('.FITS' in s) ]
        print('\ndirlist: ', len(dirlist))
        print('\nbias\': ', len(bias))
        print('\nflats: ', len(flats))
        print('\nlights: ', len(lights))
        print('\ntotal: ', len(lights) + len(flats) + len(bias))

        return bias, flats, lights

def get_series(directory, imlist, unit = u.adu):
        """
        plate_solve takes fits image file data and the corresponding file string to the data and calls nova.astrometry.net to obtain and then integrate WCS into the HDU.

        Parameters
        ----------
        directory: filestring
                Path to data directory containing files.
        imlist: array[string]
                array of filestrings for images.
        unit: astropy.unit
                unit for the CCDdata.
        Returns
        -------
        series: array[CCDdata]
                The CCDdata.
        """
        # directory, night, imlist, expath = '', unit = u.adu
        ## rewrite to match get series in reduce_series
        stardir = os.getcwd()
        # print(stardir)
        path = directory # + '/' + night + '/' + expath
        # print(path)
        os.chdir(path)
        series = []
        for i in range(len(imlist)):
                # os.chdir(path)
                hdu = CCDData.read(imlist[i], unit=unit)
                series.append(hdu)
        # series = ccdproc.ImageFileCollection(filenames=imlist)
        os.chdir(stardir)


        return series

def write_series(directory, series, target):
        """
        write_series intakes a series of CCD images, a target name for filestring 
        creation and a data directory path and writes the series to the directory.
        
        Parameters
        ----------
        directory: filestring
                Path to the directory.
        series: array[CCDdata]
                Data series to write.
        target: String
                Target name to use in the file name prefix.

        Returns
        -------
        None
        """

        #directory, night, series, target
        stardir = os.getcwd()
        # caldir = directory + night + '/wrk/calibrated'
        os.chdir(directory)
        for i in range(len(series)):
                series[i].write(target + '_' + str(i) + '.calibrated.fit')


        os.chdir(stardir)

def get_im(directory, imname):
        """
        get_im intakes a filename and directory of a fits image and returns the 
        data and header of the image.
        To be depreciated.

        Parameters
        ----------
        directory: filestring
                Path to the image.
        imname: filestring
                Image filestring.
        Returns
        -------
        hdu_data: hdu.data
                The fits image data.
        hdu_header: hdu.data
                The fits image data.
        """
        os.chdir(directory)
        file_string = imname
        hdu_data = fits.getdata(file_string)
        hdu_header = fits.getheader(file_string)

        return hdu_data, hdu_header

def file_string(directory, imname):
        """
        file_string takes a directory filestring and image filename and combines 
        them into a single filestring.
        To be depreciated.

        Parameters
        ----------
        directory: filestring
                Path to the image.
        imname: filestring
                Image filestring.
        Returns
        -------
        path: filestring
                combined filestring.
        """
        # directory, night, im, expath = ''
        # this is a temporary function for ease of testing
        path = directory + imname
         # path = directory + '/' + night + '/' + expath + im
        return path

# def lightcurve_save
# def timing/logging