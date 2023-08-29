import optuna
import subprocess
import pickle
import sys
import os
import logging
import typing
from typing import Any, List, Dict, Tuple

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

    hyperparameter_names = [name for name in hyperparameters.keys()]
    
    if not os.path.exists("hpl-2.3/"):
        logging.info("hpl-2.3/ not found -> Running 'SLURM/setup.slurm'")

        slurm_script_path = 'SLURM/setup.slurm'
        #Run the SLURM script directly
        try:
            subprocess.run(['bash', slurm_script_path], check=True)
            logging.debug("SLURM script executed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing SLURM script: {e}")

    study = optuna.create_study(direction = "maximize",pruner=optuna.pruners.MedianPruner())
    study.optimize(lambda trial : objective(trial, hyperparameters, runtimeparameters), n_trials=10)

    best_params = study.best_params
    print('Best Parameters:')#Leaving in for the moment. must be moved to an output script :)
    print(best_params)

def edit_HPL_dat(limits):

    #! Search through File, remove hardcoded lines - JONNY ON IT
    #* search for line including varname and srt

    with open('hpl-2.3/testing/HPL.dat.scaffold', 'r') as file:
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

def retrieve_latest_gflops(): #likely more robust to search instead of hard coding the value. id imagine itll be needed for generalization anyway
    with open('hpl-2.3/testing/hpl.log','r') as f:

        summary_lines = f.readlines()
        summary_line = [line for line in summary_lines if "gflops" in line]
        summary_line = summary_line.split()
        gflops = summary_line[-1]

        summary_line.replace("\n", "")
        entrys = summary_line.split(" ")
        entrys = [entry for entry in entrys if entry != " "]
                

        return float(gflops)

def objective(trial, hyperparameters, runtimeparameters):
    hyperparameter_names = [name for name in hyperparameters.keys()]
    
    # Choosing hyperparameter values
    limits = {key: trial.suggest_int(key, hyperparameters[key][0], hyperparameters[key][1]) for key in hyperparameter_names}
    
    #! Do we need to bound the values of p and q to prevent them both being chosen as maximum? <-- Use runtimeparameters

    edit_HPL_dat(limits)
    run_hpl_benchmark()

    try:
        gflops= retrieve_latest_gflops()
    except:
        return 0
    

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