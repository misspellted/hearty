
# Overview

The collection of outstanding tasks in the code, some may require research, others require time. Some both!

## Candidate Dump Directories Scanning

Previously, [fitted]HashedFitFiles::scan(dir) expected a directory of dump directories, and returned the list of candidate directories that could be read into the files collection. This expectation and end result was not brought over in the merging of the fitted and hearty projects. Instead, [hearty]FitDeviceFiles::scan(dir) expects an individual dump directory, indicating if it is ready to be read into the files repository.

As a consequence, the FitDeviceFiles::scan() caller, if desired, would need to perform this functionality. Another possibility would be to add some kind of "overscan" method to FitDeviceFiles (optionally UniqueFilesRepository) to recapture that feature.

## GarminDevice.xml vs DEVICE.FIT

The current FitDeviceFiles::scan() looks for the existence of both GarminDevice.xml and DEVICE.FIT files at the base of the dump directory:

```
<dump_directory>
+ DEVICE.FIT
+ GarminDevice.xml
+ ACTIVITY/
+ MONITOR/
+ DEBUG/
+ <etc>
```

The `DEVICE.FIT` file can (effectively) report the manufacturer, which would inform the XML file name (_if_ it differs between manufacturers); conversely, the `GarminDevice.xml` file describes a FITBinary "DataType" pointing to the location of the DEVICE.FIT file (since it is marked as InputOutput). The issue is determining which one to use as the starting point:

* If `GarminDevice.xml` always exists (the manufacturer doesn't provide their own `*Device.xml` file), then it should be the "controlling" file, and the `DEVICE.FIT` file can be pulled from it.
* If `DEVICE.FIT` always exists, then the `*Device.xml` file can be identified accordingly (if there are different variants of this file per manufacturer).

## Dump Directory Structure

Currently, the scanning and reading for FitDeviceFiles expects the files to be at the base of the dump directory, and then the additional directories and their files as dumped.

However, the `GarminDevice.xml` file (from a Forerunner 35) appears to reference files starting at the `GARMIN` directory (the directory from which all the files and subdirectories are copied as a dump directory, but not including the `GARMIN` directory itself).

A complication of scanning not having the definitive direction for looking for either `DEVICE.FIT` or `GarminDevice.xml` as the controlling/starting file is that this parent `GARMIN` folder is not included as part of the dump directory path/name, and if the source device isn't made by Garmin, then this parent folder may not be named `GARMIN`, causing difficulting in device identification and dump directory processing.

As a secondary consideration, the `fr35` "project" (it's not quite consolidated in a project, per se) makes assumptions of such parent folder. If this parent folder cannot be assumed anymore, the `fr35` files will need to be device-specific, and that may be more a nuisance than a complex endeavor to adapt.

## Dump Directory Deletion

After processing a dump directory, [fitted]HashedFitFiles wiped the directory (and since it operated with a list of dump directories, it would wipe them all). This cullumnated in the directories being erased from the storage medium after all unique files were copied to the collection.

Now, [hearty]FitDeviceFiles also requests file deletions, but it does not delete the dump directory itself. This could be a function of FitDeviceFiles::wipe(), but it not yet implemented.

## FIT::BaseType::String

Can a device report/record an empty string (a 1-byte array containing just 0x00 as a null-termination marker)? The unit tests assume that an empty string is _not_ allowed.

## FIT::BaseType::Float32

Need some additional test cases for values other than invalid or incorrect ones.
A useful source of values that could be tested: https://en.wikipedia.org/wiki/Single-precision_floating-point_format#Notable_single-precision_cases

## FIT::BaseType::Float64

Also need some additional test cases for values other than invalid or incorrect ones.
A useful source of values that could be tested: https://en.wikipedia.org/wiki/Double-precision_floating-point_format#Double-precision_examples

## FitDeviceFiles::on_file

The `DEVICE.FIT` and `GarminDevice.xml` files are inspected in the ::on_fine() method, where previously they were inspected in ::scan().

They were moved to restore the unit tests functioning without having a testable version of either that passes such inspection.

It is not entirely sure if they should be pulled back into ::scan(), although it's probably a better location than ::on_file().

## FIT::Fields::common_fields

Convert common fields into a map of {field_number: <new_instance_function>}, like as is FIT::Messages::global_messages.

## FIT::RecordMessage

There is not much implemented besides knowing the global message number.

## FIT::FileIdMessage

### Timestamp Reference

As seen at https://developer.garmin.com/fit/protocol/#record2datamessage:file_idlocalmsgtype0, the `time_created` field having a value of 621463080 corresponds to 14 Aug 2009.

Is this value referenced from the Unix epoch?

### Base Type Expectation

Ensure the base type from the file record is expected. The FIELDS map towards the top of the file has details in comments regarding the base type for each field, but they are not mapped to actual FIT::BaseType::* implementations. Once that's in place...

### Base Type Evaluation

Evaluate the value through the base type. Instead of just storing the `btn_val` as part of the attribute.

### Developer Fields

The base message types might be expandable with developer fields, as https://developer.garmin.com/fit/protocol/#record7definitionmessage:recordmesg_num0x14 demonstrates a redefined Record (global number 20) that includes developer fields.

Therefore, the base messages must be able to accept developer fields as well.

## FIT::FieldDescriptionMessage

Even less implemented than FIT::RecordMessage, hahaha! Basically, just comments with a link! /me shakes head

## FIT::DevDataIdMessage

Same as FIT:FieldDescriptionMessage above.

### Application IDs

Not sure when this becomes useful, but it does appear that `app_id` value, shown at https://developer.garmin.com/fit/protocol/#record4datamessage:dev_data_idlocalmsgtype0, looks like a UUID (or similar).

## FIT::Messages

Continue importing message implementations.

## FIT::Fields

Discern whether a value was invald or a failure during evaluation.

## FIT Profiles

The majority of the data definitions seem to be not documented very well, outside of the SDK.

Since the SDK is behind an agreement that seemed not favorable to open source, namely Section 2 ("Use Restrictions") part d, "[Licensee shall not, and shall not permit any third party to, directoly or indirectly] distribute the Licensed Technology or any derivatives thereof so that any part of it becomes subject to any licesne that requires that the Licensed Technology or any of Garmin's other intellectual property be disclosed to distributed in source code form, or that others have rights to modify it.", it would seem that Garmin is not really open-source friendly.

So, the profiles mentioned in the documentation that is publicly available indicates data definitions are extracted away from the implementation. Therefore, profile support is probably going to take time as data is collected.

## FIT::GarminDevice.xml

Not quite sure what use the `UpdateFile` elements could be useful for, besides extracting part numbers. As the majority of these file definitions seem to be describing where to put update files _onto_ the device, there's not much point in trying to pull the data _from_ the device.

But there's a commented `self.device["MassStorageMode"]["UpdateFile"] = []` line for the future, even if, again, to grab the part numbers...

## FIT File CRC Verification

Their presence is detected and value extracted, but not verified. Both in the header and at the "footer" of the file.
