#!/bin/bash

set -e

echo loading modules
module purge
module load python/3.8.6 numpy

output=contact.plo
inputs=`echo $output.{0..9}`

cd ..

for job in *; do
    if [ ! -d "$job/analysis" ]; then continue; fi
    if [ ! -e "$job/analysis/$output.1" ]; then continue; fi

    cd $job/analysis

    echo doing $job
    catplot $inputs -o $output

    # uncomment this when you are sure the rest of the script works...
    #rm $output.*

    cd ../..
done

echo done
