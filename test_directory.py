import directory


class TestDirectory(directory.Directory):
    def __init__(self, path):
        self.path = path
        directory.Directory.__init__(self, path)

    def create(self, description, project_file_name):
        directory.Directory.make_dirs(self)
        tail = directory.Directory.get_name_suffix(self)

        create_cmakelists(self.path, tail)
        create_source_file(self.path, project_file_name)
        create_main(self.path)


def create_cmakelists(path, tail):
    with open(f'{path}/CMakeLists.txt', "w") as testsCmake:
        testsCmake.write(
            f"""

set(BINARY ${{CMAKE_PROJECT_NAME}}_{tail}_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${{TEST_SOURCES}})

include(${{CMAKE_BINARY_DIR}}/conanbuildinfo.cmake)  # Includes the contents of the conanbuildinfo.cmake file.
conan_basic_setup()  # Prepares the CMakeList.txt for Conan.

include_directories(../include)

add_executable(${{BINARY}} ${{TEST_SOURCES}})
target_link_libraries(${{BINARY}} PUBLIC ${{CONAN_LIBS}})

add_test(NAME ${{BINARY}} COMMAND ${{BINARY}})
    """)


def create_source_file(path, project_file_name):
    with open(f'{path}/Test{project_file_name}.cpp', "w") as testSrc:
        testSrc.write(
            f"""
#include "gtest/gtest.h"
#include "{project_file_name}.h"

TEST(blaTest, test1) {{
    ASSERT_EQ (1, 0);

}}
                """
        )


def create_main(path):
    with open(f'{path}/main.cpp', "w") as main:
        main.write(
            """
#include "gtest/gtest.h"

int main(int argc, char **argv) {
::testing::InitGoogleTest(&argc, argv);
return RUN_ALL_TESTS();
}
            """
        )
