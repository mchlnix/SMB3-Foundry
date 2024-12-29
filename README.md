# A modern Super Mario Bros. 3 Level Editor

[![YouTube Video of Version 1.0](https://i.imgur.com/ZQXDyCr.png)](https://youtu.be/7_22cAffMmE)
YouTube Video of 1.0 Beta Version

## Downloads

SMB3 Foundry Level Editor: <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/linux-smb3-foundry">Linux</a>, <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/win64-smb3-foundry.exe">Windows</a>, <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/osx-smb3-foundry">OSX</a>  
SMB3 Scribe Overworld Editor: <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/linux-smb3-scribe">Linux</a>, <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/win64-smb3-scribe.exe">Windows</a>, <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/osx-smb3-scribe">OSX</a>  
Manuals: <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/manual-foundry.pdf">SMB3 Foundry</a>, <a href="https://github.com/mchlnix/SMB3-Foundry/releases/download/1.4/manual-scribe.pdf">SMB3 Scribe</a>

## Features right now

 - Level selection
 - Level view
 - Block Viewer
 - Object-Viewer
 - Loading/Saving of levels
 - Zooming
 - Select, Move and Remove multiple Objects
 - Copy/Cut/Paste Objects
 - Supports editing Vertical Levels
 - Undo/Redo System
 - Change Palettes, Music and Jumps to other Levels
 - Play any level directly, without having to overwrite your ROM
 - Make screenshots of your Level

## To come

 - Better interface concerning level size

## Not planned right now

 - Support of other versions, other than the US release

## Contact

Come to the [SMB3 Romhacking Discord](https://discord.gg/pm87gm7) and message Michael.

## How to run

### The Easy Way
You can use the executables in the [Releases](https://github.com/mchlnix/SMB3-Foundry/releases) tab on Github under **Assets**. Those should work out of the box.

Alternatively you can try the methods below.

### Windows

1. You need to have at least Python 3.10 (3.11 recommended) installed. To do that, go to
https://www.python.org/downloads. Make sure to tick the box "Add Python to
Path"!
2. You need to install the Qt for Python GUI framework. To do that, open a command
prompt (search cmd in Windows) and type in `pip install -r requirements.txt`. This should work automatically.
3. Click on smb3-foundry.py and the level editor should open up, asking you to
select the ROM you want to load. Preferably the US version of SMB3 or a Hack
based on it.

### Linux

1. The `python3` package should already be installed on your system. If not then do it using your distributions package manager.
2. Install `python3-pip` using the package manager as well.
3. Install the dependencies, using `pip3 install -r requirements.txt`.
4. You can start the level editor using `python3 smb3-foundry.py` using the terminal.
