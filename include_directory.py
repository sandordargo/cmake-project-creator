import directory


class IncludeDirectory(directory.Directory):
    def __init__(self, path, description, dependencies):
        self.path = path
        directory.Directory.__init__(self, path, description, dependencies)

    def create(self, project_file_name, parsed_dirs):
        directory.Directory.make_dirs(self)
        with open(f'{self.path}/{project_file_name}.h', "w") as header:
            header.write(
                f"""
        #pragma once

        class {project_file_name} {{
        public:
          void hello();
        }};
        """)

