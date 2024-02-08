#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


DIRECT_TAUS = 2., 5.
TAUS = [str(t) for t in (*DIRECT_TAUS, 'fit')]  # for printing
COLS = [round(dtau*10)+1 for dtau in DIRECT_TAUS]
MID_SLICE = None

for plastic in ('pet', 'pef'):
    # aggregate across replicas
    aggregate = []
    for rep in (1, 2, 3):
        project = f"{plastic}_co2_{rep}"

        # each line of fit is: midpoint slope y-intercept rvale pvalue stderr
        fit = np.loadtxt(f"{project}_fit_D.dat")

        fig, ax = plt.subplots()
        plt.errorbar(
            fit[:,0]*10,     # X axis: bin midpoint (convert nm to Å)
            fit[:,1]/2,        # Y axis: diffusion constant
            yerr=fit[:,-1],  # ± standard error of line fit
            label=f'{plastic.upper()} (rep {rep}) with CO$_2$',
            fmt='-o',
        )

        plt.legend()
        ax.set_xlim(-40,40)
        ax.set_ylim(0, 0.25)
        ax.set_xlabel('Bin midpoint (Å)')
        ax.set_ylabel('Diffusion coefficient (nm$^2$/ns)')
        plt.savefig(f"figures/{project}.png")

        fit = np.hstack([fit[:,0,np.newaxis], fit[:,1,np.newaxis]/2])
        #np.savetxt(f"{project}_D_final.dat", fit)

        # combine direct diffusion calculations into a single file for plotting
        agg = np.loadtxt(f"{project}_D.dat")[:,COLS]
        # columns: [bins, tau1,...,tau_final, fitted]
        agg = np.hstack([fit[:,0,np.newaxis], agg, fit[:,1,np.newaxis]])
        aggregate.append(agg)

    # axes: [replica, bin, tau]
    aggregate = np.array(aggregate)

    # axes: [bin, tau (1st half: diffusion constants, 2nd half: stderrs)]
    agg = np.hstack([
        aggregate[0,:,0,np.newaxis],           # bin location
        aggregate[:,:,1:].mean(axis=0),        # diffusion constants across replicas
        stats.sem(aggregate[:,:,1:], axis=0),  # and their standard error
    ])

    # get index of ±1.5 nm
    if MID_SLICE is None:
        bins = fit[:,0]
        # more accurate than checking == ±1.5 due to floating point nonsense
        MID_SLICE = slice(
            np.argmin(np.abs(bins + 1.5)),
            np.argmin(np.abs(bins - 1.5))+1  # make inclusive range
        )

    # np.mean() supports flattening multiple dimensions, but stats.sem does not
    mid_only = aggregate[:,MID_SLICE,1:]
    mos = mid_only.shape
    mid_norep = mid_only.reshape(mos[0]*mos[1], mos[2])
    mid_D, mid_se = mid_norep.mean(axis=0), stats.sem(mid_norep, axis=0)
    print(f"{plastic}:")
    print('    '+('{:19s} '*len(TAUS)).format(*TAUS))
    print('    ', end='')
    for D, se in zip(mid_D, mid_se):
        print(f"{D:.3e}±{se:.3e}", end=' ')
    print()

    # report weighted mean ± s.e.m. within middle of plastic
    #np.savetxt(f"{plastic}_co2_avg.dat", agg)
