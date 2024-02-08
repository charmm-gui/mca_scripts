#!/usr/bin/env python
import numpy as np
from scipy.stats import sem

# plt.style.use('_mpl-gallery')

for ttype in ['easy', 'hard']:
    data = np.loadtxt(f'stats.{ttype}.dat')

    # remove all entries after 100% fail rate
    nrep = 12
    nfails = None
    prev_vv = -1
    rm_idx = len(data)
    for idx, entry in enumerate(data):
        vv = entry[0]
        if vv != prev_vv:
            nfails = 0
            prev_vv = vv

        failed = entry[-1]
        if failed:
            nfails += 1
            if nfails >= nrep:
                rm_idx = idx+1
                break

    data = data[:rm_idx]

    # reformat 3 reps into a separate axis
    nrow, ncol = data.shape
    try:
        data = data.reshape(nrow//nrep, nrep, ncol)
    except:
        breakpoint()
        pass

    # average along reps axis
    means = data.mean(axis=1)
    sems = sem(data, axis=1)

    out = np.hstack([
        data[:,0,0,np.newaxis],    # target % v/v
        means[:,2,np.newaxis],     # mean runtime
        sems[:,2,np.newaxis],      # s.e.m. runtime
        means[:,3,np.newaxis],     # fail rate
    ])

    np.savetxt(f'stats.{ttype}.avg.dat', out)
