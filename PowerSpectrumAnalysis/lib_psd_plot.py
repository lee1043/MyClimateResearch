import matplotlib.pyplot as plt
import numpy as np

from pylab import rcParams
rcParams['figure.figsize'] = 15, 6
rcParams['axes.titlepad'] = 50
rcParams['axes.titlesize'] = 20
rcParams['axes.labelsize'] = 15
rcParams['lines.linewidth'] = 3
rcParams['lines.markersize'] = 10
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14

def plot_psd(freqs, psd, rn, siglevel,
             r1=None, hpf=None,
             logScale=False, yaxislabel='Power', seg_length_yr=50,
             AnnotatePeaks=False, num_peak_to_plot=5,
             title='PSD: power spectral density', outfile='test_plot.png'):
    
    freqs = np.array(freqs)
    psd = np.array(psd)
    rn = np.array(rn)
    siglevel = np.array(siglevel)
    
    fig = plt.figure(figsize=(6, 5))
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    
    new_tick_labels = [seg_length_yr]
    #for yr in [100, 10, 5, 3, 2, 1, 0.5]:
    for yr in [10, 5, 3, 2, 1, 0.5]:
        if yr < seg_length_yr:
            new_tick_labels.append(yr)
    
    if logScale:
        ax1.set_xscale('log')
        ax2.set_xscale('log')
        ax2.get_xaxis().set_tick_params(which='minor', size=0)
        ax2.get_xaxis().set_tick_params(which='minor', width=0) 

    ax1.plot(freqs, psd, c='k')
    ax1.plot(freqs, rn, c='red')
    ax1.plot(freqs, siglevel, c='green')
        
    new_tick_locations = 1/(np.array(new_tick_labels)*12.)
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(new_tick_locations)
    ax2.set_xticklabels(new_tick_labels)    

    if AnnotatePeaks:

        # Mark maximum peak
        max_peak_psd = max(list(psd))
        max_peak_psd_index = list(psd).index(max_peak_psd)
        max_peak_freq = list(freqs)[max_peak_psd_index]
        ax1.plot(max_peak_freq, max_peak_psd, 'ro', mfc='none', markersize=20)

        # Identify all peaks
        peak = (psd > np.roll(psd,1)) & (psd > np.roll(psd,-1))
        peak_indecis = peak.nonzero()[0]

        # Save peaks
        peak_freqs_psd=[]
        for i in peak_indecis:
            peak_freqs_psd.append((freqs[i],psd[i]))

        # Sort peaks by magnitude: sort a list of tuples by the 2nd item in descending order
        peak_freqs_psd = sorted(peak_freqs_psd, key=lambda x: x[1], reverse=True) 

        # Mark max to N-th max peaks
        for i in range(num_peak_to_plot):
            freqs_i = peak_freqs_psd[i][0]
            psd_i = peak_freqs_psd[i][1]
            ax1.plot(freqs_i, psd_i, 'ro')

            # Annotate periods of peaks
            number = "%.1f" % (1./(freqs_i*12.))  # period [year]
            ax1.annotate(str(number)+'yr',
                    xy=(freqs_i, psd_i),
                    xytext=(freqs_i*0.9, psd_i*1.1),
                    xycoords='data', textcoords ='data')

        ax1.set_ylim(top=max_peak_psd*1.1+1)

    if logScale:
        ax1.set_xlim(right=freqs[-1])
    else:
        ax1.set_xlim(0,1/12.)

    ax1.set_ylim(bottom=0)
    ax1.set_ylabel(yaxislabel)
    ax1.set_xlabel('Frequency (cycles mo$^-$$^1$)')
    ax2.set_xlabel('Period (years)')
    plt.title(title)

    ymin, ymax = plt.ylim()
    xmin, xmax = plt.xlim()

    # Statistics on plot
    xt = 0.75 # x location for text, 0(left)~1(right) in graph
    yt = 0.9 # y location for text, 0(bottom)~1(top) in graph

    # lag-1 auto-correlation
    if r1 is not None:
        plt.text(xt, yt, 'r1='+str("%.2f" % r1), fontsize=12, 
                 horizontalalignment='left', verticalalignment='center', 
                 transform=ax1.transAxes)
        yt = yt-0.1

    # half point period and frequency
    if hpf is not None:
        plt.text(xt, yt, 'hp (yr)='+str("%.1f" % (1./(hpf*12))), fontsize=12, 
                 horizontalalignment='left', verticalalignment='center', 
                 transform=ax1.transAxes)
        ax1.axvline(hpf, c='b', linestyle='--')
        yt = yt-0.1

    # max power
    plt.text(xt, yt, 'P$_{max}$='+str("%.2f" % max_peak_psd), fontsize=12, 
             horizontalalignment='left', verticalalignment='center', 
             transform=ax1.transAxes)
    yt = yt-0.1

    # accumulated total power
    plt.text(xt, yt, 'P$_{tot}$='+str("%.2f" % sum(psd)), fontsize=12, 
             horizontalalignment='left', verticalalignment='center', 
             transform=ax1.transAxes)

    # Save plot
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()
