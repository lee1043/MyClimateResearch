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
    mip = 'cmip5'
    mip = 'cmip6'
    mip = 'cmip5+6'
    #stat = 'rmse'
    #stat = 'rmsc'
    stat = 'stdv_ratio'
    SideBySide = True
    #OrgInPaper = True
    OrgInPaper = False

    #modes = ['SAM', 'NAM', 'NAO', 'PNA', 'PDO']
    modes = ['SAM', 'NAM', 'NAO', 'PNA']
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
    #imgName = 'PortraitPlot_'+mip+'_'+stat
    imgName = 'PortraitPlot_'+mip+'_'+stat+'_GFDL'
    if OrgInPaper:
        imgName = imgName+'_OrgInPaper'
    # ----------------
    if mip in ['cmip5', 'cmip6']:
        stat_xy = getData(mip, stat, modes, OrgInPaper)
        stat_xy.id = stat
    elif mip in ['cmip5+6']:
        stat_xy_0 = getData('cmip5', stat, modes, OrgInPaper)
        stat_xy_0_pi = getData('cmip5', stat, modes, OrgInPaper, piControl=True)
        stat_xy_1_pi = getData('cmip6', stat, modes, OrgInPaper, piControl=True)
        # Merge into one array
        stat_xy = np.concatenate((stat_xy_0, stat_xy_0_pi, stat_xy_1_pi), axis=1)
        xaxis_label = list(stat_xy_0.getAxis(1)) + list(stat_xy_0_pi.getAxis(1)) + list(stat_xy_1_pi.getAxis(1))
        # Reduce text for x-axis label on plot
        xaxis_label = reduce_text(xaxis_label)
        # Decorate axes
        X = cdms2.createAxis(xaxis_label)
        Y = cdms2.createAxis(stat_xy_0.getAxis(0)[:])
        stat_xy = MV2.array(stat_xy, axes=(Y,X), id=stat)
    else:
        sys.exit('Error: mip '+mip+' not defined')
    # Normalize rows by its median
    if Normalize:
        # Normalize by median value
        stat_xy = normalize_by_median(stat_xy)
        # Revise image file name
        imgName = imgName+'_normalized'
    # Colormap to be used 
    if stat in ['rmse', 'rmsc']:
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
        #ccolors[4:8] = [1,2,2,3]
        #print('ccolors', ccolors)
    #
    # Portrait plot
    #
    plot_portrait(stat_xy, imgName, plotTitle=plotTitle,
        colormap=colormap, clevels=clevels, ccolors=ccolors,
        parea=(.05, .88, .25, .9),
        img_length=2600, img_height=800, xtic_textsize=10, ytic_textsize=10, 
        missing_color='grey', logo=False,
        #Annotate=True, 
        )
    try:
        xaxis_label_2 = reduce_text(xaxis_label_2)
        X2 = cdms2.createAxis(xaxis_label_2)
        stat_xy_2 = MV2.array(stat_xy_2, axes=(Y,X2), id=stat)
        imgName2 = imgName + '_2'
        plot_portrait(stat_xy_2, imgName2, plotTitle=plotTitle,
            colormap=colormap, clevels=clevels, ccolors=ccolors,
            parea=(.05, .88, .25, .9),
            img_length=1300, img_height=800, xtic_textsize=10, ytic_textsize=10,
            missing_color='grey', logo=False,
            )
    except:
        pass


def getData(mip, stat, modes, OrgInPaper, piControl=False):
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
            if piControl:
                json_dir = './json_files_cmip5_v20190313_GFDL-CM3_piControl'
                json_file = 'var_mode_%(mode)_EOF1_stat_cmip5_piControl_mo_atm_1900-2005.json'
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
        if piControl:
            json_dir = './json_files_cmip6_v20190313_GFDL-CM4_piControl'
            #json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_historical_mo_atm_1900-2005.json'
            json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_piControl_mo_atm_1900-2005.json'
        else:
            json_dir = './json_files_cmip6_v20190308'
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
                if model in ['GFDL-CM3', 'GFDL-CM4']:
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


def reduce_text(label_list):
    label_list_return = list(label_list)
    for i, label in enumerate(label_list):
        if i > 0:
            tmp = label_list[i-1]
            tmp_split = tmp.split('_')
            label_split = label.split('_') 
            if label_split[0] == tmp_split[0]:  # when they are from same model
                for word in label_split:
                    if word in tmp_split:
                        label_split.remove(word)
                label_list_return[i] = '_'.join(label_split)
                if label.split(' ')[0] == '*':  # cmip6 mark
                    label_list_return[i] = '* ' + label_list_return[i]
            else:
                label_list_return[i] = label_list[i]
    return label_list_return
            

if __name__ == '__main__':
    main()
