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
        project_url="https://github.com/thombashi/{}".format(PROJECT_NAME),
    )

    maker.inc_indent_level()
    maker.write_chapter("Summary")
    maker.write_introduction_file("summary.txt")
    maker.write_introduction_file("badges.txt")

    maker.write_file(maker.doc_page_root_dir_path.joinpath("installation.rst"))

    maker.set_indent_level(0)
    maker.write_chapter("Documentation")
    maker.write_lines(["https://{:s}.rtfd.io/".format(PROJECT_NAME)])

    return 0


if __name__ == "__main__":
    sys.exit(main())
