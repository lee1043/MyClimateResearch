import cdms2
import genutil
import math
import MV2
import numpy as np
import os
import requests
import vcs

from scipy import signal
from scipy.stats import chi2

def readDataTextIn(f):
    d=[]
    for line in f:
        line = line.strip()
        columns = line.split()
        ts = columns[0]
        data = float(columns[1])
        d.append(data)
    f.close()

    d = np.array(d)
    return d

def taper(data_in,t_frac):
    """ 
    INPUT TIME SERIES OF LENGTH IKT TO APPLY A SPLIT-COSINE BELL TAPER
    TO REDUCE LEAKAGE (see Bloomfield, p.84-85, 116)

    data is the time series of data that is tapered (input and output)
    ikt is the number of time points (input)
    t_fract the total fraction of data to be tapered (input)
    """ 
    data = data_in.copy()
    ikt = len(data)

    if((t_frac <= 0.0) or (t_frac > 1.0)):
        pass
    else:
        m=int(t_frac*float(ikt)+0.5)/2
        for i in range(m):
            weight=0.5-0.5*math.cos(math.pi*(float(i)-0.5)/float(m))
            data[i]=data[i]*weight
            data[ikt-1-i]=data[ikt-1-i]*weight

    return (data)

def lag1_autocorrelation(x):
    result = float(genutil.statistics.autocorrelation(x, lag=1)[-1])
    return result

def rednoise(VAR,NUMHAR,R1):
    """
    Modification of K. Sperber's FORTRAN code:
      
    THIS PROGRAM IS USED TO CALCULATE THE RED NOISE SPECTRUM OF 
    AN INPUT SPECTRUM. 

    - var    : array of spectral estimates (input)
    - numhar : number of harmonics (input)
    - r1     : lag correlation coefficient (input)
    - rn     : array of null rednoise estimates (output)
    """
    WHITENOISE = sum(VAR)/float(NUMHAR)
    
    """
    CALCULATE "NULL" RED NOISE
    """
    R1X2 = 2.*R1
    R12 = R1*R1
    TOP = 1. - R12
    BOT = 1. + R12

    RN = []
    for K in range(NUMHAR):
        RN.append(WHITENOISE*(TOP/(BOT - R1X2*float(math.cos(math.pi*K/NUMHAR)))))

    return (RN)

def RedNoiseSignificanceLevel(segments, rn):   
    """
    nu is the number of degrees of freedom (2 in case of an fft). 
    Note: As per Wilks (1995, p. 351, Section 8.5.4) when calculating  
    the mean of M spectra and rednoise estimates nu will be nu*M (input)
    
    factor is the scale factor by which the rednoise must be multiplied by to 
    obtain the 95% rednoise confidence level (output)
    Note: the returned value is the reduced chi-square value
    
    95% Confidence CHI-SQUARED FOR NU DEGREES OF FREEDOM 
    """    
    
    p = 0.050
    nu = 2 * len(segments) # Degree of freedom
    factor = chi2.isf(p, nu)/nu
    siglevel = MV2.multiply(rn, factor)
    return siglevel

def Get_SegmentAveraged_PowerSpectrum_and_RedNoise(d, SegmentLength, TaperingRatio, SegmentOverlapping=False):
    seg_starting_i = []
    segments = []
    freqs_segs = 0
    psd_segs = 0
    rn_segs = 0
    num_segs=0
    r1_segs = [] # Lag-1 autocorrelation

    if SegmentOverlapping:
        jump = SegmentLength/2
    else:
        jump = SegmentLength

    for i in range(0,len(d),jump):
        ie = i + SegmentLength
        if ie <= len(d):
            seg_starting_i.append(i)
            seg_starting_i.append(ie)

            d_i= d[i:ie].copy()
            # Tapering
            d_i = taper(d_i, TaperingRatio)
            segments.append([range(i,ie),d_i])

            # Power spectrum
            freqs_i, psd_i = signal.welch(np.array(d_i), nperseg=len(d_i), noverlap=0, window='boxcar')

            # Red noise
            r1_i = lag1_autocorrelation(d_i)
            rn_i = rednoise(psd_i, len(freqs_i), r1_i)
            r1_segs.append(float(r1_i))
            
            # Collect power spectrum and red noise of each segment to average later
            freqs_segs = MV2.add(freqs_i,freqs_segs)
            psd_segs = MV2.add(psd_i,psd_segs)
            rn_segs = MV2.add(rn_i,rn_segs)

            # Count number of segments to be used for averaging
            num_segs += 1
            
            print 'segment (num)', i, ie, '(', num_segs, ')'

    freqs_avg = MV2.divide(freqs_segs,num_segs)
    psd_avg = MV2.divide(psd_segs,num_segs)
    rn_avg = MV2.divide(rn_segs,num_segs)
    r1_avg = sum(r1_segs)/float(len(r1_segs))
    
    return segments, np.array(freqs_avg), np.array(psd_avg), np.array(rn_avg), r1_avg

def FindHalfPoint(y,freqs):
    x = range(len(y)) # harmonics    
    asum = sum(y) # sum of powers
    
    for i, xi in enumerate(x):
        ai = sum(y[0:i+1]) # accumulate powers for harmonic 0 to i
        if ai == asum/2.:
            hp = x[i]
            hpf = freq[i]
            break
        elif ai > asum/2.:
            w2 = asum/2./ai
            hp2 = x[i]*w2
            hp2f = freqs[i]*w2
            
            w1 = asum/2./sum(y[0:i]) # accumulate powers for harmonic 0 to i-1
            hp1 = x[i-1]*w1
            hp1f = freqs[i-1]*w1

            hp = (hp1+hp2)/2.
            hpf = (hp1f+hp2f)/2.

            break
    return hp, hpf
