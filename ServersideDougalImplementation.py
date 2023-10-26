import os
import pickle

USE_LOCAL_DATA = True #Means Dougal input not required so only change if you know what you're doing

if USE_LOCAL_DATA:

    #! Time data will need to be in hh:mm:ss format

    data = ({'Ns': [115000, 115000], 'Ps': [2, 24]}, {'BLAS Modules': ['openblas'], 'MPI Modules': ['intelmpi'], 'Compilers': ['intel']}, {'Max Runtime In Hours': ["12:00:00"], 'Number Of Nodes': [1], 'Cores Per Node Input': [24], 'Memory Per Node GB': [120], 'Number Of Trials' : [1000]})

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)

os.system("python3 start_TLDR.py data.input")