#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --output=outputs/3/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/3run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load intel
module load openblas
module load openmpi

OMP_NUM_THREADS=1 mpirun -np 12 xhpl > hpl.log 
