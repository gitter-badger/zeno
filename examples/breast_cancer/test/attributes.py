from zeno import slicer


@slicer
def age_above50(metadata):
    return metadata[metadata["age"] > "050Y"].index


@slicer
def age_50below(metadata):
    return metadata[metadata["age"] <= "050Y"].index


@slicer
def female(metadata):
    return metadata[metadata["sex"] == "F"].index


@slicer
def male(metadata):
    return metadata[metadata["sex"] == "M"].index


@slicer
def no_implant(metadata):
    return metadata[metadata["implant"] == "NO"].index


@slicer
def implant(metadata):
    return metadata[metadata["implant"] == "YES"].index
