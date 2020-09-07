import directory


class SourceDirectory(directory.Directory):
    def __init__(self, path, description, dependencies):
        self.path = path
        directory.Directory.__init__(self, path, description, dependencies)

    def __str__(self):
        return super(directory.Directory, self).__str__()

    def __repr__(self):
        return super(directory.Directory, self).__repr__()

    def create(self, project_file_name, parsed_dirs):
        directory.Directory.make_dirs(self)
        tail = directory.Directory.get_name_suffix(self)
        has_include = self.description["include"] == 'true'
        is_library = self.description["library"] if "library" in self.description else None
        is_executable = self.description["executable"] if "executable" in self.description else "false"

        create_cmakelists(has_include, self.path, tail, self.description["dependencies"],
                          parsed_dirs, is_executable, is_library)
        create_source_file(has_include, self.path, project_file_name)
        create_main(self.description, has_include, self.path, project_file_name)


def create_main(description, has_include, path, project_file_name):
    if description['executable'] == 'true':
        with open(f'{path}/main.cpp', "w") as main:
            main.write(
                f"""
        #include "{project_file_name}.{'h' if has_include else 'cpp'}"

        int main() {{
            {project_file_name} o;
            o.hello();
        }}
        """)


def create_source_file(has_include, path, project_file_name):
    with open(f'{path}/{project_file_name}.cpp', "w") as source:
        include_statement = f'#include "{project_file_name}.h"' if has_include else ''
        source.write(
            f"""
    {include_statement}
    #include <iostream>

    void {project_file_name}::hello() {{
        std::cout << "hello" << std::endl;
    }}

    """)


def create_cmakelists(has_include, path, tail, dependencies, parsed_dirs, executable=True, library=None):
    link_directories_commands = []
    include_dependent_libraries_commands = []
    for dependency in dependencies:
        if dependency['type'] == "internal":
            print(f"Dependency on {dependency['link']}")
            raise_if_invalid_dependency(dependency, parsed_dirs)

            link_directories_commands.extend([f"include_directories(${{PROJECT_SOURCE_DIR}}/{get_include_library_of_directory(d)})"
                                              for d in parsed_dirs
                                              if d.description["type"] and "include" in d.description and d.description["include"] == "true" and d.get_path_without_project_root() == dependency['link']])
            link_directories_commands.append(f"link_directories(${{PROJECT_SOURCE_DIR}}/{dependency['link']})")

        else:
            print(f"Dependency on {dependency['link']} has an unsupported type: {dependency['type']}")
    executable_command = f"add_executable(myProject_{tail} ${{SOURCES}})" if executable else ""
    library_command = ""
    if library:
        library_command =  f"add_library(${{BINARY}}_lib {library.upper()} ${{SOURCES}})"

    link_directories_command = "\n".join(link_directories_commands)
    include_dependent_libraries_command = "\n".join(include_dependent_libraries_commands)

    with open(f'{path}/CMakeLists.txt', "w") as cmake:
        content = f"""

set(BINARY ${{CMAKE_PROJECT_NAME_{tail}}})

{link_directories_command}

{"include_directories(../include)" if has_include else ""}
{include_dependent_libraries_command}

file(GLOB SOURCES *.cpp)
set(SOURCES ${{SOURCES}})

{executable_command}
{library_command}
    """
        cmake.write(content)


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
