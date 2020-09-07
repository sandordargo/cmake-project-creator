import source_directory
import include_directory
import test_directory
import dependency


def make(path, description):
    mapper = {
        "source": source_directory.SourceDirectory,
        "include": include_directory.IncludeDirectory,
        "tests": test_directory.TestDirectory,
    }

    dependencies = make_dependencies(description["dependencies"]) if "dependencies" in description else []
    return mapper[description["type"]](path, description, dependencies)


def make_dependencies(raw_dependencies):
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
        dependencies.append(dependency.Dependency(dependency_type, dependency_name, dependency_version))
    return dependencies