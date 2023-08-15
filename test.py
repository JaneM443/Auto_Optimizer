varnames = ['Ns', 'NBs', 'Ps', 'Qs']

with open('HPL.dat', 'r') as file:
        lines = file.readlines()

line_indicies = []

for varname in varnames:
    for line_index, line in enumerate(lines):
        if f" {varname}" in line:
            print(f"{line_index + 1} {varname}")

    