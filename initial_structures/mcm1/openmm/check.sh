#!/bin/bash

i=1
while [ 1 ]; do
    dcd=step7_${i}.dcd 
    if [ ! -e $dcd ]; then
        echo missing $dcd
        exit
    fi
    ((++i))
done
