import cdms2
import cdutil
import genutil
import glob
import matplotlib.pyplot as plt
import MV2
import os
import pcmdi_metrics
import sys

from collections import defaultdict
from lib_psd import *
from lib_psd_plot import plot_psd
from pcmdi_metrics.pcmdi.pmp_parser import PMPParser

#------------------------------------------------------------
# Read from "my_Param.py"
# How to run: python run_psd_loop.py -p my_Param.py
#------------------------------------------------------------
P = PMPParser() # Includes all default options
param = P.get_parameter()

modes = param.modes
PlotOn_xlog = param.PlotOn_xlog
PlotOn_xlinear = param.PlotOn_xlinear
NormalizePCts = param.NormalizePCts
outdir = param.outdir
TaperingRatio = param.TaperingRatio
SegmentLengthRatio = param.SegmentLengthRatio
SegmentOverlapping = param.SegmentOverlapping
debug = param.debug # if debug=True, run only for obs, not models
#------------------------------------------------------------

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

    if not debug:
      ncfile_list.extend(glob.glob(os.path.join(basedir,tier1,tier2,modfiles)))
    
    for ncfile in sorted(ncfile_list):
    
      figfilename = ncfile.split('/')[-1].split('.')[0]
      print 'figfilename: ', figfilename
  
      if figfilename.split('_')[4] == 'obs':
        title = mode+', OBS ['+obs_data+']'
        if debug:
          PlotOn = True
      else:
        model = figfilename.split('_')[5]
        run = figfilename.split('_')[7]
        title = mode+', '+model+' ('+run+')'

        if debug:
          if run == 'r1i1p1':
            PlotOn = True
          else:
            PlotOn = False
    
      f = cdms2.open(ncfile)
      d = f(varname_pc)
      f.close()

      if NormalizePCts:
        d = MV2.divide(d,float(calcSTD(d)))

      d_avg = cdutil.averager(d,axis='0')
      print 'series mean: ', d_avg

      SegmentLength = int(len(d)*SegmentLengthRatio)

      freqs, psd, rn, siglevel, r1, hpf, psd_max = PowerSpectrumAnalysis(
           d, SegmentLength, 
           TaperingRatio=TaperingRatio, 
           SegmentOverlapping=SegmentOverlapping,
           debug=debug)
    
      # Plot
      if PlotOn_xlog:
        figfile = os.path.join(outdir,mode+'_'+obs_data,figfilename+'_xlog.png')
        plot_psd(freqs, psd, rn, siglevel, 
                 r1=r1, hpf=hpf, 
                 logScale=True, seg_length_yr=SegmentLength/12, 
                 AnnotatePeaks=True, 
                 title=title,
                 outfile=figfile)

      if PlotOn_xlinear:
        figfile = os.path.join(outdir,mode+'_'+obs_data,figfilename+'_xlin.png')
        plot_psd(freqs, psd, rn, siglevel, 
                 r1=r1, hpf=hpf, 
                 logScale=False, seg_length_yr=SegmentLength/12, 
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
