#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --output=tldr_slurm_script_output.log
#SBATCH --error=tldr_slurm_script_error.log

python3 TLDR.py data.input
    