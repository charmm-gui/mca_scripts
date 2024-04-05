# Dependencies

 - Python 3.x
 - OpenMM
 - (Recommended): CUDA (preferred) or OpenCL

# Before simulating

Input structures are compressed in `openmm_structures.tgz` and force fields in `toppar.tgz`. Their uncompressed sizes are:

 - `openmm_structures.tgz`: 1.7 GB
 - `toppar.tgz`: 710 MB

So ensure you have plenty of space before continuing.

Extract with:

```
    $ tar xf toppar.tgz
    $ tar xf openmm_structures.tgz
```

Note that they extract into the already existing directories.

# Description: top level files

Each directory corresponds to a simulation project:

 - `mcmX`: Mica + (POPC) membrane, where X is the initial distance between POPC and Mica in nanometers.
 - `pef_co2_X` and `pet_co2_X`: PEF<sub>90</sub> or PET<sub>90</sub> with CO<sub>2</sub>. X is independent replica number.
 - `pef_co2` and `pet_co2`: base case for PEF/PET used to create replicas.

All other directories contain proteins at either 5% (`_5`), 10% (`_10`) or 30% (`_30`) volume fraction:

 - `axolemma`: Previously simulated axolemma
 - `ha`: hydroxyapatite
 - `membrane`: POPC + PSM + Cholesterol in (1:1:1) ratio.
 - `peo`: polymer EO<sub>40</sub>EE<sub>37</sub>

Simulation SLURM job submission
-----

`submit.sh` handles submission to a SLURM scheduler and (by default) targets 1000 nanoseconds of simulation. This can be changed with the `MAXSTEP` parameter on line 9.

Example usage:

```
    # submit all projects
    $ ./submit.sh
    # submit a specific project, e.g. axolemma_5
    $ ./submit.sh axolemma_5
    # pre-queue a singleton SLURM job when another has already been submitted:
    $ ./submit.sh --resubmit axolemma_5
```

Read SLURM documentation for more info on the effects of `--dependency` and `--export` flags.

Simulation Bash script
-----

`run.sh` is the script that gets submitted to SLURM by `submit.sh`. It expects to be run from within an openmm directory. This is automatically handled by `submit.sh`, but `run.sh` can be used to run a simulation in an interactive session:

```
    # run axolemma_5 simulation
    $ cd axolemma_5/openmm
    $ ../../run.sh
```

