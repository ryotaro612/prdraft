import prdraft.args as args
import logging
import prdraft.init as init
import sys


def main():
    """The entrypoint"""
    sys.exit(_main(sys.argv[1:]))


def _main(arguments: list[str]) -> int:
    options = args.parse(arguments)
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    return_code: int
    if options.subcommand == "init" and isinstance(options, init.Args):
        return_code = init.run(options)
    else:
        args.parse(["--help"])
        return 0
    return return_code
