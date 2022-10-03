"""
This modules represents a CMake test module
"""
from cmake_project_creator import directory


class TestDirectory(directory.Directory):
    """
    This class creates a test module of a Cmake project
    """

    def __init__(self, project_home, path, description, project_file_name, dependencies):
        super().__init__(project_home,
                         path,
                         description,
                         project_file_name,
                         dependencies)

    def create(self, parsed_dirs):
        """
        Creates all the files needed for a test module
        """
        directory.Directory.make_dirs(self)

        file_creators = [
            self.create_cmakelists,
            self.create_source_file,
            self.create_main
        ]
        for file_creator in file_creators:
            self.write_file(*file_creator(parsed_dirs))

    def create_cmakelists(self, parsed_dirs):
        """
        :return: the path and content of CMakelists.txt in a test module
        """
        is_conan = any(dependency.type == "conan" for dependency in self.dependencies)
        parent_path_to_look_for = self.path[:self.path.rfind('/')]

        is_there_source_dir = any(k.startswith(parent_path_to_look_for) and  v.description["type"] == "source" and v.description["library"] is not None 
                                  for k, v in parsed_dirs.items())

        src_lib_to_link = "${CMAKE_PROJECT_NAME}_src_lib" if is_there_source_dir else ""

        tail = directory.Directory.get_name_suffix(self)

        return f'{self.path}/CMakeLists.txt', \
               f"""set(BINARY ${{CMAKE_PROJECT_NAME}}_{tail}_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${{TEST_SOURCES}})

{"include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)" if is_conan else ""}
{"conan_basic_setup()  # Prepares the CMakeList.txt for Conan." if is_conan else ""}

include_directories(../include)

add_executable(${{BINARY}} ${{TEST_SOURCES}})
{str("target_link_libraries(${BINARY} PUBLIC ${CONAN_LIBS} " + src_lib_to_link).strip() + ")" if is_conan else ""}

add_test(NAME ${{BINARY}} COMMAND ${{BINARY}})
"""

    def create_source_file(self, _):
        """
        :return: the path and content of cpp file in a test module
        """
        return f'{self.path}/Test{self.project_file_name}.cpp', \
               f"""#include "gtest/gtest.h"
#include "{self.project_file_name}.h"

TEST(blaTest, test1) {{
    ASSERT_EQ (1, 0);
}}
"""

    def create_main(self, _):
        """
        :return: the path and content of main.cpp in a test module
        """
        content = \
            """#include "gtest/gtest.h"

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
"""
        return f'{self.path}/main.cpp', content
