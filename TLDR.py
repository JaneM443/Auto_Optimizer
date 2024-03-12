import optuna
import subprocess
import pickle
import sys
import os
import shutil
import logging
from typing import Any, Dict, Tuple, List
import time

###-------------------------------------------------------------------------###
### Runs multiple trials and logs results                                   ###
###-------------------------------------------------------------------------###

def load_logger(output_file_path):
    ###---------------------------------------------------------------------###
    ### Configure logging format, sending all files to that directory       ###
    ###---------------------------------------------------------------------###
    
    AUTO_CLEAR = True
    logging.basicConfig(
        filename = f"{output_file_path}/TLDR_output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s'"
        )

    logging.info("Logger Loaded")

    #-----------------------------------------------------------------------###

def main(data) -> None:
    ###---------------------------------------------------------------------###
    ### Sets up, runs and concludes the full trial
    ###---------------------------------------------------------------------###

                            # Dict[Param Name: Tuple[Min, Max]] (Ns, Ps)
    hyperparameters         : Dict[str       : Tuple[Any, Any]] = data[0]

                            # Dict[Parameter Name: Value] (SLURM Parameters)
    runtimeparameters       : Dict[str           : Any            ] = data[2]

    # HPL file paths

    folder_path = "hpl-2.3/"
    file_path = "hpl-2.3.tar.gz"
    
    # Remove HPL and run setup from scratch

    logging.info("Running 'SLURM/setup_hpl.sh'")
    try:
        shutil.rmtree(folder_path)
        os.remove(file_path)
    except OSError as e:
        print(f"Error: {folder_path} could not be removed - {e}")

    slurm_script_path = 'SLURM/setup_hpl.sh'
    try:
        subprocess.run(['bash', slurm_script_path], check=True)
        logging.debug("SLURM script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")
        raise e
    
    # Create optuna study and runs the full trial

    study = optuna.create_study(direction = "maximize", 
                                pruner=optuna.pruners.MedianPruner())
    study.optimize(lambda trial : objective(trial, 
                                            hyperparameters, 
                                            runtimeparameters), 
                   n_trials = runtimeparameters["Number Of Trials"][0])

    # Returns the best parameters found from the trials

    best_params = study.best_params
    best_value = study.best_value
    best_trial = study.best_trial

    # Logs those results

    logging.info("Best Parameters: "+str(best_params))
    logging.info("Best Value: "+str(best_value))
    logging.info("Best Study: "+str(best_trial))

    #-----------------------------------------------------------------------###

def edit_HPL_dat(limits):
    ###---------------------------------------------------------------------###
    ### Changes parameters in HPL dat
    ###---------------------------------------------------------------------###

    with open('Extra/HPL.dat.scaffold', 'r') as file:
        hpl_file_data = file.read()

    for param_name in limits.keys():
        hpl_file_data = hpl_file_data.replace(f"{{{param_name}}}", f"{limits[param_name]}")

    with open("hpl-2.3/testing/HPL.dat", 'w') as file:
        file.write(hpl_file_data)

    #-----------------------------------------------------------------------###

def run_hpl_benchmark():
    ###---------------------------------------------------------------------###
    ### Runs one HPL trial
    ###---------------------------------------------------------------------###

    slurm_script_path = 'SLURM/run_hpl.sh'
   
    try:
        subprocess.run(['bash', slurm_script_path], check=True)
        logging.debug("SLURM script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")
        raise e
    
    #-----------------------------------------------------------------------###

def retrieve_latest_gflops():
    ###---------------------------------------------------------------------###
    ### Extracts GFLOPS data from HPL log file
    ###---------------------------------------------------------------------###

    with open('hpl-2.3/testing/hpl.log','r') as file:
        hpl_log_lines = file.readlines()

    data_indicies = [index + 2 for (index, line) in enumerate(hpl_log_lines) if "Gflops" in line]
    data_indicies = data_indicies[1:]
    data_lines = [line.strip('\n').split(' ') for (index, line) in enumerate(hpl_log_lines) if index in data_indicies]
    data_lines = [[data for data in line if data != ''] for line in data_lines]
    Gflops = [line[-1] for line in data_lines]

    if(len(Gflops) != 1):
        logging.critical(f"{len(Gflops)} is an invalid number of lines returned from data search. Expecting 1")
        raise Exception(f"{len(Gflops)} is an invalid number of lines returned from data search. Expecting 1")

    return float(Gflops[0])

    #-----------------------------------------------------------------------###

def objective(trial, hyperparameters, runtimeparameters):
    ###---------------------------------------------------------------------###
    ### The study, lays out method for each trial
    ###---------------------------------------------------------------------###

    # Logging information

    current_time = time.perf_counter()
    logging.info("Trial Started")
    hyperparameter_names = [name for name in hyperparameters.keys()]
    
    # Choosing hyperparameter values

    nodes = runtimeparameters["Number Of Nodes"][0]
    cores = runtimeparameters["Cores Per Node"][0]
    number_of_ranks = nodes*cores

    # Optuna picks a value within the user specified range for hyperparameters
    limits = {key: trial.suggest_int(key, 
                                     hyperparameters[key][0], 
                                     hyperparameters[key][1]) 
                for key in hyperparameter_names if key not in ("Ps", "Qs")}
    # Selects possible P values in the user specified range that divide ranks
    divisors = [divisor for divisor in range(hyperparameters["Ps"][0], 
                                             hyperparameters["Ps"][1]) 
                                             if number_of_ranks % divisor == 0]
    # Optuna selects one of these divisors
    Ps = trial.suggest_categorical("Ps", divisors)
    # Q is then fixed by this choice
    Qs = number_of_ranks // Ps

    #! Temporary remove once latency is gone
    limits.update({"Ps":Ps, "Qs":Qs})

    logging.info(f"Limits : {str(limits)}")
    
    # Run Benchmark with these values and extract GFLOPS

    # Update HPL dat file
    edit_HPL_dat(limits)
    # Run the HPL benchmark while time stamping 
    os.system("echo `date -u` > hpl_submission.tstamps")
    run_hpl_benchmark()
    os.system("echo `date -u` >> hpl_submission.tstamps")
    # Retrieve result of trial
    gflops = retrieve_latest_gflops()
    logging.info(f"Gflops : {gflops}")


    delta_time = time.perf_counter() - current_time
    logging.info(f"Trial Ended : Elapsed time |{delta_time}|")

    return gflops

    #-----------------------------------------------------------------------###

if __name__ == "__main__":
    
    ###----------------------------------------------------------------------###
    ### User interacts here to change run parameters                         ###
    ###----------------------------------------------------------------------###
    
    # File path for current logging
    current_directories = os.listdir("Outputs")
    current_id = max(int(dir_id) for dir_id in current_directories)

    output_file_path = f"Outputs/{current_id}"

    load_logger(output_file_path) # Points logger to directory


    # Loads data from ServersideDougal

    FILE_PATH = sys.argv[1]

    try:
        with open(FILE_PATH, "rb") as file:
            data = pickle.load(file)
            logging.info(f"Loaded Data : {data}")
    except Exception as exception:
        logging.critical(f"Error with loading Dougal data: {type(exception).__name__} - {exception}")
        raise Exception

    main(data)                  

    #-----------------------------------------------------------------------###