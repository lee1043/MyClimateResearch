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


def main():
    # User options ---    
    #exp = 'cmip5'
    #exp = 'cmip6'
    exp = 'cmip5+6'
    #stat = 'rmse'
    stat = 'stdv_ratio'
    SideBySide = True
    # ----------------
    if stat == 'rmse':
        Normalize = True
        plotTitle = 'RMS using CBF approach with 20CR'
    elif stat == 'stdv_ratio':
        Normalize = False
        plotTitle = 'Ratio of Model CBF and Obs PC std with 20CR'
    # ----------------
    imgName = 'PortraitPlot_'+exp+'_'+stat
    # ----------------
    if exp in ['cmip5', 'cmip6']:
        stat_xy = getData(exp, stat)
        stat_xy.id = stat
    elif exp in ['cmip5+6']:
        stat_xy_0 = getData('cmip5', stat)
        stat_xy_1 = getData('cmip6', stat)
        if SideBySide:
            # CMIP5 and CMIP6 side by side if from same model family
            # Merge x-axis
            model_run_cmip5 = list(stat_xy_0.getAxis(1)[:])
            model_run_cmip6 = list(stat_xy_1.getAxis(1)[:])
            model_run_all = model_run_cmip5 + model_run_cmip6
            model_run_all = sort_human(model_run_all)
            model_run_selected = []
            for c, model_run in enumerate(model_run_all):
                model_header = ''.join([ i for i in model_run.split('_')[0].split('-')[0] if not i.isdigit()])
                #print(model_header)
                if model_run in model_run_cmip5 and any(model_header in s for s in model_run_cmip6):
                    idx = model_run_cmip5.index(model_run)
                    try:
                        empty_array = np.concatenate((empty_array, stat_xy_0[:,idx])) 
                    except:
                        empty_array = stat_xy_0[:,idx].copy()
                    model_run_selected.append(model_run)
                elif model_run in model_run_cmip6:
                    idx = model_run_cmip6.index(model_run)
                    try:
                        empty_array = np.concatenate((empty_array, stat_xy_1[:,idx])) 
                    except:
                        empty_array = stat_xy_1[:,idx].copy()
                    model_run_selected.append('* '+model_run)
            #xaxis_label = model_run_all
            xaxis_label = model_run_selected
            #imgName = imgName+'_SideBySide'
            imgName = imgName+'_SideBySide_selected'
            stat_xy = np.transpose(np.reshape(empty_array, (len(xaxis_label), len(stat_xy_0.getAxis(0)))))
            print(stat_xy.shape)
            print(len(xaxis_label))
        else:
            # Add empty column for clear separation btw cmip 5 and 6
            empty_col = np.empty((len(stat_xy_0.getAxis(0)),3))
            empty_col[:] = np.nan
            stat_xy = np.concatenate((stat_xy_0, empty_col, stat_xy_1), axis=1)
            # Customize x-axis label
            xaxis_label = ( 
                ['[CMIP5] '+stat_xy_0.getAxis(1)[0]]  # cmip5, 1st model
                + [r for r in list(stat_xy_0.getAxis(1)[1:])]  # cmip5, rest
                + [' '] * 3  # separation
                + ['[CMIP6] '+stat_xy_1.getAxis(1)[0]]
                + [r for r in list(stat_xy_1.getAxis(1)[1:])])
        # Decorate axes
        X = cdms2.createAxis(xaxis_label)
        Y = cdms2.createAxis(stat_xy_0.getAxis(0)[:])
        stat_xy = MV2.array(stat_xy, axes=(Y,X), id=stat)
    else:
        sys.exit('Error: exp '+exp+' not defined')
    # Normalize rows by its median
    if Normalize:
        # Normalize by median value
        stat_xy = normalize_by_median(stat_xy)
        # Revise image file name
        imgName = imgName+'_normalized'
    # Colormap to be used 
    if stat == 'rmse':
        colormap = "bl_to_darkred"
        clevels = [-1.e20, -.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, 1.e20]
        ccolors = vcs.getcolors(clevels, split=0, colors=range(16,240))
    elif stat == 'stdv_ratio':
        colormap = "bl_to_darkred"
        clevels = [r/10. for r in list(range(5,16,1))]
        clevels.insert(0, -1.e20) 
        clevels.append(1.e20) 
        ccolors = vcs.getcolors(clevels, split=0, colors=range(16,240))
        ccolors[4:8] = ['lightgreen', 'green', 'green', 'darkgreen']
    #
    # Portrait plot
    #
    plot_portrait(stat_xy, imgName, plotTitle=plotTitle,
        colormap=colormap, clevels=clevels, ccolors=ccolors,
        parea=(.05, .88, .25, .9),
        img_length=2600, img_height=800, xtic_textsize=10, ytic_textsize=10, 
        missing_color='grey', logo=False,
        )


