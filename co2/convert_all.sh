#!/bin/bash

set -e

for sys in pe{t,f}_co2_{1..3}; do
    echo $sys
    #if [ -e $sys.dcd ]; then continue; fi
    ./convert.py $sys $sys.pdb
    #mdconvert -o $sys.dcd -a indices.txt -t $sys/step5_input.pdb $sys/step7_{1..2000}.dcd
done

echo done
