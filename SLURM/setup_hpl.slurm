#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=128G
#SBATCH --time=00:15:00
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --partition test

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

    