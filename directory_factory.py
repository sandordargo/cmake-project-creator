import source_directory
import include_directory
import test_directory


def make(dir_type, path):
    mapper = {
        "source": source_directory.SourceDirectory,
        "include": include_directory.IncludeDirectory,
        "tests": test_directory.TestDirectory,
    }
    return mapper[dir_type](path)
