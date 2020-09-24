from cmake_project_creator import test_directory, dependency, include_directory, source_directory


def make(project_home, path, description, project_file_name):
    mapper = {
        "source": source_directory.SourceDirectory,
        "include": include_directory.IncludeDirectory,
        "tests": test_directory.TestDirectory,
    }

    dependencies = dependency.make_dependencies(description["dependencies"]) if "dependencies" in description else []
    return mapper[description["type"]](project_home, path, description, project_file_name, dependencies)


