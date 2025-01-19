"""
Copyright (c) 2022-2025 Wojciech Graj

Licensed under the MIT license: https://opensource.org/licenses/MIT
Permission is granted to use, copy, modify, and redistribute the work.
Full license information available in the project LICENSE file.

DESCRIPTION:
    Generate satcat_code.h and satcat_code.c based on data from celestrak.org
"""

import requests
import typing as t
from html.parser import HTMLParser

class HTMLTableReader(HTMLParser):
    def __init__(self) -> None:
        HTMLParser.__init__(self)
        self.table_data = []
        self.in_tbody = False
        self.ins_next = False

    def handle_starttag(self, tag, attrs) -> None:
        if (tag == "td"):
            self.ins_next = True
        elif (tag == "tbody"):
            self.in_tbody = True

    def handle_endtag(self, tag) -> None:
        if (tag == "tbody"):
            self.in_tbody = False

    def handle_data(self, data) -> None:
        if (self.ins_next and self.in_tbody):
            self.ins_next = False
            self.table_data.append(data.strip("'"))

    def get_table(self, content: str) -> list[tuple[str, str]]:
        self.feed(content)
        return [tuple(self.table_data[i:i+2]) for i in range(0, len(self.table_data), 2)]

def write_header(fh: t.TextIO, fc: t.TextIO) -> None:
    copyright_notice = (
        "/*\n"
        " * Copyright (c) 2022-2025 Wojciech Graj\n"
        " *\n"
        " * Licensed under the MIT license: https://opensource.org/licenses/MIT\n"
        " * Permission is granted to use, copy, modify, and redistribute the work.\n"
        " * Full license information available in the project LICENSE file.\n"
        " **/\n"
        "\n"
    )
    fh.write((
        f"{copyright_notice}"
        "#ifndef SATCAT_CODE_H\n"
        "#define SATCAT_CODE_H\n"
        "\n"
        "#ifdef _ISOC99_SOURCE\n"
        "#include <stdint.h>\n"
        "typedef uint64_t sc_code_t;\n"
        "#else\n"
        "#include <limits.h>\n"
        "#if (UINT_MAX >= 0xFFFFFFFFFFUL)\n"
        "typedef unsigned sc_code_t;\n"
        "#elif (ULONG_MAX >= 0xFFFFFFFFFFUL)\n"
        "typedef unsigned long sc_code_t;\n"
        "#else\n"
        "typedef unsigned long long sc_code_t;\n"
        "#endif\n"
        "#endif\n"
        "\n"
        "#define SC_STR5_TO_CODE(s)\\\n"
        "\t(sc_code_t)((sc_code_t)(s)[0]\\\n"
        "\t| (sc_code_t)(s)[1] << 8\\\n"
        "\t| (sc_code_t)(s)[2] << 16\\\n"
        "\t| (sc_code_t)(s)[3] << 24\\\n"
        "\t| (sc_code_t)(s)[4] << 32)\n"
        "\n"
        "/* Functions */\n"
        "const char *sc_status_str(char code);\n"
        "const char *sc_source_str(sc_code_t code);\n"
        "const char *sc_launch_site_str(sc_code_t code);\n"
        "\n"
    ))
    fc.write((
        f"{copyright_notice}"
        '#include "satcat_code.h"\n'
        "\n"
        "#include <stddef.h>\n"
        "\n"
    ))

def write_footer(fh: t.TextIO, fc: t.TextIO) -> None:
    fh.write((
        "#endif /* SATCAT_CODE_H */"
    ))

def str5_to_code(s: str) -> int:
    return ord(s[0]) + (ord(s[1]) << 8) + (ord(s[2]) << 16) + (ord(s[3]) << 24) + (ord(s[4]) << 32)

def write_body_5byte(fh: t.TextIO, fc: t.TextIO, table: list[tuple[str, str]], prefix: str, name: str, fname: str) -> str:
    bodyh = "".join([f'#define {prefix}_{r[0].ljust(5)} (sc_code_t){str5_to_code(r[0].ljust(5))}UL\n' for r in table])
    fh.write((
        f"/* {name} */\n"
        f"{bodyh}"
        "\n"
    ))
    funcc = "".join([f'\tcase {prefix}_{r[0]}:\n\t\treturn "{r[1]}";\n' for r in table])
    fc.write((
        f"const char *sc_{fname}_str(const sc_code_t code)\n"
        "{\n"
        "\tswitch (code) {\n"
        f"{funcc}"
        "\tdefault:\n"
        "\t\treturn NULL;\n"
        "\t}\n"
        "}\n"
        "\n"
    ))

def write_status_enum(fh: t.TextIO, fc: t.TextIO) -> None:
    fh.write((
        "/* Status */\n"
        "#define SCSTAT_OPERATIONAL '+'\n"
        "#define SCSTAT_NONOPERATIONAL '-'\n"
        "#define SCSTAT_PARTIALLY_OPERATIONAL 'P'\n"
        "#define SCSTAT_BACKUP 'B'\n"
        "#define SCSTAT_SPARE 'S'\n"
        "#define SCSTAT_EXTENDED_MISSION 'X'\n"
        "#define SCSTAT_DECAYED 'D'\n"
        "#define SCSTAT_UNKNOWN '?'\n"
        "\n"
    ))
    fc.write((
        "const char *sc_status_str(const char code)\n"
        "{\n"
        "\tswitch(code) {\n"
        "\tcase SCSTAT_OPERATIONAL:\n"
        '\t\treturn "Operational";\n'
        "\tcase SCSTAT_NONOPERATIONAL:\n"
        '\t\treturn "Nonoperational";\n'
        "\tcase SCSTAT_PARTIALLY_OPERATIONAL:\n"
        '\t\treturn "Partially Operational";\n'
        "\tcase SCSTAT_BACKUP:\n"
        '\t\treturn "Backup/Standby";\n'
        "\tcase SCSTAT_SPARE:\n"
        '\t\treturn "Spare";\n'
        "\tcase SCSTAT_EXTENDED_MISSION:\n"
        '\t\treturn "Extended Mission";\n'
        "\tcase SCSTAT_DECAYED:\n"
        '\t\treturn "Decayed";\n'
        "\tcase SCSTAT_UNKNOWN:\n"
        '\t\treturn "Unknown";\n'
        "\tdefault:\n"
        "\t\treturn NULL;\n"
        "\t}\n"
        "}\n"
        "\n"
    ))

def main() -> None:
    tabs = (
        {"url": "http://www.celestrak.org/satcat/sources.php", "name": "Source", "prefix": "SCSRC", "fname": "source"},
        {"url": "http://www.celestrak.org/satcat/launchsites.php", "name": "Launch Site", "prefix": "SCSITE", "fname": "launch_site"},
    )

    fh = open("src/satcat_code.h", "w")
    fc = open("src/satcat_code.c", "w")
    write_header(fh, fc)

    write_status_enum(fh, fc)

    for t in tabs:
        r = requests.get(t["url"])
        table = HTMLTableReader().get_table(str(r.content))
        write_body_5byte(fh, fc, table, t["prefix"], t["name"], t["fname"])

    write_footer(fh, fc)

    fh.close()
    fc.close()

if __name__ == "__main__":
    main()
