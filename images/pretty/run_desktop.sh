#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: missing system"
    exit 1
fi

HOST=desktop
IMDIR=charmm/mca_new/images

# push
rsync -avP .. $HOST:$IMDIR

ssh -Y $HOST "cd $IMDIR/pretty; ./run.sh $@"

# pull
rm out/*.ppm
rsync -avP $HOST:$IMDIR/pretty/out/ out

open */*.ppm
