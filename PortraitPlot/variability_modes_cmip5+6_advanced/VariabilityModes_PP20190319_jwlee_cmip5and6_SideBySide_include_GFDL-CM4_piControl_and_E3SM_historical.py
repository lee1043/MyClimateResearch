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

    AverageRuns = True
    #AverageRuns = False

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
    imgName = 'PortraitPlot_'+mip+'_'+stat+'_include_GFDL-CM4_piControl_and_E3SM_historical'
    if OrgInPaper:
        imgName += '_OrgInPaper'
    if AverageRuns:
    	imgName += '_AverageRuns'
    # ----------------
    if mip in ['cmip5', 'cmip6']:
        stat_xy = getData(mip, stat, modes, OrgInPaper=OrgInPaper, AverageRuns=AverageRuns)  # cmip5 or cmip6
        stat_xy.id = stat
    elif mip in ['cmip5+6']:
        stat_xy_0 = getData('cmip5', stat, modes, OrgInPaper=OrgInPaper, AverageRuns=AverageRuns)  # cmip5
        stat_xy_1 = getData('cmip6', stat, modes, AverageRuns=AverageRuns)  # cmip6
        stat_xy_1_pi = getData('cmip6', stat, modes, piControl=True, AverageRuns=AverageRuns)  # cmip6 gfdl picontrol
        stat_xy_1_e3 = getData('cmip6_e3sm', stat, modes, AverageRuns=AverageRuns)  # cmip6 e3sm historical
        if SideBySide:
            # CMIP5 and CMIP6 side by side if from same model family
            # Merge x-axis
            model_run_cmip5 = list(stat_xy_0.getAxis(1)[:])
            model_run_cmip6 = list(stat_xy_1.getAxis(1)[:])
            #model_run_cmip6.remove('GFDL-CM4')  # exclude GFDL-CM4, which historical is yet to available, to prevent repeating
            model_run_cmip6_pi = list(stat_xy_1_pi.getAxis(1)[:])  # GFDL-CM4 picontrol
            model_run_cmip6_e3 = list(stat_xy_1_e3.getAxis(1)[:])
            model_run_all = model_run_cmip5 + model_run_cmip6 + model_run_cmip6_pi + model_run_cmip6_e3
            model_run_all = sort_human(model_run_all)
            print('model_run_cmip5:', model_run_cmip5)
            print('model_run_cmip6:', model_run_cmip6)
            print('model_run_cmip6_pi:', model_run_cmip6_pi)
            print('model_run_cmip6_e3:', model_run_cmip6_e3)
            print('model_run_all:', model_run_all)
            model_run_selected = []
            model_run_selected_2 = []
            # Arbitrary and temporary switch for GFDL-CM4 
            # -- It prevents showing 2 identical columns for GFDL-CM4, which caused because FDL-CM4 is in both model_run_cmip6 and model_run_cmip6_pi
            GFDL_CM4_repeat_prevent_switch = False
            # Loop start
            for c, model_run in enumerate(model_run_all):
                model_header = ''.join([ i for i in model_run.split('_')[0].split('-')[0] if not i.isdigit()])
                model = ''.join([ i for i in model_run.split('_')[0] if not i.isdigit()])
                run = ''.join([ i for i in model_run.split('_')[-1] if not i.isdigit()])
                print(model_header, model, run)
                # cmip5 models
                if model_run in model_run_cmip5:
                    # in case cmip5 model has corresponding cmip6 model -- 1st portrait plot
                    idx = model_run_cmip5.index(model_run)
                    #if any(model_header in s for s in model_run_cmip6) and model_header != 'GFDL':
                    if any(model_header in s for s in model_run_cmip6) and model != 'GFDL-CMp':
                        try:
                            empty_array = np.concatenate((empty_array, stat_xy_0[:,idx])) 
                        except:
                            empty_array = stat_xy_0[:,idx].copy()
                        model_run_selected.append(model_run)
                    # in case corresponding cmip6 model is not available -- go to 2nd portrait plot
                    else:
                        if ((OrgInPaper and model_run not in ['HadGEM2-CC_r2i1p1', 'HadGEM2-CC_r3i1p1'])
                            or (not OrgInPaper and not np.isnan(stat_xy_0[:,idx]).any())):  # exclude missing column
                            try:
                                empty_array2 = np.concatenate((empty_array2, stat_xy_0[:,idx]))
                            except:
                                empty_array2 = stat_xy_0[:,idx].copy()
                            model_run_selected_2.append(model_run)
                # cmip6 models
                elif (model_run in model_run_cmip6 and model_header != 'GFDL'):
                    idx = model_run_cmip6.index(model_run)
                    try:
                        empty_array = np.concatenate((empty_array, stat_xy_1[:,idx])) 
                    except:
                        empty_array = stat_xy_1[:,idx].copy()
                    model_run_selected.append('* '+model_run)  # add star mark for x-axis labels
                # GFDL picontrol
                elif (model_run in model_run_cmip6_pi and model_header == 'GFDL' and not GFDL_CM4_repeat_prevent_switch):
                    idx = model_run_cmip6_pi.index(model_run)
                    try:
                        empty_array = np.concatenate((empty_array, stat_xy_1_pi[:,idx])) 
                    except:
                        empty_array = stat_xy_1_pi[:,idx].copy()
                    model_run_selected.append('p* '+model_run)  # add star mark for x-axis labels, p for picontrol
                    if AverageRuns:
                        GFDL_CM4_repeat_prevent_switch = True
                    else:
                        GFDL_CM4_repeat_prevent_switch = False
                # E3SM historical
                elif (model_run in model_run_cmip6_e3):
                    idx = model_run_cmip6_e3.index(model_run)
                    try:
                        empty_array = np.concatenate((empty_array, stat_xy_1_e3[:,idx])) 
                    except:
                        empty_array = stat_xy_1_e3[:,idx].copy()
                    model_run_selected.append('* '+model_run)  # add star mark for x-axis labels  
                else:
                    print('Skip '+model_run)
            imgName = imgName+'_SideBySide_selected'
            xaxis_label = model_run_selected
            xaxis_label_2 = model_run_selected_2
            stat_xy = np.transpose(np.reshape(empty_array, (len(model_run_selected), len(stat_xy_0.getAxis(0)))))
            stat_xy_2 = np.transpose(np.reshape(empty_array2, (len(model_run_selected_2), len(stat_xy_0.getAxis(0)))))
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
        sys.exit('Error: mip '+mip+' not defined')
    #
    # Normalize rows by its median
    # NOTE: This part should be revised to work with rmse. 
    # I am leaving it for now because only dealing with stdv_ratio,
    # which does not need normalization (thus, Normalize = False)
    #
    if Normalize:
        # Normalize by median value
        stat_xy = normalize_by_median(stat_xy)
        # Revise image file name
        imgName = imgName+'_normalized'
    #
    # Prepare plotting
    #
    # Reduce text on x-axis and redecorate array
    xaxis_label = reduce_text(xaxis_label)
    X = cdms2.createAxis(xaxis_label)
    stat_xy = MV2.array(stat_xy, axes=(Y,X), id=stat)
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
    # axes label font size
    if AverageRuns:
        xtic_textsize = 14
        ytic_textsize = 14
    else:
        xtic_textsize = 11
        ytic_textsize = 14
    # title
    if mip == 'cmip5+6':
        plotTitle2 = '[CMIP5 & 6] '+plotTitle
    else:
        plotTitle2 = '['+mip.upper()+'] '+plotTitle
    #
    # Portrait plot
    #
    plot_portrait(stat_xy, imgName, plotTitle=plotTitle2,
        colormap=colormap, clevels=clevels, ccolors=ccolors,
        parea=(.05, .88, .25, .9),
        img_length=2600, img_height=800, xtic_textsize=xtic_textsize, ytic_textsize=ytic_textsize,
        missing_color='grey', logo=False,
        )
    try:
        plotTitle2 = '[CMIP5] '+plotTitle
        xaxis_label_2 = reduce_text(xaxis_label_2)
        X2 = cdms2.createAxis(xaxis_label_2)
        stat_xy_2 = MV2.array(stat_xy_2, axes=(Y,X2), id=stat)
        imgName2 = imgName + '_2'
        plot_portrait(stat_xy_2, imgName2, plotTitle=plotTitle2,
            colormap=colormap, clevels=clevels, ccolors=ccolors,
            parea=(.1, .88, .25, .9),
            img_length=1300, img_height=800, xtic_textsize=xtic_textsize, ytic_textsize=ytic_textsize,
            missing_color='grey', logo=False,
            )
    except:
        pass


