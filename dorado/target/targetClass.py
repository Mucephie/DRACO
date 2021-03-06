import warnings
warnings.filterwarnings('ignore')
import os
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord as acoord
import numpy as np
import astropy.units as un

__all__ = ['Target', 'Fournax']

class Target:
    '''
        The TOI class represents an astronomical target of interest (TOI) and handles the targets relevent attributes.
        Unpassed target parameters will be gathered via astroquery (SIMBAD).


        Attributes
        ----------

        name: str
            name of target in string format.
    '''
    def __init__(self, name):
        self.name = name
        # Call Simbad for relevent data
        try:
            s = Simbad()
            r = s.query_object(self.name)
            self.coords = acoord(ra = r['RA'], dec = r['DEC'], unit = (un.hourangle, un.deg), frame = 'icrs')
        except:
            raise Exception('Error initializing Target.')
        
        self.filters = {}
        self.ts = []

        
    def calcmag(self, filter):
        '''
        calcmag converts the targets flux and associated uncertainty into an 
        instrumental magnitude and uncertainty.

        Parameters
        ----------
        filter: str
            String representation of the relevent filter.

        Returns
        -------
        self.ts[filter]['mag'], self.ts[filter]['mag_unc']

        '''
        flux  = self.ts[self.filters[filter]]['flux']
        flux_unc = self.ts[self.filters[filter]]['flux_unc']
        magnitudes = -2.5 * np.log10(flux / 15)
        mag_unc = flux_unc / ((flux / 15) * 2.30258509)
        self.ts[self.filters[filter]]['mag'] = magnitudes
        self.ts[self.filters[filter]]['mag_unc'] = mag_unc

    def record(self, filer, cr, saveType = 'fits'):
        '''
        record writes each filters timeseries to the dorado working data directory
        for the relevent date and target.

        Parameters
        ----------
        filer: Filer instance
            The active instance of filer to handle writing the file

        cr: Ceres instance
            The relevent instance of Ceres for which the timeseries was derived. The save location 
            will be the working directory for this instance.
            
        saveType: str
            String representation of the file extension to save to. Default is 'fits'. See 
            'astropy.table - write()' for acceptable values.

        Returns
        -------
        None
        '''
        wrkdir = filer.dordir / 'data' / 'wrk'
        if cr.datestr == None:
            cr.datestr = filer.getDateString(cr)
        datestr = cr.datestr
        wrdir = wrkdir / datestr
        filer.mkwrk(cr)
        for fi in self.filters.keys():
            wrts = self.ts[self.filters[fi]]
            fname = str(self.name) + '_' + str(fi) + '-' + str(int(cr.date.mjd)) + '.' + saveType
            wrts.toTable(self.name)
            wrts.table.write(wrdir / fname, overwrite = True)
        
    def export(self, filer, objectClass = None):
        '''
        export will record the TOI object into the dorado targets directory for future use 
        and reference. This function is not implemented yet.

        Parameters
        ----------
        filer: Filer instance
            The active instance of filer to handle writing the target file

        objectClass: str
            Class of object to save the target under. 

        Notes
        -----
        Examples of object classes may be: 'star', 'galaxy', 'exoplanet', 'minor planet', 'satellite', 
        'white dwarf', 'nebula', 'messier_object', 'O_star', 'binary', 'globular_cluster', 'open_cluster', 
        'galaxy_cluster', 'quasar', 'AGN'. 
        
        Users can craft their own object naming schemes.
        '''
        tardir = filer.dordir / 'data/targets'
        if objectClass:
            os.makedirs(tardir / objectClass, exist_ok = True)
            tardir = tardir / objectClass
        



'''
Fournax is an abbreviation of Fourier numerical astronomy extension, its name is a backronym styled to match the constellation 'fornax'. 

'''

from scipy.signal import find_peaks

