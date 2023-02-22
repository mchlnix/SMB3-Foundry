import json

from smb3parse.util.parser import FoundLevel


def test_found_level_json():
    found_level = FoundLevel([123, 234], [234, 345], 1, 234, 567, 5, 50, True, False, True)

    as_json = json.dumps(found_level.to_dict())

    recovered_found_level = FoundLevel.from_dict(json.loads(as_json))

    assert recovered_found_level == found_level
