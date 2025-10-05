def remove_front_matter(markdown: str) -> str:
    """
    Remove the front matter from a markdown string.

    Args:
        markdown (str): The markdown content.

    Returns:
        str: The markdown content without the front matter.
    """
    lines = markdown.splitlines()
    idx = [i for i, line in enumerate(lines) if line.startswith("---")]
    if len(idx) < 2:
        return markdown  # No front matter found

    return "\n".join(lines[idx[1] + 1 :])
