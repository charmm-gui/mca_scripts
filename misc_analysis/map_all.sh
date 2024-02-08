#!/bin/bash

make_map=$PWD/make_map3.py
cd ..

for project in axo* ha_* mem* peo*; do
    (
        echo starting $project
        cd $project/analysis
        $make_map
    )
done
