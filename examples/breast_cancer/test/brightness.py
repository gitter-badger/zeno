import PIL
from zeno import slicer, transform, preprocess

# Ref https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def get_brightness(im):
    im = im.convert('L')
    stat = PIL.ImageStat.Stat(im)
    return stat.mean[0]


@preprocess
def brightness(images):
    return [get_brightness(im) for im in images]


@slicer
def low_exposure(metadata):
    return metadata[metadata["brightness"] < 50].index


@slicer
def high_exposure(metadata):
    return metadata[metadata["brightness"] > 90].index

