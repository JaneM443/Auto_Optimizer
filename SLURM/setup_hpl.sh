#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:15:00
#SBATCH --output=Outputs/9/setup_hpl_slurm_script_output.log
#SBATCH --error=Outputs/9/setup_hpl_slurm_script_error.log

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzf hpl-2.3.tar.gz  

module purge

module load gcc
module load openblas
module load openmpi

cd hpl-2.3 
./configure --prefix=$HOME/Auto_Optimizer CFLAGS="-O3 -march=native"
make clean
make -j 8
make install -j8

