def naive_linechunk(text, chunk_size):
    """
    Splits the input text into chunks of approximately `chunk_size` lines.

    This function is very naive and does not take into account the length of
    individual lines. It is mainly useful for small chunks and for testing
    purposes. If you need to split large texts, you should use a more
    sophisticated algorithm.

    Args:
        text (str): The text to split.
        chunk_size (int): Number of lines per chunk.

    Returns:
        List[str]: List of text chunks.
    """
    lines = text.splitlines()
    return [
        "\n".join(lines[i:i + chunk_size])
        for i in range(0, len(lines), chunk_size)
    ]
