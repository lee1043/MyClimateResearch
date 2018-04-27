import cdms2 as cdms
import json
import os, sys
import genutil

libfiles = ['../../../../lib/default_regions.py']

for lib in libfiles:
  execfile(os.path.join('./',lib))

#-------------------------------------------------------------
def get_field(nc_path, unitvariance):
  f = cdms.open(nc_path)
  if unitvariance:
    d = f('slope')
  else:
    d = f('eof1')
  f.close()
  return d

def get_grid(nc_path):
  f = cdms.open(nc_path)
  d = f('slope')
  grid = d.getGrid()
  f.close()
  return grid 

def calcSCOR(nc_path1, nc_path2, ref_grid, unitvariance):
  # a, b: cdms 2d variables on the different grid (lat, lon), global 
  a = get_field(nc_path1, unitvariance)
  b = get_field(nc_path2, unitvariance)

  a_regrid = a.regrid(ref_grid, regridTool='regrid2', mkCyclic=True)
  b_regrid = b.regrid(ref_grid, regridTool='regrid2', mkCyclic=True)

  a_regrid_subdomain = a_regrid(regions_specs[mode]['domain'])
  b_regrid_subdomain = b_regrid(regions_specs[mode]['domain'])

  result = float(genutil.statistics.correlation(a_regrid_subdomain, b_regrid_subdomain, axis='xy', weights='weighted'))
  return result
#-------------------------------------------------------------

debug = False
#debug = True

#cbf = True 
cbf = False

unitvariance = True
#unitvariance = False

#-------------------------------------------------------------
stats = ['tcor_pseudo_vs_model_pcs']
modes = ['NAM', 'NAO', 'SAM', 'PNA', 'PDO']

if debug:
  modes = [modes[0]]
  stats = [stats[0]]

#==================================================================
# Loop for start
#------------------------------------------------------------------
if debug: stats = [stats[0]]
for stat in stats:
  print '==== '+ stat +' ====='

  #==================================================================
  # Loop for mode
  #------------------------------------------------------------------
  if debug: modes = [modes[0]]
  for mode in modes:

    print '---- '+ mode +' -----'

    json_path = '../create_EOF_swap_json_chk_model_period_correct_model_name'
    json_file_name = 'var_mode_'+mode+'_EOF1_stat_cmip5_historical_mo_atm_1900-2005_adjust_based_'+stat
    json_file = json_file_name + '.json'

    d = {}
    fj = open(os.path.join(json_path,json_file))
    d = json.loads(fj.read())
    fj.close()

    models = d['RESULTS'].keys()
    models = sorted(models, key=lambda s:s.lower()) # Sort list alphabetically, case-insensitive

    if mode == 'PDO':
      seasons = ['monthly']
      var = 'ts'
    else:
      seasons = ['DJF', 'MAM', 'JJA', 'SON']
      var = 'psl'

    #==================================================================
    # Loop for season
    #------------------------------------------------------------------
    if debug: seasons = [seasons[0]]
    for season in seasons:
      print season

      model_runs = []
      model_runs.append('obs')

      ncfile_dict = {} 

      obs_ncfile_frame = '../../result/'+mode+'/'+mode+'_'+var+'_EOF1_'+season+'_obs_????-????.nc'
      obs_ncfile_lst = os.popen('ls '+obs_ncfile_frame).readlines()
      obs_ncfile = obs_ncfile_lst[0]

      ncfile_dict['obs'] = obs_ncfile

      #==================================================================
      # Loop for model
      #------------------------------------------------------------------
      #if debug: models = [models[0]]
      #if debug: models = models[:5]
      for model in models:
        if debug: print '  ', model

        runs = d['RESULTS'][model].keys()
        runs = sorted(runs, key=lambda s:s.lower())

        # Check available runs first
        runs_adj = []
        for run in runs:
          try:
            check = d['RESULTS'][model][run]['defaultReference'][mode][season]['cor']
            if check is not None:
              runs_adj.append(run)
          except:
            pass
        runs = runs_adj

        if model.lower() in ['inmcm4', 'fio-esm', 'bcc-csm1-1-m', 'bcc-csm1-1']:
          modelb = model.lower()
        else:
          modelb = model

        #==================================================================
        # Loop for runs (realizations)
        #------------------------------------------------------------------
        for run in runs:
          if debug: print '  --', run

          #==================================================================
          # Check model period 
          #------------------------------------------------------------------
          if cbf:
            ncfile_frame = '../../result/'+mode+'/'+mode+'_'+var+'_EOF1_'+season+'_cmip5_'+modelb+'_historical_'+run+'_mo_atm_????-????_pseudo.nc'
          else:
            ncfile_frame = '../../result/'+mode+'/'+mode+'_'+var+'_EOF1_'+season+'_cmip5_'+modelb+'_historical_'+run+'_mo_atm_????-????.nc'

          ncfile_lst = os.popen('ls '+ncfile_frame).readlines()

          if any('2005' in s for s in ncfile_lst):
            ncfile = filter(lambda x: '2005' in x, ncfile_lst)[0]
          else:
            ncfile = ncfile_lst[0].strip()

          if cbf:
            msyear = ncfile.split('.nc')[0].split('_')[-2].split('-')[0]
            meyear = ncfile.split('.nc')[0].split('_')[-2].split('-')[-1]
          else:
            msyear = ncfile.split('.nc')[0].split('_')[-1].split('-')[0]
            meyear = ncfile.split('.nc')[0].split('_')[-1].split('-')[-1]

          #######################
          # Chk period matching
          #######################
          if (msyear == '1900' or msyear == '1955')  and meyear == '2005':
            model_runs.append(model+'_'+run)
            ncfile_dict[model+'_'+run] = ncfile

      print model_runs

      from collections import OrderedDict
      M = OrderedDict()
      #M = {}
      for model_run1 in model_runs:
        M[model_run1] = OrderedDict()
        for model_run2 in model_runs:
          M[model_run1][model_run2] = {}

      for model_run1 in model_runs:
        if model_run1 == 'obs':
          print model_run1, ncfile_dict[model_run1]
          ref_grid = get_grid(ncfile_dict['obs'])
        else:
          model = model_run1.split('_')[0]
          run = model_run1.split('_')[1]
          print model, run, ncfile_dict[model_run1]

        for model_run2 in model_runs:
          if not M[model_run1][model_run2]: ## run below only when dict is empty
            if model_run1 == model_run2:
              M[model_run1][model_run2] = 1.
              M[model_run2][model_run1] = 1.
            else:
              # Get PCOR between field1 and field2
              pcor = calcSCOR(ncfile_dict[model_run1], ncfile_dict[model_run2], ref_grid, unitvariance)
              #print model_run1, model_run2, pcor
              M[model_run1][model_run2] = pcor
              M[model_run2][model_run1] = pcor
  
        json_filename = 'M_'+mode+'_'+season
        if cbf: json_filename = json_filename + '_cbf'
        if unitvariance: json_filename = json_filename + '_unitvariance'
        json.dump(OrderedDict(M), open(json_filename+'.json','w'), indent=4, separators=(',', ': '))
