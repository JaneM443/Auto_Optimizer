def run(data):
    
    import subprocess
    import sys
    import pickle

    bytes_like_data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    result = subprocess.run([sys.executable, "TLDR_trial.py"], input=bytes)

var_data = ("Ns", 0, 150000), ("NBs", 0, 512), ("Ps", 0, 128), ("Qs", 0, 128)
module_data = ("BLAS library", ("OpenBlas", "ClosedBlas", "BlahBlahBlas"))
runtime_data = ("Time Limit in Hours", 1.0), ("Cores per Node", 128)

data_to_send_to_TDLR = (var_data, module_data, runtime_data)

run(data_to_send_to_TDLR)