class Fournax(Target):
    '''
        The Fournax class extends the TOI target class to provide a consistent simple, yet robust interface to targets with regular or semi-regular photometric variability for the purposes of lightcurve/timeseries fourier analysis.  

        Fournax is an abbreviation of Fourier numerical astronomy extension, its name is a backronym styled to match the constellation 'fornax'. 

        Attributes
        ----------

        name: str
            name of target in string format.

        epoch: float or astropy.Time
            Epoch for the targets ephemeris of which the theoretical times of extrema will be extrapolated from.

        period: float
            The period between extrema of interest corresponding to the ephemeris epoch given. 

    '''
    def __init__(self, name, epoch = None, period = None): 
        ## Inherit from Ceres object (date, ts, etc.) 
        Target.__init__(self, name)

        self.freq = [] # Array of observed frequencies (Raw)
        ## NOTE:: Should frequencies be cleaned for aliasing, can the spread of aliasing peak values provide a measure of uncertainty on the fundamental frequency?

        self.Operiod = None # Observed period
        self.Operiod_unc = None # Uncertainty on period
        self.Ofreq = None # observed frequencies


        ## verify ephemeris TODO:: make into a dummy function
        if (epoch == None) and (period == None):
            print('No ephemeris data given for target')

        elif (epoch != None) and (period != None):
            self.epoch = epoch
            self.period = period # Must have units (TODO:: consider falling back to default unit if none)
            ## should these values be combined into an ephemeris dictionary to accomodate for an observational period to be determined later?

        elif (epoch != None):
            self.epoch = epoch 
            print('Period data not given.')
        elif (period != None):
            self.period = period
            print('Epoch data not given.')

        else:
            print('Unknown ephemeris error encountered. Please report via Dorado Github issues page.')
            print('Period given: ', period)
            print('Epoch given: ', epoch)

        
    def OMinusC(self, filter):
        '''
            OMinusC takes observed time(s) of max light for a repeating variable star and ephemeris data and returns O-C values as well as the corresponding cycle.



            Returns
            -------

            cycle: float, list, or array
                    The cycle corresponding to the time(s) of max light

            OmC: float, list, or array
                    The O-C value for the time(s) of max light
        '''

        ## TODO:: accomodate an array of toml values. This will shift this function from returning values to a wrapper function to setting values.
        
        cycle_ref = (self.ts[self.filters[filter]].toml - self.epoch) / self.period
        cycle = np.round(cycle_ref)
        OmC = self.ts[self.filters[filter]].toml - (self.epoch + cycle * self.period)

        self.ts[self.filters[filter]].OmC = OmC
        self.ts[self.filters[filter]].cycle = cycle
   
    def superfit(self, filter, terms, s):
        '''
            superfit takes a raw timeseries and performs a multistep smoothed fit of the data
            which includes a spline fit tailored with the curvature of knots from a spline
            fit of a Fourier fit. The result is then expanded and then convoluted with a
            'blackman' window function.
            Parameters
            ----------
            x, y: array
                    timeseries arrays to be fit
            terms: int
                    terms to retain in the fourier fit.
            s: int
                    new data array size 
            Returns
            -------
            X, Y: array
                    The superfit timeseries arrays.
        '''

        ## NOTE:: The name is tacky.
        ## TODO:: accomodate flux uncertainties
        ## TODO:: Zero mean of signal.

        y = self.ts[self.filters[filter]].flux
        x = self.ts[self.filters[filter]].times ## TODO:: convert to float friendly format like mjd

        # Fourier fit the data to model curvature
        f = np.fft.rfft(y)
        # Null or zero coefficients above ammount of series "terms"
        # This corresponds to undesired high-frequency terms
        f[terms+1:] = 0
        # Collapse back into function space, result is smoothed Fourier curve
        F = np.fft.irfft(f)
        # Create a spline fit of the fourier fit to extract knots
        tispl = InterpolatedUnivariateSpline(x[:len(F)], F, k = 5)
        # feed knots into spline of raw data
        LSQspl = LSQUnivariateSpline(x, y, tispl.get_knots()[1:-1]) 

        X = np.linspace(np.min(x), np.max(x), s)
        Y = self.smooth(LSQspl(X), window = 'blackman')[5:-5]

        self.ts[self.filters[filter]].fit_flux = Y
        self.ts[self.filters[filter]].fit_times = X

    def smooth(self, x, window_len=11, window='hanning'):
        """smooth the data using a window with requested size.
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
        output:
        the smoothed signal
        example:
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        see also: 
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
        2017-07-13 (last modified), 2006-10-31 (created)
        Section author: Unknown[1], GaelVaroquaux, Unknown[142], Unknown[143], Unknown[144], Unknown[145], Unknown[146], Unknown[147], WesTurner, Christian Gagnon, clecocel
        """
        ## Should this be removed from the class and instead be relegated to being a utility? Can this utiity be located in Dorado dependencies?
        if x.ndim != 1:
                raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
                raise ValueError("Input vector needs to be bigger than window size.")


        if window_len<3:
                return x


        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                raise ValueError("Window is none of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


        s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]
        # print(len(s))
        if window == 'flat': # moving average
                w = np.ones(window_len,'d')
        else:
                w = eval('np.' + window +'(window_len)')

        y = np.convolve(w/w.sum(), s, mode='valid')

        return y

    def analyze(self, filter, graphical = True):

        self.superfit(filter = filter, terms = len(self.flux)/3, s = len(self.flux))
        # Find times of max light
        self.tomlFind(filter = filter)
        # calculate O-C
        self.OMinusC(filter = filter)
        # frequency analysis
        self.fourFind(filter = filter)
    
    def fourFind(self, filter, fitted = True):
        if fitted and (self.ts[self.filters[filter]].fit_flux != []):
            Y = self.ts[self.filters[filter]].fit_flux
            X = self.ts[self.filters[filter]].fit_times 
        else:
            Y = self.ts[self.filters[filter]].flux
            X = self.ts[self.filters[filter]].times 
             
        # Set up a Fourier power spectra from photometric amplitude values
        # Compute real valued Fourier transform
        f = np.fft.fft(Y)
        p = np.square(np.abs(f))
        # timestep currently defaults to units of days, whereas exposure time is in seconds
        timestep = (np.mean(self.ts[self.filters[filter]].exptimes) * un.sec).to(un.day).value

        # Build an array of frequencies to plot against
        freq_vec = np.fft.fftfreq(len(Y), d = timestep)

        # find frequency peaks
        peaks, _ = find_peaks(p, height = np.mean(p))

        # Return frequency vector for plotting?

    def tomlFind(self, filter, fitted = True):
        if fitted and (self.ts[self.filters[filter]].fit_flux != []):
            Y = self.ts[self.filters[filter]].fit_flux
            X = self.ts[self.filters[filter]].fit_times 
        else:
            Y = self.ts[self.filters[filter]].flux
            X = self.ts[self.filters[filter]].times 
        
        peaks, _ = find_peaks(Y, height = 1.1 * np.mean(Y))

        toml = X[peaks]

        self.ts[self.filters[filter]].toml = toml