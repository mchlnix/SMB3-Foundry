import os
import subprocess
from pathlib import Path

current_tag = os.environ["TAG_NAME"].strip()

if not current_tag:
    print("No tag set. Proceed.")
    quit(0)

if current_tag != "nightly":
    print("Not a nightly build. Proceed.")
    quit(0)

# the current commit is tagged as a nightly
# change the VERSION file to "nightly-commit" as well

version_file = Path("VERSION")

current_commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()

version_file.write_text(f"nightly-{current_commit_hash}")
