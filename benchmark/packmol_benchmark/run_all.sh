#!/bin/bash

set -e

NCPUS=4
NREPS=12
if [ -z "$@" ]; then
    # call self w/ up to 8 parallel processes
    #for t in easy hard; do
    #for t in easy; do
    for t in hard; do
        for vv in {10..40}; do
            for rep in `seq $NREPS`; do
                echo test_${t}_${vv}_${rep}
            done
        done
    done | xargs -n 1 -P $NCPUS $0
else
    if [ ! -e $1 ]; then exit; fi
    if [ -e $1/pack.out ]; then exit; fi
    echo running $1
    cd $1
    packmol < pack.inp > pack.out
fi
