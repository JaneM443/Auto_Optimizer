#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=240G
#SBATCH --time=24:00:00
#SBATCH --output=tldr_slurm_script_output.log
#SBATCH --error=tldr_slurm_script_error.log
#SBATCH --partition multi

python3 TLDR.py data.input
    