# SMB3Foundry User Manual

This document is supposed to help new users take their first steps using this Super Mario Bros. 3 (SMB3) Level editor. It will explain core concepts of SMB3 hacking, but is not meant to be an exhaustive resource on that topic.

## What is this?

This editor takes a ROM file of the Nintendo Entertainment System (NES) game Super Mario Bros. 3 and allows the user to edit the level, change their order, appearance, music etc.

This leads to something called a "ROM hack", which describes an altered game with user created content, packaged like the original, so other users can play it in an emulator or even the original hardware, as if it was released 30 years ago.

In short you can make your own version of Super Mario Bros. 3.

## What is a ROM?

A ROM in this context is a file, that contains all the game data of a particular game. This includes the game logic, the graphics, the level data, music and everything else.

ROM means Read Only Memory. This originally describes a kind of memory chip, that can only be written to once (in the factory, burning the game onto it), and is subsequently read from everytime the game is played inside a console.

All the information that is on this ROM chip is read out bit by bit and stored in the ROM file, so emulators and editors can work with and store data in it, just as it was/would've been on the original memory chip.

## How does a ROM editor work?

To be able to change the layout of a level or the graphics of a sprite an editor needs to understand the format this information is stored in the ROM in. Additionally editors need to know where to look for the data, so the locations of the levels in memory need to be known, beforehand.

Luckily community members found out and wrote down the addresses of all the levels in the original SMB3, the location of the graphic data and more, which makes it easier to find, read and parse this data.

More advanced editors will incorporate knowledge of the program code, for example how levels are loaded, how the game knows where to find them, or how it makes actual items out of graphics data and code. This allows them to add new levels, move them around and add new jumps to other levels.

The specific features of an editor are highly dependent on the game it is made for. Since most NES games are different in how their memory is used, stored and interpreted, every game needs its own editor made specifically for it.

## Installation

