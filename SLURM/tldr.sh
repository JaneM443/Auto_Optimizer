#!/bin/bash

#SBATCH --time=72:00:00
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=128
#SBATCH --output=Outputs/7/slurm_output.log
#SBATCH --error=Outputs/7/trial_summary.log

python3 TLDR.py data.input
    