import os
import pickle

USE_LOCAL_DATA = True #Means Dougal input not required so only change if you know what you're doing

if USE_LOCAL_DATA:

    #! Time data will need to be in hh:mm:ss format

    data = ({'Ns': [150, 200], 'Ps': [1, 12]}, {'BLAS Modules': ['openblas'], 'MPI Modules': ['openmpi'], 'Compilers': ['intel']}, {'Max Runtime In Hours': ["12:00:00"], 'Number Of Nodes': [1], 'Cores Per Node Input': [12], 'Memory Per Node GB': [128], 'Number Of Trials' : [100]})

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)

os.system("python3 start_TLDR.py data.input")