import optuna
import subprocess
import pickle
import sys
import os
import logging
import typing
from typing import Any, List, Dict, Tuple

def find_parameter_locations(file_path, parameter_names):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        print(line)

def load_logger():
    #----------------------------------------------
    AUTO_CLEAR = True
    logging.basicConfig(
        filename = "output.log",
        level = logging.DEBUG,
        filemode = 'a' if AUTO_CLEAR == False else 'w',
        format = "%(levelname)s | %(asctime)s | '%(message)s' | %(funcName)s%(args)s @ line %(lineno)d in %(filename)s from %(module)s | StackInfo : %(stack_info)s | ProcessInfo : %(processName)s(%(process)d) | ThreadInfo : %(threadName)s(%(thread)d)")

    logging.info("Logger Loaded")
    #----------------------------------------------

def main(data) -> None:
                     # dict[param_name: tuple[param_minimum, param_maximum]]
    hyperparameters  : Dict[str       : Tuple[Any          , Any          ]] = data[0]

                     # dict[module_type: list[module1, ...]]
    moduledata       : Dict[str        : List[str    , ...]] = data[1]

                     # dict[parameter_name: parameter_value]
    runtimeparameters: Dict[str           : Any            ] = data[2]

    #----------------------------------------------

    hyperparameter_names = [name for name in hyperparameters.keys()]
    hyperparameter_locations = find_parameter_locations(file_path = "HPL.dat", parameter_names = hyperparameter_names)

        #!!! best practice to zero index the lines
    # lines = {
    # 'n': 6 -> 5,
    # 'p': 11 -> 10,
    # 'q': 12 -> 11,
    # 'nb': 8 -> 7,
    # }
    # Same as above just more general
    
    # Location of important hyperparameters
    lines = {key : value for key, value in zip(hyperparameter_names, hyperparameter_locations)}

    

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
    study.optimize(objective, n_trials=10)

    best_params = study.best_params
    print('Best Parameters:')#Leaving in for the moment. must be moved to an output script :)
    print(best_params)

def edit_HPL_dat(limits,hyper_parameters):

    for parameter in hyper_parameters:
        with open('hpl-2.3/testing/HPL.dat', 'r') as f:
            hpl_input = f.readlines()

        line = hpl_input[lines[parameter]]
        old = ""
        for i in line:
            if i == " ":
                break
            old += i
        hpl_input[lines[parameter]] = line.replace(old, str(limits[parameter]))
        with open('hpl-2.3/testing/HPL.dat', 'w') as f:
            f.writelines(hpl_input)

def run_hpl_benchmark():
    shell_script = "SLURM/run_hpl.slurm"
    
    try:
        subprocess.run(["bash", shell_script], check=True)
        logging.debug("SLURM script executed successfully.")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing SLURM script: {e}")

def retrieve_latest_gflops(): #likely more robust to search instead of hard coding the value. id imagine itll be needed for generalization anyway
    with open('hpl-2.3/testing/hpl.log','r') as f:

        summary_line = f.readlines()[38]
        gflops = summary_line.split()[-1]

        return float(gflops)

def objective(trial, hyperparameters, runtimeparameters):
    hyperparameter_names = [name for name in hyperparameters.keys()]
    hyperparameter_ranges = [parameter_range for parameter_value in hyperparameters.values()]
    
    # Set values within a range for each hyperparameter each trial
    # limits = {
    #     'n' : trial.suggest_int('n', 0, 1000),
    #     'p' = trial.suggest_int('p', 1, 4)
    #     'q' = trial.suggest_int('q', 1, 3)
    #     'nb' = trial.suggest_int('nb', 1, 6)
    # } 
    
    # Same done below just more general
    limits = {key: trial.suggest_int(key, hyperparameters[key][0], hyperparameters[key][1]) for key in hyperparameter_names}

    limits['nb'] = 2 ** 8 #512
    limits['p'] = runtimeparameters['number_of_nodes'] * runtimeparameters['number_of_cores']
    limits['q'] = runtimeparameters['number_of_nodes'] * runtimeparameters['number_of_cores']

    edit_HPL_dat(limits,hyper_parameters)
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
    except Exception as exception:
        logging.critical(f"Error with loading Dougal data: {type(exception).__name__} - {exception}")
        raise Exception

    main(data)                  