#!/bin/bash

if [ -z "$1" ]; then
    echo "Missing arguments: system"
    exit 1
fi

system=$1
if grep -qE "\.tcl$" <<< $system; then
    system=${system%.tcl}
fi


disp=""
uname=$(uname)
if [ $uname == "Linux" ]; then
    disp="-dispdev none"
fi

vmd $disp -e make_pretty.tcl -args $system
