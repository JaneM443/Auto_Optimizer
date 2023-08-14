#!/bin/bash

# Load the MPI module (specific to your cluster setup)
module purge
module load gcc
module load openblas
module load openmpi

cd hpl-2.3
cd testing

# Run the MPI executable using mpirun
mpirun -n 128 ./xhpl > hpl.log