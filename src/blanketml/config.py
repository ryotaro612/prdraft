import tomllib
import typing
import dataclasses


@dataclasses.dataclass
class Post:
    """Represents a post with its details."""

    ja: str
    en: typing.Union[str, None]
    paper: str


@dataclasses.dataclass
class Config:
    insutruction: str
    posts: typing.Dict[str, Post]


def load(config_path: str) -> Config:
    """
    Load a configuration file from the given path.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration as a dictionary.
    """

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

        posts = {
            name: Post(ja=post["ja"], en=post.get("en", None), paper=post["paper"])
            for name, post in config["posts"].items()
        }

        return Config(config["instruction"], posts)
