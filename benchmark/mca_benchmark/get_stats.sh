#!/bin/bash

is_fail() {
    if [ -z "$1" ]; then exit 2; fi
    tail -n 100 $1 | grep -q "ABNORMAL TERMINATION"
    # invert return value
    echo $(($?^1))
}

get_runtime() {
    if [ -z "$1" ]; then exit 2; fi
    n=$(tail $1 | grep "ELAPSED TIME:" | grep -Eo "[0-9.]+[0-9]")
    m=$(tail $1 | grep "ELAPSED TIME:" | grep -Eo "SECOND|MINUTE|HOUR")
    if [ -z "$n" ]; then return; fi
    if [ "$m" == SECOND ]; then
        mul=1
    elif [ "$m" == MINUTE ]; then
        mul=60
    elif [ "$m" == HOUR ]; then
        mul=3600
    fi
    python -c "print(f'{$n * $mul:.5e}')"
}

nreps=12
for t in easy hard; do
    resultfile=stats.$t.dat
    echo '# vv rep runtime result (0=success, 1=fail)' >$resultfile
    for vv in {10..42}; do
        for rep in `seq $nreps`; do
            tname=test_${t}_${vv}_${rep}
            outfile=$tname/step2_molpacking.out
            echo -en "\r$tname     "

            if [ ! -e $outfile ]; then
                echo
                echo no outfile for $tname
                continue
            fi

            runtime=`get_runtime $outfile`

            if [ -z "$runtime" ]; then
                echo
                echo no runtime for $tname
                continue
            fi

            result=`is_fail $outfile`

            echo "$vv $rep $runtime $result" >>$resultfile
        done
    done
done
