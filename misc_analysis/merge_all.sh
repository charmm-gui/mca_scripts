#!/bin/bash

set -e

merge_contact=$PWD/merge_contact.py
for project in axo* ha* mem* peo*; do
    #if [ "$project" == membrane_10 ]; then continue; fi
    echo starting $project
    cd $project/analysis
    #$merge
    head -n 1 cluster.dat.0 > cluster.dat
    i=0
    while [ -f cluster.dat.$i ]; do
        grep -v "^#" cluster.dat.$i >> cluster.dat
        ((++i))
    done
    cd ../..
done

#wait
echo all done
