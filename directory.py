import os


class Directory:
    def __init__(self, path):
        self.path = path

    def make_dirs(self):
        print("Create directory: ", self.path)
        os.makedirs(self.path)

    def get_name_suffix(self):
        if "/" in self.path:
            tail = self.path.split('/')[-2]
        else:
            tail = self.path
        print("tail is ", tail)
        return tail
