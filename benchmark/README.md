# Dependencies

 - Python >= 3.8
 - MDAnalysis >= 2.6.1
 - CHARMM >= c47b1
 - PACKMOL >= 20.14.2
 - gnuplot >= 5.4
 - scipy >= 1.11.3
 - numpy >= 1.24.3

# MCA benchmark

CHARMM writes verbose output, so ensure you have several GB of free space available before running any of the commands below. It is also recommended to have at least 8 GB of RAM, as each MCA process uses around 3.5 GB RAM; otherwise, you can lower the `N_CPUS` setting described below.

Benchmark parameters
-----

To run a new benchmark, first open `mca_benchmark/settings.sh` in a text editor:
```
#
# edit this file to adjust benchmark parameters
#

# number of simultaneous tests to run. N.B. CHARMM is very memory intensive,
# so this should not necessarily be the same as the number of CPUs on your
# machine.
N_CPUS=2

# number of replicas to run for each volume fraction (% v/v)
nreps=12

# lowest % v/v to run
first_vv=10

# highest % v/v to run
last_vv=42
```

Set the desired values in this file before continuing.

Create test directories
-----

`test_easy` and `test_hard` are the starting points for benchmarking with MCA. The benchmark procedure creates a new directory for each combination of volume fraction and replica. With default settings, that will result in 396 new directories. Create them like so:
```
    ./setup_tests.sh
```

Run benchmark
-------------

Running a new benchmark requires only a single command:
```
    ./run_all.sh
```

# PACKMOL benchmark

Benchmark parameters
-----

Two files need to be edited to ensure the benchmark parameters are consistent.

First, open `packmol_benchmark/settings.sh` in a text editor:
```
#
# edit this file to adjust benchmark parameters
#

# number of simultaneous tests to run. Unless you are creating a very large
# system, it is probably safe to set this to the actual number of CPUs on
# your machine.
N_CPUS=4

# number of replicas to run for each volume fraction (% v/v)
NREPS=12

# lowest % v/v to run
first_vv=10

# highest % v/v to run
last_vv=39
```
Set the desired values in this file before continuing.

Next, edit the top of `setup_tests.py`:
```
nreps = 12
first_vv = 10
last_vv = 39
```
Ensure those values are the same as what you used in `settings.sh`.

Create test directories
-----

A separate directory is created for each replica and volume fraction with this command:
```
    $ ./setup_tests.py
```

Run benchmark
-------------

This command will run all benchmark tests:
```
    $ ./run_all.sh
```

# Analysis programs

Calculate asphericity
-----

`asphericity` uses the MDAnalysis [asphericity](https://docs.mdanalysis.org/2.6.1/documentation_pages/core/groups.html#MDAnalysis.core.groups.AtomGroup.asphericity) function to create a table showing the asphericity and number of atoms of each PDB file, which is assumed to contain one major structure.

When run with the `-h` flag it shows the following usage info:
```
    usage: asphericity [-h] [-n] [filename ...]

    positional arguments:
      filename    structure file(s) to analyze

    options:
      -h, --help  show this help message and exit
      -n          sort by # atoms (default: sort by asphericity)
```

Here's how to use it was used in this study:
```
    $ cd packmol_benchmark
    $ ../analysis/asphericity
      molecule   asph   # atoms
    ---------------------------
          trna  0.34760    1622
          pdhb  0.12515    2540
          pdha  0.08522    2856
           pgk  0.20190    3190
           nox  0.09613    3609
           if2  0.51490    3847
           fba  0.39249    4400
           pta  0.37052    4998
          eftu  0.10316    5427
          acka  0.31377    6248
           pgi  0.02704    6970
           eno  0.07187    7032
          gapa  0.00372   10256
          pdhx  0.19714   13709
          grol  0.06896   63273
```

Average replica performance
-----

Takes statistics stored in `stats.easy.dat` and `stats.hard.dat` and aggregates them into `stats.easy.avg.dat` and `stats.hard.avg.dat`. The `avg.dat` files contain mean runtime, standard error of the mean of runtime, and the fail rate for each volume aggregated by volume fraction (% v/v).

__Setup__

The number of replicas expected is hard-coded in line 9:
```
    nrep = 12
```

You must change this number of you want to analyze a different number of replicas.

__Usage__

You should not need to run this command manually, as it is automatically run by `get_statas.sh`.

Nevertheless, to do it yourself, after running the PACKMOL benchmark:

```
    $ cd packmol_benchmark
    $ ../analysis/avg.py
```

or after the MCA benchmark:
```
    $ cd mca_benchmark
    $ ../analysis/avg.py
```

Individual replica performance
-----
CHARMM and PACKMOL format their outputs differently, so each benchmark directory defines its own procedure to calculate performance: `mca_benchmark/get_stats.sh` and `packmol_benchmark/get_stats.sh`.

However, both benchmark analysis and their aggregation can be run at once:
```
    $ cd analysis
    $ ./get_stats.sh
```

Plotting benchmark results
-----
`plot.gpl` plots aggregated runtime and failure rates in postscript format.

Usage:
```
    $ cd analysis
    $ ./plot.gpl
```
