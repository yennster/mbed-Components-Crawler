# ARMmbed Components Crawler
A python web crawler that determines if an mbed component's Hello World program uses the old mbed library and outputs this data to an Excel sheet.

## Logs
Logs are sorted into folders based on which `mbed compile` command was run to create the log. For example, for programs compiled with `mbed compile -m K64F -t ARM`, the log files are placed in the folder "K64F-logs" and each log file is named with the format: `Username-RepoName-log.txt`.

Each log contains the output of `mbed compile -m <target> -t <toolchain>` in addition to the Hello World Program's mbed Developer site URL (added to the bottom of the file).
