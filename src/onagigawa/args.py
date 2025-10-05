import argparse


def parse(args: list[str]):
    parser = argparse.ArgumentParser(description="onagigawa")
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(help="subcommand help")

    pr_parser = subparsers.add_parser("pr", help="get pull requests")
    pr_parser.add_argument("organization", help="organization")
    pr_parser.add_argument("repository", help="repository")
    pr_parser.add_argument(
        "--size",
        help="# of pull requests that a response from GItHub API contains.",
        default="30",
        type=int,
    )
    pr_parser.add_argument(
        "--offset",
        help="The number of page that the subcommand fetches from GitHub API. Specify this value to resume from the previous state.",
        default="1",
        type=int,
    )
    pr_parser.add_argument(
        "destination",
        help="Write the fetched pull requests to this file in JSON line format.",
    )

    return parser.parse_args(args)
