import prdraft.args as args
import logging
import prdraft.init as init
import prdraft.fetch as fetch
import prdraft.embed as embed
import sys


def main():
    """The entrypoint"""
    sys.exit(_main(sys.argv[1:]))


def _main(arguments: list[str]) -> int:
    parser = args.Parser()
    options = parser.parse(arguments)
    if options is None:
        parser.print_help()
        return 1
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    return_code: int
    if options.command == "init":
        return_code = init.run(options)
    elif options.command == "pr":
        if options.subcommand == "fetch":
            return_code = fetch.run(options)
        elif options.subcommand == "embed":
            return_code = embed.run(options)
        else:
            parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1
    return return_code
