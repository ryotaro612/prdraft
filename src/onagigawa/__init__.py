import sys
import logging
import onagigawa.args
import onagigawa.pr as pr
import onagigawa.embed as embed
import onagigawa.metadata as metadata


def main():
    """Entry point for onagigawa command line interface."""

    args = onagigawa.args.parse(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.subcommand == "pr" and isinstance(args, pr.Args):
        sys.exit(pr.run(args))
    if args.subcommand == "diff" and isinstance(args, metadata.Args):
        sys.exit(metadata.run(args))
    if args.subcommand == "embed" and isinstance(args, embed.Args):
        sys.exit(embed.run(args))
    else:
        logging.error("Unknown subcommand: %s", args.subcommand)
        sys.exit(1)
