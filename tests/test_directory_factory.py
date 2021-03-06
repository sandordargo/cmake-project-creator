from nose.tools import raises

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

    assert isinstance(directory, source_directory.SourceDirectory) is True


def test_make_include():
    description = {
        "name": "include",
        "type": "include",
        "subdirectories": []
    }
    directory = directory_factory.make("projects_root", "foo", description, "DummyProjectFileName")

    assert isinstance(directory, include_directory.IncludeDirectory) is True


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

    assert isinstance(directory, test_directory.TestDirectory) is True


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
