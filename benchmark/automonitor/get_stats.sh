#!/bin/bash

is_fail() {
    if [ -z "$1" ]; then exit 2; fi
    tail $1 | grep -q "Solution written to file"
    echo $?
}

get_runtime() {
    if [ -z "$1" ]; then exit 2; fi
    tail $1 | grep "Running time" | grep -Eo "[0-9.]+[0-9]"
}

get_stats() {
    nreps=12
    for t in easy hard; do
        resultfile=stats.$t.dat
        echo '# vv rep runtime result (0=success, 1=fail)' >$resultfile
        for vv in {10..39}; do
            nfail=0
            for rep in `seq $nreps`; do
                tname=test_${t}_${vv}_${rep}
                outfile=$tname/pack.out
                tgzfile=$tname/pack.full.tgz
                tailfile=$tname/pack.tail
                pidfile=$tname/pack.pid

                if [ -e "$pidfile" ]; then
                    return 0
                fi

                if [ ! -e $outfile ]; then
                    # job has not run
                    echo job not run: $tname
                    return 0
                fi

                if [[ ! -e $tgzfile || -e $tailfile ]]; then
                    # job is not complete
                    echo job not complete: $tname
                    return 0
                fi

                runtime=`get_runtime $outfile`

                if [ -z "$runtime" ]; then
                    # something went wrong
                    echo no runtime for $tname
                    return 1
                fi

                result=`is_fail $outfile`

                let "nfail = nfail + $result"

                echo "$vv $rep $runtime $result" >>$resultfile
            done

            # this v/v has failed; stop here
            if [[ "$nfail" -ge $nreps ]]; then
                echo "Stopping tests"
                find . -name '*.pid' -execdir bash -c 'kill `cat "{}"`'  \; -delete
                return 1
            fi

            # all tests have somehow succeeded
            if [ "$vv" -eq 39 ]; then
                echo 'How did we get here?'
                return 1
            fi
        done
    done

    pid1=*.pid
    if [ -e "$pid1" ]; then
        # this line reached if tests were terminated early by user
        echo Stopping monitor
        exit
    fi
}

if [ -n "$1" ]; then
    # run continuously
    while get_stats; do sleep 60; done
else
    get_stats
fi
