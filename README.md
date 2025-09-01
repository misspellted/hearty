# Overview

This project intends to process fitness data locally for human consumption. The requirements of an online account, possible paywalls, unreasonable license agreements, or other such nonsensicals, just to read the data that is generated locally to the human likely wanted to review the data in the future, is unreasonable and places an unfair burden on the consumer. Especially in light of data breaches, and the type of data being stored is pretty personal (potentially personally identifying), it is in the interests of the consumer to store the data on systems they have complete adminstrative control over, up to and including full and permanent deletion at their discretion, instead of "deactivation" where the data is still subject to breach, even if it is considered "dormant".

The project stands as a compilations of previous efforts, after observing that connecting a Garmine Forerunner 35 to my desktop over USB provided a USB mass storage device-type interface - where I could simply copy files over for future processing:

## fr35

This "project" is actually a collection of files used to semi-automate dumping (copying the files from the device mounted over USB as a mass storage device). While there isn't a local Git repository of the files, I could easily collect them in such a way to facilitate absorption, but their contents still need auditing to determine what could be included for publication via the `hearty` project. Namely, I am concerned with hard coded values that might expose information more than I want with what is already accounted for with via (heh) online accounts, such as this GitHub one.

## pyfr

It started out as the `pyfr` project ([py]thon [f]ore[r]unner) as I have a Garmin Forerunner 35 (the latest fitness wearable I've owned since a Fitbit Flex 2 and I forget the second Fitbit I had). The objective was to extract various tidbits, unfiddled by online accounts, online storage not under my control with a side of possible privacy invasion, and make it consumable by this human (arguable...) in a graphical manner for review and decision making for future fitness endeavors.

The end point (at the time of creating `fitted` below) was a reworked "time-stream" file, so that the record stream was aligned with time (using the `.FITS` extension). I hadn't yet made it graphically represent the data, but time-stream data is likely the precursor, so that is what I was working on.

There was a start to rewrite `pyfr` as `pyfit` (for potential upload to GitHub for dissemination/release management), but that did not get too far...

## fitted

`fitted` was going to take over the `pyfit` rewrite, but instead it became the solution to handling multiple `fr35` dumps having the same files over time. For example, having X copies of a walk activity might count X times towards fitness goals, which would contribute to a misrepresentation of progress.

I didn't have a good idea of how to identifiy unique files over dated dump directories (and such dump directory names weren't consistent at the beginning, but cleaned up with `fr35` becoming useful). I had the thought of hashing the file contents, and tested it out with SHA3-512. Why 3-512? No idea, but 3 > 2, and SHA1 is effectively compromisable (more so for MD5), so... 3 it was. And 512 is a nice number, and while it could be 1024, such bits are not yet available, or at least, that I didn't see in the `hashlib` that comes with Python. I even had to install the `sha3sum` package to test the results of the hashing, which became a useful tidbit of information when working on the unit tests!

Also, given my online handle of 'misspellted', `*ted`-suffixed projects tend to have a soft spot in the ol' ticker. But as we all know, good times do come to an end, especially when a new project name idea arises: `hearty` (speaking of ticker, lol!).

# Roadmap

* [x] Random explorative coding sessions to learn how FIT files are structured.
* [x] Semi-automated dumps (sorry, just gotta chuckle) - still requires manual invocation since mounting is not (yet?) automated upon connecting the FR35 to the computer over USB.
* [x] Unique file determination and organization.
* [ ] Return to form with processing for graphical output.
* [ ] Refactor everything again, for the 127th time. (yes, this is a reference! woo!)
* [ ] Anyways, back to it, I guess. And by it, I mean, procrastination.
* [ ] Maybe a walk.
* [ ] Later.
