import json
import matplotlib.pyplot as plt
import os
import sys
from pylab import rcParams

# Plot
rcParams['figure.figsize'] = 8, 6
rcParams['axes.titlepad'] = 20
rcParams['axes.titlesize'] = 20
rcParams['axes.labelsize'] = 15
rcParams['lines.linewidth'] = 2
rcParams['lines.markersize'] = 10
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14

modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']

stat = 'halfpoint_yr' # x-axis

TaperTest = False
SegTest = True
 
if TaperTest:
  # Tapering Compare
  datadir1 = './result_20180321_taper20_NoSegmenting'
  datadir2 = './result_20180307_tapering98p'
  data1 = 'taper20'
  data2 = 'taper98'
  outdir = './analysis_compare'
elif SegTest:
  # Segmentation Compare
  datadir1 = './result_20180321_taper20_NoSegmenting'
  datadir2 = './result_20180321_taper20_HalpLengthSegment'
  data1 = 'NoSeg'
  data2 = 'HalfLengthSeg'
  outdir = './analysis_compare'

for mode in modes:

  if mode in ['PDO']:
    defaultObsData = 'HadISSTv1.1'
    alterObsDataSets = ['HadISSTv2.1', 'ERSSTv3b']
  elif mode in ['NAM', 'NAO', 'PNA', 'SAM']:
    defaultObsData = 'NOAA-CIRES_20CR'
    alterObsDataSets = ['ERA20C', 'HadSLP2r']
  
  # Read
  json_file1 = os.path.join(datadir1, mode+'_'+defaultObsData, mode+'_psd.json')
  json_file2 = os.path.join(datadir2, mode+'_'+defaultObsData, mode+'_psd.json')

  with open(json_file1, 'r') as f1:
    d1 = json.load(f1)

  with open(json_file2, 'r') as f2:
    d2 = json.load(f2)
  
  s1 = [] # List of values for each bar
  s2 = [] # List of values for each bar
  
  for i, model in enumerate(['obs']+sorted(d1['RESULTS'].keys(), key=lambda s: s.lower())):
    if model == 'obs':
      stat_number1 = d1['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat]
      stat_number2 = d2['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat]
      s1.append(('obs',stat_number1))
      s2.append(('obs',stat_number2))
    else:
      run_stats1 = []
      run_stats2 = []
      for run in sorted(d1['RESULTS'][model].keys()):
        stat_number1 = d1['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo'][stat]
        stat_number2 = d2['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo'][stat]
        #plt.plot(i,stat_number,'ko', markersize=5, markeredgecolor='k')
        run_stats1.append(stat_number1)
        run_stats2.append(stat_number2)
        plt.plot(stat_number1, stat_number2, 'o', c='k', markersize=2)
  
      runs_ave1 = sum(run_stats1)/float(len(run_stats1))
      runs_ave2 = sum(run_stats2)/float(len(run_stats2))
      s1.append((model, runs_ave1))
      s2.append((model, runs_ave2))
  
  plt.scatter([s1[i][1] for i in range(len(s1))], [s2[i][1] for i in range(len(s2))], c='gray')
  plt.plot(s1[0][1], s2[0][1], 's', c='k',label=defaultObsData, markersize=10)
  plt.title(mode)
  plt.xlabel(stat+'_'+data1)
  plt.ylabel(stat+'_'+data2)
  
  plt.legend(loc=4)
  plt.tight_layout()

  # Create Output directory
  try:
    os.makedirs(os.path.join(outdir))
  except:
    pass

  plt.savefig(os.path.join(outdir, mode+'_Scatter_'+data1+'_vs_'+data2+'.png'))
  #plt.show()
  plt.clf()
