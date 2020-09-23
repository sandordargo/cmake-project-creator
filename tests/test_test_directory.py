import test_directory
import dependency


class Test_TestDirectory:

    def test_create_main(self):
        td = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject", [])
        expected = \
"""#include "gtest/gtest.h"

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
"""
        actual_path, actual_content = td.create_main()
        assert 'root/path/main.cpp' == actual_path
        assert expected == actual_content

    def test_source_file(self):
        td = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject", [])
        expected = \
"""#include "gtest/gtest.h"
#include "DummyProject.h"

TEST(blaTest, test1) {
    ASSERT_EQ (1, 0);
}
"""
        actual_path, actual_content = td.create_source_file()
        assert 'root/path/TestDummyProject.cpp' == actual_path
        assert expected == actual_content

    def test_create_cmakelists_no_conan(self):
        td = test_directory.TestDirectory("projects_root", "root/path", {}, "DummyProject", [])
        expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})




include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})


add_test(NAME ${BINARY} COMMAND ${BINARY})
"""
        actual_path, actual_content = td.create_cmakelists()
        assert 'root/path/CMakeLists.txt' == actual_path
        assert expected == actual_content

    def test_create_cmakelists_conan(self):
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
        td = test_directory.TestDirectory("projects_root", "root/path", description, "DummyProject", [conan_dependency])
        expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path_test)
file(GLOB_RECURSE TEST_SOURCES LIST_DIRECTORIES false *.h *.cpp)

set(SOURCES ${TEST_SOURCES})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)  # Includes the contents of the conanbuildinfo.cmake file. 
conan_basic_setup()  # Prepares the CMakeList.txt for Conan.

include_directories(../include)

add_executable(${BINARY} ${TEST_SOURCES})
target_link_libraries(${BINARY} PUBLIC ${CONAN_LIBS})

add_test(NAME ${BINARY} COMMAND ${BINARY})
"""
        actual_path, actual_content = td.create_cmakelists()
        print(actual_content)
        assert 'root/path/CMakeLists.txt' == actual_path
        assert expected == actual_content