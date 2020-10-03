#!/usr/bin/env python3

import argparse
import os
import shutil
import stat
import json
from cmake_project_creator import directory_factory


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description',
                        default="examples/single.json",
                        type=str,
                        dest='description',
                        help='Project description'
                        )
    parser.add_argument('-o', '--output',
                        default="generated_projects",
                        type=str,
                        dest='output_root',
                        help='The directory where your new projects will be generated. '
                             'In case you want to generate MyCmakeProject and you set '
                             '--output to MyProjects, '
                             'MyProjects/MyCmakeProject will be generated. '
                             'In case the directory doesn\'t exist '
                             'it will be still created.'
                        )
    parser.add_argument('-c', '--cleanup',
                        action='store_true',
                        dest='cleanup',
                        help='Tries to remove target directory before running the script'
                        )
    arguments = parser.parse_args()
    return arguments


def create_plumbing(output_root, path, subdirs, parsed_directories):
    conan_dependencies = collect_conan_dependencies(parsed_directories)
    is_conan = len(conan_dependencies) > 0

    conan_install = "conan install .. -s compiler.libcxx=libstdc++11" if is_conan else ""

    print(subdirs)
    runtest = " ; ".join(
        f"./{sd}/bin/{path}_{sd.split('/')[-2] if '/' in sd else sd}_test"
        for sd in subdirs if 'test' in sd)
    runtest = f"({runtest})" if runtest else ""

    with open(f'{os.path.join(output_root, path)}/runTests.sh', "w") as runTests:
        runTests.write(
            f"""CURRENT_DIR=`pwd`
cd build && rm -rf * && {(conan_install + "&&") if conan_install else ""} cmake .. && make {"&& " + runtest if runtest else ""}
cd "${{CURRENT_DIR}}"
""")
    st = os.stat(f'{os.path.join(output_root, path)}/runTests.sh')
    os.chmod(f'{os.path.join(output_root, path)}/runTests.sh', st.st_mode | stat.S_IEXEC)

    if is_conan:
        with open(f'{os.path.join(output_root, path)}/conanfile.txt', "w") as conanfile:
            requires = [f"{name}/{version}" for name, version in conan_dependencies.items()]
            requires_command = "\n".join(requires)
            conanfile.write(
                f"""[requires]
{requires_command}

[generators]
cmake
""")


def collect_cmake_subdirectories(directories, name="", paths=None):
    if not paths:
        paths = []
    for directory in directories:
        if 'type' in directory and directory['type'] in ["source", "tests"]:
            paths.append(os.path.join(name, directory['name']))
        if 'subdirectories' in directory:
            paths = collect_cmake_subdirectories(directory['subdirectories'],
                                                 os.path.join(name, directory['name']),
                                                 paths)
    return paths


def create_main_cmakelists(output_root, project_directory_name, subdirectories, cpp_version):
    add_subdirectories_commands = ""
    if cpp_version is None:
        cpp_version = "17"
    if cpp_version not in ["98", "11", "14", "17", "20"]:
        raise ValueError(f"{cpp_version} is not among the supported C++ versions")
    for subdirectory in subdirectories:
        add_subdirectories_commands += f'add_subdirectory("{subdirectory}")' + "\n"

        content = \
            f"""cmake_minimum_required(VERSION 3.10)
project({project_directory_name})
set(CMAKE_CXX_STANDARD {cpp_version})

{add_subdirectories_commands.strip()}
"""
    return f'{os.path.join(output_root, project_directory_name)}/CMakeLists.txt', content


def parse_directories(directories, project_home, relative_root, project_file_name):
    parsed_directories = []
    for directory in directories:
        rel_path = os.path.join(relative_root, directory['name'])

        if directory["type"] == "intermediate":
            parsed_directories.extend(parse_directories(directory['subdirectories'],
                                                        project_home,
                                                        rel_path,
                                                        project_file_name))
            continue

        parsed_directories.append(directory_factory.make(project_home,
                                                         rel_path,
                                                         directory,
                                                         project_file_name))
    return parsed_directories


def create_cpp_project(parsed_directories):
    for directory in parsed_directories:
        directory.create(parsed_directories)


def collect_conan_dependencies(parsed_directories):
    conan_dependencies = {}
    for directory in parsed_directories:
        for dependency in directory.dependencies:
            if dependency.type == "conan":
                if dependency.name in conan_dependencies:
                    if dependency.version != conan_dependencies[dependency.name]:
                        raise ValueError(f"{dependency.name} is referenced with multiple versions")
                else:
                    conan_dependencies[dependency.name] = dependency.version
    return conan_dependencies


def cleanup_project_folder(project_directory):
    try:
        shutil.rmtree(project_directory)
    except Exception as e:
        print(f"Cleanup of {project_directory} failed due to {e}")


def prepare_build_directory(project_directory):
    os.makedirs(os.path.join(project_directory, 'build'))


def write_file(full_path, content):
    if full_path and content:
        with open(full_path, "w") as file:
            file.write(content)


def run():
    arguments = parse_arguments()

    with open(arguments.description) as json_file:
        project_description = json.load(json_file)

    output_root = arguments.output_root

    project_dir_name = project_description['projectName']
    project_file_name = project_description['projectName'].capitalize()

    if arguments.cleanup:
        cleanup_project_folder(os.path.join(arguments.output_root, project_dir_name))

    prepare_build_directory(os.path.join(arguments.output_root, project_dir_name))

    cmake_subdirectories = collect_cmake_subdirectories(project_description['directories'])
    print(f"The identified sub cmake projects are {cmake_subdirectories}")

    write_file(*create_main_cmakelists(arguments.output_root,
                                       project_dir_name,
                                       cmake_subdirectories))

    parsed_directories = parse_directories(project_description['directories'],
                                           arguments.output_root,
                                           project_dir_name,
                                           project_file_name)
    create_plumbing(arguments.output_root,
                    project_dir_name,
                    cmake_subdirectories,
                    parsed_directories)
    create_cpp_project(parsed_directories)


if __name__ == "__main__":
    run()
