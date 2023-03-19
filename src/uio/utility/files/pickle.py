"""
File operations with [pickles](https://docs.python.org/3/library/pickle.html).
"""

import pathlib
import pandas


def openPickleAsPandasTable(f: str) -> pandas.DataFrame:
    """
    Example:

    ``` py
    from uio.utility.files import pickle

    pnd = pickle.openPickleAsPandasTable("/path/to/some.pkl")
    #print(pnd.head(15))
    ```
    """
    filePath = pathlib.Path(f)
    if not filePath.exists():
        raise SystemError(f"The path [{filePath}] does not exist")
    if not filePath.is_file():
        raise SystemError(f"The [{filePath}] is not a file")
    return pandas.read_pickle(filePath)