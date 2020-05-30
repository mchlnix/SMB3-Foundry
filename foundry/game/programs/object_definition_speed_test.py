import numpy
import perfplot

import json
import yaml
from yaml import Loader, CLoader
import pandas
"""File for testing various methods of loading yaml files"""


def setup(n):
    data = numpy.random.rand(n, 3)

    with open('out.yml', 'w') as f:
        yaml.dump(data.tolist(), f)

    #with open('out.json', 'w') as f:
    #    json.dump(data.tolist(), f, indent=4)

    #with open('out.dat', 'w') as f:
    #    numpy.savetxt(f, data)

    return


def yaml_python(arr):
    with open('out.yml', 'r') as f:
        out = yaml.load(f, Loader=Loader)
    return out


def yaml_c(arr):
    with open('out.yml', 'r') as f:
        out = yaml.load(f, Loader=CLoader)
    return out


def json_read(arr):
    with open('out.json', 'r') as f:
        out = json.load(f)
    return out


def loadtxt(arr):
    with open('out.dat', 'r') as f:
        out = numpy.loadtxt(f)
    return out


def pandas_read(arr):
    out = pandas.read_csv('out.dat', header=None, sep=' ')
    return out.values


perfplot.show(
    setup=setup,
    kernels=[
        yaml_python, yaml_c
        ],
    n_range=[2**k for k in range(18)],
    logx=True,
    logy=True,
    )