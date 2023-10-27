#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/40/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/40run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

source /apps/intel/setvars.sh
module load hpl/intel

export OMP_NUM_THREADS=1
export I_MPI_FABRICS=ofi
export FI_PROVIDER=tcp
OMP_NUM_THREADS=1 mpirun -np 24 xhpl > hpl.log 
    