#!/bin/bash

set -e

is_abnormal() {
    if [ -z "$1" ]; then exit 1; fi
    tail -n 6 $@ | grep ABNORMAL | wc -l
}

is_normal() {
    if [ -z "$1" ]; then exit 1; fi
    tail -n 100 $@ | grep "CHARMM> *energy" | wc -l
}

outfile=step2_molpacking.out

ntfail=0
for t in easy hard; do
    for vprev in {11..50}; do
        tname="${t}_$vprev"
        echo checking $tname ...

        prev_test=test_${t}_${vprev}_*/$outfile
        n_abnml=$(is_abnormal $prev_test)
        n_nml=$(is_normal $prev_test)

        echo "    normal terminations: $n_nml"
        echo "    abnormal terminations: $n_abnml"

        set +e
        let "n_fail = (3 - n_nml) + n_abnml"
        echo "    failures: $n_fail"

        if [ "$n_fail" -ge 3 ]; then
            echo $tname failed
            tfails[$ntfail]="${t}_$(($vprev-1))"
            ((++ntfail))
            break
        fi
        set +e

        echo $tname is normal
        echo
    done
done

echo
echo "Highest density packing systems:"
echo ${tfails[*]}
