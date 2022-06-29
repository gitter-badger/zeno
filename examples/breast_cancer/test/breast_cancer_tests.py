import os

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from examples.breast_cancer.vgg_old import vgg16_bn
from PIL import Image
from sklearn.metrics import f1_score, recall_score
from zeno import ZenoOptions, metric_function, predict_function

transform_image = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
)

classes = ("normal", "lesion")


num_classes = 2
image_res = 512
transform_image = transforms.Compose(
    [
        transforms.Resize(image_res),
        transforms.ToTensor(),
    ]
)


# Type 1
# @load_model
# def load_model(model_path):
#     # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = vgg16_bn(pretrained=False)
#     model.classifier.fc8a = nn.Linear(model.classifier.fc8a.in_features, num_classes)
#     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

#     def pred(instances):
#         imgs = torch.stack([transform_image(img) for img in instances], dim=0)
#         with torch.no_grad():
#             out = model(imgs)
#             prob = F.softmax(out, dim=1)
#         return [classes[i] for i in torch.argmax(prob, dim=1).detach().numpy()]
#     return pred

# Type 2
# @load_model
# def load_model(model_path):
#     # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = vgg16_bn(pretrained=False)
#     model.classifier.fc8a = nn.Linear(model.classifier.fc8a.in_features, num_classes)
#     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))

#     def pred(instances):
#         imgs = torch.stack([transform_image(img) for img in instances], dim=0)
#         prob = []
#         with torch.no_grad():
#             for img in imgs:
#                 out = model(img)
#                 p = F.softmax(out, dim=1)
#                 prob.append(classes[torch.argmax(p, dim=1).detach().numpy()])
#         return prob
#     return pred

# Type 3
@predict_function
def load_model(model_path):
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = vgg16_bn(pretrained=False)
    model.classifier.fc8a = nn.Linear(model.classifier.fc8a.in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))

    # a dict to store the activations
    activation = {}

    def getActivation(name):
        # the hook signature
        def hook(model, input, output):
            activation[name] = output.detach()

        return hook

    # register forward hooks on the layers of choice
    h = model.classifier.fc7.register_forward_hook(getActivation("emb"))

    def pred(df, ops: ZenoOptions):
        imgs = torch.stack(
            [
                transform_image(Image.open(os.path.join(ops.data_path, img)))
                for img in df[ops.data_column]
            ],
            dim=0,
        )
        prob = []
        emb = None
        with torch.no_grad():
            for img in imgs:
                out = model(img.unsqueeze(0))
                if emb is None:
                    emb = activation["emb"]
                else:
                    emb = torch.cat((emb, activation["emb"]), 0)
                p = F.softmax(out, dim=1)
                index = (torch.argmax(p, dim=1).detach().numpy())[0]
                prob.append(classes[index])
        h.remove()
        return prob, emb.detach().numpy()
        # batches

    return pred


# @load_model
# def load_model(model_path):
#     # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = vgg16_bn(pretrained=False)
#     model.classifier.fc8a = nn.Linear(model.classifier.fc8a.in_features, num_classes)
#     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
#     # a dict to store the activations
#     activation = {}

#     def getActivation(name):
#         # the hook signature
#         def hook(model, input, output):
#             activation[name] = output.detach()
#         return hook

#     # register forward hooks on the layers of choice
#     h = model.classifier.relu7.register_forward_hook(getActivation('emb'))

#     def pred(instances):
#         imgs = torch.stack([transform_image(img) for img in instances], dim=0)
#         emb = []
#         with torch.no_grad():
#             out = model(imgs)
#             emb.append(activation['emb'])
#             prob = F.softmax(out, dim=1)
#         h.remove()
#         return [classes[i] for i in torch.argmax(prob, dim=1).detach().numpy()], emb[0].detach().numpy()
#     return pred


@metric_function
def accuracy(df, ops: ZenoOptions):
    if len(df) == 0:
        return 0
    return 100 * (df[ops.label_column] == df[ops.output_column]).sum() / len(df)


@metric_function
def recall(df, ops: ZenoOptions):
    return 100 * recall_score(df[ops.label_column], df[ops.output_column])


@metric_function
def f1(df, ops: ZenoOptions):
    return 100 * f1_score(df[ops.label_column], df[ops.output_column])
