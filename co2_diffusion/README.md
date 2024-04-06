# Dependencies

 - Python >= 3.8
 - MDAnalysis >= 2.6.1
 - gnuplot >= 5.4
 - scipy >= 1.11.3
 - numpy >= 1.24.3
 - mdtraj >= 1.9.9
 - matplotlib >= 3.8.2
 - pint >= 0.22

The commands below assume you have 2 microseconds of simulation for 3 replicas each of PET and PEF systems.

# Usage

Directory access
-----

Create a shortcut to the directories containing your full trajectories. E.g.:
```
    $ for sys in pe{t,f}_co2_{1..3}; do
    >     ln -s $PWD/../initial_simulations/$sys/openmm $sys
    > done
```
This will create a symlink to the openmm directory of each replica in the current directory, named according to the replica.

Trajectory reduction
-----

For this analysis, we only need the carbon atom of CO2 from all saved frames. This command creates a reduced trajectory and places it in this directory, named according to the replica:

```
    ./convert_all.sh
```

If you have a different number of trajectory files than 2000, edit line 8 of `convert_all.sh`, which looks like this:

```
    mdconvert -o $sys.dcd -a indices.txt -t $sys/step5_input.pdb $sys/step7_{1..2000}.dcd
```

Diffusion analysis
-----

The program `diffusion_z.py` uses mdtraj to calculate a Z-dependent mean square displacement (MSD). Running it with the `-h` flag describes each of its options:

```
    $ ./diffusion_z.py -h
    usage: diffusion_z.py [-h] [-f] [-maxt TAU] -from TAU -to TAU [-dt STEP_SIZE]
                          [-binsize BINSIZE]
                          project

    In all arguments, units are whatever is used by the trajectory file

    positional arguments:
      project           simulation DCD name, not including `.dcd`

    options:
      -h, --help        show this help message and exit
      -f, --force       recalculate MSD if outfile already exists
      -maxt TAU         maximum lag time to calculate (default: 5000)
      -from TAU         minimum lag time for line fitting
      -to TAU           maximum lag time for line fitting
      -dt STEP_SIZE     time between recorded frames in trajectory (default: 0.1)
      -binsize BINSIZE  bin size to use for Z-dependent MSD calculation (default:
                        0.1)
```

`diffusion_z.py` creates four files for each project. If used on `pet_co2_1.dcd`, it will create:

 - `pet_co2_1_D.dat`: Diffusion calculated from standard deviation of displacement
 - `pet_co2_1_MSD.dat`: Mean square displacements
 - `pet_co2_1_fit_D.dat`: Diffusion calculated by fitting a line to MSD
 - `pet_co2_1_samples.dat`: Sample size of each bin

It can be run for individual trajectories, e.g., to help decide what options look interesting. But once you have identified settings to apply to all systems, the quickest way to run the analysis is via `calc_all.sh`. Edit the top of this file to contain your desired settings:
```
    maxt=21
    _from=1
    _to=10
    dt=0.1
    binsize=0.1
```

Then perform the analysis on all trajectories:
```
    ./calc_all
```
