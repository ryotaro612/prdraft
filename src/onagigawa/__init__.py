import sys
import logging
import onagigawa.args
import onagigawa.pr as pr
import onagigawa.patch as patch
import onagigawa.importpr as importpr


def main():
    """Entry point for onagigawa command line interface."""

    args = onagigawa.args.parse(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.subcommand == "pr" and isinstance(args, pr.Args):
        sys.exit(pr.run(args))
    if args.subcommand == "importpr" and isinstance(args, importpr.Args):
        sys.exit(importpr.run(args))
    elif args.subcommand == "patch" and isinstance(args, patch.Args):
        sys.exit(patch.run(args))