def getData(mip, stat, modes, OrgInPaper=False, piControl=False, AverageRuns=False):
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

        if piControl:
            json_dir = './json_files_cmip6_v20190313_GFDL-CM4_piControl'
            json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_piControl_mo_atm_1900-2005.json'
        else:
            #json_dir = './json_files_cmip6'
            json_dir = './json_files_cmip6_v20190308'
            json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_historical_mo_atm_1900-2005.json'
    elif mip == 'cmip6_e3sm':
        if stat == 'rmse':
            statistics = 'rms_cbf'
        elif stat == 'rmsc':
            statistics = 'rmsc_cbf'
        elif stat == 'stdv_ratio':
            statistics = 'stdv_pc_ratio_cbf_over_obs'
        else:
            sys.exit('Error: stat '+stat+' not defined')
        json_dir = './json_files_cmip6_v20190315_E3SM_historical'
        json_file = 'var_mode_%(mode)_EOF1_stat_cmip6_historical_mo_atm_1900-2005.json'    	
    # Get data as MV2 2d array
    stat_xy = read_json_and_merge_axes(json_dir, json_file, statistics, modes, AverageRuns=AverageRuns) 
    return stat_xy


def read_json_and_merge_axes(json_dir, json_file, statistics, modes, AverageRuns=False):
    runs_list_dic = {}
    model_run_list = []
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
                runs_list_dic[model] = runs_list
                for run in runs_list:
                    model_run_list.append(model+'_'+run)
            print(model_run_list)
        # season depending on mode
        if mode == 'PDO':
            seasons = ['monthly']
        else:
            seasons = ['DJF', 'MAM', 'JJA', 'SON']
        # season loop
        for season in seasons:
            mode_season_list.append(mode+'_'+season)
            if AverageRuns:
                for model in models_list:
                    b = []
                    for run in runs_list_dic[model]:
                        try:
            	            tmp = d["RESULTS"][model][run]["defaultReference"][mode][season][statistics]
	                    if statistics == 'std_pseudo_pcs':
	                       	tmp = tmp / d["REF"]["obs"]["defaultReference"][mode][season]["pc1_stdv"]
	                    b.append(tmp)
	                except:
	                    tmp = np.nan
	            tmp2 = float(np.mean(np.array(b)))
	            a.append(tmp2)
            else:
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
    if AverageRuns: 
        #xaxis_label = models_list
        xaxis_label = [model+'  ('+str(len(runs_list_dic[model]))+')' for model in models_list]
    else:
        xaxis_label = model_run_list
    print('xaixs_label:', xaxis_label, len(xaxis_label))
    a = np.array(a).reshape(len(mode_season_list), len(xaxis_label))
    X = cdms2.createAxis(xaxis_label)
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
