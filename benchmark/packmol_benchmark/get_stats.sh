#!/bin/bash

is_fail() {
    if [ -z "$1" ]; then exit 2; fi
    tail $1 | grep -q "Solution written to file"
    echo $?
}

get_runtime() {
    if [ -z "$1" ]; then exit 2; fi
    tail $1 | grep "Running time" | grep -Eo "[0-9.]+[0-9]"
}

NREPS=12
for t in easy hard; do
    resultfile=stats.$t.dat
    echo '# vv rep runtime result (0=success, 1=fail)' >$resultfile
    for vv in {10..39}; do
        for rep in `seq $NREPS`; do
            tname=test_${t}_${vv}_${rep}
            outfile=$tname/pack.out

            if [ ! -e $outfile ]; then
                echo no outfile for $tname
                continue
            fi

            runtime=`get_runtime $outfile`

            if [ -z "$runtime" ]; then
                echo no runtime for $tname
                continue
            fi

            result=`is_fail $outfile`

            echo "$vv $rep $runtime $result" >>$resultfile
        done
    done
done
