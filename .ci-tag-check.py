"""
If there is a tag set at the current commit, then check if it is the same as in the version file.
If not, error out.

This is done, so that the VERSION is always up to date, when a new release is build by the Travis CI,
which in turn only happens on tagged commits.
"""

import os
from pathlib import Path

current_tag = os.environ["TAG_NAME"].strip()

if not current_tag:
    print("No tag set. Proceed.")
    quit(0)

current_release_version = Path("VERSION").read_text().strip()
nightly_version = "nightly"

if current_tag not in [current_release_version, nightly_version]:
    print(f"VERSION: '{current_release_version}', TAG: '{current_tag}'")
    quit(1)
