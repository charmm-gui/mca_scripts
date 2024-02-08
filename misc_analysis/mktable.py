#!/usr/bin/env python
import os
import re
import sys
from glob import glob

SYSTEMS = {
    'axolemma': (5, 10, 30),
    'membrane': (5, 10, 30),
    'mcm': (1, 2, 3)
}

MSD_RE = re.compile(r'^[^=]*= (?P<msd>[0-9.-]*)[^-]*- (?P<error>[0-9.-]*)')

def get_lipids():
    with open('msd.config') as config_file:
        return [line.strip().split()[0] for line in config_file]

def get_msd(filename):
    global MSD_RE

    with open(filename) as msd_file:
        for line in msd_file:
            if not line.startswith('# D['):
                continue
            break

        m = MSD_RE.match(line)
        try:
            return float(m.group('msd')), float(m.group('error'))
        except:
            print(f"Can't convert float in {filename}: {line.strip()}")
            sys.exit(1)

for system, nums in SYSTEMS.items():
    for num in nums:
        if system == 'mcm':
            os.chdir(f'{system}{num}/gromacs')
        else:
            os.chdir(f'{system}_{num}/gromacs')

        lipids = get_lipids()
        for lipid in lipids:
            lower = lipid.lower()
            #for half in ('first', 'second', 'all'):
            for half in ('first',):
                if 'mcm' in system:
                    msd, error = get_msd(f'msd_{lower}_top_{half}.xvg')
                else:
                    msd, error = get_msd(f'msd_{lower}_{half}.xvg')

                # MSD is given in the bewildering units of 1e-5 nm^2/s
                print(f"{system:>8s} {num:d} {lipid:5s} {half:6s} {msd: .1e} {error: .1e}")
                #print(f"{system:>8s}_{num:d} {lipid:5s} {half:6s} {msd: .1e} {error: .1e}")

        os.chdir('../..')
