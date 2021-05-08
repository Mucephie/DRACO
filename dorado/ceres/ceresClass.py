import warnings
warnings.filterwarnings('ignore')
# import sys
# import os

# import numpy as np
import ccdproc
from astropy.time import Time
from astropy.table import QTable, Table
import astroalign as aa
from astropy.wcs import WCS
from astropy.utils.console import ProgressBar, ProgressBarOrSpinner
# from astropy.coordinates import SkyCoord as acoord
# import astropy.units as un
from astropy.io import fits

from astropy.nddata.ccddata import CCDData

# photometry imports
from photutils.psf import IntegratedGaussianPRF, DAOGroup
from photutils.background import MMMBackground, MADStdBackgroundRMS
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from photutils.psf import IterativelySubtractedPSFPhotometry
from photutils import DAOStarFinder
from astropy.stats import mad_std
# from astroquery.simbad import Simbad

from ..timeseries import timeSeries

'''
Ceres is the handler of image series in Dorado,
'''

__all__ = ['Ceres']

class Ceres:
    '''
        The Ceres class encapsulates a set of astronomical data from a single night of observation.
        Ceres can handle multiple stacks of data in different filters and perform a variety of
        actions on them in an orgainized fashion.

        Attributes
        ----------

        filters: dictionary

        data: Stack array

        bias: CCDdata

        time: 'astropy.Time' 

        datestr: str

        
    '''
    def __init__(self, filters = {}, data = [], bias = None, time = None, datestr = None):
        # metadata
        self.filters = filters
        self.data = data
        self.bias = bias
        self.time = time
        self.datestr = datestr
        
        # location, weather, timezone, camera, observer array

        # refering instance of clippy to call and save later?
        # or call clippy directly and feed it a ceres object

        try:
            self.date = Time(int(self.time.mjd), format = 'mjd')
        except:
            self.date = None
        
    def add_stack(self, stack):
        # eventually stacks themelves should have some metadata 
        # to denote stuff like calibration status
        self.filters[stack.filter] = len(self.data)
        self.data.append(stack)

    def rem_stack(self, filter):
        del self.data[self.filters[filter]]
        # delete time strings

    def calibrate(self, filter):
        # for bla in series: add bias corrected = True to header
        stack = self.data[self.filters[filter]]
        flat = stack.flat
        bias = self.bias
        c_series = []
        with ProgressBar(len(stack.data)) as bar:
            for im in stack.data:
                bar.update()
                im.data = im.data.astype('uint16') 
                flat.data = flat.data.astype('uint16') 
                bias.data = bias.data.astype('uint16') 
                im = ccdproc.ccd_process(im, master_bias = bias, master_flat = flat)
                im.data = im.data.astype('uint16') 
                c_series.append(im)
        self.data[self.filters[filter]].data = c_series
        self.data[self.filters[filter]].calibrated = True

    def imarith(self, filter, operator, operand):
        # mod to check datatype using type()
        # mod to remove im_count and make possible to use single image
        # mod to accomodate CCDdata object
        series = self.data[self.filters[filter]]
        for i in range(len(series)):
            if (operator == '+'):
                series[i].data = series[i].data  + operand
            elif (operator == '-'):
                series[i].data = series[i].data - operand
            elif (operator == '/'):
                series[i].data = series[i].data  / operand
            elif (operator == '*'):
                series[i].data = series[i].data  * operand
        
        self.data[self.filters[filter]] = series

    def getWCS(self, filter, filer, alignto = None, cache = True):
        series = self.data[self.filters[filter]]
        if alignto == None:
            alignto = series.alignTo
        if cache:
            hdulist = fits.open(filer.dordir / 'cache' / 'astrometryNet' / 'solved.fits') 
            self.data[self.filters[filter]].wcs = WCS(hdulist[0].header, hdulist)
            self.data[self.filters[filter]].solved = CCDData.read(filer.dordir / 'cache' / 'astrometryNet' / 'solved.fits')
            hdulist.close()
        else:
            toalign = series.data[alignto]
            fname, cachedir = filer.mkcacheObj(toalign, 'astrometryNet')
            path = [cachedir, fname]
            writearray = [cachedir, 'solved.fits']
            solved, wcs_header = filer.plate_solve(path, writearray = writearray)
            filer.delcacheObj( fname, 'astrometryNet')
            self.data[self.filters[filter]].wcs = WCS(wcs_header)
            self.data[self.filters[filter]].solved = solved

    def align(self, filter, filer, alignto = None, getWCS = True, cache = False):
        series = self.data[self.filters[filter]]
        if alignto == None:
            alignto = series.alignTo
        toalign = series.data[alignto]
        ## TODO :: make this use ceres.getWCS()
        if getWCS:
            if cache:
                toalign =  CCDData.read(filer.dordir / 'cache' / 'astrometryNet' / 'solved.fits', unit = filer.unit)
                hdulist = fits.open(filer.dordir / 'cache' / 'astrometryNet' / 'solved.fits') 
                self.data[self.filters[filter]].wcs = WCS(hdulist[0].header, hdulist)
                hdulist.close()
                self.data[self.filters[filter]].solved = toalign
            else:
                fname, cachedir = filer.mkcacheObj(toalign, 'astrometryNet')
                path = [cachedir, fname]
                writearray = [cachedir, 'solved.fits']
                solved, wcs_header = filer.plate_solve(path, writearray = writearray)
                toalign = solved
                clippy.delcacheObj( fname, 'astrometryNet')
                self.data[self.filters[filter]].wcs = WCS(wcs_header)
                self.data[self.filters[filter]].solved = solved
                # delete cache object
                # save solved to target

        aa_series = []
        ## TODO :: fix this progressbar so it prints on one line then updates that line.
        with ProgressBar(len(series.data)) as bar:
            for image in series.data:
                bar.update()
                try:
                    img, _ = aa.register(image.data, toalign.data)
                    image.data = img
                    aa_series.append(image)
                except:
                    print('Image skipped')

        self.data[self.filters[filter]].data = aa_series
        self.data[self.filters[filter]].aligned = True

    def dorphot(self, filter, toi, control_toi = None, shape = 21):
        # get seeing from PSF
        stack = self.data[self.filters[filter]]
        # if no wcs, complain alot
        w = stack.wcs
        xy = w.wcs_world2pix(toi.coords.ra.deg, toi.coords.dec.deg, 1)
        if control_toi != None:
            xyc = w.wcs_world2pix(control_toi.coords.ra.deg, control_toi.coords.dec.deg, 1)
            pos = Table(names=['x_0', 'y_0'], data = ([float(xy[0]), float(xyc[0])], [float(xy[1]), float(xyc[1])]))

        else:
            pos = Table(names=['x_0', 'y_0'], data = ([float(xy[0])], [float(xy[1])]))

        sigma_psf = 2.0
        bkg_sigma = mad_std(stack.data[0]) 
        daofind = DAOStarFinder(fwhm = 4., threshold = 3. * bkg_sigma)  
        daogroup = DAOGroup(2.0 * sigma_psf * gaussian_sigma_to_fwhm)
        mmm_bkg = MMMBackground()

        psf_model = IntegratedGaussianPRF(sigma = sigma_psf)
        psf_model.x_0.fixed = True
        psf_model.y_0.fixed = True

        fitter = LevMarLSQFitter()
        bkgrms = MADStdBackgroundRMS()

        times = []
        exptimes = []
        ray = []
        decx = []
        x = []
        y = []
        flux = []
        fluxunc = []
        apsum = []
        apsum_unc = []
        # if radec get xy
        itera = 0
        with ProgressBarOrSpinner(len(stack.data), msg = 'Performing PSF photometry') as bar:
            for image in stack.data:
                bar.update(itera)
                itera = itera + 1
                photometry = IterativelySubtractedPSFPhotometry(finder = daofind, group_maker = daogroup, bkg_estimator = mmm_bkg,
                        psf_model = psf_model, fitter = LevMarLSQFitter(), niters = 1, fitshape = (shape, shape))
                results = photometry(image = image, init_guesses= pos)
                [ra, dec] = w.wcs_pix2world(results['x_fit'], results['y_fit'], 1)
                
                times.append(Time(image.header['DATE-OBS']))
                exptimes.append(image.header['EXPTIME'])
                ray.append(ra)
                decx.append(dec)
                x.append(results['x_fit'][0])
                y.append(results['y_fit'][0])

                if control_toi != None:
                    apsum.append(results['flux_fit'][0] - results['flux_fit'][1])
                    flux.append((results['flux_fit'][0] - results['flux_fit'][1])/image.header['EXPTIME'])
                else:
                    apsum.append(results['flux_fit'][0])
                    flux.append(results['flux_fit'][0]/image.header['EXPTIME'])

                fluxunc.append(results['flux_unc'][0]) ## TODO:: modify this to account for exposure time and control
                apsum_unc.append(results['flux_unc'][0])

        # ts = QTable([times, exptimes, x, y, ray, decx, flux, fluxunc], names=('time', 'exptime', 'x', 'y', 'ra', 'dec', 'flux', 'flux_unc'), meta={'name': filter})
        ts = timeSeries(times = times, flux = flux, exptimes = exptimes, x = x, y = y, ra = ray, dec = decx, flux_unc = fluxunc, apsum = apsum, apsum_unc = apsum_unc)
        toi.filters[filter] = len(toi.ts)
        toi.ts.append(ts)

