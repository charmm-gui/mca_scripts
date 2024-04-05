#!/bin/bash

set -e

source settings.sh

base=step2_molpacking
infile=$base.inp
outfile=$base.out
errfile=$base.err

if [ -z "$1" ]; then
    (
        for t in easy hard; do
            for vv in `seq $first_vv $last_vv`; do
                for rep in `seq $nreps`; do
                    echo $t $vv $rep
                done
            done
        done
    ) | xargs -n 3 -P $N_CPUS $0
else
    t=$1
    vv=$2
    rep=$3

    dir=test_${t}_${vv}_${rep}
    echo running $dir

    cd $dir
    charmm testtype=$t proteinvv=.$vv -i $infile -o $outfile 2>$errfile
fi
