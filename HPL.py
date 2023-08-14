class HPL:
    def __init__(limits,hyper_parameters):
        self.lines = {
            'n': 6,
            'p': 11,
            'q': 12,
            'nb': 8,
            }
        self.limits = {}
    
    def setupt_HPL_file():
        pass

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

    def run_HPL_benchmark():

        shell_script = "run_hpl.slurm"
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