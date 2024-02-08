#!/bin/bash

maxt=21
_from=1
_to=10
dt=0.1
binsize=0.1

set -e

PROG=./diffusion_z.py
# WARNING: --force flag overwrites data files!
FORCE="--force"
#FORCE=""
ARGS="$FORCE -maxt $maxt -from $_from -to $_to -dt $dt -binsize $binsize"

N_CPU=8
echo pe{t,f}_co2_{1..3} | xargs -P $N_CPU -n 1 $PROG $ARGS
