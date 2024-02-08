#!/usr/bin/env python3
from os import chdir, getcwd
from os.path import basename, join as pjoin
import gc
import math
import sys

import numpy as np
import MDAnalysis as mda
from MDAnalysis.transformations import center_in_box, wrap
import utils

analysis_dirname = basename(getcwd())
output_filename = pjoin(analysis_dirname, 'density_z.plo')
chdir('..')

s = utils.GetSettings().get('density_z')
if s is None or \
        (isinstance(s, str) and s == 'skip'):
    print('Skipping density Z analysis', file=sys.stderr)
    sys.exit(0)
else:
    s = utils.Settings(**s)
    # extra options are allowed for selections
    _new_components = []
    for component in s.components:
        _new_component = {'updating': False}
        if isinstance(component, dict):
            _new_component.update(component)
        else:
            _new_component['sel'] = component
        _new_components.append(_new_component)
    components = _new_components

    if s.bin_size is None:
        # bin_size = 1. # in angstrom
        bin_size = 2.5  # in angstrom

if s.bin_max is None or s.bin_min is None:
    print("auto-determining boundaries; set bin_max and bin_min to skip")
    _max_z = None

    sys_info_file = pjoin(analysis_dirname, 'sys_info.plo')
    s.bin_min, s.bin_max = utils.get_bounds(sys_info_file,
                                            cols=3, recenter=True)
    s.bin_min -= bin_size/2
    s.bin_max += bin_size/2

if s.symmetrize:
    s.bin_min = 0.

print("Loading PSF and trajectories ...")
psf_dcd = utils.get_psf_dcd_from_settings()
psf, dcds = psf_dcd[0], psf_dcd[1:]
u = mda.Universe(psf, dcds[0])

accum_time = 0

# initialize bins to 0
num_bins = math.ceil((s.bin_max - s.bin_min) / bin_size)
histogram_shape = (len(components), num_bins)
bin_range = s.bin_min, s.bin_max

print("Beginning Z density analysis")
center_atoms = u.select_atoms(s.centersel)
if not len(center_atoms):
    print("No atoms selected by", s.centersel)
    sys.exit(1)

other_atoms_selected = [u.select_atoms(**opts) for opts in components]

output_fmt = '%.2f '+' '.join(['%.2e']*len(components))
accum_time = 0

traj_len = len(u.trajectory)    # total length of a SINGLE trajectory
dcd_len = len(dcds) * traj_len  # total length of ALL dcds

MAX_DCD = 2000
MAX_FRAME = MAX_DCD * traj_len

T0 = 0
T1 = MAX_FRAME//3
T2 = MAX_FRAME*2//3
T3 = MAX_FRAME

bin_totals = {
    range(0, 10*traj_len): np.zeros(histogram_shape)
}

bin_totals = {
    range(0, 10*traj_len): np.zeros(histogram_shape),
    range(T0, T1): np.zeros(histogram_shape),  # 1st third
    range(T1, T2): np.zeros(histogram_shape),  # 2nd third
    range(T2, T3): np.zeros(histogram_shape),  # 3rd third
    range(T0, T3): np.zeros(histogram_shape),  # whole traj
}

# bin_totals = {
#     range(          0, 1*dcd_len//3): np.zeros(histogram_shape),   # 1/3
#     range(1*dcd_len//3, 2*dcd_len//3): np.zeros(histogram_shape),  # 2/3
#     range(2*dcd_len//3, 3*dcd_len//3): np.zeros(histogram_shape),  # 3/3
#     range(          0, 3*dcd_len//3): np.zeros(histogram_shape),   # all
# }

dcd_num = 0
for u in utils.try_reader(psf, dcds):
    if dcd_len is None:
        traj_len = len(u.trajectory)
        dcd_len = traj_len * len(dcds)

    for ts in u.trajectory:
        if '-q' not in sys.argv:
            print("\rFrame: {} / {}".format(dcd_num+1, MAX_FRAME), end='')

        # stop if not in any range
        in_range = False
        for rng, total in bin_totals.items():
            if dcd_num in rng:
                in_range = True

        if not in_range:
            break

        #
        # center system so membrane is along Z=0
        #

        center_atoms = u.select_atoms(s.centersel)
        other_atoms_selected = [u.select_atoms(**opts) for opts in components]
        if s.imaging is not None:
            # multi-step centering
            # MDA does not allow redefinition of center during wrap ...
            ts = center_in_box(center_atoms[0:1])(ts)
            ts = wrap(u.atoms, compound='atoms')(ts)
            ts = center_in_box(center_atoms)(ts)

        ts = wrap(u.atoms, compound='atoms')(ts)
        ts = center_in_box(center_atoms, point=(0, 0, 0))(ts)

        for sel_ind, other_atoms in enumerate(other_atoms_selected):
            # calculate histogram as a probability density
            other_Z = other_atoms.positions[:, 2]

            if s.symmetrize:
                other_Z = np.abs(other_Z)

            bins, edges = np.histogram(other_Z, bins=num_bins, range=bin_range,
                                       density=True)

            # accumulate each frame's density
            for rng, total in bin_totals.items():
                if dcd_num in rng:
                    total[sel_ind, :] += bins

        dcd_num += 1

    # needed to force garbage collection, see utils.try_reader: gc.collect()
    del u

    if not in_range:
        break

gc.collect()

if '-q' not in sys.argv:
    print()

# turn the accumulated density into a mean density
for rng, total in bin_totals.items():
    total /= len(rng) * traj_len

    # calculate bin midpoints
    midpoints = list(map(lambda left, right:
                         (right+left)/2, edges[:-1], edges[1:]))

    # concatenate bin midpoints and densities along a new axis and transpose
    # them so that midpoints and bin_totals are columns
    output = np.stack([midpoints, *total]).T

    outfile = output_filename.split('.')
    outfile.insert(1, f'{rng.start}.{rng.stop}')
    if s.symmetrize:
        outfile.insert(1, 'sym')
    outfile = '.'.join(outfile)
    print('writing', outfile)

    np.savetxt(outfile, output, fmt=output_fmt, header='midpoint density')
