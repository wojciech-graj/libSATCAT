# libSATCAT

C Parser for the SATCAT Format.

ANSI C compliant and linkable with C++.

- SATCAT Format Documentation: https://www.celestrak.org/satcat/satcat-format.php
- SATCAT Data: https://www.celestrak.org/pub/satcat.txt

## Build

The demo program `test/test.c` can be compiled as follows:

```
cd test
gcc ../src/satcat.c ../src/satcat_code.c test.c -lm -ansi -I../src -o bin
./bin
```

Yielding the following output:

```
Parsed and Validated 52802 satellites in 0.066405s.
Found 51898 valid satellites and 904 invalid satellites.

First satellite:
Name: SL-1 R/B
Catalog Number: 1
Status: Decayed
Source: Commonwealth of Independent States (former USSR)
Launch Site: Tyuratam Missile and Space Center, Kazakhstan
```

## Usage

By default, strings within `struct SatCat` are **NOT** NULL-terminated, and are right-padded with spaces. To enable NULL-terminated strings, define `SC_CSTRING`.

The SATCAT library consists of the following files:

#### `satcat.c` + `satcat.h`

Parses and validates SATCAT strings.

- `sc_parse`: Parses a SATCAT-formatted string into a `struct SatCat`
- `sc_validate`: Validates if string is SATCAT-formatted

#### `satcat_code.c` + `satcat_code.h` [**Optional**]

Provides description strings for SATCAT Operational Status, Source, and Launch Site Codes.

- `SC_STR5_TO_CODE` macro: converts a 5-character code (either `char source[5]` or `char launch_site[5]` in `struct SatCat`) into a numeric contant of type `sc_code_t`, equal to one of `SCSRC_*` or `SCSITE_*`
- `sc_source_str` & `sc_launch_site_str`: takes a `sc_code_t` code and return a verbose description of the satellite's source or launch site.
- `sc_status_str`: takes an Operational Status Code (`char opstat` in `struct SatCat`, or `SCSTAT_*`), and returns a description of the satellite's status.

These files can be regenerated using `util/gen_code.py` if the SATCAT Operational Status, Source, and Launch Site Codes are expanded.
