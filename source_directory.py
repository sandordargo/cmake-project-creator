import directory


class SourceDirectory(directory.Directory):
    def __init__(self, path):
        self.path = path
        directory.Directory.__init__(self, path)

    def create(self, description, project_file_name):
        directory.Directory.make_dirs(self)
        tail = directory.Directory.get_name_suffix(self)
        has_include = description["include"] == 'true'

        create_cmakelists(has_include, self.path, tail, description["main"], description["library"])
        create_source_file(has_include, self.path, project_file_name)
        create_main(description, has_include, self.path, project_file_name)


def create_main(description, has_include, path, project_file_name):
    if description['main'] == 'true':
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


def create_cmakelists(has_include, path, tail, executable=True, library=None):
    executable_command = f"add_executable(myProject_{tail} ${{SOURCES}})" if executable else ""
    library_command = ""
    if library:
        library_command =  f"add_library(${{BINARY}}_lib {library.upper()} ${{SOURCES}})"

    with open(f'{path}/CMakeLists.txt', "w") as cmake:
        content = f"""

set(BINARY ${{CMAKE_PROJECT_NAME_{tail}}})

{"include_directories(../include)" if has_include else ""}

file(GLOB SOURCES *.cpp)
set(SOURCES ${{SOURCES}})

{executable_command}
{library_command}
    """
        cmake.write(content)
