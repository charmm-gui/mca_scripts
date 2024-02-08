#!/usr/bin/env python
import numpy as np
from scipy.stats import sem

# plt.style.use('_mpl-gallery')

for ttype in ['easy', 'hard']:
    data = np.loadtxt(f'stats.{ttype}.dat')

    # reformat 3 reps into a separate axis
    nrep = 3
    nrow, ncol = data.shape
    data = data.reshape(nrow//nrep, nrep, ncol)

    # average along reps axis
    means = data.mean(axis=1)
    sems = sem(data, axis=1)

    out = np.hstack([
        data[:,0,0,np.newaxis],    # target % v/v
        means[:,2,np.newaxis],     # mean runtime
        sems[:,2,np.newaxis],      # s.e.m. runtime
        means[:,3,np.newaxis],     # fail rate
        sems[:,3,np.newaxis],      # s.e.m. fail rate
    ])

    np.savetxt(f'stats.{ttype}.avg.dat', out)
