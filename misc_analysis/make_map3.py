#!/usr/bin/env python3
import os
import itertools as it

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

SHOW_MEMB = False
MINIMAL = True
ALL_BOLD = False

outfile = 'contact_clean.png' if MINIMAL else 'contact.png'

name_to_label = {
    'PAA': 'Ubiquitin',
    'PAB': 'Villin',
    'PAC': 'Protein G',
    'MEMB': 'Membrane',
    'H*': 'Membrane'
}

project = os.getcwd().split(os.sep)[-2]
name, rep = project.split('_')

if name == 'peo':
    name_to_label['H*'] = 'Polymer'
elif name == 'ha':
    name_to_label['H*'] = 'HAP'

selections = []
with open('settings.str') as settings_file:
    for line in settings_file:
        if '!' in line:
            line = line[:line.index('!')]
        line = line.upper().strip()
        if line.startswith('SET '):
            selections.append(line.split()[-1])
nselsx = len(selections)
nselsy = nselsx

if ALL_BOLD:
    for setting in mpl.rcParams.find_all('weight').keys():
        mpl.rcParams[setting] = 'bold'
mpl.rcParams['font.size'] = 18
mpl.rcParams['figure.subplot.left'] = 0.20
mpl.rcParams['figure.dpi'] = 300

pairs = it.combinations_with_replacement(selections, r=2)
skip_pairs = (('MEMB',)*2, ('H*',)*2)
probabilities = np.zeros((nselsy, nselsx))

data = np.loadtxt('contact.dat', dtype=str)
for pair in pairs:
    if pair in skip_pairs:
        continue
    pair_str = '_'.join(pair)

    # isolate the entries for this pair
    pair_data = data[data[:,1] == pair_str]

    # remove middle column
    pair_data = pair_data[:,(0,2)].astype(float)

    i, j = map(selections.index, pair)
    probability = pair_data[:,1].mean()
    probabilities[i,j] = pair_data[:,1].mean()
    probabilities[j,i] = pair_data[:,1].mean()
    print(*pair, f'({i}, {j})', probability)

# membrane is always in contact with itself
if SHOW_MEMB:
    probabilities[-1,-1] = 1
else:
    # remove bottom row
    nselsy -= 1
    probabilities = probabilities[:-1,:]

im = plt.imshow(probabilities)
ax = im.axes

if MINIMAL:
    plt.set_cmap(mpl.colormaps['jet'])
    plt.clim(0, 1)

    labels = [''] * len(selections)

    # similar effect to ax.label_outer()
    if name == 'peo':
        ax.set_xticks([i for i in range(nselsx)], labels=labels)
    else:
        ax.set_xticks([])

    if rep == '5':
        ax.set_yticks([i for i in range(nselsy)], labels=labels[:nselsy])
    else:
        ax.set_yticks([])
else:
    cbar = plt.colorbar(im)
    plt.set_cmap(mpl.colormaps['jet'])
    plt.clim(0, 1)

    labels = [name_to_label[sel] for sel in selections]

    ax.set_xticks([i for i in range(nselsx)], labels=labels, rotation=45)
    ax.set_yticks([i for i in range(nselsy)], labels=labels[:nselsy])
    cbar.ax.set_ylabel('Interaction Probability', labelpad=8)

if name == 'membrane':
    name = 'CHL1/POPC/PSM'
elif name == 'ha':
    name = 'HAP'
elif name == 'peo':
    name = 'EE$_{37}$EO$_{40}$'
else:
    name = name.capitalize()

if not MINIMAL:
    ax.set_title(f'{name} ({rep}% v/v)')

# show probability as text in cell centers
for i in range(nselsy):
    for j in range(nselsx):
        # ha: horizontal alignment, va: vertical alignment
        p = probabilities[i,j]
        color = 'black' if p >= .3 and p <= .7 else 'white'
        ax.text(j, i, f'{p:.3f}', ha='center', va='center', color=color,
                fontsize=14, fontweight='bold')

    plt.savefig(outfile)
