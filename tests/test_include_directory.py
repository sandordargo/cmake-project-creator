from cmake_project_creator import include_directory


class TestIncludeDirectory:

    def test_header(self):
        directory = include_directory.IncludeDirectory("projects_root",
                                                       "root/path",
                                                       {},
                                                       "DummyProject",
                                                       [])
        expected = \
"""#pragma once

class DummyProject {
public:
  void hello();
};
"""
        actual_path, actual_content = directory.create_header_content()
        assert 'root/path/DummyProject.h' == actual_path
        assert expected == actual_content
