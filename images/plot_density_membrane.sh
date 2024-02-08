#!/bin/bash

set -e

if [ -e density_z ]; then
    rm -r density_z
fi

mkdir density_z
image_dir=$PWD
dz="$image_dir/density_z"

cd ..

for sys in axolemma ha membrane peo; do
    ln -vs ../../${sys}_5/analysis/plot_density.gpl "$dz/plot_${sys}.gpl"
    for rep in 5 10 30; do
        cd ${sys}_$rep/analysis
        ./plot_density.gpl
        cp -v *density*.eps "$dz"
        cd ../..
    done
done
