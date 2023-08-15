#!/bin/bash

# Request resources:
#SBATCH -n 128
#SBATCH -N 1
#SBATCH -t 00:15:00
#SBATCH -p test

# Load required modules (e.g., compilers, Python)
wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  # get the package tarball
tar xzpf hpl-2.3.tar.gz  # extract the tarball into a folder

# hamilton-specific module dependencies
module purge

module load gcc
module load openblas
module load openmpi

cd hpl-2.3  # enter directory
./configure

make clean
make

cd testing        # enter the directory
cp ptest/HPL.dat .  # copy the template HPL.dat file into the current directory