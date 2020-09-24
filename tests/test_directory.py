from cmake_project_creator.directory import Directory

class TestDirectory:

    def test_get_suffix(self):
        directory = Directory("projects_root", "ProjectRoot/Suffix/Extension", {}, "DummyProjectFileName")
        assert "Suffix" == directory.get_name_suffix()

    def test_only_project_root(self):
        directory = Directory("projects_root", "ProjectRoot", {}, "DummyProjectFileName")
        assert "ProjectRoot" == directory.get_name_suffix()

    def test_get_path_without_project_root(self):
        directory = Directory("projects_root", "ProjectRoot/Suffix/Extension", {}, "DummyProjectFileName")
        assert "Suffix/Extension" == directory.get_path_without_project_root()

    def test_nice_formatting(self):
        directory = Directory("projects_root", "ProjectRoot/Suffix/Extension", {}, "DummyProjectFileName")
        assert "Directory(path: ProjectRoot/Suffix/Extension, description:{})" == str(directory)
