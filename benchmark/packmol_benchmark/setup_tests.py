#!/usr/bin/env python
import os

########################
# EDIT BELOW THIS LINE #
########################

nreps = 12
first_vv = 10
last_vv = 39

########################
# EDIT ABOVE THIS LINE #
########################

header = """
# dcut used by MCA
tolerance 2.5

output out.pdb
filetype pdb

seed -1
"""

tpl = """
structure ../STRUCT
    number CNT
    resnumbers 0
    inside cube XMIN YMIN ZMIN DLEN
end structure
"""


def get_dim(protein_vv, test_name):
    """Returns the length of a cube that achieves a given protein volume
    fraction `protein_vv` for `count` copies of each protein"""

    global VOLUME

    protein_volume = 0.
    for name in COUNT[test_name].keys():
        protein_volume += VOLUME[name] * COUNT[test_name][name]
    total_volume = protein_volume / protein_vv

    side_length = total_volume ** (1/3)

    return side_length


# volumes given given in Å**3 / molecule
VOLUME = {
    '1ubq': 9367.97827,
    '1vii': 4426.59750,
    '3gb1': 6623.51780,
    'if2': 59748.3237,
    'trna': 21482.9442,
    '1mjc': 7839.39617,
    '1vii': 4426.5975,
    '2hac': 7777.6000,
    '3gb1': 6623.5178,
    '6y3g': 21536.3379,
}
COUNT = {
    'unused': {
        'if2': 10,
        'trna': 20,
    },
    'easy': {
        '1ubq': 10,
        '1vii': 10,
        '3gb1': 10,
    },
    'hard': {
        '1mjc': 8,
        '1vii': 8,
        '2hac': 8,
        '3gb1': 8,
        '6y3g': 8,
    }
}

vvs = [(i+first_vv)/100 for i in range(last_vv - first_vv + 1)]
for difficulty in ('easy', 'hard'):
    for protein_vv in vvs:
        D = get_dim(protein_vv, difficulty)
        center = 0., 0., 0.

        script_tpl = tpl.replace('DLEN', f"{D:.5f}")

        script = [header]
        for name in COUNT[difficulty].keys():
            struct = script_tpl.replace('STRUCT', name+'.pdb') \
                               .replace('CNT', str(COUNT[difficulty][name]))
            for dim, c in zip('XYZ', center):
                d_min = -D / 2. + c
                struct = struct.replace(dim+'MIN', f"{d_min:.5f}")
            script.append(struct)

        script = "\n".join(script)

        dirname = f"test_{difficulty}_{round(protein_vv*100)}"

        for rep in range(1, nreps+1):
            if not os.path.exists(f'{dirname}_{rep}'):
                print(f'Creating {dirname}_{rep}')
                os.mkdir(f'{dirname}_{rep}')
                with open(f'{dirname}_{rep}/pack.inp', 'w') as fh:
                    print(script, file=fh)
            else:
                continue
