import json
import matplotlib.pyplot as plt
import os
import sys
from pylab import rcParams

# Plot
rcParams['figure.figsize'] = 15, 6
rcParams['axes.titlepad'] = 20
rcParams['axes.titlesize'] = 20
rcParams['axes.labelsize'] = 15
rcParams['lines.linewidth'] = 2
rcParams['lines.markersize'] = 10
rcParams['xtick.labelsize'] = 14
rcParams['ytick.labelsize'] = 14

# modes
modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']
stats = ['halfpoint_yr', 'lag1-auto_correlation', 'peak_max_power']

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
  
  # Create Output directory
  try:
    os.makedirs(os.path.join(outdir,mode))
  except:
    pass
    
  # Read
  json_file = os.path.join(datadir, mode+'_'+defaultObsData, mode+'_psd.json')
  with open(json_file, 'r') as f:
    d = json.load(f)
    
  for stat in stats:

    s = [] # List of values for each bar
    MinMaxFind = [] # List of simply appended all statistical numbers for later use of min, max finding
    
    for i, model in enumerate(['obs']+sorted(d['RESULTS'].keys(), key=lambda s: s.lower())):
      if model == 'obs':
        stat_number = d['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat]
        s.append(('obs',stat_number))
        MinMaxFind.append(stat_number)
      else:
        run_stats = []
        for run in sorted(d['RESULTS'][model].keys()):
          stat_number = d['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo'][stat]
          plt.plot(i,stat_number,'ko', markersize=5, markeredgecolor='k')
          run_stats.append(stat_number)
          MinMaxFind.append(stat_number)
        runs_ave = sum(run_stats)/float(len(run_stats))
        s.append((model, runs_ave))
    
    plt.bar(range(len(s)), [val[1] for val in s], align='center',color='gray')
    plt.bar(0,s[0][1],color='k')
    plt.xticks(range(len(s)), [val[0] for val in s])
    plt.xticks(rotation=90)
    plt.axhline(s[0][1],c='k',label=defaultObsData)
    plt.title(mode+', '+stat)
    plt.xlabel('Model')
    if stat == 'halfpoint_yr':
      plt.ylabel('Period (Year)')
    elif stat == 'peak_max_power':
      plt.ylabel('Power')
    
    # Add alternative observation datasets
    colors = ['r', 'b']
    for c, alterObsData in enumerate(alterObsDataSets):
      json_file = os.path.join(datadir, mode+'_'+alterObsData, mode+'_psd.json')
      with open(json_file, 'r') as f:
        d2 = json.load(f)
      tmp = d2['REF']['obs']['defaultReference'][mode]['pc']['mo'][stat]
      plt.plot(0, tmp, colors[c]+'o', markersize=10, markeredgecolor='k', label=alterObsData)
    
    if stat == 'lag1-auto_correlation':
      yaxisbottom = min(MinMaxFind)*0.9
      plt.ylim(yaxisbottom,1)
    
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(outdir,mode,mode+'_barChart_'+stat+'.png'))
    plt.clf()
