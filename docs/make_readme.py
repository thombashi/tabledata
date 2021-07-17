#!/usr/bin/env python

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import sys

from readmemaker import ReadmeMaker


PROJECT_NAME = "tabledata"
OUTPUT_DIR = ".."


def main():
    maker = ReadmeMaker(
        PROJECT_NAME,
        OUTPUT_DIR,
        is_make_toc=True,
        project_url=f"https://github.com/thombashi/{PROJECT_NAME}",
    )

    maker.inc_indent_level()
    maker.write_chapter("Summary")
    maker.write_introduction_file("summary.txt")
    maker.write_introduction_file("badges.txt")

    maker.write_introduction_file("installation.rst")

    maker.set_indent_level(0)
    maker.write_chapter("Documentation")
    maker.write_lines([f"https://{PROJECT_NAME:s}.rtfd.io/"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
