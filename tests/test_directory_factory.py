from nose.tools import raises
import nose.tools

from cmake_project_creator import test_directory, include_directory, \
    directory_factory, source_directory


def test_make_source():
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
    directory = directory_factory.make("projects_root", "foo", description, "DummyProjectFileName")

    nose.tools.ok_(isinstance(directory, source_directory.SourceDirectory))


def test_make_include():
    description = {
        "name": "include",
        "type": "include",
        "subdirectories": []
    }
    directory = directory_factory.make("projects_root", "foo", description, "DummyProjectFileName")

    nose.tools.ok_(isinstance(directory, include_directory.IncludeDirectory))


def test_make_test():
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
    directory = directory_factory.make("projects_root", "foo", description, "DummyProjectFileName")

    nose.tools.ok_(isinstance(directory, test_directory.TestDirectory))


@raises(KeyError)
def test_incorrect_type():
    description = {
        "name": "tests",
        "type": "incorrect",
        "dependencies": [{
            "type": "conan",
            "name": "gtest",
            "version": "1.8.1"
        }],
        "subdirectories": []
    }
    directory_factory.make("projects_root", "foo", description, "DummyProjectFileName")
