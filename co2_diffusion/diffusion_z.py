#!/usr/bin/env python
import mdtraj as md
import numpy as np
from scipy import stats


def calc_MSD(traj_file, top_file, dt=0.1, bin_size=0.1, maxt=5000):
    """Also calculates instantaneous D and the number of samples in each bin"""
    traj = md.load(traj_file, top=top_file)

    # NVT simuation: constant unit cells
    unit_cell = traj.unitcell_lengths[0,:]
    unit_Z = unit_cell[2]
    center = unit_cell / 2
    center_Z = center[2]

    # get Z coordinates centered w/ membrane at Z=0
    all_Z = traj.xyz[:,:,2] - center_Z

    # lag_time: [bin_values]
    bins_MSD = {}
    bins_D = {}
    bins_samples = {}
    # left bin edges centered on membrane
    edges = np.arange(0., unit_Z+bin_size, bin_size) - center_Z - bin_size/2
    midpoints = edges + bin_size/2

    #
    # Calculation of diffusion (D) from standard deviation of displacement (∆z)
    #
    # D = <[∆z(t) - <∆z(t)>]^2>/(2*tau)
    # where ∆z(t) = z(t+tau) - z(t)

    eps = dt/10  # don't rely on <= and < giving different results
    for lag_time in np.arange(dt, maxt+eps, dt):
        print(f'\rlag_time = {lag_time:.1f} ns', end='')
        nstep = round(lag_time / dt)
        # z(t) for all t at least tau before simulation end
        zt = all_Z[:-nstep,:]
        # z(t+tau) for all t at least tau after simulation start
        ztt = all_Z[nstep:,:]
        # ∆z(t) = z(t+tau) - z(t)
        dzt = np.abs(ztt - zt)

        # PBC correction, N.B. this is NOT the same as unwrapping the
        # trajectory and only works if tau is small
        dzt = np.min([dzt, unit_Z-dzt], axis=0)

        # bin z(t)
        mean_square_displacement = []
        diffusion = []
        samples = []
        for edge in edges:
            in_bin = np.all([edge <= zt, zt < edge+bin_size], axis=0)

            if in_bin.size:
                bin_dzt = dzt[in_bin]

                # MSD(∆t) = 2*d*D*∆t, where d is the number of dimensions of motion
                MSD = ((bin_dzt - bin_dzt.mean())**2).mean()
                # D = MSD(∆t) / (2*d*∆t); d is 1 since we're doing a Z profile
                D = MSD / (2*lag_time)

                mean_square_displacement.append(MSD)
                diffusion.append(D)

                # sample sizes, for curiosity
                samples.append(len(bin_dzt))
            else:
                diffusion.append(None)

        if None in diffusion:
            print('idk what to do here')
            breakpoint()
            quit()

        bins_MSD[lag_time] = np.array(mean_square_displacement)
        bins_D[lag_time] = np.array(diffusion)
        bins_samples[lag_time] = np.array(samples)

    print()

    data_MSD = np.array(list(bins_MSD.values()))
    data_MSD = np.hstack([midpoints[...,np.newaxis], data_MSD.T])

    data_D = np.array(list(bins_D.values()))
    data_D = np.hstack([midpoints[...,np.newaxis], data_D.T])

    data_samples = np.array(list(bins_samples.values()))
    data_samples = np.hstack([midpoints[...,np.newaxis], data_samples.T])

    header = 'midpoint ' + ' '.join([f'τ={k:.1f}' for k in bins_MSD.keys()])
    return data_MSD, data_D, data_samples, header


