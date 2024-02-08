#!/bin/csh
#

module load cuda/10.0
module load gcc/6.1.0

set python = /share/ceph/woi216group-c2/shared/apps/python-3.7.4/bin/python3

setenv OPENMM_PLUGIN_DIR /share/ceph/woi216group-c2/shared/apps/openmm-7.4.1/lib/plugins
setenv PYTHONPATH /share/ceph/woi216group-c2/shared/apps/openmm-7.4.1/lib/python3.7/site-packages
setenv LD_LIBRARY_PATH /share/ceph/woi216group-c2/shared/apps/openmm-7.4.1/lib:$LD_LIBRARY_PATH

${python} -u ommrst2crd.py -i step7_500.rst -p step5_charmm2omm.psf -o step7_500.crd

