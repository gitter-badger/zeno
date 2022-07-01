from abc import ABC, abstractmethod
from typing import Union


# def get_XY_ndarray(ndarray):
#     return ndarray[:, 0], ndarray[:, 1]


# def plot_3d(x, y, z, colors=[]):
#     import matplotlib.pyplot as plt

#     plt.rcParams["figure.figsize"] = [7.00, 3.50]
#     plt.rcParams["figure.autolayout"] = True
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection="3d")
#     if len(colors) == 0:
#         colors = z
#     ax.scatter(x, y, z, c=colors, alpha=0.8)
#     plt.show()


# def extract_dims_3D(data):
#     x = data[:, 0]
#     y = data[:, 1]
#     z = data[:, 2]
#     return x, y, z


class ParametricProjectionAbstract(ABC):
    def __init__(self, instances=None):
        self.projector = None
        self.projection = None
        self.instances = instances

    @abstractmethod
    def save(self, filepath: Union[None, str] = None):
        assert self.projector is not None, "load the projection first with load()"
        assert filepath is not None, "Supply a filepath that is a string"

    @abstractmethod
    def new(self):
        pass

    @abstractmethod
    def load(self, filepath: Union[None, str] = None):
        assert filepath is not None, "Supply a filepath that is a string"

    @abstractmethod
    def fit(self, instances=None):
        if instances is not None:
            self.instances = instances

    @abstractmethod
    def transform(self, instances=None):
        if instances is not None:
            self.instances = instances

    def fit_transform(self, instances: list):
        self.fit(instances)
        self.projection = self.transform(instances)

        return self.projection

    # def plot_projection_2D(self,
    #                         extract_xy=get_XY_ndarray,
    #                         *plot_args,
    #                         **plot_kwargs):
    #     if self.projection is not None:
    #         import matplotlib.pyplot as plt

    #         x, y = extract_xy(self.projection)
    #         plt.scatter(x, y, *plot_args, **plot_kwargs)

    #     return self

    # def create_fake_3D_data(self, n_samples=1000, centers=[[0, 1, 2], [-5, -5, -5]]):
    #     from sklearn.datasets import make_blobs

    #     self.instances, self.colors = make_blobs(
    #         n_samples=n_samples, n_features=3, centers=centers
    #     )
    #     return self

    # def plot_instances_3D(self):
    #     if self.instances is not None:
    #         x, y, z = extract_dims_3D(self.instances)
    #         plot_3d(x, y, z, self.colors)

    def outputs(self):
        return self.projection

    def __call__(self, instances):
        self.transform(instances)
        return self.outputs()
