from smb3parse.constants import Constants, reset_global_offsets


def test_reset_to_defaults():
    assert Constants.Airship_Layouts == Constants._Airship_Layouts

    old_value = Constants.Airship_Layouts

    assert Constants._Airship_Layouts == old_value

    Constants.Airship_Layouts += 1

    assert Constants._Airship_Layouts == old_value

    assert Constants.Airship_Layouts != old_value

    reset_global_offsets()

    assert Constants.Airship_Layouts == old_value
