from .imgconverter import ImgConverter
from .unpacker import Unpacker
from .util.json import loadJson


class Dataminer:
    def __init__(self, config="dataminer2.json"):
        self.config = loadJson(config)

        if self.config is None:
            print("Dataminer configuration file missing")
            return

        self.imgconverter = ImgConverter
        self.unpacker = Unpacker
