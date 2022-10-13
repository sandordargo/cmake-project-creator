from cmake_project_creator.directory import Directory
import nose.tools


def test_get_suffix():
    directory = Directory("projects_root", "ProjectRoot/Suffix/Extension",
                          {}, "DummyProjectFileName")
    nose.tools.eq_(directory.get_name_suffix(), "Suffix")


def test_only_project_root():
    directory = Directory("projects_root", "ProjectRoot", {}, "DummyProjectFileName")
    nose.tools.eq_(directory.get_name_suffix(), "ProjectRoot")


def test_get_path_without_project_root():
    directory = Directory("projects_root", "ProjectRoot/Suffix/Extension",
                          {}, "DummyProjectFileName")
    nose.tools.eq_(directory.get_path_without_project_root(), "Suffix/Extension")


def test_nice_formatting():
    directory = Directory("projects_root", "ProjectRoot/Suffix/Extension",
                          {}, "DummyProjectFileName")
    nose.tools.eq_(str(directory), "Directory(path: ProjectRoot/Suffix/Extension, description:{})")
