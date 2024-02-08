#!/usr/bin/env python
import os
import sys
import mdtraj as md
import numpy as np


def main(top):
    pdb = md.load('step5_input.pdb')
    C_idxs = pdb.top.select('resname CO2 and name C')
    return pdb, C_idxs


if __name__ == '__main__':
    orig_dir = os.getcwd()
    openmm_dir = sys.argv[1]
    output_pdb = sys.argv[2]

    os.chdir(openmm_dir)
    pdb, idx = main('step5_input.pdb')
    os.chdir(orig_dir)

    np.savetxt('indices.txt', idx, fmt='%d')
    pdb.atom_slice(idx).save_pdb(output_pdb)
