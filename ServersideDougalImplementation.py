import os
import pickle

USE_LOCAL_DATA = True #Keep this true Until I say so. Means Dougal input not required so only change if you know what youre doing

if USE_LOCAL_DATA == True:
    data = ({'Ns': [1, 2], 'NBs': [1, 2], 'Ps': [1, 2], 'Qs': [1, 2]}, {'BLAS Modules': ['a'], 'MPI Modules': ['a'], 'Compilers': ['a']}, {'Max Runtime In Hours': [12.0], 'Number Of Nodes': [12], 'Cores Per Node input': [12], 'Memory Per Node GB': [12]})

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)

os.system("python3 start_TLDR.py data.input")