#!/usr/bin/env python3
from os import chdir, getcwd
from os.path import basename, exists, join as pjoin
import math
import sys

import numpy as np
import utils

analysis_dirname = basename(getcwd())
output_filename = pjoin(analysis_dirname, 'density_z.plo')
chdir('..')

selections = utils.GetSettings().get('density_z')
if selections is None or (isinstance(selections, str) and selections == 'skip'):
    print('Skipping density Z analysis', file=sys.stderr)
    sys.exit(0)
else:
    _vars = 'bin_size', 'bin_min', 'bin_max', 'centersel', 'components', 'imaging'
    for var in _vars:
        globals()[var] = selections.get(var)

    # extra options are allowed for selections
    _new_components = []
    for component in components:
        _new_component = {'updating': False}
        if isinstance(component, dict):
            _new_component.update(component)
        else:
            _new_component['sel'] = component
        _new_components.append(_new_component)
    components = _new_components

    if bin_size is None:
        bin_size = 1. # in angstrom

if bin_max is None or bin_min is None:
    print("auto-determining boundaries; set bin_max and bin_min to skip")
    _max_z = None

    sys_info_file =  pjoin(analysis_dirname, 'sys_info.plo')
    bin_min, bin_max = utils.get_bounds(sys_info_file, cols=3, recenter=True)
    bin_min -= bin_size/2
    bin_max += bin_size/2

print("Importing modules ...")
from MDAnalysis.transformations import center_in_box, wrap, unwrap
import MDAnalysis as mda

print("Loading PSF and trajectories ...")
psf_dcd = utils.get_psf_dcd_from_settings()
u = mda.Universe(*psf_dcd)

last_time = 0
accum_time = 0
dcd_len = len(u.trajectory)

# initialize bins to 0
num_bins = math.ceil((bin_max - bin_min) / bin_size)
histogram_shape = (len(components), num_bins)
bin_range = bin_min, bin_max
bin_totals = np.zeros(histogram_shape)

print("Beginning Z density analysis")
center_atoms = u.select_atoms(centersel)
other_atoms_selected = [u.select_atoms(**opts) for opts in components]

output_fmt = '%.1f '+' '.join(['%.2e']*len(components))
last_time = 0
accum_time = 0

for dcd_num, ts in enumerate(u.trajectory):
    # get accumulated time
    if ts.time < last_time:
        accum_time += last_time
    time = (accum_time + ts.time) / 1000
    last_time = ts.time

    if not '-q' in sys.argv:
        print("\rFrame: {} / {}; time = {:.2f}".format(dcd_num+1, dcd_len, time), end='')

    #
    # center system so membrane is along Z=0
    #

    if imaging is not None:
        # multi-step centering
        # MDA does not allow redefinition of center during wrap ...
        ts = center_in_box(center_atoms[0:1])(ts)
        ts = wrap(u.atoms, compound='atoms')(ts)
        ts = center_in_box(center_atoms)(ts)

    ts = wrap(u.atoms, compound='atoms')(ts)
    ts = center_in_box(center_atoms, point=(0,0,0))(ts)

    for sel_ind, other_atoms in enumerate(other_atoms_selected):
        # calculate histogram as a probability density
        other_Z = other_atoms.positions[:,2]
        bins, edges = np.histogram(other_Z, bins=num_bins, range=bin_range, density=True)

        # accumulate each frame's density
        bin_totals[sel_ind,:] += bins

if not '-q' in sys.argv:
    print()

# turn the accumulated density into a mean density
bin_totals /= dcd_len

# calculate bin midpoints
midpoints = list(map(lambda left, right: (right+left)/2, edges[:-1], edges[1:]))

# concatenate bin midpoints and densities along a new axis and transpose
# them so that midpoints and bin_totals are columns
output = np.stack([midpoints, *bin_totals]).T

np.savetxt(output_filename, output, fmt=output_fmt, header='midpoint density')

