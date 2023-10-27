#!/bin/bash

#SBATCH --nodes=73
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/29/tldr_slurm_script_output.log
#SBATCH --error=outputs/29/tldr_slurm_script_error.log

python3 TLDR.py data.input
    