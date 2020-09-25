import os


class Directory:
    def __init__(self, output_root, path, description, project_file_name, dependencies=None):
        self.output_root = output_root
        self.path = path
        self.description = description
        self.project_file_name = project_file_name
        self.dependencies = dependencies

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Directory(path: {self.path}, description:{self.description})"

    def make_dirs(self):
        print("Create directory: ", self.path)
        os.makedirs(os.path.join(self.output_root, self.path))

    def get_name_suffix(self):
        if "/" in self.path and len(self.path.split('/')) > 2:
            tail = self.path.split('/')[-2]
        elif "/" in self.path and len(self.path.split('/')) > 1:
            tail = self.path.split('/')[-1]
        else:
            tail = self.path
        print(self.path)
        print("tail is ", tail)
        return tail

    def get_path_without_project_root(self):
        return "/".join(self.path.split('/')[1:])

    def write_file(self, full_path, content):
        if full_path and content:
            with open(os.path.join(self.output_root, full_path), "w") as file:
                file.write(content)
