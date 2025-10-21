import prdraft.args as args
import logging
import sys


def main():
    """The entrypoint"""
    options = args.parse(sys.argv[1:])
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # if args.verbose:
    #     logging.basicConfig(level=logging.DEBUG)
