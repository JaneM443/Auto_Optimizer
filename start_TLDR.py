import subprocess
import logging
import pickle
import sys
from typing import Any, List, Dict

PARTITION = "test"

#! Generate and sbatch tldr SLURM File

def load_logger():
    #----------------------------------------------
    AUTO_CLEAR = True
    logging.basicConfig(
        filename = "start_TLDR_output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s' | %(funcName)s%(args)s @ line %(lineno)d in %(filename)s from %(module)s | StackInfo : %(stack_info)s | ProcessInfo : %(processName)s(%(process)d) | ThreadInfo : %(threadName)s(%(thread)d)"
        )

    logging.info("Logger Loaded")

def generate_tldr_slurm_script_content(runtimeparameters):
    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input'][0]}
#SBATCH --mem={runtimeparameters['Memory Per Node GB'][0]}G
#SBATCH --time={runtimeparameters['Max Runtime In Hours'][0]}
#SBATCH --output=tldr_slurm_script_output.log
#SBATCH --error=tldr_slurm_script_error.log
#SBATCH --partition {PARTITION}

python3 TLDR.py data.input
    """

    return content

def generate_run_hpl_slurm_script_content(runtimeparameters, moduledata):
    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks={runtimeparameters['Cores Per Node Input'][0]}
#SBATCH --mem={runtimeparameters['Memory Per Node GB'][0]}G
#SBATCH --time=00:15:00
#SBATCH --output=run_hpl_slurm_output.log
#SBATCH --error=run_hpl_slurm_error.log
#SBATCH --partition test
module purge
module load {moduledata['Compilers'][0]}
module load {moduledata['BLAS Modules'][0]}
module load {moduledata['MPI Modules'][0]}

cd hpl-2.3
cd testing

mpirun -np {runtimeparameters['Number Of Nodes'][0]*runtimeparameters['Cores Per Node Input'][0]} ./xhpl > hpl.log 
"""

    return content

def generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata):
    content = f"""\
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem={runtimeparameters['Memory Per Node GB'][0]}G
#SBATCH --time=00:15:00
#SBATCH --output=setup_hpl_slurm_script_output.log
#SBATCH --error=setup_hpl_slurm_script_error.log
#SBATCH --partition test

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzpf hpl-2.3.tar.gz  

module purge
module load {moduledata['Compilers'][0]}
module load {moduledata['BLAS Modules'][0]}
module load {moduledata['MPI Modules'][0]}

cd hpl-2.3 
./configure
make clean
make
"""

    return content

def main(data) -> None:

                             # dict[module_type: list[module1, ...]]
    moduledata               : Dict[str        : List[str    , ...]] = data[1]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------

    # Generate the SLURM script content
    
    tldr_slurm_script = "SLURM/tldr.slurm"
    run_hpl_slurm_script = "SLURM/run_hpl.slurm"
    setup_hpl_slurm_script = "SLURM/setup_hpl.slurm" 

    tldr_slurm_script_content    = generate_tldr_slurm_script_content(runtimeparameters)
    run_hpl_slurm_script_content = generate_run_hpl_slurm_script_content(runtimeparameters, moduledata)
    setup_hpl_slurm_script_content = generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata)

    # Write the generated content to a SLURM script file
    
    with open(tldr_slurm_script, "w") as f:
        f.write(tldr_slurm_script_content)
    with open(run_hpl_slurm_script, "w") as f:
        f.write(run_hpl_slurm_script_content)
    with open(setup_hpl_slurm_script, "w") as f:
        f.write(setup_hpl_slurm_script_content)

    try:
        subprocess.run(["sbatch", tldr_slurm_script], check=True)
        logging.debug("Job submitted successfully.")
        
    except subprocess.CalledProcessError as e:
        pass
        logging.error(f"Error submitting job: {e}")
        raise e

if __name__ == "__main__":

    FILE_PATH = sys.argv[1]
    load_logger()

    try:
        with open(FILE_PATH, "rb") as file:
            data = pickle.load(file)
            logging.info(f"Loaded Data : {data}")
    except Exception as exception:
        logging.critical(f"Error with loading Dougal data: {type(exception).__name__} - {exception}")
        raise Exception
    
    main(data)  