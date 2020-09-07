import os


class Directory:
    def __init__(self, path, description, dependencies = None):
        self.path = path
        self.description = description
        self.dependencies = dependencies

    def __str__(self):
        return f"Directory(path: {self.path}, description:{self.description})"

    def __repr__(self):
        return f"Directory(path: {self.path}, description:{self.description})"

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

    def get_path_without_project_root(self):
        return "/".join(self.path.split('/')[1:])
