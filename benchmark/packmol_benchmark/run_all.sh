#!/bin/bash

set -e

source settings.sh

if [ -z "$@" ]; then
    # call self w/ up to $NCPUS parallel processes
    for t in easy hard; do
        for vv in `seq $first_vv $last_vv`; do
            for rep in `seq $NREPS`; do
                echo test_${t}_${vv}_${rep}
            done
        done
    done | xargs -n 1 -P $NCPUS $0
else
    # skip nonexistent test
    if [ ! -e $1 ]; then exit; fi
    # skip already finished test
    if [ -e $1/pack.out ]; then exit; fi

    echo running $1
    cd $1
    packmol < pack.inp > pack.out
fi
