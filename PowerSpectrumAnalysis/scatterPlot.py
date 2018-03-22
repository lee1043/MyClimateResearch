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

stat1 = 'halfpoint_yr' # x-axis
stat2 = 'lag1-auto_correlation' # y-axis
 
#datadir = './result'
datadir = './result_20180321_taper20_NoSegmenting'
#outdir = './analysis'
outdir = './analysis_20180321_taper20_NoSegmenting'

for mode in modes:

  if mode in ['PDO']:
    defaultObsData = 'HadISSTv1.1'
    alterObsDataSets = ['HadISSTv2.1', 'ERSSTv3b']
  elif mode in ['NAM', 'NAO', 'PNA', 'SAM']:
    defaultObsData = 'NOAA-CIRES_20CR'
    alterObsDataSets = ['ERA20C', 'HadSLP2r']
  
  # Read
  json_file = os.path.join(datadir, mode+'_'+defaultObsData, mode+'_psd.json')
  with open(json_file, 'r') as f:
    d = json.load(f)
  
  s1 = [] # List of values for each bar
  s2 = [] # List of values for each bar
  
  for i, model in enumerate(['obs']+sorted(d['RESULTS'].keys(), key=lambda s: s.lower())):
    if model == 'obs':
      stat_number1 = d['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat1]
      stat_number2 = d['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat2]
      s1.append(('obs',stat_number1))
      s2.append(('obs',stat_number2))
    else:
      run_stats1 = []
      run_stats2 = []
      for run in sorted(d['RESULTS'][model].keys()):
        stat_number1 = d['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo'][stat1]
        stat_number2 = d['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo'][stat2]
        #plt.plot(i,stat_number,'ko', markersize=5, markeredgecolor='k')
        run_stats1.append(stat_number1)
        run_stats2.append(stat_number2)
        plt.plot(stat_number1, stat_number2, 'o', c='k', markersize=2)
  
      runs_ave1 = sum(run_stats1)/float(len(run_stats1))
      runs_ave2 = sum(run_stats2)/float(len(run_stats2))
      s1.append((model, runs_ave1))
      s2.append((model, runs_ave2))
  
  plt.scatter([s1[i][1] for i in range(len(s1))], [s2[i][1] for i in range(len(s2))], c='gray')
  plt.plot(s1[0][1], s2[0][1], 'o', c='k',label=defaultObsData)
  plt.title(mode)
  plt.xlabel(stat1)
  plt.ylabel(stat2)
  
  # Add alternative observation datasets
  colors = ['r', 'b']
  for c, alterObsData in enumerate(alterObsDataSets):
    json_file = os.path.join(datadir,mode+'_'+alterObsData, mode+'_psd.json')
    with open(json_file, 'r') as f:
      d2 = json.load(f)
    tmp1 = d2['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat1]
    tmp2 = d2['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat2]
    plt.plot(tmp1, tmp2, colors[c]+'o', markersize=10, markeredgecolor='k', label=alterObsData)
  
  plt.legend(loc=4)
  plt.tight_layout()

  # Create Output directory
  try:
    os.makedirs(os.path.join(outdir,mode))
  except:
    pass

  plt.savefig(os.path.join(outdir, mode, mode+'_Scatter_'+stat1+'_vs_'+stat2+'.png'))
  #plt.show()
  plt.clf()
