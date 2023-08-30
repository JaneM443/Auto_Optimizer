import os
import pickle

USE_LOCAL_DATA = True #Keep this true Until I say so. Means Dougal input not required so only change if you know what youre doing

if USE_LOCAL_DATA == True:
    data = ({'Ns': [1000, 10000], 'NBs': [64, 256], 'Ps': [1, 8], 'Qs': [1, 8]}, {'BLAS Modules': ['openblas'], 'MPI Modules': ['openmpi'], 'Compilers': ['gcc']}, {'Max Runtime In Hours': [3.0], 'Number Of Nodes': [12], 'Cores Per Node Input': [12], 'Memory Per Node GB': [12]})

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)

os.system("python3 TLDR.py data.input")