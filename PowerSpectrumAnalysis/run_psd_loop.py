import cdms2
import glob
import matplotlib.pyplot as plt
import os
import pcmdi_metrics
import sys

from collections import defaultdict
from lib_psd import *
from lib_psd_plot import *

#============================================================
def PowerSpectrumAnalysis(d, debug=False):
#------------------------------------------------------------
  # Power spectrum analysis
  segments, freqs, psd, rn, r1 = Get_SegmentAveraged_PowerSpectrum_and_RedNoise(
      d, SegmentLength=len(d), TaperingRatio=0.98)
  
  # Significance level derived from red noise
  siglevel = RedNoiseSignificanceLevel(segments, rn)
  
  # Find half point
  hp, hpf = FindHalfPoint(psd, freqs)
  
  # Max psd
  psd_max = max(psd)

  if debug:
    print 'lag-1 auto-correlation :', r1
    print 'half point (harmonic) :', hp
    print 'half point (freq) :', hpf
    print 'max psd :', psd_max
  
  return freqs, psd, rn, siglevel, r1, hpf, psd_max
#------------------------------------------------------------

modes = ['NAM']
modes = ['NAO']
modes = ['PNA']
modes = ['SAM']
modes = ['PDO']
modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']

PlotOn = True
#PlotOn = False

outdir = './result'

for mode in modes:

  print mode

  if mode in ['PDO']:
    obs_list = ['HadISSTv1.1', 'HadISSTv2.1', 'ERSSTv3b']
    ver_list = ['3.1', '3.4', '3.0']
  else:
    obs_list = ['NOAA-CIRES_20CR', 'ERA20C', 'HadSLP2r']

  for o, obs_data in enumerate(obs_list):
  
    print mode, obs_data

    # Create Output directory
    try:
      os.makedirs(os.path.join(outdir,mode+'_'+obs_data))
    except:
      pass

    def tree(): return defaultdict(tree)
    var_mode_stat_dic = tree()
  
    if mode in ['NAM', 'NAO', 'PNA', 'SAM']:
      basedir = '/work/lee1043/cdat/pmp/variability_mode/scripts_CleanUp_ParameterFile'
      tier1 = 'result_'+obs_data
      tier2 = mode
      varname = 'psl'
      varname_pc = 'pc'
      obsfileframe = 'MODE_VAR_EOF1_monthly_obs_1900-2005.nc'
      modfileframe = 'MODE_VAR_EOF1_monthly_cmip5_MODEL_historical_REAL_mo_atm_1900-2005_cbf.nc'
    elif mode in ['PDO']:
      basedir = '/work/lee1043/cdat/pmp/variability_mode/scripts_consistency_test_b/SAM_redo_with_late_20C_OBS'
      tier1 = 'result_v'+ver_list[o]+'b_3/result'
      tier2 = mode
      varname = 'ts'
      varname_pc = 'pc1'
      obsfileframe = 'MODE_VAR_EOF1_monthly_obs_1900-2005.nc'
      modfileframe = 'MODE_VAR_EOF1_monthly_cmip5_MODEL_historical_REAL_mo_atm_1900-2005_pseudo.nc'
  
    obsfiles = obsfileframe.replace('MODE',mode).replace('VAR',varname)
    modfiles = modfileframe.replace('MODEL','*').replace('REAL','*').replace('MODE',mode).replace('VAR',varname)
    
    ncfile_list = glob.glob(os.path.join(basedir,tier1,tier2,obsfiles))
    ncfile_list.extend(glob.glob(os.path.join(basedir,tier1,tier2,modfiles)))
    #ncfile_list = [ncfile_list[0]]
    #print 'ncfile_list: ', ncfile_list
    
    for ncfile in sorted(ncfile_list):
    
      #print 'ncfile: ', ncfile
    
      figfilename = ncfile.split('/')[-1].split('.')[0]
      print 'figfilename: ', figfilename
  
      if figfilename.split('_')[4] == 'obs':
          title = mode+', OBS ['+obs_data+']'
      else:
        model = figfilename.split('_')[5]
        run = figfilename.split('_')[7]
        title = mode+', '+model+' ('+run+')'
    
      f = cdms2.open(ncfile)
      d = f(varname_pc)
      f.close()
    
      freqs, psd, rn, siglevel, r1, hpf, psd_max = PowerSpectrumAnalysis(d)
    
      # Plot
      if PlotOn:
        figfile = os.path.join(outdir,mode+'_'+obs_data,figfilename+'.png')
        plot_psd(freqs, psd, rn, siglevel, 
                 r1=r1, hpf=hpf, 
                 logScale=True, seg_length_yr=len(d)/12, 
                 AnnotatePeaks=True, 
                 title=title,
                 outfile=figfile)
      
      # Statistics
      if figfilename.split('_')[4] == 'obs': # observation
        var_mode_stat_dic['REF']['obs']['defaultReference'][mode]['pc']['mo']['lag1-auto_correlation'] = float(r1)
        var_mode_stat_dic['REF']['obs']['defaultReference'][mode]['pc']['mo']['halfpoint_yr'] = float(1./(hpf*12))
        var_mode_stat_dic['REF']['obs']['defaultReference'][mode]['pc']['mo']['peak_max_power'] = float(psd_max)
      else: # models
        var_mode_stat_dic['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo']['lag1-auto_correlation'] = float(r1)
        var_mode_stat_dic['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo']['halfpoint_yr'] = float(1./(hpf*12))
        var_mode_stat_dic['RESULTS'][model][run]['defaultReference'][mode]['cbf-pc']['mo']['peak_max_power'] = float(psd_max)
  
    #=================================================
    # Write dictionary to json file
    #-------------------------------------------------
    json_filename = mode+'_psd'
    JSON = pcmdi_metrics.io.base.Base(os.path.join(outdir,mode+'_'+obs_data),json_filename)
    JSON.write(var_mode_stat_dic,json_structure=["model","realization","reference","mode","season","statistic"],
               sort_keys=True, indent=4, separators=(',', ': '))
