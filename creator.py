import argparse
import os
import shutil
import stat
'''
TODO:
- add tests
- add runtests.sh
- adds coverage
- comp flags
# - nest everything one more level
# - add lib...
- add a language describing the folder structure
- - needs a path
- - executable / library / with test
- - conan or submodule
- - depenedency among others /probably needs a test

? shared/static
? where to create components
? recursive runtest
-- test implies a dependency on gtest and src on the same level
{
"src" : {"type": "source", "main": "true", "dependencies":[]},
"include" : {"type": "include",},
"test" : {"type": "test", "dependencies":[] },
}
'''

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--projectName',
                        default="myProject",
                        type=str,
                        dest='name',
                        help='Project name to be used'
                        )
    parser.add_argument('-t', '--tests',
                        action='store_true',
                        dest='tests',
                        help='If specified the project will be generated with unit tests'
                        )
    parser.add_argument('-c', '--cleanup',
                        action='store_true',
                        dest='cleanup',
                        help='Tries to remove target directory before running the script'
                        )
    arguments = parser.parse_args()
    return arguments

if __name__ == "__main__":
    arguments = parse_arguments()
    project_dir_name = arguments.name
    project_file_name = project_dir_name.capitalize()

    if arguments.cleanup:
        shutil.rmtree(project_dir_name)

    os.makedirs(f'{project_dir_name}/include')
    os.makedirs(f'{project_dir_name}/src')
    os.makedirs(f'{project_dir_name}/build')
    if arguments.tests:
        with open(f'{project_dir_name}/runTests.sh', "w") as runTests:
            runTests.write(

                f"""
CURRENT_DIR=`pwd`
cd build && rm -rf * && conan install .. -s compiler.libcxx=libstdc++11 && cmake .. && make && ./tests/bin/{project_dir_name}_test
cd $CURRENT_DIR
                """
            )
        st = os.stat(f'{project_dir_name}/runTests.sh')
        os.chmod(f'{project_dir_name}/runTests.sh', st.st_mode | stat.S_IEXEC)

        os.makedirs(f'{project_dir_name}/tests')
        with open(f'{project_dir_name}/conanfile.txt', "w") as conanfile:
            conanfile.write(
                """
[requires]
gtest/1.8.1

[generators]
cmake
                """
            )
        with open(f'{project_dir_name}/tests/main.cpp', "w") as main:
            main.write(
                """
#include "gtest/gtest.h"

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
                """
            )
        with open(f'{project_dir_name}/tests/Test{project_file_name}.cpp', "w") as testSrc:
            testSrc.write(
                    f"""
#include "gtest/gtest.h"
#include "{project_file_name}.h"

TEST(blaTest, test1) {{
    ASSERT_EQ (1, 0);

}}
                """
            )
        with open(f'{project_dir_name}/tests/CMakeLists.txt', "w") as testsCmake:
                testsCmake.write(
                    """

set(BINARY ${CMAKE_PROJECT_NAME}_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)  # Includes the contents of the conanbuildinfo.cmake file.
conan_basic_setup()  # Prepares the CMakeList.txt for Conan.

include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})
target_link_libraries(${BINARY} PUBLIC ${CONAN_LIBS})

add_test(NAME ${BINARY} COMMAND ${BINARY})
        """)

    with open(f'{project_dir_name}/CMakeLists.txt', "w") as cmake:
        content = f"""

cmake_minimum_required(VERSION 3.10)
project({project_dir_name})

set(CMAKE_CXX_STANDARD 17)

{"add_subdirectory(tests)" if arguments.tests else ""}
include_directories(include)

file(GLOB SOURCES src/*.cpp)
set(SOURCES ${{SOURCES}})

add_executable(myProject ${{SOURCES}})
{"add_library(${BINARY}_lib STATIC ${SOURCES})" if arguments.tests else ""}
"""
        cmake.write(content)

    with open(f'{project_dir_name}/include/{project_file_name}.h', "w") as header:
        header.write(
f"""
#pragma once

class {project_file_name} {{
public:
  void hello();
}};
""")

    with open(f'{project_dir_name}/src/{project_file_name}.cpp', "w") as source:
        source.write(
f"""
#include "{project_file_name}.h"
#include <iostream>

void {project_file_name}::hello() {{
    std::cout << "hello" << std::endl;
}}

""")

    with open(f'{project_dir_name}/src/main.cpp', "w") as main:
        main.write(
f"""
#include "{project_file_name}.h"

int main() {{
    {project_file_name} o;
    o.hello();
}}
""")


