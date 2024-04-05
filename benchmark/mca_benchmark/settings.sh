#
# edit this file to adjust benchmark parameters
#

# number of simultaneous tests to run. N.B. CHARMM is very memory intensive,
# so this should not necessarily be the same as the number of CPUs on your
# machine.
N_CPUS=2

# number of replicas to run for each volume fraction (% v/v)
nreps=12

# lowest % v/v to run
first_vv=10

# highest % v/v to run
last_vv=42
