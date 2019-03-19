"""
WORKING CONDITION: JL's local Mac, conda env: pmp_nightly_20180622
"""

from __future__ import print_function
from genutil import StringConstructor
from plot_portrait import plot_portrait, normalize_by_median
import cdms2
import json
import MV2
import numpy as np
import os
import pcmdi_metrics
import pcmdi_metrics.graphics.portraits
import re
import sys
import vcs

import matplotlib.pyplot as plt

from VariabilityModes_PP20190301_jwlee_cmip5and6_SideBySide import read_json_and_merge_axes, sort_human
from collections import OrderedDict


def main():
    # User options ---    
    #stat = 'rmse'
    #stat = 'rmsc'
    stat = 'stdv_ratio'
    OrgInPaper = True
    #OrgInPaper = False
    # ---------------- 
    if stat == 'rmse':
        Normalize = True
        plotTitle = 'RMS using CBF approach with 20CR'
    elif stat == 'rmsc':
        Normalize = True
        plotTitle = 'Centered RMS using CBF approach with 20CR'
    elif stat == 'stdv_ratio':
        Normalize = False
        plotTitle = 'Ratio of Model CBF and Obs PC std with 20CR'
    # ----------------
    imgName = 'Scatter_cmip5and6_'+stat
    if OrgInPaper:
        imgName = imgName+'_OrgInPaper'
    # ----------------
    stat_xy_0 = getData('cmip5', stat, OrgInPaper)
    stat_xy_1 = getData('cmip6', stat, OrgInPaper)

    # CMIP5 and CMIP6 side by side if from same model family
    # Merge x-axis
    model_run_cmip5 = list(stat_xy_0.getAxis(1)[:])
    model_run_cmip6 = list(stat_xy_1.getAxis(1)[:])
    model_run_all = model_run_cmip5 + model_run_cmip6
    model_run_all = sort_human(model_run_all)
    model_run_selected = []
    model_header_selected = []
    for c, model_run in enumerate(model_run_all):
        model_header = ''.join([i for i in model_run.split('_')[0].split('-')[0] if not i.isdigit()])
        if (model_run in model_run_cmip5
            and any(model_header in s for s in model_run_cmip6)
            and model_header != 'GFDL'):
            idx = model_run_cmip5.index(model_run)
            try:
                empty_array = np.concatenate((empty_array, stat_xy_0[:,idx]))
            except:
                empty_array = stat_xy_0[:,idx].copy()
            model_run_selected.append(model_run)
            model_header_selected.append(model_header)
        elif (model_run in model_run_cmip6 and model_header != 'GFDL'):
            idx = model_run_cmip6.index(model_run)
            try:
               empty_array = np.concatenate((empty_array, stat_xy_1[:,idx]))
            except:
                empty_array = stat_xy_1[:,idx].copy()
            model_run_selected.append(model_run)
            model_header_selected.append(model_header)
        else:
            print('Skip '+model_run)
    # Remove duplicates in lists
    model_header_selected = list(OrderedDict.fromkeys(model_header_selected))
    print(model_header_selected)
    # Prepare for decorating axes 
    xaxis_label = model_run_selected
    stat_xy = np.transpose(np.reshape(empty_array, (len(xaxis_label), len(stat_xy_0.getAxis(0)))))
    # Decorate axes
    X = cdms2.createAxis(xaxis_label)
    Y = cdms2.createAxis(stat_xy_0.getAxis(0)[:])
    stat_xy = MV2.array(stat_xy, axes=(Y,X), id=stat)

    #
    scatter_data = []
    for model_header in model_header_selected:
        print(model_header)
        for c, mode_season in enumerate(Y[:]):
            #if mode_season in ['NAM_DJF', 'NAO_DJF', 'PNA_DJF', 'SAM_JJA']:
                tmp1 = []
                tmp2 = []
                for r, model_run in enumerate(model_run_selected):
                    model_header_i = ''.join([i for i in model_run.split('_')[0].split('-')[0] if not i.isdigit()])
                    if model_header_i == model_header:
                        if model_run in model_run_cmip5:
                            tmp1.append(stat_xy[c][r])
                        elif model_run in model_run_cmip6:
                            tmp2.append(stat_xy[c][r])
                #print(model_header, mode_season, tmp1, tmp2) 
                scatter_data.append((model_header, mode_season, tmp1, tmp2))
    plot_scatter(scatter_data, model_header_selected)


