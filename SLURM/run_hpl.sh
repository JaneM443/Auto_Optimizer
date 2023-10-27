#!/bin/bash

#SBATCH --nodes=73
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/29/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/29run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing


module load openblas
module load openmpi

mca_params="--mca btl tcp,self --mca btl_tcp_if_include eth0 --mca mtl ^psm2"
OMP_NUM_THREADS=1 mpirun $mca_params -np 1752 ./xhpl > hpl.log 
    