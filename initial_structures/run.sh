#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SABTCH --ntasks-per-node=1
#SBATCH --export=ALL
#SBATCH -t 24:00:00

cntmax=${cntmax-100}

########################
# Edit below this line #
########################

# Set up environment so OpenMM can run on GPU.

module load cuda/11.6.0

python=/path/to/python

export OPENMM_PLUGIN_DIR=/path/to/openmm/plugin/dir
export PYTHONPATH=/path/to/python/site-packages
export LD_LIBRARY_PATH=/path/to/cuda/lib:$LD_LIBRARY_PATH
export OPENMM_CUDA_COMPILER=/path/to/nvcc

########################
# Edit above this line #
########################

# infer system type (membrane vs. solution)
if [ -e step6_production.inp ]; then
    systype=solution
    init=step4_input
    equi_prefix=step5_equilibration
    prod_prefix=step6_production
    prod_step=step6
else
    systype=membrane
    init=step5_input
    equi_prefix=step6.%d_equilibration
    prod_prefix=step7_production
    prod_step=step7
fi
echo systype: $systype

# get initial step number
if [ ! -e .steps.done ]; then
    touch .steps.done
fi

cnt=$(cat .steps.done | tail -n 1)
if [ -z "$cnt" ]; then
    cnt=1
elif [ "$cnt" -ge 1 ]; then
    # .steps.done shows which steps finished; run the next step
    ((cnt++))
fi

if [ $systype == solution ]; then
    # Solution Equilibration
    input_param="-t toppar.str -p ${init}.psf -c ${init}.crd -b sysinfo.dat"
    if [ $cnt == 1 ]; then
        echo running equilibration
        echo "$python -u openmm_run.py -i ${equi_prefix}.inp ${input_param} -orst ${equi_prefix}.rst -odcd ${equi_prefix}.dcd > ${equi_prefix}.out"
        set -e
        $python -u openmm_run.py -i ${equi_prefix}.inp ${input_param} -orst ${equi_prefix}.rst -odcd ${equi_prefix}.dcd > ${equi_prefix}.out
        set +e
        cnt=1
    fi
else
    # Membrane/Periodic Equilibration
    if [ $cnt == 1 ]; then
        while [ ${cnt} -le 6 ]; do
            let "pcnt = $cnt - 1"
            istep=`printf ${equi_prefix} ${cnt}`
            pstep=`printf ${equi_prefix} ${pcnt}`
            input_param="-t toppar.str -p ${init}.psf -c ${init}.crd"
            if [ ${cnt} == 1 ]; then
                input_param=`echo "${input_param} -b sysinfo.dat"`
            else
                input_param=`echo "${input_param} -irst ${pstep}.rst"`
            fi
            echo running equilibration step $pcnt
            echo "$python -u openmm_run.py -i ${istep}.inp ${input_param} -orst ${istep}.rst -odcd ${istep}.dcd > ${istep}.out"
            set -e
            $python -u openmm_run.py -i ${istep}.inp ${input_param} -orst ${istep}.rst -odcd ${istep}.dcd > ${istep}.out
            set +e
            ((cnt++))
        done
        cnt=1
    fi
fi

# run production
while [ $cnt -le $cntmax ]; do
    let "pcnt = $cnt - 1"
    istep=${prod_step}_$cnt
    pstep=${prod_step}_$pcnt
    if [ $systype == solution ]; then
        if [ $cnt == 1 ]; then pstep=$equi_prefix; fi
    else
        if [ $cnt == 1 ]; then pstep=`printf $equi_prefix 6`; fi
    fi
    input_param="-t toppar.str -p $init.psf -c $init.crd -irst $pstep.rst"
    echo "$python -u openmm_run.py -i ${prod_prefix}.inp ${input_param} -orst $istep.rst -odcd $istep.dcd > $istep.out"
    set -e
    $python -u openmm_run.py -i ${prod_prefix}.inp ${input_param} -orst $istep.rst -odcd $istep.dcd > $istep.out
    set +e
    echo $cnt >> .steps.done
    ((cnt++))
done

if [ $cnt -gt $cntmax ]; then
    echo Done
    exit
fi

# resubmit self
if [[ -n "$SLURM_JOB_NAME" ]]; then
    echo resubmitting
    cd ../..
    set -e
    ./submit.sh --resubmit "$SLURM_JOB_NAME"
    set +e
else
    echo not resubmitting
fi
