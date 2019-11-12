import argparse
import sys

from .utils import datapackage_to_datasette


def parse_args(args):
    arg_parser = argparse.ArgumentParser(
        description="Load a datapackage into SQLite and generate datasette metadata"
    )
    arg_parser.add_argument("dbname", help="Name of the SQLite database file")
    arg_parser.add_argument("data_package", help="Path or URL to datapackage")
    arg_parser.add_argument(
        "metadata_filename", help="Name of datasette metadata file to write"
    )
    arg_parser.add_argument(
        "--write-mode",
        help="Pass 'replace' or 'merge' to overwrite or merge with an existing datasette metadata file",
        default=None,
        choices=["replace", "merge"],
    )
    return arg_parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    datapackage_to_datasette(
        dbname=args.dbname,
        data_package=args.data_package,
        metadata_filename=args.metadata_filename,
        write_mode=args.write_mode,
    )
