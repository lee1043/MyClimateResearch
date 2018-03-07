import matplotlib.pyplot as plt

from lib_psd import *
from lib_psd_plot import *

#f = open('tg_79_07_mseas.190E_240E_5N_5S.nino3.4','r')
f = open('soi_slp_79_07_mseas.tahiti-darwin_norm', 'r')
d = readDataTextIn(f)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(np.array(d), 'k', label='raw')
ax.legend()
fig.savefig('test1.png')

# Power spectrum analysis
segments, freqs, psd, rn, r1 = Get_SegmentAveraged_PowerSpectrum_and_RedNoise(
    d, SegmentLength=len(d), TaperingRatio=0.98)

siglevel = RedNoiseSignificanceLevel(segments, rn)

print 'lag-1 auto-correlation :', r1

# Find half point
hp, hpf = FindHalfPoint(psd, freqs)

print 'half point (harmonic) :', hp
print 'half point (freq) :', hpf

# Max psd
psd_max = max(psd)
print 'max psd :', psd_max

# Plot
plot_psd(freqs, psd, rn, siglevel, r1=r1, hpf=hpf, logScale=True, seg_length_yr=len(d)/12, AnnotatePeaks=True)

plt.savefig('test2.png')
