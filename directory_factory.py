import source_directory
import include_directory
import test_directory
import dependency


def make(project_home, path, description, project_file_name):
    mapper = {
        "source": source_directory.SourceDirectory,
        "include": include_directory.IncludeDirectory,
        "tests": test_directory.TestDirectory,
    }

    dependencies = dependency.make_dependencies(description["dependencies"]) if "dependencies" in description else []
    return mapper[description["type"]](project_home, path, description, project_file_name, dependencies)


