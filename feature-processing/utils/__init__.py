def flatten(nested_list: list) -> list:
    """
    flattening nested list
    """
    return [item for sublist in nested_list for item in sublist]
