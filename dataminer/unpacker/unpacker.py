import os
import shutil
import zipfile
import mimetypes
from enum import Enum


class Unpacker:
    class FileType(str, Enum):
        UNKNOWN = 'UNKNOWN'
        DIRECTORY = 'DIRECTORY'
        ZIP = 'ZIP'
        PNG = 'PNG'

    def __init__(self, filename, outdir):
        self.filename = filename
        self.outdir = os.path.abspath(outdir)

        self.tree = {}
        self._preprocess()

    def _preprocess(self):
        # Unpacked directory
        os.makedirs(self.outdir, exist_ok=True)
        root_node = {
            "path": os.path.abspath(self.outdir),
            "type": self.FileType.DIRECTORY,
            "childnum": 0,
            "child": [],
        }

        # Copy files
        file_basename = os.path.basename(self.filename)
        shutil.copy(self.filename, os.path.join(self.outdir, file_basename))

        # Recursively generate unpack tree
        self.tree = self._generateChildNodes(root_node)

    def _generateChildNodes(self, parentNode):
        parentPath = parentNode["path"]
        children = os.listdir(parentPath)

        while len(children) > 0:
            child_basename = children.pop(0)
            child = os.path.join(parentPath, child_basename)

            childType = self._getFileType(child)
            childPath = os.path.splitext(child)[0]

            if childType == self.FileType.ZIP:
                # Do not append a zip file directly
                # Extract the zip and append directory instead
                with zipfile.ZipFile(child, 'r') as zf:
                    zipInfo = zf.infolist()
                    for e in zipInfo:
                        e.filename = e.filename.encode(
                            'cp437').decode('euc-kr')
                        zf.extract(member=e, path=childPath)
                os.remove(child)
                children.append(os.path.splitext(child_basename)[0])
            elif childType == self.FileType.DIRECTORY:
                node = {
                    "path": childPath,
                    "type": self.FileType.DIRECTORY,
                    "childnum": 0,
                    "child": [],
                }
                # Recursively generate child nodes
                node = self._generateChildNodes(node)
                parentNode["child"].append(node)
            elif childType == self.FileType.PNG:
                node = {
                    "path": childPath,
                    "type": self.FileType.PNG,
                }
                parentNode["child"].append(node)
            else:
                # TODO
                node = {
                    "path": childPath,
                    "type": self.FileType.UNKNOWN,
                    "child": []
                }
                parentNode["child"].append(node)

        parentNode["childnum"] = len(parentNode["child"])
        return parentNode

    def _getFileType(self, filename):
        if os.path.isdir(filename):
            return self.FileType.DIRECTORY
        if os.path.isfile(filename):
            file_mime = mimetypes.guess_type(filename)
            if 'application/x-zip-compressed' in file_mime:
                return self.FileType.ZIP
            if 'image/png' in file_mime:
                return self.FileType.PNG
        return self.FileType.UNKNOWN
