import optuna
import subprocess
import pickle
import sys
import os
import shutil
import logging
from typing import Any, Dict, Tuple, List
import time

def load_logger():

    #----------------------------------------------
    current_directory_id_list = os.listdir("outputs")

    current_max_id = max(int(dir_id) for dir_id in current_directory_id_list)

    dir_path = f"outputs/{current_max_id}"
    AUTO_CLEAR = True
    logging.basicConfig(
        filename = f"{dir_path}/TLDR_output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s' | %(funcName)s%(args)s @ line %(lineno)d in %(filename)s from %(module)s | StackInfo : %(stack_info)s | ProcessInfo : %(processName)s(%(process)d) | ThreadInfo : %(threadName)s(%(thread)d)"
        )

    logging.info("Logger Loaded")
    #----------------------------------------------

def main(data) -> None:
                             # dict[param_name: tuple[param_minimum, param_maximum]]
    hyperparameters          : Dict[str       : Tuple[Any          , Any          ]] = data[0]

                            # dict[module_type: list[module1, ...]]
    moduledata               : Dict[str        : List[str    , ...]] = data[1]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------
    folder_path = "hpl-2.3/"
    file_path = "hpl-2.3.tar.gz"
    
    logging.info("Running 'SLURM/setup_hpl.sh'")
    try:
        shutil.rmtree(folder_path)
        os.remove(file_path)
    except OSError as e:
        print(f"Error: {folder_path} could not be removed - {e}")

    slurm_script_path = 'SLURM/setup_hpl.sh'
    #Run the SLURM script directly
    try:
        subprocess.run(['bash', slurm_script_path], check=True)
        logging.debug("SLURM script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")
        raise e

    logging.debug("nodes: "+str(runtimeparameters["Number Of Nodes"][0]))
    logging.debug("cores: "+str(runtimeparameters["Cores Per Node Input"][0]))
        
    study = optuna.create_study(direction = "maximize",pruner=optuna.pruners.MedianPruner())
    study.optimize(lambda trial : objective(trial, hyperparameters, runtimeparameters), n_trials=runtimeparameters["Number Of Trials"][0])

    best_params = study.best_params
    best_value = study.best_value
    best_trial = study.best_trial

    logging.info("Best Parameters: "+str(best_params))
    logging.info("Best Value: "+str(best_value))
    logging.info("Best Study: "+str(best_trial))

def edit_HPL_dat(limits):
    with open('Extra/HPL.dat.scaffold', 'r') as file:
        hpl_file_data = file.read()

    for param_name in limits.keys():
        hpl_file_data = hpl_file_data.replace(f"{{{param_name}}}", f"{limits[param_name]}")

    with open("hpl-2.3/testing/HPL.dat", 'w') as file:
        file.write(hpl_file_data)

def run_hpl_benchmark(runtimeparameters):

    slurm_script_path = 'SLURM/run_hpl.sh'
    #Run the SLURM script directly
    try:
        subprocess.run(['bash', slurm_script_path], check=True)
        logging.debug("SLURM script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")
        raise e

def retrieve_latest_gflops():
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

def objective(trial, hyperparameters, runtimeparameters):
    current_time = time.perf_counter()
    logging.info("Trial Started")
    hyperparameter_names = [name for name in hyperparameters.keys()]
    
    # Choosing hyperparameter values

    number_of_ranks = runtimeparameters["Number Of Nodes"][0]*runtimeparameters["Cores Per Node Input"][0]

    limits = {key: trial.suggest_int(key, hyperparameters[key][0], hyperparameters[key][1]) for key in hyperparameter_names if key not in ("Ps", "Qs")}
    divisors = [divisor for divisor in range(hyperparameters["Ps"][0], hyperparameters["Ps"][1]) if number_of_ranks % divisor == 0]

    Ps = trial.suggest_categorical("Ps", divisors)
    Qs = number_of_ranks // Ps

    limits.update({"Ps":Ps, "Qs":Qs})

    logging.info(f"Limits : {str(limits)}")
    
    edit_HPL_dat(limits)
    run_hpl_benchmark(runtimeparameters)

    gflops = retrieve_latest_gflops()
    logging.info(f"Gflops : {gflops}")


    delta_time = time.perf_counter() - current_time
    logging.info(f"Trial Ended : Elapsed time |{delta_time}|")

    return gflops

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
