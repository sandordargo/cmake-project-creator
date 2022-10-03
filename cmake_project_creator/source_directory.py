from cmake_project_creator import directory


class SourceDirectory(directory.Directory):
    def __init__(self, project_home, path, description, project_file_name, dependencies):
        super().__init__(project_home,
                         path,
                         description,
                         project_file_name,
                         dependencies)
        self.path = path
        self.has_include = "include" in self.description and self.description["include"] == 'true'

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o) and self.path == o.path and self.has_include == o.has_include

    def create(self, parsed_dirs):
        directory.Directory.make_dirs(self)

        file_creators = [
            self.create_cmakelists,
            self.create_source_file,
            self.create_main
        ]

        for file_creator in file_creators:
            self.write_file(*file_creator(parsed_dirs.values()))

    def create_main(self, _):
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

    def create_source_file(self, _):
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
        dependencies = self.description["dependencies"]

        is_conan = any(dependency["type"] == "conan" for dependency in self.description["dependencies"])

        link_directories_commands = []
        include_dependent_libraries_commands = []
        for dependency in dependencies:
            if dependency['type'] == "internal":
                print(f"Dependency on {dependency['link']}")
                raise_if_invalid_dependency(dependency, parsed_dirs)

                link_directories_commands.extend(self.build_include_directories_for_dependency(
                    parsed_dirs, dependency))
                link_directories_commands.append(
                    f"link_directories(${{PROJECT_SOURCE_DIR}}/{dependency['link']})")

            elif dependency['type'] == "conan":
                pass
            else:
                print(f"Dependency on {dependency['link']} has an unsupported type: \
{dependency['type']}")

        link_directories_command = "\n".join(link_directories_commands)
        include_dependent_libraries_command = "\n".join(include_dependent_libraries_commands)

        content = \
            f"""set(BINARY ${{CMAKE_PROJECT_NAME}}_{directory.Directory.get_name_suffix(self)})

{"include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)" if is_conan else ""}
{"conan_basic_setup()  # Prepares the CMakeList.txt for Conan." if is_conan else ""}

{link_directories_command}

{"include_directories(../include)" if self.has_include else ""}
{include_dependent_libraries_command}

file(GLOB SOURCES *.cpp)
set(SOURCES ${{SOURCES}})

{self.build_executable_command()}
{self.build_library_command()}
"""
        return f'{self.path}/CMakeLists.txt', content

    def build_executable_command(self):
        executable = self.description["executable"] if "executable" in self.description else "false"
        if not executable:
            return ""
        is_custom_name_defined = "executable_name" in self.description
        executable_name = self.description["executable_name"] if is_custom_name_defined \
            else f"{self.project_file_name}_{directory.Directory.get_name_suffix(self)}"

        executable_command = f"add_executable({executable_name} ${{SOURCES}})"
        return executable_command

    def build_library_command(self):
        library = self.description["library"] if "library" in self.description else None
        if not library:
            return ""
        is_custom_executable_name_defined = "executable_name" in self.description
        executable_name = self.description["executable_name"] if is_custom_executable_name_defined \
            else f"{self.project_file_name}_{directory.Directory.get_name_suffix(self)}"

        is_custom_name_defined = "library_name" in self.description
        library_name = self.description["library_name"] if is_custom_name_defined \
            else f"${{BINARY}}_lib"

        library_command = \
            f"""add_library({library_name} {library.upper()} ${{SOURCES}})
target_link_libraries({executable_name} ${{BINARY}}_lib)"""
        return library_command

    def build_include_directories_for_dependency(self, parsed_dirs, dependency):
        return [f"include_directories(${{PROJECT_SOURCE_DIR}}/" \
                f"{get_include_library_of_directory(d)})"
                for d in parsed_dirs
                if d.description["type"] and
                "include" in d.description and
                d.description["include"] == "true" and
                d.get_path_without_project_root() == dependency['link']]


def raise_if_invalid_dependency(dependency, parsed_dirs):
    valid_dependency = False
    for directory in parsed_dirs:
        if directory.description["type"] and \
                directory.description["type"] in ["source", "include"] and \
                directory.get_path_without_project_root() == dependency["link"]:
            valid_dependency = True
            break
    if not valid_dependency:
        raise ValueError(f"dependent directory {dependency['link']} doesn't exist")


def get_include_library_of_directory(directory):
    return "/".join(directory.path.split('/')[1:-1]) + "/include"
