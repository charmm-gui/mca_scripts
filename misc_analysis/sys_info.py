#!/usr/bin/env python3
#
# Reads system dimensions for each frame and calculates the volume
#
print("Importing modules ...")
from os import chdir, getcwd
from os.path import basename, exists, join as pjoin
import sys
import utils
import MDAnalysis as mda

analysis_dir = basename(getcwd())
chdir('..')

if '--equilibration' in sys.argv:
    psf_dcd = utils.get_equilibration_from_settings()
    output_filename = pjoin(analysis_dir, 'sys_equi.plo')
else:
    psf_dcd = utils.get_psf_dcd_from_settings()
    output_filename = pjoin(analysis_dir, 'sys_info.plo')

psf, dcds = psf_dcd[0], psf_dcd[1:]

print("Loading PSF and trajectories ...")
u = mda.Universe(psf, dcds[0])

print("Beginning system size analysis")

# output format: 5 columns of floats with precision of 10**-2 (0.01)
output_fmt = ' '.join(["{:.2f}"]*5)
last_time = 0
accum_time = 0

traj_len = len(u.trajectory)
dcd_len = len(dcds) * traj_len

dcd_num = 0
with open(output_filename, 'w') as outfile:
    print("#time xtla xtlb xtlc volume", file=outfile)
    for u in utils.try_reader(psf, dcds):
        for ts in u.trajectory:
            # ts.time cycles from 100-1000 for each DCD
            # we want to report total accumulated time
            if ts.time < last_time:
                accum_time += last_time
            time = (accum_time + ts.time) / 1000

            # show time progress on a single updating line
            if '-q' not in sys.argv:
                print("\rFrame: {} / {}; time = {:.2f}".format(dcd_num+1, dcd_len, time), end='')

            # write dimensions at this time step
            x, y, z, alpha, beta, gamma = ts.dimensions
            volume = x*y*z
            output = output_fmt.format(time, x, y, z, volume)
            print(output, file=outfile)

            last_time = ts.time
            dcd_num += 1


print()  # clear the last line
