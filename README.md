# Firefox Portable Profile Fix  
Python script that fixes Firefox browser profile migration.  
This script fixes addon related paths in addonStartup.json.lz4 and extensions.json files.  
AddonStartup.json.lz4 unpack function was taken from here - https://github.com/digitalsleuth/pyson4

The standalone exe compilation was done with pyinstaller.

usage: `-profile <profile dir> -app <app path>`
  
options:  
  `-app <app path>`           Path to firefox.exe or any firefox-based browser  
  `-profile <profile dir> `   Path to firefox profile  

sample:  
 `main.py -app "C:\Program Files\Mozilla Firefox\firefox.exe" -profile "C:\profiles\Default"`
