from blanketml import parser
import blanketml.config as conf


def main(args: list[str]) -> None:
    """
    Main function to parse command line arguments and execute the parser.

    Args:
        args (list[str]): List of command line arguments.
    """
    res = parser.parse(args)
    config = conf.load(res.config_file)
