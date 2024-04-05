# Dependencies:

 * CHARMM c47b1 or later
 * Python 2.11+ or 3.x
 * OpenMM

# Example usage

Step 0: Extract input structures
-----

These are the files we will be processing for upload to CHARMM-GUI.

```
    $ tar xf input_structures.tgz
```

This adds the following new files to the current directory:

```
    step5_charmm2omm.psf
    step7_500.rst
    toppar.str
    toppar/*
```

The `toppar.str` and `toppar/*` files are needed for running CHARMM.

Step 1: Convert PSF + RST to CHARMM CRD
-----

This approach uses `ommrst2crd.py` (convert OpenMM RST to CRD).

If your Python and OpenMM dependencies were installed correctly, you should be able to get program usage:

```
    $ python ommrst2crd.py -h
    usage: ommrst2crd.py [-h] -i INPFILE -p PSFFILE [-o OUTFILE]

    optional arguments:
      -h, --help  show this help message and exit
      -i INPFILE  Input OpenMM RST file
      -p PSFFILE  Input PSF file
      -o OUTFILE  Output CHARMM CRD file
```

I.e., we need an RST file, a PSF file, and an output filename. A later script we use (`convert.inp`) assumes the CRD file is named `step7_500.crd`, so use this:
```
    $ python ommrst2crd.py -i step7_500.rst -p step5_charmm2omm.psf -o step7_500.crd
```

This should result in a new file named `step7_500.crd`.

Step 1 (Alternative) Convert PSF + DCD to CHARMM CRD
-----

If you instead have a PSF and DCD file, you can use `psfdcd2pdbcrd`. This program requires CHARMM.

Detailed usage is provided in the comment from lines 7 through 39. For example, suppose we had a dcd file named `step7_1.dcd` and wanted its first frame:

```
    $ ./psfdcd2pdbcrd psf=step5_charmm2omm.psf dcd=step7_1.dcd out=step7_500 frame=1
```

Step 2: Strip water and ions, save output as axolemma.psf / axolemma.crd
-----

This step requires CHARMM and `toppar.str` + `toppar/*` in the current directory.

```
    $ charmm -i convert.inp
```

You should have two new files in your directory: `axolemma.psf` and `axolemma.crd`. If not, check the output or errors. If errors occur before reading PSF/CRD files, then delete or comment out lines 5-6 (`prnlev 0` and `wrnlev 0`), which reduce the massive amount of output that results from reading `toppar.str`.
