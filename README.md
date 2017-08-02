# ARMmbed Components Crawler
A python web crawler that determines if an mbed component's Hello World program uses the old mbed library and outputs this data to an Excel sheet.

## Logs
Logs are sorted into folders based on which `mbed compile` command was run to create the log. For example, for programs compiled with `mbed compile -m K64F -t ARM`, the log files are placed in the folder "K64F-logs" and each log file is named with the format: `Username-RepoName-log.txt`.

Each log contains the output of `mbed compile -m <target> -t <toolchain>` in addition to the Hello World Program's mbed Developer site URL (added to the bottom of the file).

## Data
The "Components" sheet of the `data.xlsx` Excel workboook is organized by the following columns:

Note: The data in columns [A] - [G] were gathered via the [Python web crawler script](https://github.com/yennster/mbed-Components-Crawler/blob/master/url.py) & [Python Hello World testing script](https://github.com/yennster/mbed-Components-Crawler/blob/master/test.py).

- **[A] Component Type:** The type of Component (as listed on the [mbed Developer Components page](https://developer.mbed.org/components/))
- **[B] Component URL:** The URL to the Component (relative to the [mbed Developer site](https://developer.mbed.org/))
- **[C] Hello World URL:** The URL to the Component's Hello World mbed repository, if one exists (relative to the [mbed Developer site](https://developer.mbed.org/))
- **[D] Is a library?:** FALSE = the repo *does not* contain a `main.cpp` file meaning the program cannot be compiled, TRUE = the repo *does* contain a `main.cpp` file
- **[E] Contains mbed-os.lib?:** FALSE = the repo contains an older version of mbed OS, TRUE = the repo contains mbed OS 5 (`mbed-os.lib`)
- **[F] Compiled for K64F?:** After removing the old mbed OS and running `mbed deploy` - FAIL = the Hello World program failed to compile for K64F, SUCCESS = the Hello World program successfully compiled for K64F
- **[G] Compiled for LPC1768?:** After removing the old mbed OS and running `mbed deploy` - FAIL = the Hello World program failed to compile for LPC1768, SUCCESS = the Hello World program successfully compiled for LPC1768
- **[H] Success on one platform?:** Excel macro that determines if the Hello World program had successful compilation on either the K64F or LPC1768 platforms, TRUE = compiled on at least one platform, FALSE = did not compile on either platform
- **[I] mbed Team Member?:** Excel macro that determines if the Hello World repo is owned by an ARM mbed team member 
  - ARM mbed team members: /users/chris, /users/simon, /users/bridadan, /users/mbed_official, /users/Kojto, /users/sam_grove, /users/mbedAustin, /users/JimCarver, /users/andcor02, /teams/mbed-os-examples, /users/MACRUM, /users/Donatien
- **[J] mbed Partner?:** Excel macro that determines if the Hello World repo is owned by an ARM mbed partner
  - ARM mbed partners: /teams/ST, /users/nxp_ip, /teams/NXP, /teams/Freescale, /teams/AnalogDevices, /teams/Maxim-Integrated, /teams/ublox, /teams/WIZnet, /teams/Avnet, /users/ytsuboi, /users/Sissors, /users/Kaizen, /users/Jksoft

## Update Methodology
The following steps can be used to update a component's Hello World repo:

1. Clone the Hello World repo: `hg clone {link to mbed developer site repo}`
2. Remove the old mbed OS library file (i.e. `mbed.bld`)
3. Add mbed OS 5 and update other libraries: `mbed deploy`
4. Verify the program compiles: `mbed compile -t {toolchain] -m {platform}`
5. Add the new mbed-os.lib file to the repo: `hg add mbed-os.lib`
6. Commit the changes: `hg commit`
6. Push the changes: `hg push`
