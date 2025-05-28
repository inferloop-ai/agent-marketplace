def naive_linechunk(text: str, max_lines: int):
    """
    Splits the input text into chunks, each containing at most max_lines lines.

    Args:
        text (str): The text to split.
        max_lines (int): The maximum number of lines per chunk.

    Returns:
        List[str]: List of text chunks, each with up to max_lines lines.
    """
    lines = text.splitlines()
    chunks = []
    for i in range(0, len(lines), max_lines):
        chunk = "\n".join(lines[i:i + max_lines])
        chunks.append(chunk)
    return chunks
