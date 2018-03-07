import glob
import math
import os
import sys
from PIL import Image
from PIL import ImageDraw

debug = True

#modes = ['NAM', 'NAO', 'PNA', 'SAM', 'PDO']
modes = ['NAM']
modes = ['NAO']
modes = ['PNA']
modes = ['SAM']
modes = ['PDO']
modes = ['NAM', 'NAO', 'PNA', 'SAM']

datadir = './result'
outdir = os.path.join(datadir,'combined_psd_plots')

for mode in modes:

  print mode

  if mode in ['PDO']:
    obs_list = ['HadISSTv1.1', 'HadISSTv2.1', 'ERSSTv3b']
  else:
    obs_list = ['NOAA-CIRES_20CR', 'ERA20C', 'HadSLP2r']

  files = []

  for obs in obs_list:
    files.extend(glob.glob(os.path.join(datadir,mode+'_'+obs,'*_obs_*.png')))

  files.extend(sorted(glob.glob(os.path.join(datadir,mode+'_'+obs_list[0],'*_cmip5_*.png'))))
      
  # Calculate optimum row/col ---
  num = len(files)
  col = 5
  row = num // col
  if num % col > 0: row = row + 1
  if debug: print(num, col, row)
  
  # Set thumbnail plot size ---
  hor = 400
  ver = 400
  
  # Open new image ---
  result = Image.new("RGB", (col*hor, row*ver), (255,255,255,0))
  
  # Append plots ---
  for index, file in enumerate(files):
      if debug: print(index, file)
      path = os.path.expanduser(file)
      img = Image.open(path.strip())
      draw = ImageDraw.Draw(img)
      img.thumbnail((hor, ver), Image.ANTIALIAS)
  
      x = index % col * hor
      y = index // col * ver
      w, h = img.size
      if debug: print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
      result.paste(img, (x, y, x + w, y + h))
  
  # Save image ---
  output_png = 'combine_psd_'+mode+'.png'
  result.save(os.path.join(outdir,output_png))
