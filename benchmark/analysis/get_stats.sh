#!/bin/bash

avg=$PWD/avg.py

for dir in ../*_benchmark/; do
    pushd $dir
    (./get_stats.sh ; $avg ) &
    popd
done

wait
echo Done
