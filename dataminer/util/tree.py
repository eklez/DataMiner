import os
import hashlib
from enum import Enum
from .json import loadJson


class FileType(str, Enum):
    UNKNOWN = 'UNKNOWN'
    DIRECTORY = 'DIRECTORY'
    ZIP = 'ZIP'
    PNG = 'PNG'


def calcFileHash(filename):
    """Calculate hash value of given file

    :param filename: Filename

    :return: Sha1 hash value. Return False if there is no file.
    """
    if not os.path.isfile(filename):
        return False

    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def readTree(treejson):
    """Read tree json file

    :param treejson: Json file name

    :return: (True, tree) if success
             (False, None) if there is no tree information
    """
    if not os.path.isfile(treejson):
        return False, None

    loaded = loadJson(treejson)
    if "hash" not in loaded:
        return False, None

    return True, loaded
