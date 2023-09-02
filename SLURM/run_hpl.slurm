#!/bin/bash

#SBATCH --nodes=6
#SBATCH --ntasks-per-node=12
#SBATCH --mem=12
#SBATCH --time=03:00:00
#SBATCH --output=output.log
#SBATCH --error=error.log

module purge
module load gcc
module load openblas
module load openmpi

cd hpl-2.3
cd testing

mpirun -np 72 ./xhpl > hpl.log 

    