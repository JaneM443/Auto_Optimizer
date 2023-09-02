#!/bin/sh

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=128G
#SBATCH --time=03:00:00
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --partition multi

python3 TLDR.py data.input

    