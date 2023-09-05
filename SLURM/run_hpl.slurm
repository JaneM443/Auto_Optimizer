#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --mem=120G
#SBATCH --time=00:15:00
#SBATCH --output=run_hpl_slurm_output.log
#SBATCH --error=run_hpl_slurm_error.log
#SBATCH --partition test
module purge
module load intel
module load openblas
module load intelmpi

cd hpl-2.3
cd testing

mpirun -np 128 ./xhpl > hpl.log 
