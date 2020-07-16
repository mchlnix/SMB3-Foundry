import pickle

from foundry import data_dir

with open(data_dir.joinpath("sprite_loader/objects.pickle"), "rb") as f:
    object_definitions = pickle.load(f)
print(object_definitions)