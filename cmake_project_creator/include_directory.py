from cmake_project_creator import directory


class IncludeDirectory(directory.Directory):
    def __init__(self, project_home, path, description, project_file_name, dependencies):
        self.path = path
        directory.Directory.__init__(self, project_home, path, description, project_file_name, dependencies)

    def create(self, parsed_dirs):
        directory.Directory.make_dirs(self)

        self.write_file(*self.create_header_content())

    def create_header_content(self):
        return f'{self.path}/{self.project_file_name}.h', \
f"""#pragma once

class {self.project_file_name} {{
public:
  void hello();
}};
"""
