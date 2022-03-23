from .imgconverter import ImgConverter
from .unpacker import Unpacker


class Dataminer:
    def __init__(self):
        self.imgconverter = ImgConverter
        self.unpacker = Unpacker
