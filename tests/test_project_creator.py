from nose.tools import raises
import nose.tools

from cmake_project_creator import dependency, project_creator, source_directory

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


def test_collect_cmake_subdirectories():
    paths = project_creator.collect_cmake_subdirectories(DIRECTORIES)
    nose.tools.eq_(['proj/code/src', 'proj/code/tests',
            'proj/othercode/src', 'proj/othercode/tests'], paths)


def test_parse_directories():
    single_directory = [{
        "name": "src",
        "type": "source",
        "executable": "true",
        "include": "true",
        "dependencies": [],
        "subdirectories": []
    }]
    expected = {"src": source_directory.SourceDirectory("projects_root", "src", single_directory[0],
                                                 "DummyProject", [])}
    parsed_directories = project_creator.parse_directories(single_directory,
                                                           "projects_root", "", "DummyProject")
    nose.tools.eq_(expected, parsed_directories)


def test_collect_conan_dependencies():
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

    parsed_directories = [
        source_directory.SourceDirectory("projects_root", "src", single_directory[0],
                                         "DummyProject", [conan_dependency])]
    nose.tools.eq_({'gtest': '1.8.1'}, project_creator.collect_conan_dependencies(parsed_directories))

def test_collect_conan2_dependencies():
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

    conan_dependency = dependency.Dependency("conan2", "gtest", "1.8.1")

    parsed_directories = [
        source_directory.SourceDirectory("projects_root", "src", single_directory[0],
                                         "DummyProject", [conan_dependency])]
    nose.tools.eq_({'gtest': '1.8.1'}, project_creator.collect_conan2_dependencies(parsed_directories))



@raises(ValueError)
def test_conflicting_conan_deps():
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

    parsed_directories = [
        source_directory.SourceDirectory("projects_root", "src", single_directory[0],
                                         "DummyProject", [conan_dependency, conan_dependency2])]
    print(project_creator.collect_conan_dependencies(parsed_directories))


@raises(ValueError)
def test_unsupported_cpp_standard():
    _, _ = project_creator.create_main_cmakelists("projects_root", "dummy",
                                                  ["src", "test"], "12")

def test_create_main_cmakelists_default_version():
    expected = \
        """cmake_minimum_required(VERSION 3.10)
project(dummy)
set(CMAKE_CXX_STANDARD 17)

add_subdirectory("src")
add_subdirectory("test")
"""
    actual_path, actual_content = project_creator.create_main_cmakelists("projects_root", "dummy",
                                                                         ["src", "test"], None)

    nose.tools.eq_(actual_content, expected)
    nose.tools.eq_(actual_path, "projects_root/dummy/CMakeLists.txt")


def test_create_main_cmakelists_with_compiler_options():
    expected = \
        """cmake_minimum_required(VERSION 3.10)
project(dummy)
set(CMAKE_CXX_STANDARD 17)
add_compile_options(-Wall -Wextra -Wpedantic -Werror)

add_subdirectory("src")
add_subdirectory("test")
"""
    actual_path, actual_content = project_creator.create_main_cmakelists("projects_root", "dummy",
                                                                         ["src", "test"], None, ["-Wall", "-Wextra", "-Wpedantic", "-Werror"])

    nose.tools.eq_(actual_content, expected, "%r != %r" % (actual_content, expected))
    nose.tools.eq_(actual_path, "projects_root/dummy/CMakeLists.txt")



def test_create_main_cmakelists():
    expected = \
        """cmake_minimum_required(VERSION 3.10)
project(dummy)
set(CMAKE_CXX_STANDARD 14)

add_subdirectory("src")
add_subdirectory("test")
"""
    actual_path, actual_content = project_creator.create_main_cmakelists("projects_root", "dummy",
                                                                         ["src", "test"], "14")

    nose.tools.eq_(actual_content, expected)
    nose.tools.eq_(actual_path, "projects_root/dummy/CMakeLists.txt")

def test_collect_compiler_options():
    project_description = {	"compilerOptions": [
		"-Wall", "-Wextra", "-Wpedantic", "-Werror"
	]}
    expected = ["-Wall", "-Wextra", "-Wpedantic", "-Werror"]

    nose.tools.eq_(project_creator.collect_compiler_options(project_description), expected)

def test_collect_compiler_options_missing_input():
    project_description = {}
    expected = []

    nose.tools.eq_(project_creator.collect_compiler_options(project_description), expected)

def test_create_runtest_with_conan2():
    expected = """CURRENT_DIR=`pwd`
rm -rf build && mkdir build && conan install . --output-folder=build --build=missing && cd build && cmake .. -DCMAKE_TOOLCHAIN_FILE=build/Release/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release && cmake --build . && (./tests/dummy_tests_test)
cd "${CURRENT_DIR}"
"""
    subdirectories = ['src', 'tests']

    nose.tools.eq_(project_creator.create_runtest(2, "dummy", ['src', 'tests']), expected)

def test_create_runtest_with_conan1():
    expected = """CURRENT_DIR=`pwd`
rm -rf build && mkdir build && conan install . -s compiler.libcxx=libstdc++11 && cd build && cmake ..  && cmake --build . && (./tests/dummy_tests_test)
cd "${CURRENT_DIR}"
"""
    subdirectories = ['src', 'tests']

    nose.tools.eq_(project_creator.create_runtest(1, "dummy", ['src', 'tests']), expected)


def test_create_conanfile():
    expected = \
    """[requires]
gtest/1.8.1

[generators]
cmake
"""
    conan_dependencies = {"gtest": "1.8.1"}
    nose.tools.eq_(project_creator.create_conanfile(conan_dependencies), expected)

def test_create_conanfile2():
    expected = \
    """[requires]
    gtest/1.14.0

[generators]
CMakeDeps
CMakeToolchain

[layout]
cmake_layout
"""
    conan2_dependencies = {"gtest": "1.14.0"}
    nose.tools.eq_(project_creator.create_conanfile2(conan2_dependencies), expected)
