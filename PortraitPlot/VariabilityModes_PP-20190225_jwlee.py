"""
WORKING CONDITION: JL's local Mac, conda env: pmp_nightly_20180622
"""

from __future__ import print_function
import base64
import cdms2
import genutil
import json
import MV2
import numpy as np
import os
import pcmdi_metrics
import pcmdi_metrics.graphics.portraits
import re
import sys
import tempfile
import vcs


def main():
    stat = 'rms_alt'
    modes = ['SAM', 'NAM', 'NAO', 'PNA', 'PDO']
    stat_xy = read_json_and_merge_axes(stat, modes)
    imgName = 'test_PP'
    generate_portrait(stat_xy, imgName)


def read_json_and_merge_axes(stat, modes):
    model_run_list = []
    mode_season_list = []
    a = []
    for mode in modes:
        input_file = 'var_mode_'+mode+'_EOF1_stat_cmip5_historical_mo_atm_1900-2005_adjust_based_tcor_pseudo_vs_model_pcs.json'
        # open json
        with open(os.path.join('json_files', input_file)) as f:
            d = json.load(f)
        # Get potential x-axis first
        if mode == modes[0]:
            models_list = sorted(list(d["RESULTS"].keys()))
            for model in models_list:
                runs_list = sort_human(list(d["RESULTS"][model].keys()))
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
            for model_run in model_run_list:
                model = model_run.split('_')[0]
                run = model_run.split('_')[-1]
                try:
                    a.append(d["RESULTS"][model][run]["defaultReference"][mode][season][stat])
                except:
                    #a.append(-1.e20)
                    a.append(np.nan)
    # convert to array and decorate axes
    a = np.array(a).reshape(len(mode_season_list), len(model_run_list))
    X = cdms2.createAxis(model_run_list)
    Y = cdms2.createAxis(mode_season_list)
    a = MV2.array(a, axes=(Y,X), id=stat)
    return a


def sort_human(l):
  convert = lambda text: float(text) if text.isdigit() else text
  alphanum = lambda key: [ convert(c) for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key) ]
  l.sort( key=alphanum )
  return l


def generate_portrait(stat_xy, imgName):
    # Get median
    median = genutil.statistics.median(stat_xy, axis=1)[0]
    print(median)
    print(median.shape)
    # Match shapes
    stat_xy, median = genutil.grower(stat_xy,median)
    print(stat_xy.shape)
    print(median.shape)
    # Normalize by median value
    median = np.array(median)
    stat_xy_normalized = MV2.divide(MV2.subtract(stat_xy,median),median)
    print(stat_xy_normalized.shape)
    stat_xy_normalized.setAxisList(stat_xy.getAxisList())
    #
    # Plotting
    #
    # Set up VCS Canvas
    class VCSAddonsNotebook(object):
        def __init__(self,x):
            self.x = x
        def _repr_png_(self):
            fnm = tempfile.mktemp()+".png"
            self.x.png(fnm)
            encoded = base64.b64encode(open(fnm, "rb").read())
            return encoded
        def __call__(self):
            return self
    # VCS Canvas
    x = vcs.init(bg=True,geometry=(2600,800))
    show = VCSAddonsNotebook(x)
    # Load our "pretty" colormap
    x.scriptrun(
        os.path.join(
            sys.prefix,
            "share",
            "pmp",
            "graphics",
            'vcs',
            'portraits.scr'))
    # Set up Portrait Plot
    P = pcmdi_metrics.graphics.portraits.Portrait()
    xax = [t+' ' for t in stat_xy_normalized.getAxis(1)[:]]
    yax = [t+' ' for t in stat_xy_normalized.getAxis(0)[:]]
    # Preprocessing step to "decorate" the axis
    P.decorate(stat_xy_normalized, yax, xax)
    #
    # Customize
    #
    SET = P.PLOT_SETTINGS
    # Viewport on the Canvas
    SET.x1 = .05
    SET.x2 = .88
    SET.y1 = .25
    SET.y2 = .9
    # Both X (horizontal) and y (VERTICAL) ticks
    # Text table
    SET.tictable = vcs.createtexttable()
    SET.tictable.color="black"
    # X (bottom) ticks
    tictextsize = 9
    # Text Orientation
    SET.xticorientation = vcs.createtextorientation()
    SET.xticorientation.angle = -90
    SET.xticorientation.halign="right"
    SET.xticorientation.height = tictextsize 
    # Y (vertical) ticks
    SET.yticorientation = vcs.createtextorientation()
    SET.yticorientation.angle = 0
    SET.yticorientation.halign="right"
    SET.yticorientation.height = tictextsize
    # We can turn off the "grid"
    SET.draw_mesh = "y"
    # Control color for missing
    SET.missing_color = "grey"
    # Tics length
    SET.xtic1.y1 = 0
    SET.xtic1.y2 = 0
    # Timestamp
    SET.time_stamp = None
    # Colormap
    SET.colormap = "bl_to_darkred"
    # level to use
    SET.levels = [-.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5]
    SET.levels.insert(0,-1.e20)
    SET.levels.append(1.e20)
    # colors to use
    SET.fillareacolors = vcs.getcolors(SET.levels,split=0,colors=range(16,240))
    # Plot
    P.plot(stat_xy_normalized, x=x)
    # Save
    x.png(imgName+'.png')
    #
    # Annotated Plot 
    #
    Annotated = False
    if Annotated:
        x.clear()
        SET.values.show = True
        SET.values.array = stat_xy
        P.plot(stat_xy_normalized,x=x,bg=0)
        x.png(imgName+'_annotated.png')


if __name__ == '__main__':
    main()
