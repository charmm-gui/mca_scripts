#!/bin/bash

# ps, but quiet; just returns the exit status
qps() {
    ps $@ >/dev/null 2>/dev/null
}

get_runtime() {
    if [ -z "$1" ]; then exit 2; fi
    if [ ! -e "$1" ]; then exit 3; fi
    tail $1 | grep "Running time" | grep -Eo "[0-9.]+[0-9]"
}

check_for_runner() {
    if [ -e pack.pid ]; then
        if qps $(cat pack.pid); then
            echo "Tests already running"
            exit 1
        fi
        pidfiles=*/*.pid
        if [ "$pidfiles" != '*/*.pid' ]; then
            echo "Some tests are running, although $0 has been terminated"
            echo "They can be killed with this command:"
            echo "kill */*.pid"
            exit 1
        fi
    fi

    # ensure any early terminated jobs can be rerun
    for f in test_{easy,hard}_*; do
        pushd $f >/dev/null

        if [ ! -e pack.out ]; then
            popd >/dev/null
            continue
        fi

        runtime=`get_runtime pack.out`

        if [ -z "$runtime" ]; then
            echo "Cleaning $f"
            for outfile in pack.out pack.full.tgz pack.tail; do
                if [ -e "$outfile" ]; then
                    rm "$outfile"
                fi
            done
        fi
        popd >/dev/null
    done
}

# run tests
nreps=12
N_CPU=4
if [ -z "$@" ]; then
    check_for_runner


    # call self w/ up to N_CPU parallel processes
    for t in easy hard; do
        # make get_stats.sh signal subjobs
        (
            # monitors tests, kills this job early if further testing is unneeded
            ./get_stats.sh $t &
            stats_pid=$!
            echo $$ > pack.pid
            for vv in {10..40}; do
                for rep in `seq $nreps`; do
                    echo test_${t}_${vv}_${rep}
                done
            done
            rm pack.pid 

            kill $stats_pid
            ./get_stats.sh
        ) &
        wait
    done | xargs -n 1 -P $N_CPU $0
else
    if [ ! -e $1 ]; then
        echo no such project: $1
        exit
    fi
    cd $1

    didrun=0

    if [ ! -e pack.out ] || ! get_runtime pack.out >/dev/null; then
        didrun=1
        echo running $1
        echo $$ > pack.pid

        packmol < pack.inp > pack.out &

        # ensure packmol can be stopped too
        echo $! > pack.pid
        wait

        rm pack.pid
    else
        echo skipping $1
        sleep 1
    fi

    if [ ! -e pack.full.tgz ] || [ $didrun -eq 1 ]; then
        echo compressing $1
        # make this early so other procs know we're done
        tail pack.out > pack.tail

        # make a compressed backup of the output
        tar czf pack.full.tgz pack.out

        # replace output with just the last part
        mv pack.tail pack.out
    fi
fi
