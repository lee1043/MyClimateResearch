import numpy as np
import matplotlib.pyplot as plt

import matplotlib.cm as cmx
import matplotlib.colors as mcolors

import os

import json
from collections import OrderedDict

import mne
from mne.datasets import sample
from mne.minimum_norm import apply_inverse_epochs, read_inverse_operator
from mne.connectivity import spectral_connectivity
from mne.viz import circular_layout, plot_connectivity_circle

#==========================================================
# User option
#----------------------------------------------------------
mode = 'NAM'
season = 'DJF'

cbf = True
#cbf = False

unitvariance = False

#==========================================================
# READ DATA IN
#----------------------------------------------------------

json_path = '.'
json_filename = 'M_'+mode+'_'+season
if cbf: json_filename = json_filename + '_cbf'
if unitvariance: json_filename = json_filename + '_unitvariance'

d = OrderedDict() 
fj = open(os.path.join(json_path, json_filename+'.json'))
d = json.loads(fj.read(), object_pairs_hook=OrderedDict)
fj.close()

model_runs = d.keys()

OnePerMod = True

if OnePerMod:

  models = []
  models_only = []
  model_runs_adj = []
  
  for i, model_run in enumerate(model_runs):
    if model_run == 'obs':
      models.append('obs')
    else:
      model = model_run.split('_')[0]
      run = model_run.split('_')[1]
      models.append(model)
  
  for i, model in enumerate(models):
   if i==0:
     models_only.append(model)
     model_runs_adj.append(model_runs[i])
   else:
     if models[i] != models[i-1]:
       models_only.append(model)

       model = model_runs[i].split('_')[0]
       run = model_runs[i].split('_')[1]
       
       if run == 'r10i1p1':
         run = 'r1i1p1'

       model_runs_adj.append(model+'_'+run)

  print model_runs_adj
  model_runs = model_runs_adj

model_runs.reverse()  ### To make the order in the plot clockwise

# Creates a list containing N lists, each of N items, all set to 0, then conver it to matrix array
N = len(model_runs)
M0 = [[0 for x in range(N)] for y in range(N)] 
M = np.array(M0)
M = M.astype(float)

for i, model_run1 in enumerate(model_runs):
  for j, model_run2 in enumerate(model_runs):
    M[i][j] = d[model_run1][model_run2]

#==========================================================
# PLOT
#----------------------------------------------------------
PLOT = True

if PLOT:

  # Title and image file output name ---
  
  title_str = mode+', '+season
  figfile_name = mode+'_'+season
  
  if cbf:
    title_str = title_str + ' (CBF)'
    figfile_name = figfile_name + '_CBF'
  else:
    title_str = title_str + ' (EOF1)'
    figfile_name = figfile_name + '_EOF1'
  
  if unitvariance:
    title_str = title_str + ': Unit Var'
    figfile_name = figfile_name + '_UnitVar'

  if OnePerMod:
    figfile_name = figfile_name + '_OnePerMod'
  
  # Group boundary (tried...) ---
  
  models = []
  models_only = []
  
  for i, model_run in enumerate(model_runs):
    if model_run == 'obs':
      models.append('obs')
    else:
      model = model_run.split('_')[0]
      run = model_run.split('_')[1]
      models.append(model)
  
  gbdy = [0]
  
  for i, model in enumerate(models):
   if i==0:
     models_only.append(model)
   else:
     if models[i] != models[i-1]:
       gbdy.append(i)
       models_only.append(model)

  print models_only

  # Color on circle edge... assign discrete colors for individual models

  values = range(len(models_only))

  #colors1 = plt.cm.Vega20_r(np.linspace(0., 1, 20))
  colors1 = plt.cm.Paired(np.linspace(0., 1, 20))
  colors = np.vstack((colors1, colors1, colors1))  ### To make sure colors are discreted to next ones..

  model_colors_only = {}
  for idx, model in enumerate(models_only):
    colorVal = tuple(colors[idx])
    model_colors_only[model] = colorVal

  model_colors = []
  for model in models:
    model_colors.append(model_colors_only[model])

 
  # Number of available connecting lines ---

  num_lines_all = (N*N) - N
  if OnePerMod:
    num_lines_plot = num_lines_all
  else:
    num_lines_plot = int(num_lines_all*0.1) # plot only 10%
  print num_lines_all, num_lines_plot
  
  # Actual plotting part starts from here ---

  if OnePerMod:
    label_names = models_only
    node_order = models_only
    print 'test1', len(models_only)
    print models_only
    print 'test2', len(model_runs)
    print model_runs
  else:
    label_names = model_runs
    node_order = model_runs


  label_colors = model_colors
  
  node_angles = circular_layout(label_names, node_order, 
                                start_pos=90,
                                #start_pos=95,
                                #group_boundaries=[0, len(label_names) / 2])
                                #group_boundaries=[0],
                                #group_boundaries=[0, len(label_names)-1],
                                #group_boundaries = gbdy,
                                )
  
  figure = plt.figure(figsize=(20,20), dpi=100, facecolor='black')

  if OnePerMod:
    ftsiz = 10
  else:
    ftsiz = 5

  fig, ax = plot_connectivity_circle(M, label_names, 
                           #n_lines=1000,
                           n_lines = num_lines_plot,
                           #node_colors=label_colors,
                           node_angles=node_angles,
                           title=title_str,
                           fig=figure, fontsize_names=ftsiz,fontsize_title=20,
                           colormap='hot',
                           #colormap='viridis',
                           #colormap='inferno',
                           #vmax=1, vmin=0.95,
                           vmax=1, vmin=0.9,
                           )
  fig.savefig(figfile_name+'.png', facecolor='black')
  plt.ion()
  #plt.show()
