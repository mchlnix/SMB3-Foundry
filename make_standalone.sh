#!/bin/bash -e

ARCHIVE_NAME="SMB3-Foundry-Linux"
FOLDER="$HOME"
TARGET="$FOLDER/$ARCHIVE_NAME"

[[ -e "$TARGET" ]] && rm -r "$TARGET"
[[ -e "$TARGET.zip" ]] && rm -r "$TARGET.zip"

mkdir "$TARGET"

pyinstaller smb3-foundry.spec

cp dist/smb3-foundry "$TARGET"
cp README.md "$TARGET"

pushd ${FOLDER}
zip "$ARCHIVE_NAME.zip" -r "$ARCHIVE_NAME" 
popd
