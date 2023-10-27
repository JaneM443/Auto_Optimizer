#!/bin/bash

#SBATCH --nodes=3
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/1/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/1run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load openblas
module load openmpi

OMP_NUM_THREADS=1 mpirun -np 72 ./xhpl > hpl.log 
    