The editor is packages as a single file executable for Windows, Linux and Mac, which you can download from the [Releases](https://github.com/mchlnix/SMB3-Foundry/releases) tab. 

The Linux version is the definitive version, since that is what the developer is using to develop it, but since the underlying technology is platform independent, there shouldn't be any big incompatibilities between the versions.

### The easy way

The easiest way is using the single executable for your operating system. You might have to give it executable rights on Linux and Mac, which is done using the terminal.

```shell script
$ chmod 755 linux-smb3-foundry
```

or

```shell script
$ chmod 755 osx-smb3-foundry
```

After that a double click should be enough to start the editor.

### The interesting way

The editor is written in the programming language Python, specifically version 3.6. If your system has this programming language available you could also download the source code directly as a .zip file and execute the editor, using

```shell script
$ python3 --version
Python 3.6.8
$ python3 foundry/smb3-foundry.py
```

Note that you need to install the graphical user interface framework, that the editor uses. This is easily done using `pip3`, which should already be installed, when having installed Python.

```shell script
$ pip3 install wxPython 
```

## Getting a ROM

As described above, the editor needs to have a ROM file of Super Mario Bros. 3 to load the graphics and level structures, etc. This editor does not come with such a file, since this would mean distributing a game, for which the developer does not hold the copyright.

You can buy specialty hardware and "dump" the contents of an actual SMB3 cartridge you own into a ROM file. This counts as a private backup, which should be legal.

Or find someone who dumped the contents of a real ROM memory chip and uploaded it onto the internet. While this is how most people do it and definitely easier, it is technically software piracy and therefore illegal, regardless of SMB3 being more than 30 years old.

Also make sure, that you have a ROM file of the North American release of SMB3, as it is currently the only supported version.

## Terminology

### Memory addresses and hexadecimal numbers

The ROM of SMB3 is almost 400,000 bytes long. In there are levels, specific graphics and music tracks. When the game wants to load Level 1-1, upon the player entering it, it needs to know which bytes among the many thousand make up the level and its objects. Thes is done by encoding a memory address.

Since technically every byte in the ROM could mean something important, such an address would be a very large number. In the computing world such memory addresses are often shown as hexadecimal numbers. These are numbers decoded not in ten possible digits, but in sixteen deploying the usual digits 0-9 with the addition of A-F. This leads to shorter addresses and easier reasoning about the underlying bytes. They are often identified by the prefix of "0x".

Since one digit in a hexadecimal number can hold up to sixteen values, it holds the same information as 4 bits or half a byte, meaning that all values one byte can hold can be displayed between 0x00 and 0xFF.

Most beginner and intermediate users don't need to understand the addresses however and can simply ignore them or copy them into the editor, when finding them in the readme of a ROM hack they want to edit.

### Objects

A level consists of objects, with most of them being visible on screen and placed at specific x and y coordinates inside the level. Note that the (0, 0) origin is not at the bottom left corner of the screen, but rather, like most graphical systems, in the upper left corner.

The objects of a level are stored one after the other in the ROM. When the level is supposed to be loaded, the game reads in the first object, determines whether or not it is 3 or 4 bytes long, reads in the rest and displays it. This continues with the next object, until a magic value is read in, that denotes the end of this specific level.

#### Object set

Not all objects can be displayed in a level at the same time however, level makers need to decide on one of 12 object sets, that their level is going to use. While some objects, like pipes, doors and coin blocks, are available in all object sets, other objects, like pyramids in the "desert" object set and ice blocks in the "ice" object set, are only available in specific object sets.

That is also the reason, why changing the object set of a level might break certain parts. Objects in different objects sets might have the same ID, but not both be 3 bytes long, for example. This can lead to the game wrongly expecting a 4 byte object and reading in a 3 byte object and the first byte of the next object. Obviously this leads to unintended behaviour and at worst to the game crashing.   
  
#### Level object

Level objects are things like platforms, clouds, coin blocks, background graphics and in general every non-interactive component that makes up a levels scenery. These are either 3 or 4 byte long each. They consist of a domain, an identifying number a position and, in case of a 4 byte object, an additional byte denoting some kind of length, be it height or with.

An example of a 4 byte object is the ground in Level 1-1, the value of the fourth byte determines the width of the ground object.

    dddy_yyyy xxxx_xxxx iiii_iiii 4444_4444
    
    d - Domain, 3 Bit
    y - Y position in the level, 5 Bit
    x - X position in the level, 8 Bit / 1 Byte
    i - Object ID, 8 Bit / 1 Byte
    4 - optional 4th byte denoting additional length, 8 Bit / 1 Byte

##### Domain

The domain describes one of 8 sub groups inside an object set. This was used to allow more objects to be put into an object set, than one ID byte would allow. With the 3 domain bits and the 8 ID bits, 2^11 or 2048 objects could fit into one object set. In reality it is much less than that however with the domains being used more to group objects by functionality or attributes.

Pipes and coin blocks, for example, are usually found in the first domain (Domain 0), while jumps to other levels are exclusively found in the 8th domain (domain 7).

##### ID

This value describes the ID of an object. Some objects, like the large group of bushes in Level 1-1 have a single ID, other objects, like coin blocks have 16 different IDs. This is used for some objects, that can have different widths or heights. A single coin block might have the ID 0x20, while 0x24 describes 5 coin blocks next to each other. This means that at most 16 coin blocks can be described as a single coin block object.

##### Additional length

Some objects need a length in 2 directions. For example the ground in Level 1-1. While its normal object ID describes how tall the ground object is, meaning how much of it is drawn downwards, the additional 4th byte describes its length. This was necessary to have ground objects that can be wider than 16 blocks. 

In theory, the 4th byte allows a ground object that is 2^8 so 256 blocks long, or the entire length of the longest SMB3 level. 

#### Enemies & Item

Enemies and Items, or generally objects the player can interact with, are part of a special object set, that all levels share. They are always 3 bytes long and are structured slightly different than level objects.

    iiii_iiii xxxx_xxxx yyyy_yyyy

    i - Object ID, 8 Bit / 1 Byte
    x - X position in the level, 8 Bit / 1 Byte
    y - Y position in the level, 5 Bit
    
They are also not following the level object in memory, but are stored separately. This may have been so multiple levels, like Bonus levels or Hammer Bros stages, which may repeat in multiple worlds, can share enemy/item data and save space on the ROM chip, which was incredibly expensive compared to todays memory prices.

#### Jumps

Jumps are a third kind of object. They are the exclusive object type of the 8th domain (domain 7) and are used in Pipes to transport a player to a different level.

    dddu_ssss aaaa_yyyy xxxx_xxxx
    
    d - Domain, always 111 in binary, meaning 7, 3 Bit
    u - unused, 1 Bit
    a - a number describing the action Mario enters the level with, 4 Bit
    y - a number describing a possible y position Mario enters the level from, 4 Bit
    x - X position Mario enters the level from, 8 Bit / 1 Byte
    
##### Exit Action

Mario has a few exit actions, like exiting from a pipe, exiting from a door, sliding into the level and more. This number describes one of these animations. It makes sense to take an action that is appropriate depending on how he exited the last level, but it is not mandatory.

##### Y Position

The y position at which Mario appears in the new level. Note that this is not the specific position, but rather points to an entry in a list of 16 different y coordinates.

8 of these can be used for horizontal levels and 8 for vertical levels. Y coordinates other than the ones in the list can not be chosen.

##### X Position

The x coordinate, however, can be chosen freely. Of note is, that the two 4 Bit groups are flipped before using. That means, if the coordinates would be saved in decimal, that the x coordinate 21 would be saved as 12 in the ROM.

In the same way the hexadecimal representation of the x coordinate 100, 0x64, is saved in memory as 0x46.

### Levels

TODO