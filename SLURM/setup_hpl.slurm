#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=240G
#SBATCH --time=00:15:00
#SBATCH --output=setup_hpl_slurm_script_output.log
#SBATCH --error=setup_hpl_slurm_script_error.log
#SBATCH --partition test

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzpf hpl-2.3.tar.gz  

module purge
module load gcc
module load openblas
module load openmpi

cd hpl-2.3 
./configure -
make clean
make
