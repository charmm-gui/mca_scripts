#!/bin/bash
# submit all jobs in this directory, named by directory
# N.B. this script is modified for scaled replicas

########################
# Edit below this line #
########################

MAXSTEP=1000

########################
# Edit above this line #
########################

runner=$PWD/run.sh
rootdir=$PWD

jobs="*"
if [ -n "$1" ]; then
    jobs=$@
fi

resubmit=0
rsflag=""
if grep -qE "(^| )\--resubmit\>" <<< $jobs; then
    resubmit=1
    rsflag="--resubmit"
fi

for job in $jobs ; do
    set +e
    if [ ! -d "$job" ]; then continue; fi
    if [ "$job" == "analysis" ]; then continue; fi

    if [[ $resubmit -eq 0 ]]; then
        if (squeue -h -u nak317 --format="%j" | grep -q "^${job}$"); then
            echo "skipping already queued job: $job"
            continue
        fi
    fi

    set -e

    set +e
    cd $job/openmm
    set -e

    if [ -e .steps.done ]; then
        next_step=$(cat .steps.done | tail -n 1)
    else
        next_step=0
    fi

    if [[ "$next_step" -le "$MAXSTEP" ]]; then
        set +e
        OPTS="-J $job --dependency=singleton --export=ALL,cntmax=$MAXSTEP $runner"
        echo sbatch $OPTS
        sbatch $OPTS
        set -e
    else
        echo "skipping completed job: $job"
    fi

    cd $rootdir
done
