from .projection.parametric_umap import ParametricUMAPNode
from pandas import DataFrame


class Pipeline:
    def __init__(self, table: DataFrame, model_name: str, id_column: str):
        self.model_name = model_name
        self.id_column = id_column
        self.global_table = table
        self.input_table = table.copy(deep=False)

        self.io_memory = {
            "model": model_name,
            "input_table": self.input_table,
            "global_table": self.global_table,
            "id_column": self.id_column,
        }

        # the nodes to update
        self.init_projection = None
        self.mutators = []
        self.weak_labeler = None

    def set_init_projection(self):
        new_node = ParametricUMAPNode()
        new_node.init(n_components=2, n_epochs=20)
        new_node.fit(input=self.io_memory)
        new_node.transform(input=self.io_memory)
        self.init_projection = new_node

        return self.init_projection.export_outputs_js()
