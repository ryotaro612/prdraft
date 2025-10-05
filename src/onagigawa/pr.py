import requests
import typing

@typing.runtime_checkable
class Args(typing.Protocol):
    """This class is runtime_checkable to select a subcommand using parsing result.
    """
    organization: str
    repository: str
    output: str
    size: int
    offset: int
    verbose: bool



def run(args: Args):
    args.output