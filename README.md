# Overview

A collection of (and working on now combining the) multiple efforts to process fitness data locally (instead of relying on corporate paywalls, online accounts, and other such nonsensicals).

## pyfr

A project that parsed FIT files with the intent to begin graphically presenting the data for human utilization.

## hearty

`hearty` (the newest variant of the efforts) started as a rewrite of the pyFR/pyfit project I was working on at the time, based on files dumped from a Garmin Forerunner 35 I have been using for a good number of months now.

## fitted

`fitted` is a project to collect the unique files dumped from the Garmin Forerunner 35, so that processing the data from the multiple dumps doesn't accidentally introduce multiplications of efforts (walking, etc) that aren't real.

### FitFilesRepository [now FitDeviceFiles] (from fitted::README.md) [was HashedFitFiles]

Given a collection of dump directories (tested with dumps from an in-use Garmin Forerunner 35) and a "library" directory, maintains a SHA3-512-based hashed collection of FIT files (and the odd ERR_LOG.TXT and GarminDevice.xml). These hashes are used to detect unique-ish-enough files across multiple dumps for later processing.

Note that this "library" path is not hard coded; this class still needs to be pointed to the directories involved, both the "library" directory and the directory of dump directories. These are provided as inputs, and it can be noted that I've got them stored under a `config.py` file, but it's suspiciously.. I mean, totally not suspecticiously... (eyes) included. It just has a couple of constants as imported in the `test.py` program file (for now); later iterations may take the values from arguments to the program, who knows... maybe even pull a totally not secret value from the cloud in the future.. but that's nonesensestalkses.

The FitFilesRepository may still retain a reference to "PyFR".

It, by way of a companion bit of shell scripting and maybe a udev rule or something (it's a bit fuzzy, I need sleep!) back a few months ago, I get "dumps" of the files on the Forerunner 35 when I mount it over USB. This generates a timestamped (yyyy-0m-0d_0h-0m-0s) dump directory containing the subdirectories mounted (under the GARMIN/GARMIN folder on the device; so, the ACTIVITY, RECORDS, DEBUG, etc subdirectories) as well as a couple of what I call "root" files (DEVICE.FIT, GarminDevice.xml).

These dump directories had similarly named FIT files in each subdirectory, and that's when I realized I could track history longer than the on-device displayed week-ish/seven days. However, I had no easy way to identify which file was the same or which was a new file in a dump. I pondered a bit, and then realized hashing could be useful. And, it turns out, it was. (Of course it did; otherwise, no need to mention it in any detail or spend a few keystrokes typing up the HashedFitFiles/whatever above, or even moving the code to here).

Now that the dump directories are all collected in a "library" of sorts with FitFilesRepository, PyFR can resume, but instead on individual dump directories, the hashed and hopefully-still-unique files of them all combined over time.

Of course, now I want to merge PyFR into this project... ah, hopes and dreams...

Anyways, back to it, I guess. And by it, I mean, procrastination.

Maybe a walk later...

## fr35

`fr35` is an unpublished "project", possibly referenced elsewhere, that aimed to develop an automated dumping process of the Garmin Forerunner 35 when mounted over USB. I haven't assessed the files for publication yet, but it's mainly the shell script and udev rules/systemd services to accomplish this goal.
