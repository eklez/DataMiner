import os
import shutil
import zipfile
import sys
import mimetypes

from ..util.tree import readTree, calcFileHash, FileType
from ..util.json import writeJson


class Unpacker:
    """Given zip(currently only support .zip) file, unpack it to output directory

    Attribute:
        tree    tree dictionary from unpacked data
    """

    def __init__(self, filename, outdir):
        self.filename = filename
        self.outdir = os.path.abspath(outdir)
        self.json = os.path.join(self.outdir, "tree.json")

        loaded, tree = readTree(self.json)
        if loaded:
            self.tree = tree
            if tree["hash"] != calcFileHash(self.filename):
                # Tree data is already exist, but file hash does not match
                # May use other out directory
                print("Tree data already exist", file=sys.stderr)
                return
            self.fileHash = tree["hash"]

        else:
            self.tree = {}
            self.fileHash = calcFileHash(self.filename)

            # Generate tree & unpack in outdir
            self._preprocess()

            writeJson(self.json, self.tree)

    def _preprocess(self):
        # Unpacked directory
        os.makedirs(self.outdir, exist_ok=True)
        root_node = {
            "path": os.path.abspath(self.outdir),
            "type": FileType.DIRECTORY,
            "hash": self.fileHash,  # Only root node
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

            if childType == FileType.ZIP:
                # Do not append a zip file directly
                # Extract the zip and append directory instead
                with zipfile.ZipFile(child, 'r') as zf:
                    zipInfo = zf.infolist()
                    for e in zipInfo:
                        # Support Korean filename
                        e.filename = e.filename.encode(
                            'cp437').decode('euc-kr')
                        zf.extract(member=e, path=childPath)
                os.remove(child)
                children.append(os.path.splitext(child_basename)[0])
            elif childType == FileType.DIRECTORY:
                node = {
                    "path": childPath,
                    "type": FileType.DIRECTORY,
                    "childnum": 0,
                    "child": [],
                }
                # Recursively generate child nodes
                node = self._generateChildNodes(node)
                parentNode["child"].append(node)
            elif childType == FileType.PNG:
                node = {
                    "path": childPath,
                    "type": FileType.PNG,
                }
                parentNode["child"].append(node)
            else:
                # TODO
                node = {
                    "path": childPath,
                    "type": FileType.UNKNOWN,
                    "child": []
                }
                parentNode["child"].append(node)

        parentNode["childnum"] = len(parentNode["child"])
        return parentNode

    def _getFileType(self, filename):
        if os.path.isdir(filename):
            return FileType.DIRECTORY
        if os.path.isfile(filename):
            file_mime = mimetypes.guess_type(filename)
            if 'application/x-zip-compressed' in file_mime:
                return FileType.ZIP
            if 'image/png' in file_mime:
                return FileType.PNG
        return FileType.UNKNOWN
