from cmake_project_creator import test_directory, dependency

import nose.tools

def test_create_main():
    test_dir = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject",
                                            [dependency.Dependency("conan", "gtest", "1.8.1")])
    expected = \
"""#include <gtest/gtest.h>

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
"""
    actual_path, actual_content = test_dir.create_main({})
    nose.tools.eq_(actual_path, 'root/path/main.cpp')
    nose.tools.eq_(actual_content, expected)


def test_source_file():
    test_dir = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject",
                                            [dependency.Dependency("conan", "gtest", "1.8.1")])
    expected = \
"""#include <gtest/gtest.h>
#include "DummyProject.h"

TEST(blaTest, test1) {
    DummyProject x;
    x.hello();
    ASSERT_EQ (1, 0);
}
"""
    actual_path, actual_content = test_dir.create_source_file({})

    nose.tools.eq_(actual_path, 'root/path/TestDummyProject.cpp')
    nose.tools.eq_(actual_content, expected)


def test_create_cmakelists_no_conan():
    test_dir = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject", [])
    expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})




include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})
target_link_libraries(${BINARY} PUBLIC)

add_test(NAME ${BINARY} COMMAND ${BINARY})
"""
    actual_path, actual_content = test_dir.create_cmakelists({})
    nose.tools.eq_(actual_path, 'root/path/CMakeLists.txt')
    nose.tools.eq_(actual_content, expected)


def test_create_cmakelists_conan():
    description = {
        "name": "tests",
        "type": "tests",
        "dependencies": [{
            "type": "conan",
            "name": "gtest",
            "version": "1.8.1"
        }],
        "subdirectories": []
    }
    conan_dependency = dependency.Dependency("conan", "gtest", "1.8.1")
    test_dir = test_directory.TestDirectory("projects_root", "root/path", description,
                                      "DummyProject", [conan_dependency])
    expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()  # Prepares the CMakeList.txt for Conan.

include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})
target_link_libraries(${BINARY} PUBLIC ${CONAN_LIBS})

add_test(NAME ${BINARY} COMMAND ${BINARY})
"""
    actual_path, actual_content = test_dir.create_cmakelists({})
    print(actual_content)
    nose.tools.eq_(actual_path, 'root/path/CMakeLists.txt')
    nose.tools.eq_(actual_content, expected)

def test_create_cmakelists_conan2():
    description = {
        "name": "tests",
        "type": "tests",
        "dependencies": [{
            "type": "conan2",
            "name": "gtest",
            "version": "1.8.1"
        }],
        "subdirectories": []
    }
    conan_dependency = dependency.Dependency("conan2", "gtest", "1.8.1")
    test_dir = test_directory.TestDirectory("projects_root", "root/path", description,
                                      "DummyProject", [conan_dependency])
    expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})
find_package(GTest REQUIRED)



include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})
target_link_libraries(${BINARY} PUBLIC gtest::gtest)

add_test(NAME ${BINARY} COMMAND ${BINARY})
"""
    actual_path, actual_content = test_dir.create_cmakelists({})
    print(actual_content)
    nose.tools.eq_(actual_path, 'root/path/CMakeLists.txt')
    nose.tools.eq_(actual_content, expected)
