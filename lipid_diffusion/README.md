# Dependencies

 - VMD >= 1.8 (tested w/ 1.9)
 - [Diffusion Coefficient Tool](https://github.com/giorginolab/vmd_diffusion_coefficient)
 - Gnuplot >= 5.4
 - CHARMM >= c47b1

The following also assumes you have at least 1 microsecond of simulation trajectories.

# Setup

The compute requirements are very high unless we first reduce the trajectory to contain only the phosphate atom from POPC head groups. Many tools can do this kind of trajectory reduction, but for example see `co2_diffusion/convert.py` and `co2_diffusion/convert_all.sh`, which demonstrate reduction of a trajectory to include only CO<sub>2</sub> carbon atoms.

Loading the correct atom topology in VMD is not strictly required, but avoids several warning/error messages. A PDB file such as the one produced by convert.py will probably do, but the example in this directory uses a PSF file produced by CHARMM.

Assuming you built a Mica + POPC system with Multicomponent Assembler, downloaded and extracted `charmm-gui.tgz`, then you can produce this PSF file by placing the CHARMM script `ponly.inp` in the root of your extracted directory. It can then be run like this:
```
    $ charmm -i ponly.inp
```

This will write a `phosphate.psf` file in the same directory, which contains the structure for only the POPC phosphate atoms.

After obtaining `phosphate.psf`, `phosphate.dcd`, and (from this repository) `get_diffusion.tcl`, it is recommended to create an `analysis` directory inside your Mica + POPC project's root directory. E.g., if your simulation project's root is `mcm1` within which exists `toppar.str`, `toppar/`, and `openmm`, then:
```
    $ cd mcm1
    $ mkdir analysis
    $ mv phosphate.psf phosphate.dcd get_diffusion.tcl analysis
    $ cd analysis
```

# Usage

To load the diffusion coefficient VMD plugin, edit line 2 of `get_diffusion.tcl`, which looks like this:
```
    source /Users/nathan/src/vmd/vmd_diffusion_coefficient/load.tcl
```
and change the path so that it points to your VMD plugin's `load.tcl` file location.

Assuming you have `get_diffusion.tcl`, `phosphate.psf`, and `phosphate.dcd` in the same directory, and the VMD CLI executable in your shell environment, the diffusion analysis is run with this command:
```
    $ vmd -e get_diffusion.tcl
```

This produces the following files:
```
    diffusion_bot_250.csv
    diffusion_bot_500.csv
    diffusion_top_250.csv
    diffusion_top_500.csv
```

Where `bot` means the leaflet closest to mica (bottom leaflet), `top` means the opposite leaflet (top leaflet), and where the number indicates the maximum lag time (tau) considered (250 or 500).

To plot the result, run `plot_msd.gpl`:
```
    $ gnuplot plot_msd.gpl
```

Which saves its plot in enhanced postscript format in a file named `msd.eps`.
