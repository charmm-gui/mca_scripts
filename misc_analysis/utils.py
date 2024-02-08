import os
import sys
from glob import glob
from os.path import exists, join as pjoin, split as psplit
from itertools import product, zip_longest

import numpy as np
import yaml

ANALYSIS_DIR = os.getcwd()
UTILS_ROOT = '.' if __name__ == '__main__' else psplit(__file__)[0]


class Settings:
    """Really just a dict that uses the dot operator"""

    def __init__(self, **attrs):
        self._attrs = attrs
        for attr, value in attrs.items():
            setattr(self, attr, value)

    def __getattr__(self, index):
        """Returns None by default"""
        return None


class GetSettings:
    """Singleton getter for inheritable settings.yml"""
    global ANALYSIS_DIR

    SETTINGS = None

    def __new__(cls):
        if cls.SETTINGS is None:
            # default settings in case none can be found
            cls.SETTINGS = {'dcd_dir': '.'}

            # possible locations for settings
            paths = [
                pjoin(UTILS_ROOT, 'settings.yml'),
                pjoin(ANALYSIS_DIR, 'settings.yml'),
            ]

            # gives priority to the most specific setting
            for path in paths:
                if exists(path):
                    cls.SETTINGS.update(load_yaml(path))

        return cls.SETTINGS


class MinMax:
    """Tracks multiple keyed minimum and maximum values"""

    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        if key not in self.data:
            return dict(min=None, max=None)
        _min, _max = self.data[key]
        return dict(min=_min, max=_max)

    def add(self, key, value):
        if key in self.data:
            _min, _max = self[key]
            _max = value if value > _max else _max
            _min = value if value > _min else _min
            self.data[key] = _max, _min
        else:
            self.data[key] = value, value


def get_dcd_sorted(dcd_dir, dcd_prefix):
    """Get all trajectory files in dcd_dir/ by counting up from 1

    Returns a list of files sorted numerically
    """
    dcd_files = []
    dcd_num = 1
    dcd_name = ""
    while True:
        dcd_name = f'{dcd_prefix}_{dcd_num}.dcd'
        dcd_path = pjoin(dcd_dir, dcd_name)

        if not exists(dcd_path):
            break

        dcd_files.append(dcd_path)
        dcd_num += 1

    if not dcd_files:
        raise FileNotFoundError(dcd_name)

    return dcd_files


def get_psf_dcd_from_settings():
    return [get_psf_from_settings()] + get_dcd_from_settings()


def get_equilibration_from_settings():
    """Return value includes PSF"""
    def dcd_order(fn):
        # reduce step6.5_equilibration.dcd to 5
        return int(fn[fn.index('.')+1:fn.index('_')])

    dcd_dir = GetSettings()['dcd_dir']
    psf = get_psf_from_settings()
    dcd = glob(pjoin(dcd_dir, 'step*equilibration.dcd'))
    dcd.sort(key=dcd_order)
    return [psf] + dcd


def get_psf_from_settings():
    dcd_dir = GetSettings()['dcd_dir']
    psf_files = glob(pjoin(dcd_dir, '*.psf'))

    if not psf_files:
        raise FileNotFoundError(f"Can't find psf file in {dcd_dir}")
    if len(psf_files) > 1:
        raise FileExistsError("Too many PSF files to choose from")

    return psf_files[0]


def get_dcd_from_settings():
    dcd_dir = GetSettings()['dcd_dir']

    # try to get *.dcd prefix
    for dcd_prefix in range(10, 0, -1):
        if exists(pjoin(dcd_dir, f'step{dcd_prefix}_1.dcd')):
            break
    if dcd_prefix == 0:
        raise FileNotFoundError("Cannot determine .dcd prefix")

    dcd_prefix = f'step{dcd_prefix}'
    return get_dcd_sorted(dcd_dir, dcd_prefix)


def load_yaml(filename):
    """Loads key/value pairs into a dictionary"""
    with open(filename) as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def mindist_pbc(p1, p2, dims):
    """Calculates the minimum distance between two points located within
    a periodic orthorhombic geometry"""
    x, y, z, _, _, _ = dims

    # check all 27 transformations for adjacent cells
    images = product(*[[-1, 0, 1]]*3)
    tfs = np.array(list(images)) * [x, y, z]
    return min(np.linalg.norm(p1-(p2+tf)) for tf in tfs)


def get_bounds(system_size, cols=(1, 2, 3), recenter=False):
    unpack = False
    if isinstance(cols, int):
        cols = (cols,)
        unpack = True
    if isinstance(system_size, str):
        if not exists(system_size):
            print("Error: no system size; run sys_info.py to fix",
                  file=sys.stderr)
            sys.exit(1)
        system_size = np.loadtxt(system_size)

    # filter columns
    ncols = system_size.shape[1]
    cols = [col in cols for col in range(ncols)]
    system_size = system_size.T[cols].T

    if recenter:
        maxs = system_size.max(axis=0) / 2
        mins = -maxs
    else:
        maxs = system_size.max(axis=0)
        mins = np.zeros(shape=maxs.shape)

    if unpack:
        mins = mins[0]
        maxs = maxs[0]

    return mins, maxs


def try_reader(psf, dcds, verbose=False):
    """The DCDReader class fails to read under mysterious circumstances. This
    generator attempts to read as many files as possible and
    recovering/retrying on failure."""
    import MDAnalysis as mda
    import gc
    from MDAnalysis.coordinates.DCD import DCDReader

    # override the MDA function that causes all those error messages during
    # __del__()
    def close_fixed(self):
        """close reader, if there is anything to close"""
        if getattr(self, '_file', None):
            self._file.close()

    DCDReader.close = close_fixed

    unread_dcds = dcds
    # MAX_READ = len(unread_dcds)
    MAX_READ = min(100, len(unread_dcds))
    while unread_dcds:
        u = None
        gc.collect()  # needed to ensure deletion of mda.Universe(...)

        try:
            dcds_to_read = unread_dcds[:MAX_READ]
            if verbose:
                print(f"trying to read from {dcds_to_read[0]} to " +
                      f"{dcds_to_read[-1]}")
            u = mda.Universe(psf, unread_dcds[:MAX_READ])
            yield u
            del u
        except OSError as e:
            import traceback
            filename_found = False
            for frame in reversed(list(traceback.walk_tb(e.__traceback__))):
                try:
                    summary = traceback.StackSummary.\
                              extract([frame], capture_locals=True)[0]
                except Exception:
                    continue

                if 'filename' in summary.locals:
                    filename = eval(summary.locals['filename'])
                    MAX_READ = unread_dcds.index(filename)
                    filename_found = True
                    if verbose:
                        print('filename causing problem:', filename)
                    break

            if not filename_found:
                if verbose:
                    print('failed to find filename in traceback')
                raise

            continue

        unread_dcds = unread_dcds[MAX_READ:]
        MAX_READ = len(unread_dcds)

    gc.collect()


def grouper(iterable, n, fillvalue=None):
    """Copied from itertools documentation

    Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
