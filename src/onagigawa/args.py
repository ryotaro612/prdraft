import argparse


def parse(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="onagigawa")
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(help="subcommand help", dest="subcommand")
    # pr subcommand
    pr_parser = subparsers.add_parser("pr", help="fetch pull requests")
    pr_parser.add_argument("organization", help="GitHub organization name")
    pr_parser.add_argument("repository", help="GitHub repository name")
    pr_parser.add_argument(
        "output",
        help="Output file path for fetched pull requests (JSON Lines format)",
    )
    pr_parser.add_argument(
        "--size",
        help="Number of pull requests per GitHub API response",
        default="30",
        type=int,
    )
    pr_parser.add_argument(
        "--offset",
        help="Page number to fetch from GitHub API (use to resume from previous state)",
        default="1",
        type=int,
    )
    # patch subcommand
    patch_parser = subparsers.add_parser(
        "patch",
        help="create pairs of pull requests and diffs",
    )
    patch_parser.add_argument(
        "pr", help="JSON Lines file containing pull request data (from pr subcommand)"
    )

    patch_parser.add_argument(
        "repository",
        help="Git repository path containing the pull requests from the pr file",
    )
    patch_parser.add_argument(
        "dir", help="Output directory for generated pairs"
    )

    return parser.parse_args(args)
