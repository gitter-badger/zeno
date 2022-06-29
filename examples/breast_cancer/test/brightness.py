from PIL import Image, ImageStat
from zeno import distill_function
import os

# Ref https://stackoverflow.com/questions/3490727/what-are-some-methods-to-analyze-image-brightness-using-python
def get_brightness(im):
    im = im.convert("L")
    stat = ImageStat.Stat(im)
    return stat.mean[0]


@distill_function
def brightness(df, ops):
    imgs = [Image.open(os.path.join(ops.data_path, img)) for img in df[ops.data_column]]
    return [get_brightness(im) for im in imgs]
