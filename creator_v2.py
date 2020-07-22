import argparse
import os
import shutil
import stat
import json

'''
TODO:
Cleanup
Create some files on the fly, so we append lines and write once in the end


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
    parser.add_argument('-d', '--description',
                        default="sample.json",
                        type=str,
                        dest='description',
                        help='Project description'
                        )
    parser.add_argument('-c', '--cleanup',
                        action='store_true',
                        dest='cleanup',
                        help='Tries to remove target directory before running the script'
                        )
    arguments = parser.parse_args()
    return arguments


def create_source_directory(path, description, project_file_name, hasTest=True):
    print("Create source")

    has_include = description["include"] == 'true'

    with open(f'{path}/CMakeLists.txt', "w") as cmake:
        content = f"""

set(BINARY ${{CMAKE_PROJECT_NAME}})

{"include_directories(../include)" if has_include else ""}

file(GLOB SOURCES *.cpp)
set(SOURCES ${{SOURCES}})

add_executable(myProject ${{SOURCES}})
{"add_library(${BINARY}_lib STATIC ${SOURCES})" if hasTest else ""}
    """
        cmake.write(content)

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

    if description['main'] == 'true':
        with open(f'{project_dir_name}/src/main.cpp', "w") as main:
            main.write(
                f"""
        #include "{project_file_name}.{'h' if has_include else 'cpp'}"

        int main() {{
            {project_file_name} o;
            o.hello();
        }}
        """)


def create_include_directory(path, description, project_file_name):
    print("Create include")

    with open(f'{path}/{project_file_name}.h', "w") as header:
        header.write(
f"""
#pragma once

class {project_file_name} {{
public:
  void hello();
}};
""")


def create_test_directory(path, description, project_file_name):
    print("Create test")
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
    with open(f'{path}/CMakeLists.txt', "w") as testsCmake:
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

def create_plumbing(path, hasTest, hasInclude):
    with open(f'{path}/runTests.sh', "w") as runTests:
        runTests.write(

            f"""
    CURRENT_DIR=`pwd`
    cd build && rm -rf * && conan install .. -s compiler.libcxx=libstdc++11 && cmake .. && make && ./tests/bin/{project_dir_name}_test
    cd $CURRENT_DIR
                    """
        )
    st = os.stat(f'{path}/runTests.sh')
    os.chmod(f'{path}/runTests.sh', st.st_mode | stat.S_IEXEC)

    with open(f'{path}/conanfile.txt', "w") as conanfile:
        conanfile.write(
            """
[requires]
gtest/1.8.1

[generators]
cmake
            """
        )
    # with open(f'{path}/CMakeLists.txt', "w") as cmake:
    #         content = f"""
    #
    # cmake_minimum_required(VERSION 3.10)
    # project({path})
    #
    # set(CMAKE_CXX_STANDARD 17)
    #
    # {"add_subdirectory(tests)" if hasTest else ""}
    # {"include_directories(include)" if hasInclude else ""}
    #
    # file(GLOB SOURCES src/*.cpp)
    # set(SOURCES ${{SOURCES}})
    #
    # add_executable(myProject ${{SOURCES}})
    # {"add_library(${BINARY}_lib STATIC ${SOURCES})" if hasTest else ""}
    # """
    #         cmake.write(content)


def collect_subdirectories(paths, directories):
    paths = []
    for dir in directories:
        if dir in ["src", "tests"]:
            paths.append(dir)
    return paths


def create_main_cmakelists(path, projectname, subdirs):
    includes = ""
    for sd in subdirs:
        includes += f'add_subdirectory("{sd}")' + "\n"

    with open(f'{path}/CMakeLists.txt', "w") as cmake:
        content = f"""

    cmake_minimum_required(VERSION 3.10)
    project({projectname})

    set(CMAKE_CXX_STANDARD 17)

    {includes}
    """
        cmake.write(content)


if __name__ == "__main__":
    arguments = parse_arguments()

    with open('sample.json') as json_file:
        project_description = json.load(json_file)

    project_dir_name = project_description['projectName']
    project_file_name = project_description['projectName'].capitalize()
    if arguments.cleanup:
        shutil.rmtree(project_dir_name)

    os.makedirs(os.path.join(project_dir_name, 'build'))
    create_plumbing(project_dir_name, True, True)

    subdirs = collect_subdirectories(project_dir_name, project_description['directories'])
    create_main_cmakelists(project_dir_name, project_description['projectName'], subdirs)

    for dir in project_description['directories']:
        rel_path = os.path.join(project_dir_name, dir)
        print(rel_path)
        os.makedirs(rel_path)
        parent = project_description['directories']
        if project_description['directories'][dir]["type"] == "source":
            create_source_directory(rel_path, project_description['directories'][dir], project_file_name)
        elif project_description['directories'][dir]["type"] == "include":
            create_include_directory(rel_path, project_description['directories'][dir], project_file_name)
        elif project_description['directories'][dir]["type"] == "tests":
            create_test_directory(rel_path, project_description['directories'][dir], project_file_name)
        else:
            print("unsupported type")

