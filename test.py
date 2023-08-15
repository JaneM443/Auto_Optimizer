varnames = ['Ns', 'NBs', 'Ps', 'Qs']

with open('auto_optimizer/HPL.dat', 'r') as file:
        lines = file.readlines()

line_indicies = []

for varname in varnames:
    for line_index, line in enumerate(lines):
        print(f"{line_index} : {varname} : {varname in line}")

    