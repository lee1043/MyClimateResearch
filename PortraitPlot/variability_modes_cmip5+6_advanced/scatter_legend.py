import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111)

colors =  plt.cm.tab20c(np.arange(20).astype(int))
#plt.scatter(np.arange(20), np.ones(20), c=colors, s=180)

modes = ['NAM', 'NAO', 'PNA', 'SAM']
seasons = ['DJF', 'MAM', 'JJA', 'SON']

# colors
SeasonColorGradation = True
if SeasonColorGradation:
    colors =  plt.cm.tab20c(np.arange(20).astype(int))
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

# Plot markers
i = 100
for mode in modes:

    if mode == 'SAM':
        seasons = ['JJA', 'SON', 'DJF', 'MAM']
    else:
        seasons = ['DJF', 'MAM', 'JJA', 'SON']

    ax.text(0.988, i, mode, va='center', ha='left')

    for season in seasons:
        # color -> mode
        if SeasonColorGradation:
            c = color_dict[mode+'_'+season]
        else:
            c = color_dict[mode]
        # shape -> season
        s = shape_dict[season]
        ax.plot(1, i, marker=s, color=c, markersize=10)
        ax.text(1.005, i, season, va='center', ha='left')
        i -= 1 

    i -= 0.5

# Save image
plt.savefig('scatter_markers.png')

