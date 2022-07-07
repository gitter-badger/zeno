from umap.parametric_umap import (  # type: ignore
    load_ParametricUMAP,  # type: ignore
    ParametricUMAP,  # type: ignore
)  # type: ignore

import numpy as np
from ...classes import ZenoColumn, ZenoColumnType


class ParametricUMAPNode:
    def __init__(self):
        self.status = ""

    def get_embeddings(self, table, model_name):
        embedding_col = ZenoColumn(
            column_type=ZenoColumnType.EMBEDDING,
            name=model_name,
            model=model_name,
            transform="",
        )
        embedding_col_name = str(embedding_col)
        embeddings_pd_col = table[embedding_col_name]  # type: ignore
        embeddings = np.stack(embeddings_pd_col.to_numpy())
        return embeddings

    def fit(self, input: dict):
        embeddings = self.get_embeddings(input["table"], input["model"])
        self.model.fit(embeddings)

        return self

    def transform(self, input: dict):
        embeddings = self.get_embeddings(input["table"], input["model"])
        self.projections = self.model.transform(embeddings)
        self.input = input

        return self

    def pipe_outputs(self):
        self.input["projection2D"] = self.projections
        return self.input

    def export_outputs_js(self):
        return {"projection2D": self.projections}

    def save(self, path: str):
        self.model.save(path)

    def load(self, path: str):
        self.model = load_ParametricUMAP(path)

    def init(self, *args, **kwargs):
        self.model = ParametricUMAP(*args, **kwargs)
