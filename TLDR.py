import optuna
import subprocess
import pickle
import sys
import os

# Location of important hyperparameters
lines = {
    'n': 6,
    'p': 11,
    'q': 12,
    'nb': 8,
}

def main(data):
    variable_data, module_data, runtime_data = data

    if not os.path.exists("hpl-2.3/"):

        slurm_script_path = 'SLURM/setup.slurm'
        #Run the SLURM script directly
        try:
            subprocess.run(['bash', slurm_script_path], check=True)
            print("SLURM script executed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error executing SLURM script:", e)

    study = optuna.create_study(direction = "maximize",pruner=optuna.pruners.MedianPruner())
    study.optimize(objective, n_trials=10)

    print('Best Parameters:')
    best_params = study.best_params
    print(best_params)

def edit_HPL_dat(limits,hyper_parameters):

    for parameter in hyper_parameters:
        with open('hpl-2.3/testing/HPL.dat', 'r') as f:
            hpl_input = f.readlines()

        line = hpl_input[lines[parameter] - 1]
        old = ""
        for i in line:
            if i == " ":
                break
            old += i
        hpl_input[lines[parameter] - 1] = line.replace(old, str(limits[parameter]))
        with open('hpl-2.3/testing/HPL.dat', 'w') as f:
            f.writelines(hpl_input)

def run_hpl_benchmark():

    shell_script = "SLURM/run_hpl.slurm"
    try:
        subprocess.run(["bash", shell_script], check=True)
        print("SLURM script executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing SLURM script:", e)

def retrieve_latest_gflops():

    with open('hpl-2.3/testing/hpl.log','r') as f:

        summary_line = f.readlines()[38]
        gflops = summary_line.split()[-1]

        return float(gflops)

def objective(trial):

    # Hard coded Suggested limits
    hyper_parameters = ['n','p','q','nb']

    # Set values within a range for each hyperparameter each trial
    limits = {
        'n' : trial.suggest_int('n', 0, 1000),
    }

    p = trial.suggest_int('p', 1, 4)
    q = trial.suggest_int('q', 1, 3)
    nb = trial.suggest_int('nb', 1, 6)

    limits['nb'] = 2 ** nb
    limits['p'] = 2 ** p
    limits['q'] = 2 ** q

    edit_HPL_dat(limits,hyper_parameters)
    run_hpl_benchmark()

    try:
        gflops= retrieve_latest_gflops()
    except:
        return 0
    

    if trial.should_prune():
        raise optuna.exceptions.TrialPruned()

    return gflops

if __name__ == "__main__":

    FILE_PATH = sys.argv[1]

    with open(FILE_PATH, "rb") as file:
        data = pickle.load(file)

    main(data)                  