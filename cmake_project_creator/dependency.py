"""
This module models a dependency of a CMake module
"""


class Dependency:
    """
    This class models a dependency of a CMake module
    """
    def __init__(self, dependency_type, name, version=None):
        self.type = dependency_type
        self.name = name
        self.version = version

    def __eq__(self, other) -> bool:
        if isinstance(other, Dependency):
            return self.type == other.type \
                   and self.name == other.name \
                   and self.version == other.version
        return False

    @staticmethod
    def make_dependencies(raw_dependencies):
        """
        creates a dependency object based on a the dependency descriptor
        :param raw_dependencies: the JSON descriptor
        :return: a dependency object
        """
        dependencies = []
        for raw_dependency in raw_dependencies:
            if "type" not in raw_dependency:
                raise ValueError(f"{raw_dependency} does not have a type")
            if raw_dependency["type"] != "internal" and "name" not in raw_dependency:
                raise ValueError(f"{raw_dependency} does not have a name")
            if raw_dependency["type"] == "internal":
                continue

            dependency_name = raw_dependency["name"]
            dependency_type = raw_dependency["type"]
            dependency_version = raw_dependency["version"] if "version" in raw_dependency else None
            dependencies.append(Dependency(dependency_type, dependency_name, dependency_version))
        return dependencies
