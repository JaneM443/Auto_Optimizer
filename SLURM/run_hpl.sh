#!/bin/bash

#SBATCH --nodes=70
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/51/run_hpl_slurm_script_output.log
#SBATCH --error=outputs/51run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

source /apps/intel/setvars.sh
module load hpl/intel

export OMP_NUM_THREADS=1
export I_MPI_FABRICS=ofi
export FI_PROVIDER=tcp
OMP_NUM_THREADS=1 mpirun -np 1680 xhpl > hpl.log 
    