# Port/Reimplementation of SMB3 Workshop by hukka

[![YouTube Video of Version 0.9](https://img.youtube.com/vi/NSQnIYQT5Go/0.jpg)](https://www.youtube.com/watch?v=NSQnIYQT5Go)  
YouTube Video of Version 0.9, check [Releases](https://github.com/mchlnix/SMB3-Foundry/releases) for more current versions

## Features right now

 - Level selection
 - Level view
 - Block Viewer
 - Object-Viewer
 - Loading/Saving of levels/world maps
 - Zooming
 - Selection of multiple objects
 - Copy/Cut/Paste objects
 - Vertical Levels
 - Undo/Redo System
 - Instant Header Editing
 - Jump (Level pointer) editing
 - Make screenshots of your Level

## To come

 - Smoothing out the rough edges
 - Pretty much the rest of SMB3 Workshops features
 - Cleaner architecture
 - dynamic level sizes

## Not planned right now

 - Support of other versions, other than the US release
 
## Contact

Come to the [SMB3 Romhacking Discord](https://discord.gg/pm87gm7) and message Michael.

## How to run

### The Easy Way
You can use the editions in the [Releases](https://github.com/mchlnix/SMB3-Foundry/releases) tab on Github under **Assets**. Those should work out of the box.

Alternatively you can try the methods below.

### Windows

1. You need to have at least Python3.6 installed. To do that, go to
https://www.python.org/downloads. Make sure to tick the box "Add Python to
Path"!
2. You need to install the wxPython GUI framework. To do that, open a command
prompt (search cmd in Windows) and type in `pip install wxpython`. This should work automatically.
3. Click on smb3foundry.py and the level editor should open up, asking you to
select the ROM you want to load. Preferably the US version of SMB3 or a Hack
based on it.

### Linux

1. The `python3` package should already be installed on your system. If not then do it using your distributions package manager.
2. Install `python3-pip` using the package manager as well.
3. Install the GUI framework, using `pip install wxpython`. Maybe you need to use `pip3` instead.
4. You can start the level editor using `python3 smb3-foundry.py` using the terminal.
