# hashbackup

The script is designed to generate sha1 checksums for every file in the source directory, to make a backups from this directory to another one and compare these checksums later. The script don't use subfolders yet, I'll do it as soon as possible.

## Requirements
* python 3.6+

## Usage

The script has two parts - generator and backupper.

### Generator
usage: hashgen.py [-h] [-g | -n] [-c] [-q] [-l  LOG] source

positional arguments:
- source

optional arguments:
- -g = Generate .sha1 for source (-g OR -n key)
- -n = Generate .sha1 only for new files. Default key
- -c = Clear .sha1 orphans (Files that left without their master).
- -q = Quiet mode, no output
- -l LOG = Write output to log file

### Backupper
usage: hashbackup.py [-h] [-a | -s] [-d] [-q] [-l  LOG] source destination

positional arguments:
 source
 destination

optional arguments:
- -a = Copy new files only. Default key
- -s = Copy new and changed files (-a OR -s key)
- -d = Delete old files in destination (Backups of files you had in source folder and don't have now)
- -q = Quiet mode
- -l LOG = Write output to log file
  
### How to use it.

Let's say you have two folders - C:\A (source) and C:\B (destination).
First generate sha1 checksums. All files are new this time, so no need to use -g or -n key now.
```
python hashgen.py C:\A
```
And backup this whole bunch to second folder.
```
python hashbackup.py C:\A C:\B
```
Now let's say you changed some files in source, deleted, added some files and you need a log-file in C:\123.
Since the files have changed, use **-g** key for hashgen, **-c** for clearing single .sha1 files and **-l** for log.
```
python hashgen.py -g -c -l C:\123\log.txt C:\A
```
And backup this bunch to second folder again, but now with **-s** (because we have not only new but changed files too, and we need to check all checksums), **-d** (only if you don't need backups of deleted source files) and **-l** keys for log.
```
python hashbackup.py -s -d -l C:\123\log.txt C:\A C:\B
```
And so on.

Why SHA1. These checksums are generating nearly as fast as MD5 on my Skylake and they're longer at the same time. I wanted long shecksums :)

## Contacts

Telegram: @berenzorn

Email: berenzorn@mail.ru

Feel free to contact me if you have a questions. Have a nice day :)
