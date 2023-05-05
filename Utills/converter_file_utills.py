def save_working_copy(file_path):
    """
    Reads the content of a file and saves it to a new file with the suffix "_working_copy".
    Returns the new file path.

    Args:
        file_path (str): The path of the file to read.

    Returns:
        str: The path of the new file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_file_path = file_path + '_working_copy'

    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return new_file_path
