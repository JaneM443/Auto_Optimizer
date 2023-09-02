import optuna
import subprocess
import pickle
import sys
import os
import logging
import typing
from typing import Any, List, Dict, Tuple
import math

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
    #----------------------------------------------

def main(data) -> None:
                             # dict[param_name: tuple[param_minimum, param_maximum]]
    hyperparameters          : Dict[str       : Tuple[Any          , Any          ]] = data[0]

                             # dict[parameter_name: parameter_value]
    runtimeparameters        : Dict[str           : Any            ] = data[2]

    #----------------------------------------------
    
    if not os.path.exists("hpl-2.3/"):
        logging.info("hpl-2.3/ not found -> Running 'SLURM/setup_hpl.slurm'")

        slurm_script_path = 'SLURM/setup_hpl.slurm'
        #Run the SLURM script directly
        try:
            subprocess.run(['bash', slurm_script_path], check=True)
            logging.debug("SLURM script executed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing SLURM script: {e}")

    study = optuna.create_study(direction = "maximize",pruner=optuna.pruners.MedianPruner())
    study.optimize(lambda trial : objective(trial, hyperparameters, runtimeparameters), n_trials=20)

    best_params = study.best_params
    best_value = study.best_value
    best_study = study.best_study

    logging.info("Best Parameters: "+str(best_params))
    logging.info("Best Value: "+str(best_value))
    logging.info("Best Study: "+str(best_study))

def edit_HPL_dat(limits):
    with open('Extra/HPL.dat.scaffold', 'r') as file:
        hpl_file_data = file.read()

    for param_name in limits.keys():
        hpl_file_data = hpl_file_data.replace(f"{{{param_name}}}", f"{limits[param_name]}")

    with open("hpl-2.3/testing/HPL.dat", 'w') as file:
        file.write(hpl_file_data)

def run_hpl_benchmark():
    shell_script = "SLURM/run_hpl.slurm"
    
    try:
        subprocess.run(["bash", shell_script], check=True)
        logging.debug("SLURM script executed successfully.")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")
        raise e(f"Error executing SLURM script: {e}")

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
    hyperparameter_names = [name for name in hyperparameters.keys()]
    
    # Choosing hyperparameter values
    #! We may want to potentially rename this variable for clarity
    limits = {key: trial.suggest_int(key, hyperparameters[key][0], hyperparameters[key][1]) for key in hyperparameter_names}
    limits["Qs"] = runtimeparameters["Number Of Nodes"][0] * runtimeparameters["Cores Per Node Input"][0] // limits["Ps"]
    logging.debug("nodes: "+str(runtimeparameters["Number Of Nodes"][0]))
    logging.debug("cores: "+str(runtimeparameters["Cores Per Node Input"][0]))
    logging.debug("P: "+str(limits["Ps"]))
    logging.debug("Q: "+str(limits["Qs"]))
    logging.debug(f"Limits : {str(limits)}")
    
    edit_HPL_dat(limits)
    run_hpl_benchmark()

    gflops = retrieve_latest_gflops()

    if trial.should_prune():
        logging.info("Trial pruned")
        raise optuna.exceptions.TrialPruned()

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