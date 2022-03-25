import os
import sys

from ..util.tree import readTree


class ImgConverter:
    """Convert image in root directory to fixed size
    """

    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.json = os.path.join(self.root, "tree.json")

        loaded, tree = readTree(self.json)
        if loaded:
            self.tree = tree
        else:
            print("There is no tree data", file=sys.stderr)
            return
