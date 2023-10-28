#!/bin/bash

#SBATCH --nodes=70
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/64/tldr_slurm_script_output.log
#SBATCH --error=outputs/64/tldr_slurm_script_error.log

python3 TLDR.py data.input
    