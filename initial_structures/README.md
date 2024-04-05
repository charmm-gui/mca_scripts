# Dependencies

 - Python 3.x
 - OpenMM

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

# Description

Each directory corresponds to a simulation project:

 - `mcmX`: Mica + (POPC) membrane, where X is the initial distance between POPC and Mica in nanometers.
 - `pef_co2_X` and `pet_co2_X`: PEF<sub>90</sub> or PET<sub>90</sub> with CO<sub>2</sub>. X is independent replica number.
 - `pef_co2` and `pet_co2`: base case for PEF/PET used to create replicas.

All other directories contain proteins at either 5% (`_5`), 10% (`_10`) or 30% (`_30`) volume fraction:

 - `axolemma`: Previously simulated axolemma
 - `ha`: hydroxyapatite
 - `membrane`: POPC + PSM + Cholesterol in (1:1:1) ratio.
 - `peo`: polymer EO<sub>40</sub>EE<sub>37</sub>

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

-----
`run.sh` expects to be run from within an openmm directory. This is automatically handled by `submit.sh`, but `run.sh` can be used to run a simulation in an interactive session:

```
    # run axolemma_5 simulation
    $ cd axolemma_5/openmm
    $ ../../run.sh
```
