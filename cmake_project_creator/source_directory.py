from cmake_project_creator import directory


class SourceDirectory(directory.Directory):
    def __init__(self, project_home, path, description, project_file_name, dependencies):
        directory.Directory.__init__(self, project_home, path, description, project_file_name, dependencies)
        self.path = path
        self.has_include = "include" in self.description and self.description["include"] == 'true'

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o) and self.path == o.path and self.has_include == o.has_include

    def create(self, parsed_dirs):
        directory.Directory.make_dirs(self)

        files_to_create = [
            self.create_cmakelists,
            self.create_source_file,
            self.create_main
        ]

        for f in files_to_create:
            self.write_file(*f(parsed_dirs))

    def create_main(self, parsed_dirs):
        if self.description['executable'] == 'true':
            content = \
f"""#include "{self.project_file_name}.{'h' if self.has_include else 'cpp'}"

int main() {{
    {self.project_file_name} o;
    o.hello();
}}
"""
            return f'{self.path}/main.cpp', content
        return None, ""

    def create_source_file(self, parsed_dirs):
        include_statement = f'#include "{self.project_file_name}.h"' if self.has_include else ''
        content = \
f"""{include_statement}
#include <iostream>

void {self.project_file_name}::hello() {{
    std::cout << "hello" << std::endl;
}}
"""
        return f'{self.path}/{self.project_file_name}.cpp', content

    def create_cmakelists(self, parsed_dirs):
        tail = directory.Directory.get_name_suffix(self)
        dependencies = self.description["dependencies"]
        library = self.description["library"] if "library" in self.description else None
        executable = self.description["executable"] if "executable" in self.description else "false"

        link_directories_commands = []
        include_dependent_libraries_commands = []
        for dependency in dependencies:
            if dependency['type'] == "internal":
                print(f"Dependency on {dependency['link']}")
                raise_if_invalid_dependency(dependency, parsed_dirs)

                link_directories_commands.extend(
                    [f"include_directories(${{PROJECT_SOURCE_DIR}}/{get_include_library_of_directory(d)})"
                     for d in parsed_dirs
                     if d.description["type"] and "include" in d.description and d.description[
                         "include"] == "true" and d.get_path_without_project_root() == dependency['link']])
                link_directories_commands.append(f"link_directories(${{PROJECT_SOURCE_DIR}}/{dependency['link']})")

            else:
                print(f"Dependency on {dependency['link']} has an unsupported type: {dependency['type']}")
        executable_command = f"add_executable(myProject_{tail} ${{SOURCES}})" if executable else ""
        library_command = ""
        if library:
            library_command = f"add_library(${{BINARY}}_lib {library.upper()} ${{SOURCES}})"

        link_directories_command = "\n".join(link_directories_commands)
        include_dependent_libraries_command = "\n".join(include_dependent_libraries_commands)

        content = \
f"""set(BINARY ${{CMAKE_PROJECT_NAME}}_{tail})

{link_directories_command}

{"include_directories(../include)" if self.has_include else ""}
{include_dependent_libraries_command}

file(GLOB SOURCES *.cpp)
set(SOURCES ${{SOURCES}})

{executable_command}
{library_command}
"""
        return f'{self.path}/CMakeLists.txt', content


def raise_if_invalid_dependency(dependency, parsed_dirs):
    valid_dependency = False
    for d in parsed_dirs:
        if d.description["type"] and d.description["type"] in ["source",
                                                               "include"] and d.get_path_without_project_root() == \
                dependency["link"]:
            valid_dependency = True
    if not valid_dependency:
        raise ValueError(f"dependent directory {dependency['link']} doesn't exist")


def get_include_library_of_directory(directory):
    return "/".join(directory.path.split('/')[1:-1]) + "/include"
