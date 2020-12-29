from foundry import data_dir
import yaml

variables = {}
path = data_dir.joinpath("smb3.txt")

with open(path) as fp:
    for cnt, line in enumerate(fp):
        line = line.split(';')[0]
        line = line.replace(" ", "")
        if line == "":
            continue
        try:
            key, item = line.split('=')
        except ValueError:
            print(line, "is not a variable")
            continue
        try:
            item = int(item[2:], 16)
        except IndexError:
            print(item, "is not a hex value")
            continue
        variables.update({key: item})

with open("../../../data/smb3_variables.yaml", "w+") as f:
    yaml.dump(variables, f)