def linregress_MSD(MSD, data_tau, from_tau, to_tau):
    """Calculates D from linear regression of MSD

    Parameters
    ==========
    MSD       B x (T+1) matrix (B: # bins, T = number of time steps) w/ bins in 1st column
    data_tau  len(T) vector containing all tau values in MSD
    from_tau  minimum tau value to use for fitting
    to_tau    maximum tau value to use for fitting
    """
    # floating point equality is dumb so we have to check "almost equal"
    ones = np.ones(data_tau.shape)

    i_start = np.argwhere(np.isclose(data_tau, from_tau * ones))
    i_end = np.argwhere(np.isclose(data_tau, to_tau * ones))

    assert i_start.shape == (1,1), f"Invalid data_tau or from_tau selection: {i_start}"
    assert i_end.shape == (1,1), f"Invalid data_tau or to_tau selection: {i_end}"

    # +1 to ignore bin location, +1 again to make range inclusive
    i_start = i_start[0,0] + 1
    i_end = i_end[0,0] + 2

    a_tau = data_tau[i_start:i_end]
    bins = MSD[:,0]

    lines = []
    for msd in MSD[:,i_start:i_end]:
        slope, intercept, rval, pval, stderr = stats.linregress(a_tau, msd)
        # D = MSD(∆t) / (2*d*∆t); d is 1 since we're doing a Z profile
        lines.append([slope, intercept, rval, pval, stderr])
    lines = np.array(lines)
    lines = np.hstack([bins[:,np.newaxis], lines])
    return lines


if __name__ == '__main__':
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="In all arguments, units are whatever is "
                                                 "used by the trajectory file")
    parser.add_argument('-f', '--force', action='store_true',
                        help="recalculate MSD if outfile already exists")
    parser.add_argument('-maxt', nargs=1, type=float, default=[5000], metavar='TAU',
                        help="maximum lag time to calculate (default: 5000)")
    parser.add_argument('-from', nargs=1, type=float, required=True, metavar='TAU',
                        help="minimum lag time for line fitting")
    parser.add_argument('-to', nargs=1, type=float, required=True, metavar='TAU',
                        help="maximum lag time for line fitting")
    parser.add_argument('-dt', nargs=1, type=float, default=[0.1], metavar='STEP_SIZE',
                        help="time between recorded frames in trajectory (default: 0.1)")
    parser.add_argument('-binsize', nargs=1, type=float, default=[0.1],
                        help="bin size to use for Z-dependent MSD calculation (default: 0.1)")
    parser.add_argument('project', help="simulation DCD name, not including `.dcd`")

    args = parser.parse_args()

    project = args.project
    outfile_MSD = f'{project}_MSD.dat'
    outfile_D = f'{project}_D.dat'
    outfile_samples = f'{project}_samples.dat'

    # if any outfile is missing (except outfile_fit), recalculate MSD
    outfiles = outfile_MSD, outfile_D, outfile_samples
    do_msd_calc = args.force or not all(os.path.exists(outfile) for outfile in outfiles)

    dt = args.dt[0]
    bin_size = args.binsize[0]
    maxt = args.maxt[0]
    if do_msd_calc:
        traj_file = f'{project}.dcd'
        top_file = f'{project}.pdb'

        print('Calculating MSD and D')
        for filename in (traj_file, top_file):
            if not os.path.exists(filename):
                print("Error: No such file: {filename}", file=sys.stderr)
                sys.exit(1)

        data_MSD, data_D, data_samples, header = calc_MSD(
            traj_file, top_file, dt=dt, bin_size=bin_size, maxt=maxt)

        np.savetxt(outfile_MSD, data_MSD, fmt='%.5f', header=header)
        np.savetxt(outfile_D, data_D, fmt='%.5f', header=header)
        np.savetxt(outfile_samples, data_samples, fmt='%.1f', header=header)

    from_tau = getattr(args, 'from')  # avoids syntax error on access to reserved keyword 'from'
    to_tau = args.to
    if (from_tau is None) or (to_tau is None):
        print('Skipping line fitting.')
        print('Include -from AND -to arguments to calculate D from line fitting')
        sys.exit(0)

    data_MSD = np.loadtxt(outfile_MSD)
    eps = dt/10  # floating point math means don't rely on <= and < giving different results
    data_tau = np.arange(dt, maxt+eps, dt)
    fitted_D = linregress_MSD(data_MSD, data_tau, from_tau, to_tau)

    outfile_fit = f'{project}_fit_D.dat'
    np.savetxt(outfile_fit, fitted_D, fmt='%.5e')
