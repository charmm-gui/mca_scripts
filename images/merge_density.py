#!/usr/bin/env python3
import numpy as np
from scipy.stats import sem

HAS_CO2 = True

if HAS_CO2:
    topologies = "pet_co2", "pef_co2"
    starts =   0,    0,  6666, 13333,     0
    ends   = 100, 6666, 13333, 20000, 20000
else:
    topologies = "pet_vac", "pef_vac"
    starts =    0, 1666, 3333,    0
    ends   = 1666, 3333, 5000, 5000

reps = 1, 2, 3


for top in topologies:
    for i in range(len(starts)):
        start = starts[i]
        end = ends[i]
        data = np.array([
            np.loadtxt(f"density/{top}_{rep}_density_z.{start}.{end}.plo") for rep in reps
        ])

        means = data.mean(axis=0)
        std_of_mean = sem(data, axis=0)

        if HAS_CO2:
            # target layout:
            # Z mean_poly sem_poly mean_co2 sem_co2
            output = np.array([
                means[:,0],       # Z
                means[:,1],       # mean_poly
                std_of_mean[:,1], # sem_poly
                means[:,2],       # mean_co2
                std_of_mean[:,2], # sem_co2
            ])
        else:
            output = np.array([
                means[:,0],       # Z
                means[:,1],       # mean_poly
                std_of_mean[:,1], # sem_poly
            ])

        #import pdb; pdb.set_trace()
        np.savetxt(f"density/{top}_density_z.{start}.{end}.plo", output.T,
                header="Z mean_poly sem_poly mean_co2 sem_co2")
