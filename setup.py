"""
Compound binary setup script

Used in conjunction with cx_Freeze.

(Requires cx_Freeze.)
"""

import cx_Freeze

cx_Freeze.setup (
    name = "guifoo",
    version = "1.0.0",
    description = "A transclusion compiler for HTML.",
    options = {
        "build_exe": {
            "packages": ["bs4", "sys", "os", "htmlmin"]
        }
    },
    executables = [cx_Freeze.Executable("compound.py")]
)
