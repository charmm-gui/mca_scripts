#!/bin/bash

set -e

source settings.sh

if [ -e test_easy_${first_vv}_1 ]; then
    read -p 'Remove existing tests? [y/N] ' do_rm
    if [[ "$do_rm" == y || "$do_rm" == Y ]]; then
        rm -rv test_{easy,hard}_*
    fi
fi

for t in easy hard; do
    orig=test_$t
    for vv in `seq $first_vv $last_vv`; do
        for rep in `seq $nreps`; do
            nextdir=${orig}_${vv}_$rep
            if [ -e "$nextdir" ]; then continue; fi
            mkdir $nextdir
            ( cd $nextdir ; ln -s ../$orig/* . )
        done
    done
done
