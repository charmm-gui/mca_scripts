#!/bin/bash

set -e

for dir in axo* ha_* mem* peo*; do
    (
        echo starting $dir
        cd $dir/analysis
        cat contact.dat.* | sort -n | uniq > contact.dat
    )
done
