from cmake_project_creator import dependency, directory, source_directory
from nose.tools import raises


class TestSourceDirectory:

    @raises(ValueError)
    def test_raiseIfInvalidDependency(self):
        description = {
            "name": "tests",
            "type": "tests",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        conan_dependency = dependency.Dependency("conan", "gtest", "1.8.1")
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [conan_dependency])
        source_directory.raise_if_invalid_dependency({
            "type": "internal",
            "link": "proj/othercode/src"
        }, [directory.Directory("projects_root", "path", description, "DummyProject")])

    @raises(KeyError)
    def test_InvalidDependecyWhenAllEmpty(self):
        sd = source_directory.SourceDirectory("projects_root", "root/path", {}, "DummyProject", [])
        source_directory.raise_if_invalid_dependency({}, [])

    def test_get_include_library_of_directory(self):
        path = "root/project/src"
        expected = "project/include"
        assert expected == source_directory.get_include_library_of_directory(
            directory.Directory("projects_root", path, {}, "", []))

    def test_creates_main(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "true",
            "include": "true",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])
        expected = \
"""#include "DummyProject.h"

int main() {
    DummyProject o;
    o.hello();
}
"""
        actual_path, actual_content = sd.create_main(None)
        assert 'root/path/main.cpp' == actual_path
        assert expected == actual_content

    def test_empty_creates_main(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "false",
            "include": "true",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])
        expected = ""
        actual_path, actual_content = sd.create_main(None)
        assert None == actual_path
        assert expected == actual_content

    def test_source_file(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "true",
            "include": "true",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])
        expected = \
"""#include "DummyProject.h"
#include <iostream>

void DummyProject::hello() {
    std::cout << "hello" << std::endl;
}
"""
        actual_path, actual_content = sd.create_source_file(None)
        assert 'root/path/DummyProject.cpp' == actual_path
        assert expected == actual_content

    def test_create_cmakelists_conan(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "true",
            "include": "true",
            "dependencies": [],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])
        expected = \
"""set(BINARY ${CMAKE_PROJECT_NAME}_path)



include_directories(../include)


file(GLOB SOURCES *.cpp)
set(SOURCES ${SOURCES})

add_executable(myProject_path ${SOURCES})

"""
        actual_path, actual_content = sd.create_cmakelists([])
        print(actual_content)
        assert 'root/path/CMakeLists.txt' == actual_path
        assert expected == actual_content

    @raises(ValueError)
    def test_create_cmakelists_conan_error(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "true",
            "include": "true",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])
        sd.create_cmakelists([])


    def test_string_representation(self):
        description = {
            "name": "src",
            "type": "source",
            "library": None,
            "executable": "true",
            "include": "true",
            "dependencies": [{
                "type": "internal",
                "link": "proj/othercode/src"
            }],
            "subdirectories": []
        }
        sd = source_directory.SourceDirectory("projects_root", "root/path", description, "DummyProject", [])

        assert """Directory(path: root/path, description:{'name': 'src', 'type': 'source', 'library': None, 'executable': 'true', 'include': 'true', 'dependencies': [{'type': 'internal', 'link': 'proj/othercode/src'}], 'subdirectories': []})""" == str(sd)
