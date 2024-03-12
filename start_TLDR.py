import subprocess
import logging
import pickle
import sys
from typing import Any, List, Dict
import os

###-------------------------------------------------------------------------###
### Generate SLURM Files, set up logging, import parameters and begin run   ###
###-------------------------------------------------------------------------###

def load_logger(output_file_path):
    ###---------------------------------------------------------------------###
    ### Configure logging format, sending all files to that new directory   ###
    ###---------------------------------------------------------------------###
    
    os.mkdir(f"{output_file_path}")

    AUTO_CLEAR = True

    logging.basicConfig(
        filename = f"{output_file_path}/start_TLDR_output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s'"
        )

    logging.info("Logger Loaded")

    #-----------------------------------------------------------------------###

def generate_tldr_slurm_script_content(runtimeparameters, output_file_path):
    ###---------------------------------------------------------------------###
    ### Generates script content for 'tldr.sh', that calls TLDR             ###
    ###---------------------------------------------------------------------###
    
    content = f"""\
#!/bin/bash

#SBATCH --time={runtimeparameters['Max Runtime In Hours'][0]}
#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node'][0]}
#SBATCH --output={output_file_path}/slurm_output.log
#SBATCH --error={output_file_path}/trial_summary.log

python3 TLDR.py data.input
    """

    return content

    #-----------------------------------------------------------------------###

def generate_run_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path):
    ###---------------------------------------------------------------------###
    ### Generates script content for 'run_hpl.sh', with relevant parameters ###
    ###---------------------------------------------------------------------###
    
    nodes = runtimeparameters['Number Of Nodes'][0]
    cores = runtimeparameters['Cores Per Node'][0]
    processes = nodes*cores

    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node'][0]}
#SBATCH --output={output_file_path}/run_hpl_slurm_script_output.log
#SBATCH --error={output_file_path}run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing

module load {moduledata["Compiler"][0]}
module load {moduledata["BLAS"][0]}
module load {moduledata["MPI"][0]}

mpirun -np {processes} xhpl > hpl.log 
"""

    return content

    #-----------------------------------------------------------------------###

def generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path):
    ###---------------------------------------------------------------------###
    ### Generates script content for 'setup_hpl.sh'                         ###
    ###---------------------------------------------------------------------###
    
    content = f"""\
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:15:00
#SBATCH --output={output_file_path}/setup_hpl_slurm_script_output.log
#SBATCH --error={output_file_path}/setup_hpl_slurm_script_error.log

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz  
tar xzf hpl-2.3.tar.gz  

module purge

module load {moduledata["Compiler"][0]}
module load {moduledata["BLAS"][0]}
module load {moduledata["MPI"][0]}

cd hpl-2.3 
./configure --prefix=$HOME/Auto_Optimizer CFLAGS="-O3 -march=native"
make clean
make -j 8
make install -j8

"""

    return content

    #-----------------------------------------------------------------------###

def main(data, output_file_path) -> None:

    ###---------------------------------------------------------------------###
    ### Creates three SLURM scripts in the SLURM folder and sbatches TLDR   ###
    ###---------------------------------------------------------------------###

                        # Dict[Module Name: Module] (BLAS, MPI, Compiler)
    moduledata          : Dict[str        : List[str    , ...]] = data[1]

                        # Dict[Parameter Name: Value] (SLURM Parameters)
    runtimeparameters   : Dict[str           : Any            ] = data[2]

    # Create SLURM Script Paths
    
    tldr_slurm_script = "SLURM/tldr.sh"
    setup_hpl_slurm_script = "SLURM/setup_hpl.sh" 
    run_hpl_slurm_script = "SLURM/run_hpl.sh" 

    # Generate the SLURM script content

    tldr_slurm_script_content    = generate_tldr_slurm_script_content(runtimeparameters, output_file_path)
    setup_hpl_slurm_script_content = generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path)
    run_hpl_slurm_script_content = generate_run_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path)

    # Write content to SLURM script
    
    with open(tldr_slurm_script, "w") as f:
        f.write(tldr_slurm_script_content)
    with open(setup_hpl_slurm_script, "w") as f:
        f.write(setup_hpl_slurm_script_content)
    with open(run_hpl_slurm_script, "w") as f:
        f.write(run_hpl_slurm_script_content)

    subprocess.run(["sbatch", tldr_slurm_script], check=True)
    logging.debug("Job submitted successfully.")

    #-----------------------------------------------------------------------###
        
if __name__ == "__main__":

    ###---------------------------------------------------------------------###
    ### Creates output folder for logging and imports the data from Dougal  ###
    ###---------------------------------------------------------------------###

    # Ensure output directory exists
    if os.path.isdir("Outputs") == False:
        os.mkdir("Outputs")

    # Creates a new directory for this run with unique ID
    current_directories = os.listdir("Outputs")
    if len(current_directories) == 0:
        next_id = 1
    else:
        current_id = max(int(dir_id) for dir_id in current_directories)
        next_id = current_id + 1

    output_file_path = f"Outputs/{next_id}"

    load_logger(output_file_path) # Points logger to new directory


    # Loads data from ServersideDougal

    FILE_PATH = sys.argv[1] # Pickle file path with run parameters
    
    try:
        with open(FILE_PATH, "rb") as file:
            data = pickle.load(file)
            logging.info(f"Loaded Data : {data}")

    except Exception as exception:
        logging.critical(f"Error with loading Dougal data: {type(exception).__name__} - {exception}")
        raise Exception
    
    main(data, output_file_path)  

    #-----------------------------------------------------------------------###