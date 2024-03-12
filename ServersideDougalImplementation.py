import os
import pickle

###-------------------------------------------------------------------------###
### User interacts here to change run parameters                            ###
###-------------------------------------------------------------------------###

USE_LOCAL_DATA = True # The HPL data is defined here

if USE_LOCAL_DATA:

    """
    ###---------------------------------------------------------------------###
   
    Manually defines the trial data
    
    : param              Ns : Matrix size range
    : param              Ps : Process grid size range
    : param            BLAS : BLAS Module
    : param             MPI : MPI Module
    : param        Compiler : Compiler Module
    : param         Runtime : Max runtime for the SLURM job in hh:mm:ss
    : param           Nodes : Number of nodes for each trial
    : param  Cores per Node : Cores per node
    : param Memory per Node : Memory per node
    : param          Trials : Number of trials
    
    ###---------------------------------------------------------------------###
    """

    data = ({'Ns': [230000, 260000], 
             'Ps': [16, 32]
            }, 
            {'BLAS'     : ['openblas'], 
             'MPI'      : ['openmpi'], 
             'Compiler' : ['gcc']
            }, 
            {'Max Runtime In Hours' : ["72:00:00"], 
             'Number Of Nodes'      : [4], 
             'Cores Per Node'       : [128], 
             'Memory Per Node GB'   : [128], 
             'Number Of Trials'     : [1]
            }
            )

    # Passes data to a pickle file, for TLDR to import

    with open("data.input", "wb") as data_file:
        pickle.dump(data, data_file, protocol = 4)


os.system("python3 start_TLDR.py data.input") # Calls start_TLDR