def getData(exp, stat):
    if exp == 'cmip5':
        if stat == 'rmse':
            statistics = 'rms_alt'
        elif stat == 'stdv_ratio':
            statistics = 'std_pseudo_pcs'
        else:
            sys.exit('Error: stat '+stat+' not defined')
        #modes = ['SAM', 'NAM', 'NAO', 'PNA', 'PDO']
        modes = ['SAM', 'NAM', 'NAO', 'PNA']
        json_dir = './json_files_cmip5'
        json_file = 'var_mode_%(mode)_EOF1_stat_cmip5_historical_mo_atm_1900-2005_adjust_based_tcor_pseudo_vs_model_pcs.json'
    elif exp == 'cmip6':
        if stat == 'rmse':
            statistics = 'rms_cbf'
        elif stat == 'stdv_ratio':
            statistics = 'stdv_pc_ratio_cbf_over_obs'
        else:
            sys.exit('Error: stat '+stat+' not defined')
            #stat = 'stdv_pc_ratio_cbf_over_obs'
        modes = ['SAM', 'NAM', 'NAO', 'PNA']
        json_dir = './json_files_cmip6'
        json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_historical_mo_atm_1900-2005.json'
    # Get data as MV2 2d array
    stat_xy = read_json_and_merge_axes(json_dir, json_file, statistics, modes) 
    return stat_xy


def read_json_and_merge_axes(json_dir, json_file, statistics, modes, minimizeText=False):
    model_run_list = []
    model_run_list_label = []
    mode_season_list = []
    a = []
    for mode in modes:
        # open json
        input_file = StringConstructor(json_file)(mode=mode)
        with open(os.path.join(json_dir, input_file)) as f:
            d = json.load(f)
        # Get potential x-axis first
        if mode == modes[0]:
            models_list = sorted(list(d["RESULTS"].keys()))
            for model in models_list:
                runs_list = sort_human(list(d["RESULTS"][model].keys()))
                for run in runs_list:
                    model_run_list.append(model+'_'+run)
                    if run == runs_list[0]:
                        model_run_list_label.append(model+'_'+run)
                    else:
                        model_run_list_label.append(run)
            print(model_run_list)
        # season depending on mode
        if mode == 'PDO':
            seasons = ['monthly']
        else:
            seasons = ['DJF', 'MAM', 'JJA', 'SON']
        # season loop
        for season in seasons:
            mode_season_list.append(mode+'_'+season)
            for model_run in model_run_list:
                model = model_run.split('_')[0]
                run = model_run.split('_')[-1]
                try:
                    tmp = d["RESULTS"][model][run]["defaultReference"][mode][season][statistics]
                    if statistics == 'std_pseudo_pcs':
                        tmp = tmp / d["REF"]["obs"]["defaultReference"][mode][season]["pc1_stdv"]
                except:
                    tmp = np.nan
                a.append(tmp)
    # convert to array and decorate axes
    a = np.array(a).reshape(len(mode_season_list), len(model_run_list))
    if minimizeText:
        X = cdms2.createAxis(model_run_list_label)
    else:
        X = cdms2.createAxis(model_run_list)
    Y = cdms2.createAxis(mode_season_list)
    a = MV2.array(a, axes=(Y,X), id=statistics)
    return a


def sort_human(l):
    convert = lambda text: float(text) if text.isdigit() else text
    alphanum = lambda key: [ convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key) ]
    l.sort( key=alphanum )
    return l


if __name__ == '__main__':
    main()
