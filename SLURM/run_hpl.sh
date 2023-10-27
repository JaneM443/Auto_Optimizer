#!/bin/bash

#SBATCH --nodes=48
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/19/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/19run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing


module load openblas
module load openmpi

mca_params="--mca btl tcp,self --mca btl_tcp_if_include eth0 --mca mtl ^psm2"
OMP_NUM_THREADS=1 mpirun $mca_params -np 1152 ./xhpl > hpl.log 
    