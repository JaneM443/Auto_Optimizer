import subprocess
import logging
import pickle
import sys
from typing import Any, List, Dict, Tuple

#! Generate and sbatch tldr SLURM File

# I replicated the structure of loading in the data input from dougal and the logger 
# - not sure is the logger should be set up here or TLDR as it will still be needed there

def load_logger():
    #----------------------------------------------
    AUTO_CLEAR = True
    logging.basicConfig(
        filename = "output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s' | %(funcName)s%(args)s @ line %(lineno)d in %(filename)s from %(module)s | StackInfo : %(stack_info)s | ProcessInfo : %(processName)s(%(process)d) | ThreadInfo : %(threadName)s(%(thread)d)"
        )

    logging.info("Logger Loaded")

def generate_tldr_slurm_script_content():
    content = f"""\
    #!/bin/bash

    #SBATCH --nodes={runtimeparameters['Number Of Nodes']}
    #SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input']}
    #SBATCH --mem={runtimeparameters['Memory Per Node GB']}
    #SBATCH --time={runtimeparameters['Max Runtime In Hours']}
    #SBATCH --output=output.log
    #SBATCH --error=error.log

    python3 TLDR.py hyperparameters

    """

    return content

def generate_run_hpl_slurm_script_content():
    content = f"""\
    #!/bin/bash

    #SBATCH --nodes={runtimeparameters['Number Of Nodes']}
    #SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input']}
    #SBATCH --mem={runtimeparameters['Memory Per Node GB']}
    #SBATCH --time={runtimeparameters['Max Runtime In Hours']}
    #SBATCH --output=output.log
    #SBATCH --error=error.log

    module purge
    module load {moduledata['MPI Modules']}
    module load {moduledata['BLAS Modules']}
    module load {moduledata['Compilers']}

    cd hpl-2.3
    cd testing

    mpirun -np $SLURM_NTASKS ./xhpl > hpl.log 

    """

    return content

def generate_setup_hpl_slurm_script_content():
    content = f"""\
    #!/bin/bash

    #SBATCH --nodes={runtimeparameters['Number Of Nodes']}
    #SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input']}
    #SBATCH --mem={runtimeparameters['Memory Per Node GB']}
    #SBATCH --time=00:15:00
    #SBATCH --output=output.log
    #SBATCH --error=error.log

    wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
    tar xzpf hpl-2.3.tar.gz  

    module purge
    module load {moduledata['MPI Modules']}
    module load {moduledata['BLAS Modules']}
    module load {moduledata['Compilers']}

    cd hpl-2.3 
    ./configure
    make clean
    make

    cd testing        
    cp ptest/HPL.dat .  # Change to copy in HPL.dat from this folder

    """

    return content

def main(data) -> None:

                             # dict[param_name: tuple[param_minimum, param_maximum]]
    hyperparameters          : Dict[str       : Tuple[Any          , Any          ]] = data[0] # These may not need to be unpacked here

                             # dict[module_type: list[module1, ...]]
    moduledata               : Dict[str        : List[str    , ...]] = data[1]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------

    hyperparameter_names = [name for name in hyperparameters.keys()]

    # Generate the SLURM script content
    # From what I understand from Arijus, all SLURM files are generated here with the values from dougal
    # The only thing we would then need is the hyperparameter information

    tldr_shell_script = "SLURM/tldr.slurm"
    run_hpl_shell_script = "SLURM/run_hpl.slurm"
    setup_hpl_shell_script = "SLURM/setup_hpl.slurm" # I may go through and change this name to prepare for new benchmarks, setup --> setup_hpl

    #? Need to decide appropriate timings for these scripts -- DONE?
    tldr_slurm_script_content    = generate_tldr_slurm_script_content()
    run_hpl_slurm_script_content = generate_run_hpl_slurm_script_content()
    setup_hpl_slurm_script_content = generate_setup_hpl_slurm_script_content()

    # Write the generated content to a SLURM script file
    with open(tldr_shell_script, "w") as f:
        f.write(tldr_slurm_script_content)

    try:
        subprocess.run(["sbatch", tldr_shell_script], check=True)
        logging.debug("Job submitted successfully.")
        
    except subprocess.CalledProcessError as e:
        pass
        logging.error(f"Error submitting job: {e}")

if __name__ == "__main__":

#! Load data here, instead of TLDR.py?

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