def getData(mip, stat, OrgInPaper):
    if mip == 'cmip5':
        if stat == 'rmse':
            if OrgInPaper:
                statistics = 'rms_alt'
            else:
                statistics = 'rms_cbf'
        elif stat == 'rmsc':
            if OrgInPaper:
                statistics = 'rmsc_alt'
            else:
                statistics = 'rmsc_cbf'
        elif stat == 'stdv_ratio':
            if OrgInPaper:
                statistics = 'std_pseudo_pcs'
            else:
                statistics = 'stdv_pc_ratio_cbf_over_obs'
        else:
            sys.exit('Error: stat '+stat+' not defined')
        #modes = ['SAM', 'NAM', 'NAO', 'PNA', 'PDO']
        modes = ['SAM', 'NAM', 'NAO', 'PNA']
        if OrgInPaper:
            json_dir = './json_files_cmip5'
            json_file = 'var_mode_%(mode)_EOF1_stat_cmip5_historical_mo_atm_1900-2005_adjust_based_tcor_pseudo_vs_model_pcs.json'
        else:
            json_dir = './json_files_cmip5_rerun_tree_20190305'
            json_file = 'var_mode_%(mode)_EOF1_stat_cmip5_historical_mo_atm_1900-2005.json'
    elif mip == 'cmip6':
        if stat == 'rmse':
            statistics = 'rms_cbf'
        elif stat == 'rmsc':
            statistics = 'rmsc_cbf'
        elif stat == 'stdv_ratio':
            statistics = 'stdv_pc_ratio_cbf_over_obs'
        else:
            sys.exit('Error: stat '+stat+' not defined')
        modes = ['SAM', 'NAM', 'NAO', 'PNA']
        #json_dir = './json_files_cmip6'
        json_dir = './json_files_cmip6_v20190308'
        json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_historical_mo_atm_1900-2005.json'
    # Get data as MV2 2d array
    stat_xy = read_json_and_merge_axes(json_dir, json_file, statistics, modes)
    return stat_xy



def plot_scatter(scatter_data, model_header_selected):

    print(model_header_selected)

    params = {'legend.fontsize': 5,
              'legend.handlelength': 2}
    plt.rcParams.update(params)

    fig = plt.figure()
    ax = fig.add_subplot(111)      

    ax.set_title('Ratio of stdv: Mod_CBF_PC/OBS_PC')
    ax.set_xlabel('CMIP5')
    ax.set_ylabel('CMIP6')

    # colors
    SeasonColorGradation = True
    if SeasonColorGradation:
        colors =  plt.cm.tab20c(np.arange(20).astype(int))
        modes = ['NAM', 'NAO', 'PNA', 'SAM']
        n = 0
        color_dict = {}
        for mode in modes:
            if mode == 'SAM':
                seasons = ['JJA', 'SON', 'DJF', 'MAM']
            else: 
                seasons = ['DJF', 'MAM', 'JJA', 'SON']
            for season in seasons:
                color_dict[mode+'_'+season] = colors[n]
                n += 1
    else:
        color_dict = {
            'NAM': [ 0.19215686,  0.50980392,  0.74117647,  1.        ],
            'NAO': [ 0.90196078,  0.33333333,  0.05098039,  1.        ],
            'PNA': [ 0.19215686,  0.63921569,  0.32941176,  1.        ],
            'SAM': [ 0.45882353,  0.41960784,  0.69411765,  1.        ],}

    # shapes
    SeasonVaryingShapes = True
    if SeasonVaryingShapes:
        shape_dict = {
            'DJF':'o',
            'MAM':'s',
            'JJA':'D',
            'SON':'^'}
    else:
        shape_dict = {
            'DJF':'o',
            'MAM':'o',
            'JJA':'o',
            'SON':'o'}

    # plot each markers
    for i, a in enumerate(scatter_data):
        x = np.mean(np.array(a[2]))  # cmip5
        y = np.mean(np.array(a[3]))  # cmip6
        model_header = a[0]
        mode = a[1].split('_')[0]
        season = a[1].split('_')[1]
        # number -> model
        n = model_header_selected.index(model_header)+1
        # color -> mode
        if SeasonColorGradation:
            c = color_dict[mode+'_'+season]
        else:
            c = color_dict[mode]
        # shape -> season
        s = shape_dict[season]
        # place markers
        ax.plot(x, y, marker=s, color=c, markersize=12, alpha=.9)
        ax.text(x, y, n, color='w', fontsize=9, ha='center', va='center')
        #ax.plot(x, y, 'o', label='_'.join([model_header, mode, season]))

    # y=x line
    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    ]
    
    # now plot both limits against eachother
    ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    # x=1, y=1 line
    plt.axvline(x=1,linestyle='--')
    plt.axhline(y=1,linestyle='--')

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    #ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=2)

    plt.savefig('test_scatter.png')


if __name__ == '__main__':
    main()
