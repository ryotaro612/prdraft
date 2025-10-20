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

    # diff subcommand
    diff_parser = subparsers.add_parser(
        "diff", help="generate diffs for pull requests."
    )
    diff_parser.add_argument(
        "pullrequests", help="a JSONL file that the pr subcommand outputs."
    )
    diff_parser.add_argument(
        "repository",
        help="Git repository path containing the pull requests from the pr file.",
    )
    diff_parser.add_argument("metadata", help="output")

    # embed subcommand
    embed_parser = subparsers.add_parser(
        "embed", help="generate embeddings for pull requests."
    )
    embed_parser.add_argument("pr", help="a JSONL file that the pr subcommand outputs.")
    embed_parser.add_argument(
        "repository", help="a JSONL file that the diff subcommand outputs."
    )
    embed_parser.add_argument("db", help="a DuckDB database file to store embeddings.")

    # mcp subcommand
    mcp_parser = subparsers.add_parser("mcp")
    mcp_parser.add_argument("repository")
    mcp_parser.add_argument("db")

    return parser.parse_args(args)
