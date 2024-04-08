# Description

The programs in this directory are used to run the following analyses:

 - Z Density profiles
 - Protein-protein and protein-membrane contact probabilities
 - System size over time

They were written to run on a centOS cluster with environment controlled by Lmod. They are included here for demonstration only; you will need to edit them if you plan to use them for your own independent analysis.

In particular, lines that look like this (taken from `join.sh`):
```
    module purge
    module load python/3.8.6 numpy
```
are specific to our cluster+Lmod setup and will likely cause errors in your case. Consult your cluster administrator about environment setup for the dependencies listed below. If you plan to run these analyses interatively on your own machine, you can simply remove all `module` commands.

# Dependencies

 - Python >= 3.8
 - MDAnalysis >= 2.6.1
 - numpy >= 1.24.3
 - matplotlib >= 3.8.2

# Directory setup

The following directory structure is assumed by these programs, where `$ROOT` is the directory containing all simulation subprojects. In this repository, it is equivalent to the `initial_structures` directory.
```
    $ROOT/axolemma_10/analysis/
    $ROOT/axolemma_10/openmm/
    $ROOT/axolemma_10/toppar/
    $ROOT/axolemma_30/analysis/
    $ROOT/axolemma_30/openmm/
    $ROOT/axolemma_30/toppar/
    $ROOT/axolemma_5/analysis/
    $ROOT/axolemma_5/openmm/
    $ROOT/axolemma_5/toppar/
    [...]
    $ROOT/analysis/
    $ROOT/images
```

Unless otherwise stated, the programs in the current directory should be placed inside `$ROOT/analysis/` and run from that location.

# Custom analysis settings

The programs `sys_info.py`, `density_z.py`, and `density_z_new.py` all use a per-project custom setting detection procedure defined in `utils.py`. The procedure works by reading analysis-specific settings from a simulation project's `analysis/settings.yml` file.

For example, create a file at `$ROOT/axolemma_5/analysis/settings.yml` and put the following contents in it:
```
density_z:
  centersel: segid MEMB and not name H*
  components:
    - segid MEMB and not name H*
    - protein and not name H*
    - resname TIP3
    - segid IONS and resname POT
    - segid IONS and resname CLA
```

`density_z['centersel']` is an MDAnalysis atom selection string defining what should be the "center" (Z=0) of the system in the Z density plot. Each item in `density_z['components']` is an atom selection string indicating which components should appear on the plot.

# Calculating system size over time

The program `sys_info.py` calculates box dimensions from DCD files. Example usage:
```
    # setup shell environment
    $ cd $ROOT/analysis
    $ analysis_dir=$PWD/analysis
    $ export PYTHON_PATH="$analysis_dir:$PYTHON_PATH" 

    # calculate box dimensions for axolemma_5 simulation
    $ cd ../axolemma_5/analysis
    $ $analysis_dir/sys_info.py
```

This will create a data file at `$ROOT/axolemma_5/analysis/sys_info.plo` containing the simulation time and box dimensions for each frame of simulation.

A different script (`images/plot_sysinfo.gpl`) is responsible for generating a graph from the data file.
