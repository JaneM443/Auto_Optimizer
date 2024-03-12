#!/bin/bash

#SBATCH --nodes=4
#SBATCH --ntasks-per-node=128
#SBATCH --output=Outputs/7/run_hpl_slurm_script_output.log
#SBATCH --error=Outputs/7run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load gcc
module load openblas
module load openmpi

mpirun -np 512 xhpl > hpl.log 
