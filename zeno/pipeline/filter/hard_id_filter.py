class HardIdFilterNode:
    def __init__(self):
        self.status = ""

    def fit(self, input):
        return self

    def __get_df_rows(self, dataframe, column, list_to_get=None):
        if list_to_get is None:
            return []
        return dataframe[dataframe[column].isin(list_to_get)]

    def get_ids(self, table, id_column, ids):
        return self.__get_df_rows(table, id_column, ids)

    def transform(self, input):
        self.input = input
        self.filter = self.get_ids(input["input_table"], **self.model)
        return self

    def pipe_outputs(self):
        self.input["input_table"] = self.filter
        return {**self.input}

    def export_outputs_js(self):
        return {"filter": self.model["ids"]}

    def save(self, path: str):
        with open(path, "w") as out_file:
            out_file.write(self.model)

    def load(self, path: str):
        with open(path, "r") as in_file:
            self.model = in_file.readline()

    def init(self, ids: list, id_column: str):
        self.model = {"ids": ids, "id_column": id_column}
