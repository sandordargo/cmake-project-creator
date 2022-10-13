from nose.tools import raises
import nose.tools

from cmake_project_creator import dependency


def test_make_dependencies_ignore_internals():
    raw_dependencies = [{
        "type": "internal",
        "link": "proj/othercode/src"
    }]

    dependencies = dependency.Dependency.make_dependencies(raw_dependencies)
    nose.tools.eq_(len(dependencies), 0)


@raises(ValueError)
def test_make_dependencies_raises_error_if_type_is_missing():
    raw_dependencies = [{
        "link": "proj/othercode/src"
    }]

    dependency.Dependency.make_dependencies(raw_dependencies)


@raises(ValueError)
def test_make_dependencies_raises_error_if_name_is_missing_for_non_internal():
    raw_dependencies = [{
        "type": "conan",
    }]

    dependency.Dependency.make_dependencies(raw_dependencies)


def test_make_dependencies_conan_is_made():
    raw_dependencies = [{
        "type": "conan",
        "name": "gtest",
        "version": "1.8.1"
    }]

    dependencies = dependency.Dependency.make_dependencies(raw_dependencies)
    nose.tools.eq_(len(dependencies), 1)
    nose.tools.eq_(dependency.Dependency("conan", "gtest", "1.8.1"), dependencies[0])


def test_dependency_does_not_equal_non_dependency_object():
    a_dependency = dependency.Dependency("Foo", "Bar")

    class Person:
        """
        dummy class so that we can test Dependency.__eq__
        """

    nose.tools.ok_(not a_dependency.__eq__(Person))
