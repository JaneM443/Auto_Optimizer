#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/38/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/38run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

source /apps/intel/setvars.sh

OMP_NUM_THREADS=1 mpirun -np 24 ./xhpl > hpl.log 
    