#!/bin/bash

#SBATCH --nodes=4
#SBATCH --ntasks-per-node=24
#SBATCH --output=run_hpl_slurm_script_output.log
#SBATCH --error=run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load openblas
module load openmpi

OMP_NUM_THREADS=1 mpirun -np 24 --host cn01,cn02,cn03,cn04 ./xhpl > hpl.log 
    