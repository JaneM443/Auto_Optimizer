#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --output=outputs/3/tldr_slurm_script_output.log
#SBATCH --error=outputs/3/tldr_slurm_script_error.log

python3 TLDR.py data.input
    