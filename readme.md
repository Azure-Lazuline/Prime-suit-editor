## Metroid Prime suit editor
by Azure Lazuline
v1.0.0

This makes a set of custom textures to load into Dolphin for custom suits in Prime 1.
Eventually i hope to get it integrated into Randovania, but for now it's standalone.

This program only works for NTSC version 1.0 on Gamecube (GM8E01).


### Instructions

Run gui.py (or the Windows standalone executable), and the interface should be pretty
self-explanatory. You can save and load full sets of suits as a file, or copy
individual ones to your clipboard (to paste into another suit, or share it with
others).

Click "Export textures" when you're done, and select Dolphin's "User" directory so it
knows where to put the files. You can find it with "File -> Open User Folder" in
Dolphin. On Windows, this is most likely in AppData, but it can vary depending on
settings and OS.

Any time you change the colors, a set of preview images gets created in the "saved"
subdirectory (which is where your settings and saved palettes get put by default
too). I figured i'd expose them in case it's useful to show people your new suits!


### Known issues

Some of the morph ball colors like the internal energy aren't accessible through
textures, so it'd need a more extensive hack to change them. This means some of the
color settings do nothing currently, but i wanted to include them for future
compatibility.
