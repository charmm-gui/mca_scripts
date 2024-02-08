#!/bin/bash

set -e

psf_in=step2.3_replacement.psf
dcd_in=openmm/step5_500.dcd

for dir in pe{t,f}_vac_{1..3}; do
    cd $dir
    psfdcd2pdbcrd psf=$psf_in dcd=$dcd_in out=$dir frame=10
    rm $dir.pdb
    cp -v $psf_in $COMPS/$dir.psf
    cp -v $dir.crd $COMPS
    cd ..
done
