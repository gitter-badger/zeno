from zeno import slicer

classes = (
    "normal",
    "lesion"
)


@slicer
def overall(metadata):
    return metadata.index


@slicer
def by_class(metadata, label_col):
    return [(c, metadata[metadata[label_col] == c].index) for c in classes]


@slicer
def age_above50(metadata):
    # get_age = metadata[metadata["age"]]
    return metadata[metadata["age"] > "050Y"].index


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