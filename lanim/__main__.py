"""
Entry point.
"""

import argparse
import multiprocessing
import pathlib

from lanim.standalone import entry_point


# -h conflicts with our `height` option, so we need to change it
parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-?", "--help", action="help")

parser.add_argument("module", help="Python module to animate")
parser.add_argument(
    "-e", "--export-name",
    metavar="IDENTIFIER",
    help="Animation name to import from the file. Defaults to `export`",
    default="export"
)

parser.add_argument("-w", "--width", type=int, help="Frame width, in pixels", default=1280)
parser.add_argument("-h", "--height", type=int, help="Frame height, in pixels", default=720)
parser.add_argument("-f", "--fps", type=int, help="Frames per second", default=30)

cpu_count = multiprocessing.cpu_count()
parser.add_argument(
    "-t", "--threads",
    type=int,
    help="Number of threads do launch. Defaults to CPU count ({} in your case)".format(cpu_count),
    default=cpu_count
)
parser.add_argument(
    "-p", "--temp-dir",
    metavar="PATH",
    type=pathlib.Path,
    help="Temporary working directory, for example /tmp/lanim. "
         "Defaults to .lanim in the current working directory",
    default=pathlib.Path("./.lanim")
)
parser.add_argument(
    "-o", "--output",
    metavar="PATH",
    type=pathlib.Path,
    help="Where to put the output file. The will be passed directly to ffmpeg, so "
         "any format it supports should work.",
    required=True
)


args = parser.parse_args()
print(args)
entry_point(args)  # type: ignore

