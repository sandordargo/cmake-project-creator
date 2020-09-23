import dependency
from nose.tools import *


class TestDependency:
    def test_make_dependencies_ignore_internals(self):
        raw_dependencies = [{
            "type": "internal",
            "link": "proj/othercode/src"
        }]

        dependencies = dependency.make_dependencies(raw_dependencies)
        assert len(dependencies) == 0

    @raises(ValueError)
    def test_make_dependencies_raises_error_if_type_is_missing(self):
        raw_dependencies = [{
            "link": "proj/othercode/src"
        }]

        dependency.make_dependencies(raw_dependencies)

    @raises(ValueError)
    def test_make_dependencies_raises_error_if_name_is_missing_for_non_internal(self):
        raw_dependencies = [{
            "type": "conan",
        }]

        dependency.make_dependencies(raw_dependencies)

    def test_make_dependencies_conan_is_made(self):
        raw_dependencies = [{
            "type": "conan",
            "name": "gtest",
            "version": "1.8.1"
        }]

        dependencies = dependency.make_dependencies(raw_dependencies)
        assert 1 == len(dependencies)
        assert dependency.Dependency("conan", "gtest", "1.8.1") == dependencies[0]

    def test_dependency_does_not_equal_non_dependency_object(self):
        a_dependency = dependency.Dependency("Foo", "Bar")

        class Person:
            pass

        assert a_dependency.__eq__(Person) is False
