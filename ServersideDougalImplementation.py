import os
import pickle

# Keep this true Until I say so - Means Dougal input not required 

USE_LOCAL_DATA = True 

if USE_LOCAL_DATA == True:

    #! Time data will need to be in hh:mm:ss format

    data = ({'Ns': [1000, 10000], 'NBs': [64, 256], 'Ps': [1, 128], 'Qs': [1, 128]}, {'BLAS Modules': ['openblas'], 'MPI Modules': ['openmpi'], 'Compilers': ['gcc']}, {'Max Runtime In Hours': ["03:00:00"], 'Number Of Nodes': [1], 'Cores Per Node Input': [128], 'Memory Per Node GB': [256]})

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)

os.system("python3 start_TLDR.py data.input")