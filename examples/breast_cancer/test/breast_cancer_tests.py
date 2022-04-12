import torchvision.transforms as transforms
import PIL
import torch
import os
from zeno import load_data, load_model, metric
from models.breast_cancer.vgg_old import vgg16_bn
import numpy as np
import torch.nn as nn
import torch.nn.functional as F

transform_image = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
)

classes = (
    "lesion",
    "normal"
)


num_classes = 2
image_res = 512
transform_image = transforms.Compose(
    [transforms.Resize(image_res), transforms.ToTensor(),
])


@load_model
def load_model(model_path):
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = vgg16_bn(pretrained=False)
    model.classifier.fc8a = nn.Linear(model.classifier.fc8a.in_features, num_classes)
    model.load_state_dict(torch.load("models/breast_cancer/best_model.pth", map_location=torch.device('cpu')))

    def pred(instances):
        imgs = torch.stack([transform_image(img) for img in instances], dim = 0)
        with torch.no_grad():
            out = model(imgs)
            prob = F.softmax(out, dim=1)
        return [classes[i] for i in torch.argmax(prob, dim = 1).detach().numpy()]

    return pred

@load_data
def load_data(df_metadata, data_path):
    return [PIL.Image.open(os.path.join(data_path, img)) for img in df_metadata.patch_dir]

@metric
def accuracy(output, metadata, label_col):
    return metadata[label_col] == output
