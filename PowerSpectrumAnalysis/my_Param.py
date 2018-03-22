# process control
modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']
#modes = ['PDO']
debug = False 

# input control
NormalizePCts = False

# power spectrum analysis adjustment
TaperingRatio = 0.2 # default is 0.2, i.e., 20%
                    # via Bloomfield, here is the reference suggesting that tapering of 10-20% of the data is a suggested. You can document this in your code, and we can refer to it in the manuscript we prepare.
                    # Tukey, J. W. (1967) An introduction to the calculations of numerical spectrum analysis. In B. Harris, Ed., Spectral Analysis of Time Series. New York, Wiley, pp. 25-46.

SegmentLengthRatio = 1 # default is 1, 0 < ratio <=1, because segment length will be int(len(timeseires)*SegmentLengthRatio)
SegmentOverlapping = False # Default is False, not allowing overlapping segments. When it is True, 50% of each segment overlaps

# output control
outdir = './result_20180321_taper20_NoSegmenting'

# output image switch
#PlotOn_xlog = True
PlotOn_xlog = False
PlotOn_xlinear = True
