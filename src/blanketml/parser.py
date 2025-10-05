import dataclasses


@dataclasses.dataclass
class Command:
    config_file: str


def parse(args: list[str]) -> Command:
    """Parses command line arguments."""
    return Command(args[0])
