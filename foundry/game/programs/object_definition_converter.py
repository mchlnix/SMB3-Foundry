import yaml
from dataclasses import asdict
from foundry.game.ObjectDefinitions import ObjectDefinition, object_metadata, load_all_obj_definitions
"""A temporary program used to convert the legacy data.dat file into yaml"""


ORIENTATION_TO_STR = {
    0: "Horizontal",
    1: "Vertical",
    2: "Diagonal Left-Down",
    3: "Desert Pipe Box",
    4: "Diagonal Right-Down",
    5: "Diagonal Right-Up",
    6: "Horizontal to the Ground",
    7: "Horizontal Alternative",
    8: "Diagonal Weird",  # up left?
    9: "Single Block",
    10: "Centered",
    11: "Pyramid to Ground",
    12: "Pyramid Alternative",
    13: "To the Sky",
    14: "Ending",
}


def dictafy_object_definitions(obj):
    """Dirty method to convert specific classes for yaml"""
    if isinstance(obj, list) or isinstance(obj, tuple):
        new_list = []
        for item in obj:
            new_list.append(dictafy_object_definitions(item))
        return new_list
    if isinstance(obj, dict):
        new_dict = {}
        for key in obj:
            new_dict.update({key: dictafy_object_definitions(obj[key])})
        return new_dict
    if isinstance(obj, int):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, ObjectDefinition):
        d = asdict(obj)
        d["bmp"].update({"obj_generator": ORIENTATION_TO_STR[d["bmp"]["obj_generator"]]})
        d.update({"block_design": obj.block_design.blocks})
        return d


load_all_obj_definitions()
l = object_metadata.copy()
l = dictafy_object_definitions(l)
d = {i: ele for i, ele in enumerate(l)}
for key, tileset in d.items():
    d[key] = {i: ele for i, ele in enumerate(tileset)}
with open("object_definitions.yaml", "w+") as f:
    yaml.dump(d, f)




