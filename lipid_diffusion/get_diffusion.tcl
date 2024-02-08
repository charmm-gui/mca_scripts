#!/usr/bin/env vmd -e
source /Users/nathan/src/vmd/vmd_diffusion_coefficient/load.tcl
package require diffusion_coefficient

mol new phosphates.psf
mol addfile phosphates.dcd waitfor -1

lassign [lindex [pbc get] 0] x y z a b c

# middle of the box along Z axis
set zh [expr $z/2]

# frame recording frequency in ns
set dt 0.1

# other options from diffusion_coefficient documentation:
#-along[x|y|z] [1|0]: whether to compute MSD along this dimension
#-removedrift [1|0]: whether to remove drift from MSD calculation (?)
#-from [frame_number]: start of MSD(tau) analysis
#-to [frame_number]: end of "" ""
#-step [frame_number]: steps between "" "" to record

# While the diffusion coefficient CLI's documentation does not explain it,
# the "save to CSV" button is accessible through the diffusion_coefficient
# namespace. This is done with the save_to_file procedure, which assumes
# all relevant args have been set via the CLI or GUI.

# MSD calculation assumes an unwrapped cell
pbc unwrap

## the full graph for the top leaflet, to find linear cutoff
#::diffusion_coefficient::parse_args -selection "z > $zh" -dt $dt \
#    -alongx 1 -alongy 1 -alongz 0 -remove_drift 1 \
#    -from 1 -to 9990 -step 20 \
#    -interval_from 0 -interval_to 9999 -interval_stride 1
#
#set outfile "diffusion_top_full.csv"
#::diffusion_coefficient::save_to_file $outfile
#
#quit

# the recommended settings
::diffusion_coefficient::parse_args -selection "z > $zh" -dt $dt \
    -alongx 1 -alongy 1 -alongz 0 -remove_drift 1 \
    -from 1 -to 5000 -step 1   \
    -interval_from 0 -interval_to 9999 -interval_stride 1

set outfile "diffusion_bot_500.csv"
::diffusion_coefficient::save_to_file $outfile

::diffusion_coefficient::parse_args -selection "z < $zh" -dt $dt \
    -alongx 1 -alongy 1 -alongz 0 -remove_drift 1 \
    -from 1 -to 5000 -step 1   \
    -interval_from 0 -interval_to 9999 -interval_stride 1

set outfile "diffusion_top_500.csv"
::diffusion_coefficient::save_to_file $outfile

# first quarter
::diffusion_coefficient::parse_args -selection "z > $zh" -dt $dt \
    -alongx 1 -alongy 1 -alongz 0 -remove_drift 1 \
    -from 1 -to 2500 -step 1   \
    -interval_from 0 -interval_to 9999 -interval_stride 1

set outfile "diffusion_bot_250.csv"
::diffusion_coefficient::save_to_file $outfile

::diffusion_coefficient::parse_args -selection "z < $zh" -dt $dt \
    -alongx 1 -alongy 1 -alongz 0 -remove_drift 1 \
    -from 1 -to 2500 -step 1   \
    -interval_from 0 -interval_to 9999 -interval_stride 1

set outfile "diffusion_top_250.csv"
::diffusion_coefficient::save_to_file $outfile

quit
