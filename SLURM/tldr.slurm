#!/bin/sh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=256G
#SBATCH --time=03:00:00
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --partition test

python3 TLDR.py data.input

    