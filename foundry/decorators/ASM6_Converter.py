import yaml
from yaml import CLoader as Loader
from foundry import data_dir


with open(data_dir.joinpath("smb3_variables.yaml")) as f:
    variables = yaml.load(f, Loader=Loader)


def to_int(input):
    if isinstance(input, str):
        if input.startswith('$'):
            input = input[1:]
            if input in variables:
                return variables[input]
            else:
                try:
                    return int(input, 16)
                except ValueError:
                    return input
        else:
            try:
                return int(input)
            except ValueError:
                return input
    else:
        return input


class ASM6ToInt:
    """Converts ASM6 strings to their int counterparts"""
    def __init__(self, func):
        self.function = func

    def __call__(self, *args, **kwargs):
        result = self.function(*[arg.to_int() for arg in args], **{k: arg.to_int() for k, arg in kwargs.items()})
        return result


