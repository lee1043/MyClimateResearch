# process control
modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']
#modes = ['PDO']
debug = False

# input control
NormalizePCts = False

# power spectrum analysis adjustment
TaperingRatio = 0.2 # default is 0.2, i.e., 20%
SegmentLengthRatio = 0.5 # default is 1, 0 < ratio <=1, because segment length will be int(len(timeseires)*SegmentLengthRatio)
SegmentOverlapping = False # Default is False, not allowing overlapping segments. When it is True, 50% of each segment overlaps

# output control
outdir = './result_20180321_taper20_HalpLengthSegment'

# output image switch
PlotOn_xlog = True
PlotOn_xlinear = True
