import subprocess
import logging
import pickle
import sys
from typing import Any, List, Dict

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
#SBATCH --output=tldr_slurm_script_output.log
#SBATCH --error=tldr_slurm_script_error.log

python3 TLDR.py data.input
    """

    return content

def generate_run_hpl_slurm_script_content(runtimeparameters):
    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input'][0]}
#SBATCH --output=run_hpl_slurm_script_output.log
#SBATCH --error=run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load openblas
module load openmpi

OMP_NUM_THREADS=1 mpirun -np 24 --host cn01,cn02,cn03,cn04 ./xhpl > hpl.log 
    """

    return content

def generate_setup_hpl_slurm_script_content(runtimeparameters):
    content = f"""\
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:15:00
#SBATCH --output=setup_hpl_slurm_script_output.log
#SBATCH --error=setup_hpl_slurm_script_error.log

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzpf hpl-2.3.tar.gz  

module purge
module load openblas
module load openmpi

cd hpl-2.3 
./configure --prefix=$HOME/Auto_Optimizer
make clean
make -j 8
make install -j8

"""

    return content

def main(data) -> None:

                             # dict[module_type: list[module1, ...]]
    moduledata               : Dict[str        : List[str    , ...]] = data[1]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------

    # Generate the SLURM script content
    
    tldr_slurm_script = "SLURM/tldr.sh"
    setup_hpl_slurm_script = "SLURM/setup_hpl.sh" 
    run_hpl_slurm_script = "SLURM/run_hpl.sh" 

    tldr_slurm_script_content    = generate_tldr_slurm_script_content(runtimeparameters)
    setup_hpl_slurm_script_content = generate_setup_hpl_slurm_script_content(runtimeparameters)
    run_hpl_slurm_script_content = generate_run_hpl_slurm_script_content(runtimeparameters)

    # Write the generated content to a SLURM script file
    
    with open(tldr_slurm_script, "w") as f:
        f.write(tldr_slurm_script_content)
    with open(setup_hpl_slurm_script, "w") as f:
        f.write(setup_hpl_slurm_script_content)
    with open(run_hpl_slurm_script, "w") as f:
        f.write(run_hpl_slurm_script_content)

    subprocess.run(["sbatch", tldr_slurm_script], check=True)
    logging.debug("Job submitted successfully.")
        

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