The version of `run.sh` in this repository contains a section labeled `Edit below/above this line`, containing a template showing how to set up the shell environment for running OpenMM on GPU. `module` is an [Lmod](https://lmod.readthedocs.io/en/latest/index.html) command that may not exist on your platform. Contact your cluster administrator for details on setting up your environment and what Lmod modules (if any) should be used for Openmm+GPU usage.

The entire `Edit` section may be deleted if running OpenMM on CPU only.

# Description: Files located in `*/openmm`

OpenMM Python script
-----

`openmm_run.py` reads simulation parameters from a `.inp` file and performs the simulation.

You should not need to run this program manually, as it is handled by `run.sh`. However, you can get usage information if necessary:

```
    $ python openmm_run.py -h
    usage: openmm_run.py [-h] [--platform PLATFORM] -i INPFILE -p TOPFILE -c CRDFILE [-t TOPPAR]
                     [-b SYSINFO] [-ff FFTYPE] [-icrst RSTFILE] [-irst RSTFILE] [-ichk CHKFILE]
                     [-opdb PDBFILE] [-orst RSTFILE] [-ochk CHKFILE] [-odcd DCDFILE] [-rewrap]

    optional arguments:
      -h, --help           show this help message and exit
      --platform PLATFORM  OpenMM platform (default: CUDA or OpenCL)
      -i INPFILE           Input parameter file
      -p TOPFILE           Input topology file
      -c CRDFILE           Input coordinate file
      -t TOPPAR            Input CHARMM-GUI toppar stream file (optional)
      -b SYSINFO           Input CHARMM-GUI sysinfo stream file (optional)
      -ff FFTYPE           Input force field type (default: CHARMM)
      -icrst RSTFILE       Input CHARMM RST file (optional)
      -irst RSTFILE        Input restart file (optional)
      -ichk CHKFILE        Input checkpoint file (optional)
      -opdb PDBFILE        Output PDB file (optional)
      -orst RSTFILE        Output restart file (optional)
      -ochk CHKFILE        Output checkpoint file (optional)
      -odcd DCDFILE        Output trajectory file (optional)
      -rewrap              Re-wrap the coordinates in a molecular basis (optional)
```

__Running equilibration manually__

E.g., to run stage 1 of equilibration manually for a membrane or membrane-like system (e.g. `axolemma_5`):
```
    $ python openmm_run.py -i step6.1_equilibration.inp -t toppar.str -p step5_input.psf -c step5_input.crd -b sysinfo.dat -orst step6.1_equilibration.rst -odcd step6.1_equilibration.dcd > step6.1_equilibration.out
```

The parameters for the stage being run are given by the `-i` flag (`step6.1_equilibration.inp` in example above).

Stages 2-6 are run by repeating the command above with `1` replaced with the stage number and adding the flag `-irst step6.X_equilibration.rst`, where `X` is the previous stager number.

To run equilibration for systems without a membrane (e.g., `solvated_5`), which have only one equilibration stage:

```
    $ python openmm_run.py -i step5_equilibration.inp -t toppar.str -p step4_input.psf -c step4_input.crd -b sysinfo.dat -orst step5_equilibration.rst -odcd step5_equilibration.dcd > step5_equilibration.out
```

__Running production manually: Membranes and membrane-like systems__

After equilibration is production (unrestrained simulation), which can be run like so for membrane systems for the first nanosecond:

```
    $ python openmm_run.py -i step7_production.inp -t toppar.str -p step5_input.psf -c step5_input.crd -irst step6.6_equilibration.rst -orst step7_1.rst -odcd step7_1.dcd > step7_1.out
```

For subsequent steps, see the example below, and replace `${step}` with the current step and `${prev}` with the previous step:
```
    $ python openmm_run.py -i step7_production.inp -t toppar.str -p step5_input.psf -c step5_input.crd -irst step7_${prev}.rst -orst step7_${step}.rst -odcd step7_${step}.dcd > step7_${step}.out
```

__Running production manually: Solution systems__


The first nanosecond after equilibration is run like so:

```
    $python -u openmm_run.py -i step6_production.inp -t toppar.str -p step4_input.psf -c step4_input.crd -irst step5_equilibration.rst -orst step6_1.rst -odcd step6_1.dcd > step6_1.out
```

For subsequent steps, see the example below, and replace `${step}` with the current step and `${prev}` with the previous step:

```
    $python -u openmm_run.py -i step6_production.inp -t toppar.str -p step4_input.psf -c step4;input.crd -irst step6_${prev}.rst -orst step6_${step}.rst -odcd step6_${step}.dcd > step6_${step}.out
```

Simulation input parameters
-----

All of the `.inp` files contain simulation settings passed to `openmm_run.py`. Modifying the values in these files will change how the simulation is run. Each setting is formatted like this:

```
    setting_name    = setting_value       # optional comment
```

The number of spaces around `=` and `#` is arbitrary. Most settings are (with their comments) pretty self-explanatory. Some examples are shown below.

From `axolemma_5/openmm/step6.1_equilibration.inp`:
```
    nstep    = 125000    # number of steps to run
    dt       = 0.001     # time-step (ps)
```
This controls the length of the simulation. 0.001 picoseconds times 125,000 steps = 125 picoseconds of simulation.

```
    nstout   = 1000     # Writing output frequency (steps)
    nstdcd   = 5000     # Writing coordinates trajectory frequency (steps)
```
The "output frequency" is the number of time-steps between OpenMM progress messages. In the commands shown above, this output is redirected (`>`) to a `.out` file. The "coordinate trajectory frequency" is the number of time-steps between writing coordinates to the trajectory (`.dcd`) file.
