import json


def loadJson(filename):
    with open(filename, "r", encoding="UTF-8") as f:
        result = json.load(f)
    return result


def writeJson(filename, jsonfile):
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(jsonfile, f, indent=2, ensure_ascii=False)
