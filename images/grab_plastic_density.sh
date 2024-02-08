#!/bin/bash

set -e

starts=( 0    0  6666 13333     0 )
ends=( 100 6666 13333 20000 20000 )

orig_dir=$PWD
new_dir=$PWD/density

if [ -e $new_dir ]; then
    rm $new_dir/*
else
    mkdir $new_dir
fi

cd ..
for project in pe{t,f}_co2_{1..3}; do
    cd "$project/analysis"

    i=0
    while [ $i -lt ${#ends[*]} ]; do
        infile="density_z.sym.${starts[$i]}.${ends[$i]}.plo"
        out_suffix="density_z.${starts[$i]}.${ends[$i]}.plo"
        ln -v "$infile" "$new_dir/${project}_${out_suffix}"
        ((++i))
    done

    cd ../..
done

if [[ "$@" == "and plot" ]]; then
    cd $orig_dir
    pwd
    ./merge_density.py
    ./plot_density_co2.gpl
fi
