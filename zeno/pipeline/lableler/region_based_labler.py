from ..executable_api import Executable


class RegionBasedLabelerNode(Executable):
    def __init__(self):
        self.status = ""

    def __point_in_polygon(self, points, polygon):
        return []

    def execute(self, input):
        self.metadata = self.__point_in_polygon(input, self.model)
        self.input = input

    def pipe_outputs(self):
        return {"input": self.input, "metadata": self.metadata}

    def export_outputs_js(self):
        return {}

    def save_executable(self, path: str):
        with open(path, "w") as out_file:
            out_file.write(self.model)

    def load_executable(self, path: str):
        with open(path, "r") as in_file:
            self.model = in_file.readline()

    def new_executable(self, polygon: list):
        self.model = polygon
