import project_creator
import source_directory
import dependency
from nose.tools import *

DIRECTORIES = [{
    "name": "proj",
    "type": "intermediate",
    "subdirectories": [

        {
            "name": "code",
            "type": "intermediate",
            "subdirectories": [{
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
            },
                {
                    "name": "include",
                    "type": "include",
                    "subdirectories": []
                },
                {
                    "name": "tests",
                    "type": "tests",
                    "dependencies": [{
                        "type": "conan",
                        "name": "gtest",
                        "version": "1.8.1"
                    }],
                    "subdirectories": []
                }
            ]
        },
        {
            "name": "othercode",
            "type": "intermediate",
            "subdirectories": [{
                "name": "src",
                "type": "source",
                "library": "static",
                "executable": "true",
                "include": "true",
                "dependencies": [],
                "subdirectories": []
            },
                {
                    "name": "include",
                    "type": "include",
                    "subdirectories": []
                },
                {
                    "name": "tests",
                    "type": "tests",
                    "dependencies": [{
                        "type": "conan",
                        "name": "gtest",
                        "version": "1.8.1"
                    }],
                    "subdirectories": []
                }
            ]
        }
    ]
}]


class TestProjectCreator:

    def test_collect_cmake_subdirectories(self):
        paths = project_creator.collect_cmake_subdirectories(DIRECTORIES)
        assert ['proj/code/src', 'proj/code/tests', 'proj/othercode/src', 'proj/othercode/tests'] == paths

    def test_parse_directories(self):
        single_directory = [{
            "name": "src",
            "type": "source",
            "executable": "true",
            "include": "true",
            "dependencies": [],
            "subdirectories": []
        }]
        expected = [source_directory.SourceDirectory("projects_root", "src", single_directory[0], "DummyProject", [])]
        parsed_directories = project_creator.parse_directories(single_directory, "projects_root", "", "DummyProject")

        assert expected == parsed_directories

    def test_collect_conan_dependencies(self):
        single_directory = [{
            "name": "src",
            "type": "source",
            "executable": "true",
            "include": "true",
            "dependencies": [{
            "type": "internal",
            "link": "proj/othercode/src"
        }],
            "subdirectories": []
        }]



        conan_dependency = dependency.Dependency("conan", "gtest", "1.8.1")

        parsed_directories = [source_directory.SourceDirectory("projects_root", "src", single_directory[0], "DummyProject", [conan_dependency])]
        print(project_creator.collect_conan_dependencies(parsed_directories))
        assert {'gtest': '1.8.1'} == project_creator.collect_conan_dependencies(parsed_directories)

    @raises(ValueError)
    def test_conflicting_conan_deps(self):
        single_directory = [{
            "name": "src",
            "type": "source",
            "executable": "true",
            "include": "true",
            "dependencies": [{
            "type": "internal",
            "link": "proj/othercode/src"
        }],
            "subdirectories": []
        }]



        conan_dependency = dependency.Dependency("conan", "gtest", "1.8.1")
        conan_dependency2 = dependency.Dependency("conan", "gtest", "1.7.1")

        parsed_directories = [source_directory.SourceDirectory("projects_root", "src", single_directory[0], "DummyProject", [conan_dependency, conan_dependency2])]
        print(project_creator.collect_conan_dependencies(parsed_directories))

    def test_create_main_cmakelists(self):
        expected = \
"""cmake_minimum_required(VERSION 3.10)
project(dummy)
set(CMAKE_CXX_STANDARD 17)

add_subdirectory("src")
add_subdirectory("test")
"""
        actual_path, actual_content = project_creator.create_main_cmakelists("projects_root", "dummy", ["src", "test"])

        assert expected == actual_content
        assert "projects_root/dummy/CMakeLists.txt" == actual_path