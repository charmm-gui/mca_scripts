#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

for plastic in ('pet', 'pef'):
    for rep in (1, 2, 3):
        project = f"{plastic}_co2_{rep}"

        MSD = np.loadtxt(f"{project}_MSD.dat")
        fit = np.loadtxt(f"{project}_fit_D.dat")

        from_t = 1.
        to_t = 10.
        dt = .1

        eps = .01
        data_tau = np.arange(dt, 21+eps, dt)
        tau = np.arange(from_t, to_t+eps, dt)

        ones = np.ones(data_tau.shape)
        t_start = np.argwhere(np.isclose(data_tau, from_t*ones))[0,0] + 1
        t_end = np.argwhere(np.isclose(data_tau, to_t*ones))[0,0] + 2

        # center bin's index
        mid = list(fit[:,0]).index(0.)

        # plot 5 lines with mid last, skipping every other bin
        start = mid - 5*2
        #end = mid + 20

        fig, ax = plt.subplots()

        #for index in range(mid, end+1, 2):
        for index in range(start, mid+1, 2):
            msd = MSD[index]
            line = fit[index,1:]

            # y = mx + b; m: slope; b: y-intercept
            m, b = line[0:2]
            line_points = np.array([m*x + b for x in tau])

            bin_midp = msd[0]
            bin_values = msd[t_start:t_end]

            mdp_line = plt.plot(tau, bin_values, label=f"Bin at {bin_midp*10: 3.0f} Å")[0]
            plt.plot(tau, line_points, color=mdp_line.get_color())

        plt.legend()
        ax.set_title(f'{plastic.upper()} rep {rep}')
        ax.set_xlabel('Lag time (ns)')
        ax.set_ylabel('MSD (nm$^2$/ns)')
        plt.savefig(f"sample_figures/{project}.png")
