#!/bin/bash

#SBATCH --nodes=3
#SBATCH --ntasks-per-node=24
#SBATCH --output=outputs/1/tldr_slurm_script_output.log
#SBATCH --error=outputs/1/tldr_slurm_script_error.log

python3 TLDR.py data.input
    