import sys
import logging
import onagigawa.args
import onagigawa.pr as pr


def main():
    """Entry point for onagigawa command line interface."""

    args = onagigawa.args.parse(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if isinstance(args, pr.Args):
        if pr.run(args):
            sys.exit(1)
