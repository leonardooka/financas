

class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.categoria = None
        self.file = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r")
        self.categoria = {}

        for line in self.file:
            categoria = line.strip()
            self.categorias[line] = categoria
            print("categoria")

        self.file.close()