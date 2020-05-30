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
$ pip3 install PySide2
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
    4 - Optional 4th byte denoting additional length, 8 Bit / 1 Byte

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

Jumps are a third kind of object. They are the exclusive object type of the 8th domain (domain 7) and are used in Pipes or Doors to transport a player to a different level.

    dddu_ssss aaaa_yyyy xxxx_xxxx
    
    d - Domain, always 111 in binary, meaning 7, 3 Bit
    u - Unused, 1 Bit
    a - Number describing the action Mario enters the level with, 4 Bit
    y - Number describing a possible y position Mario enters the level from, 4 Bit
    x - X position Mario enters the level from, 8 Bit / 1 Byte
    
##### Exit Action

Mario has a few exit actions, like exiting from a pipe, exiting from a door, sliding into the level and more. This number describes one of these animations. It makes sense to take an action that is appropriate depending on how he exited the last level, but it is not mandatory.

##### Y Position

The y position at which Mario appears in the new level. Note that this is not the specific position, but rather points to an entry in a list of 16 different y coordinates.

8 of these can be used for horizontal levels and 8 for vertical levels. Y coordinates other than the ones in the list can not be chosen, without hacking the rom manually.

##### X Position

The x coordinate, however, can be chosen freely. Of note is, that the two 4 Bit groups are flipped before using. That means, if the coordinates would be saved in decimal, that the x coordinate 21 would be saved as 12 in the ROM.

In the same way the hexadecimal representation of the x coordinate 100, 0x64, is saved in memory as 0x46.

### World Maps

World maps, or overworlds, are used to enter the levels (in most cases). The data for world maps is organized in a data structure, separate from its layout information.

#### Layout information

Since all world maps share an object set (object set 0), and every object on the world map is made up of single 16x16 blocks, the layout data does not need to be specially constructed. Instead the blocks IDs are simply stored in memory in the order they would appear in on the screen. This makes reading and parsing a world map particularly simple.

Each block ID is simply a byte, without any further information like coordinates, length, etc. 

The animation of some of the tiles is not part of the world map itself, rather their block IDs is used in a different routine and, if it is marked in that list as "animatable" a lookup will periodically exchange the normal block with animated versions of itself.

##### Screen count

How many screens a world map has, is implicitly encoded in the amount of layout bytes, that the layout consists of. It takes 16 * 9, so 144 bytes to fill one screen, so all world maps have a multiple of that many bytes in the layout data. The maximum amount of screens is 4.

#### Data structure

The data structure holds information about the positions and memory locations of the levels, among others. They are mostly organized in lists of bytes, which, for each screen, hold some part of the necessary level information.

- how many level entries are in each screen (level counts for screens, that are unused are simply 0)
- the row position and object set of every level (4 bit row, 4 bit object_set)
- the screen and column position for every level (4 bit screen, 4 bit column)
- addresses pointing to the enemy and item data of the level, that corresponds to the coordinates at the same index (the first address in the list is for the level at the first row and first column in their respective lists)
- addresses pointing to the level layout data of the level, that corresponds to the coordinates at the same index

See also [Level Loading](#Level-Loading)

### Levels

#### Object Set

#### Level Header

#### Layout Data

#### Enemy and Item data

## Mechanisms

### Level Loading

When the player stands in a location on the world map and presses the A button, the ROM will first do a check, if the block the player is standing on is marked as "enterable".

If this is the case, then the position of the player is split up into its screen, row and column value.

Afterwards the world data structure is looked up to find the corresponding lists for the world and screen.

The list of rows and object sets is traversed first, while keeping track of the index (the current position in the list). Once an entry is found, that has the same row value as the player currently has, the search is stopped. Now the search is continued in the column list, starting from the index we were at in the row list.

This works, because the row list is in normal numerical order, meaning levels at the top of the screen are listed first, while the column list is sorted from left to right, with the caveat, that levels on the same row are grouped together.

That means, that in the column list, first all levels in the first row are listed from left to right, then the ones from the second row, etc. This allows us to first find the position in the row list, marking the start of the row we are standing on and then, searching from left to right, find the level which has the column value we are looking for.

After finding the entry in column list, which corresponds to the column of the player, its position is the actual position of the level we are looking for in all of the lists.

We go again into the row list, find the correct row + object set pair, instead of the first matching, and store the object set of our level. Afterwards we go into the enemy and item data list and retrieve the address for the data, corresponding to our level. The same is done for the layout data list and we have the 3 pieces of information, that is necessary to load and build the level we want to go to.

#### Special Case Warp World

In Warp World the data structure works a bit different. While the row and column lists work the same way, here the second half of the row values are not denoting the object set, but the world to jump to.

After selecting a level, but before loading it, the current world is checked. If it is the value 8 (so World 9), then, instead of loading the level like normal, the target world is written into a special variable and the execution jumps back to where the warp world code executed to initiate the jump.
