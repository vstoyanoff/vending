from typing import Union


def validate_values(value: Union[int, float], field: str) -> int:
    """
    Helper for models validation.
    Validates if the provided value is multiple of 5 or if it is negative.

    :param: value -> number
    :param: field -> name of the field we are going to validate in the model

    :raises: ValueError

    :returns: int
    """
    if value < 0:
        raise ValueError(f"{field} must be non-negative number")
    elif value % 5 != 0:
        raise ValueError(f"{field} must be multiple of 5")
    else:
        return int(value)
