import base64


def read_bin_base64(file_path: str) -> str:
    """
    Encode a file to a base64 string.

    Args:
        file_path (str): The path to the file to be encoded.

    Returns:
        str: The base64 encoded string of the file.
    """
    with open(file_path, "rb") as file:
        file_bytes = file.read()
        encoded_file = base64.b64encode(file_bytes).decode("utf-8")
    return encoded_file


def read_file(file_path: str) -> str:
    """
    Read a file and return its content as a string.

    Args:
        file_path (str): The path to the file to be read.

    Returns:
        str: The content of the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
