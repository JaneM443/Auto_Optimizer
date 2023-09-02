#!/bin/bash

#SBATCH --nodes=6
#SBATCH --ntasks-per-node=12
#SBATCH --mem=12
#SBATCH --time=00:15:00
#SBATCH --output=output.log
#SBATCH --error=error.log

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzpf hpl-2.3.tar.gz  

module purge
module load openmpi
module load openblas
module load gcc

cd hpl-2.3 
./configure
make clean
make

    