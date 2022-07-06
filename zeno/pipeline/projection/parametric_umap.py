from umap.parametric_umap import (  # type: ignore
    load_ParametricUMAP,  # type: ignore
    ParametricUMAP,  # type: ignore
)  # type: ignore

from ..executable_api import Executable


class ParametricUMAPNode(Executable):
    def __init__(self):
        self.status = ""

    def execute(self, input):
        self.projections = self.model.fit_transform(input)
        self.input = input

    def pipe_outputs(self):
        return {"input": self.input, "projection2D": self.projections}

    def export_outputs_js(self):
        return {"projection2D": self.projections}

    def save_executable(self, path: str):
        self.model.save(path)

    def load_executable(self, path: str):
        self.model = load_ParametricUMAP(path)

    def new_executable(self, *args, **kwargs):
        self.model = ParametricUMAP(*args, **kwargs)
