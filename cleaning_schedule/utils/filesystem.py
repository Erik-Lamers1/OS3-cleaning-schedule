def get_lines_from_file(path):
    with open(path, 'r') as fh:
        return fh.read().splitlines()


def write_lines_to_file(path, lines):
    """
    Takes a list of strings and writes them to <path> with a \n after each element
    :param path: str: The filepath to write to
    :param lines: list: The list of strings to write
    """
    with open(path, 'w') as fh:
        fh.write('\n'.join(lines))
