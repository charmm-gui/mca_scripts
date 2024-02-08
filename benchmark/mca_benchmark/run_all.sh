#!/bin/bash

set -e

base=step2_molpacking
infile=$base.inp
outfile=$base.out
errfile=$base.err

N_CPUS=2

is_abnormal() {
    if [ -z "$1" ]; then exit 1; fi
    tail -n 6 $@ | grep ABNORMAL | wc -l
}

is_normal() {
    if [ -z "$1" ]; then exit 1; fi
    tail -n 100 $@ | grep "CHARMM> *energy" | wc -l
}

if [ -z "$1" ]; then
    (
        #for t in easy hard; do
        for t in easy; do
            #for vv in {10..41}; do
            for vv in 42; do
                #if [[ $t == easy && $vv -lt 30 ]]; then continue; fi
                for rep in `seq 12`; do
                    #if [[ $vv == 24 && $rep -lt 6 ]]; then continue; fi
                    echo $t $vv $rep
                done
            done
        done
    ) | xargs -n 3 -P $N_CPUS $0
else
    t=$1
    vv=$2
    rep=$3

    #if [ "$vv" == 10 ]; then
    #    :
    #else
    #    vprev=$(($vv-1))
    #    prev_test=test_${t}_${vprev}_*/$outfile
    #    n_abnml=$(is_abnormal $prev_test)
    #    n_nml=$(is_normal $prev_test)
    #    if [ "$n_abnml" -eq 3 ]; then exit 1; fi
    #    if [ "$n_nml" -eq 0 ]; then exit 1; fi
    #fi

    dir=test_${t}_${vv}_${rep}
    echo running $dir

    cd $dir
    charmm testtype=$t proteinvv=.$vv -i $infile -o $outfile 2>$errfile
fi
