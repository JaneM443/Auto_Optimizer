import subprocess
import logging
import pickle
import sys
from typing import Any, List, Dict
import os

#! Generate and sbatch tldr SLURM File

def load_logger(output_file_path):
    #----------------------------------------------
    os.mkdir(f"{output_file_path}")

    AUTO_CLEAR = True

    current_directories = os.listdir()

    logging.basicConfig(
        filename = f"{output_file_path}/start_TLDR_output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s' | %(funcName)s%(args)s @ line %(lineno)d in %(filename)s from %(module)s | StackInfo : %(stack_info)s | ProcessInfo : %(processName)s(%(process)d) | ThreadInfo : %(threadName)s(%(thread)d)"
        )

    logging.info("Logger Loaded")

def generate_tldr_slurm_script_content(runtimeparameters, output_file_path):
    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input'][0]}
#SBATCH --output={output_file_path}/tldr_slurm_script_output.log
#SBATCH --error={output_file_path}/tldr_slurm_script_error.log

python3 TLDR.py data.input
    """

    return content

def generate_run_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path):
    content = f"""\
#!/bin/bash

#SBATCH --nodes={runtimeparameters['Number Of Nodes'][0]}
#SBATCH --ntasks-per-node={runtimeparameters['Cores Per Node Input'][0]}
#SBATCH --output={output_file_path}/run_hpl_slurm_script_output.log
#SBATCH --error={output_file_path}run_hpl_slurm_script_error.log

cd hpl-2.3
cd testing


module load {moduledata["BLAS Modules"][0]}
module load {moduledata["MPI Modules"][0]}

mca_params="--mca btl tcp,self --mca btl_tcp_if_include eth0 --mca mtl ^psm2"
OMP_NUM_THREADS=1 mpirun $mca_params -np {runtimeparameters['Number Of Nodes'][0] * runtimeparameters['Cores Per Node Input'][0]} ./xhpl > hpl.log 
    """

    return content

def generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path):
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

module load {moduledata["BLAS Modules"][0]}
module load {moduledata["MPI Modules"][0]}

cd hpl-2.3 
./configure --prefix=$HOME/Auto_Optimizer
make clean
make -j 8
make install -j8

"""

    return content

def main(data, output_file_path) -> None:

                             # dict[module_type: list[module1, ...]]
    moduledata               : Dict[str        : List[str    , ...]] = data[1]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------

    # Generate the SLURM script content
    
    tldr_slurm_script = "SLURM/tldr.sh"
    setup_hpl_slurm_script = "SLURM/setup_hpl.sh" 
    run_hpl_slurm_script = "SLURM/run_hpl.sh" 

    tldr_slurm_script_content    = generate_tldr_slurm_script_content(runtimeparameters, output_file_path)
    setup_hpl_slurm_script_content = generate_setup_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path)
    run_hpl_slurm_script_content = generate_run_hpl_slurm_script_content(runtimeparameters, moduledata, output_file_path)

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

    current_directory_id_list = os.listdir("outputs")
    if len(current_directory_id_list) == 0:
        next_directory_id = 0
    else:
        current_max_id = max(int(dir_id) for dir_id in current_directory_id_list)
        next_directory_id = current_max_id + 1

    if os.path.isdir("outputs") == False:
        os.mkdir("outputs")

    output_file_path = f"outputs/{next_directory_id}"

    load_logger(output_file_path)

    try:
        with open(FILE_PATH, "rb") as file:
            data = pickle.load(file)
            logging.info(f"Loaded Data : {data}")
    except Exception as exception:
        logging.critical(f"Error with loading Dougal data: {type(exception).__name__} - {exception}")
        raise Exception
    
    main(data, output_file_path)  
