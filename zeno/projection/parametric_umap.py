from umap.parametric_umap import (  # type: ignore
    load_ParametricUMAP,  # type: ignore
    ParametricUMAP as _ParametricUMAP,  # type: ignore
)  # type: ignore

from .projection_api import ParametricProjectionAbstract


class ParametricUMAP(ParametricProjectionAbstract):
    def __init__(self, instances=None):
        super().__init__(instances)

    def new(self, *args, **kwargs):
        super().new()
        self.projector = _ParametricUMAP(*args, **kwargs)
        return self

    def load(self, filepath=""):
        super().load(filepath)
        self.projector = load_ParametricUMAP(filepath)
        return self

    def save(self, filepath=""):
        super().save(filepath)
        self.projector.save(filepath)
        return self

    def fit(self, instances=None):
        super().fit(instances)
        self.projector.fit(self.instances)
        return self

    def transform(self, instances=None):
        super().transform(instances)
        self.projection = self.projector.transform(self.instances)
        return self
