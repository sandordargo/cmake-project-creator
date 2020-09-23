import directory


class TestDirectory(directory.Directory):
    def __init__(self, project_home, path, description, project_file_name, dependencies):
        directory.Directory.__init__(self, project_home, path, description, project_file_name, dependencies)
        self.path = path

    def create(self, parsed_dirs):
        directory.Directory.make_dirs(self)

        files_to_create = [
            self.create_cmakelists,
            self.create_source_file,
            self.create_main
        ]
        for f in files_to_create:
            self.write_file(*f())


    def create_cmakelists(self):
        is_conan = any(dependency.type == "conan" for dependency in self.dependencies)
        tail = directory.Directory.get_name_suffix(self)

        return f'{self.path}/CMakeLists.txt', \
f"""set(BINARY ${{CMAKE_PROJECT_NAME}}_{tail}_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${{TEST_SOURCES}})

{"include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)  # Includes the contents of the conanbuildinfo.cmake file. " if is_conan else ""}
{"conan_basic_setup()  # Prepares the CMakeList.txt for Conan." if is_conan else ""}

include_directories(../include)

add_executable(${{BINARY}} ${{TEST_SOURCES}})
{"target_link_libraries(${BINARY} PUBLIC ${CONAN_LIBS})" if is_conan else ""}

add_test(NAME ${{BINARY}} COMMAND ${{BINARY}})
"""

    def create_source_file(self):
        return f'{self.path}/Test{self.project_file_name}.cpp', \
f"""#include "gtest/gtest.h"
#include "{self.project_file_name}.h"

TEST(blaTest, test1) {{
    ASSERT_EQ (1, 0);
}}
"""

    def create_main(self):
        content = \
"""#include "gtest/gtest.h"

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
"""
        return f'{self.path}/main.cpp', content

