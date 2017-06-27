import os
import tempfile

def get_temp_file():
    """TODO: Docstring for get_temp_file.
    :returns: TODO

    """
    h, out_path = tempfile.mkstemp()
    os.close(h)
    return out_path
