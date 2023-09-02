#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=256G
#SBATCH --time=03:00:00
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --partition test
module purge
module load gcc
module load openblas
module load openmpi

cd hpl-2.3
cd testing

mpirun -np 128 ./xhpl > hpl.log 

    