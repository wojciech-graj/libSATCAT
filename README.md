# libSATCAT

C Parser for the SATCAT Format.

ANSI C compliant and Linkable with C++.

- SATCAT Format Documentation: https://www.celestrak.com/satcat/satcat-format.php
- SATCAT Data: https://www.celestrak.com/pub/satcat.txt

## Build

The demo program `test/test.c` can be compiled as follows:

```
cd test
gcc ../src/satcat.c ../src/satcat_code.c test.c -lm -ansi -I../src -o bin
./bin
```

Yielding the following output:

```
Parsed 52802 satellites in 0.025441s.

First satellite:
Name: SL-1 R/B
Catalog Number: 1
Status: Decayed
Source: Commonwealth of Independent States (former USSR)
Launch Site: Tyuratam Missile and Space Center, Kazakhstan
```

## Usage

The SATCAT library consists of 2 source files:

#### `satcat.c` + `satcat.h`

Parses SATCAT strings.

- `sc_parse`: Parses a SATCAT-formatted string into a `struct SatCat`

Strings within `struct SatCat` are **NOT** NULL-terminated, and are right-padded with spaces.

#### `satcat_code.c` + `satcat_code.h` [Optional]

Provides description strings for SATCAT Operational Status, Source, and Launch Site Codes.

- `SC_STR5_TO_CODE` macro: converts a 5-character code (either `char source[5]` or `char launch_site[5]` in `struct SatCat`) into a numeric contant of type `sc_code_t`, equal to one of `SCSRC_*` or `SCSITE_*`
- `sc_source_str` & `sc_launch_site_str`: takes a `sc_code_t` code and return a verbose description of the satellite's source or launch site.
- `sc_status_str`: takes an Operational Status Code (`char opstat` in `struct SatCat`, or `SCSTAT_*`), and returns a description of the satellite's status.

These files can be regenerated using `util/gen_code.py` if the SATCAT Operational Status, Source, and Launch Site Codes are expanded.

## License
```
Copyright (c) 2022 Wojciech Graj

Licensed under the MIT license: https://opensource.org/licenses/MIT
Permission is granted to use, copy, modify, and redistribute the work.
Full license information available in the project LICENSE file.
```
