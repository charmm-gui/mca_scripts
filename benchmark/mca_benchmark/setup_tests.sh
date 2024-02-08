#!/bin/bash

set -e

if [ -e test_easy_10_1 ]; then
    read -p 'Remove existing tests? [y/N] ' do_rm
    if [[ "$do_rm" == y || "$do_rm" == Y ]]; then
        rm -rv test_{easy,hard}_*
    fi
fi

nreps=12
#for t in easy hard; do
for t in easy; do
    orig=test_$t
    for vv in {10..42}; do
        for rep in `seq $nreps`; do
            nextdir=${orig}_${vv}_$rep
            if [ -e "$nextdir" ]; then continue; fi
            mkdir $nextdir
            ( cd $nextdir ; ln -s ../$orig/* . )
        done
    done
done
