#!/usr/bin/env python3
import builtins
import gettext
import glob
import os
import subprocess
import sys
from pathlib import Path


DOMAIN = "smb3"
LOCALE_DIR = Path(__file__).parent / "locale"

translation = gettext.translation(
    DOMAIN,
    localedir=str(LOCALE_DIR),
    fallback=True
)
builtins.__dict__["_"] = translation.gettext

def run(command):
    subprocess.check_call(command, shell=True)

def extract():
    found_files = glob.glob("**/*.py", recursive=True)
    file_list = " ".join(found_files)

    print(f"Extracting domain ({len(found_files)} files found)")
    run(f"xgettext --from-code=UTF-8 --add-comments=TRANSLATORS -o locale/smb3.pot {file_list}")

def merge():
    print(f"Merging domain")
    for po_file in LOCALE_DIR.glob(f"*/LC_MESSAGES/smb3.po"):
        run(f"msgmerge -U {po_file} locale/smb3.pot")

def compile():
    print(f"Compiling domain")
    for po_file in LOCALE_DIR.glob(f"*/LC_MESSAGES/smb3.po"):
        mo_file = po_file.with_suffix(".mo")
        run(f"msgfmt {po_file} -o {mo_file}")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "help"

    if action == "extract":
        extract()

    elif action == "merge":
        merge()

    elif action == "compile":
        compile()

    elif action == "update":
        extract()
        merge()
        compile()

    else:
        print("Usage: python i18n.py [extract|merge|compile|update]")
