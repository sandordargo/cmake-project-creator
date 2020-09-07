import argparse
import os
import shutil
import stat
import json
import directory_factory

'''
TODO:
Cleanup
Create some files on the fly, so we append lines and write once in the end


- add tests
- add runtests.sh
- adds coverage
- comp flags
# - nest everything one more level
# - add lib...
- add a language describing the folder structure
- - needs a path
- - executable / library / with test
- - conan or submodule
- - depenedency among others /probably needs a test

? shared/static
? where to create components
? recursive runtest
-- test implies a dependency on gtest and src on the same level
{
"src" : {"type": "source", "main": "true", "dependencies":[]},
"include" : {"type": "include",},
"test" : {"type": "test", "dependencies":[] },
}


In an object model:
Have a Directory
    a Directory has a name
    a type
    it can have a main
    it can have a cmakelist
    it can contain other subdirecotires
    it can have dependencies
    
Have a Dependency
    a dependency can have a type
    and an address
    or maybe they can be subtypes, like internal, conan...
    
should we care about intermediate directories in terms os saving? maybe not...


TODO
- remove hardcoded stuff
DONE - - hasTest should be computed or passed in?, no need for the moment
- src should have include path
- test should have either or both include/src path 
DONE - has main or executable? if not is it a library? can it be both?
- optional binary/library names
DONE - v2: nested folders
DONE - v2: multiple libs
DONE - shared/static
DONE - depend on other internal lib - check in cmake, how to!
- - Files in Diff libs should have diff names
DONE - - How to refer to the project base?
DONE - - get include library from link target
DONE - - check if link is valid
DONE - - directory.path. should in contain root? probably it should not. it should, new helper introd
DONE - depend on conan libs
DONE - - conan no conflicting version
- - conan options
- optional compiler
- optional unit test pack

DONE - test samplev1
- upload
- write readme
- add tests
- add ci/cd
- refactor
- write article
- create issues
- publish
- Set C++ version
'''


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description',
                        default="examples/sample-v3.json",
                        type=str,
                        dest='description',
                        help='Project description'
                        )
    parser.add_argument('-c', '--cleanup',
                        action='store_true',
                        dest='cleanup',
                        help='Tries to remove target directory before running the script'
                        )
    arguments = parser.parse_args()
    return arguments


def create_plumbing(path, subdirs, parsed_directories):
    conan_dependencies = collect_conan_dependencies(parsed_directories)
    is_conan = len(conan_dependencies) > 0

    conan_install = "conan install .. -s compiler.libcxx=libstdc++11" if is_conan else ""

    runtest = " ; ".join(
        f"./{sd}/bin/{project_dir_name}_{sd.split('/')[-2] if '/' in sd else sd}_test" for sd in subdirs if
        'test' in sd)
    runtest = f"({runtest})" if runtest else ""

    with open(f'{path}/runTests.sh', "w") as runTests:
        runTests.write(
f"""CURRENT_DIR=`pwd`
cd build && rm -rf * && {conan_install} {"&&" if conan_install else ""} cmake .. && make {"&& " + runtest if runtest else ""}
cd "${{CURRENT_DIR}}"
""")
    st = os.stat(f'{path}/runTests.sh')
    os.chmod(f'{path}/runTests.sh', st.st_mode | stat.S_IEXEC)

    if is_conan:
        with open(f'{path}/conanfile.txt', "w") as conanfile:

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
            paths = collect_cmake_subdirectories(directory['subdirectories'], os.path.join(name, directory['name']), paths)
    return paths


def create_main_cmakelists(project_directory_name, subdirectories):
    add_subdirectories_commands = ""
    for subdirectory in subdirectories:
        add_subdirectories_commands += f'add_subdirectory("{subdirectory}")' + "\n"

    with open(f'{project_directory_name}/CMakeLists.txt', "w") as cmake:
        cmake.write(
f"""cmake_minimum_required(VERSION 3.10)
project({project_directory_name})
set(CMAKE_CXX_STANDARD 17)

{add_subdirectories_commands.strip()}
""")


def parse_directories(directories, relative_root):
    parsed_directories = []
    for directory in directories:
        rel_path = os.path.join(relative_root, directory['name'])

        if directory["type"] == "intermediate":
            parsed_directories.extend(parse_directories(directory['subdirectories'], rel_path))
            continue

        parsed_directories.append(directory_factory.make(rel_path, directory))
    return parsed_directories


def create_cpp_project(project_file_name, parsed_directories):
    for directory in parsed_directories:
        directory.create(project_file_name, parsed_directories)


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
    except:
        pass


def prepare_build_directory(project_directory):
    os.makedirs(os.path.join(project_directory, 'build'))


if __name__ == "__main__":
    arguments = parse_arguments()

    with open(arguments.description) as json_file:
        project_description = json.load(json_file)

    project_dir_name = project_description['projectName']
    project_file_name = project_description['projectName'].capitalize()

    if arguments.cleanup:
        cleanup_project_folder(project_dir_name)

    prepare_build_directory(project_dir_name)

    cmake_subdirectories = collect_cmake_subdirectories(project_description['directories'])
    print(f"The identified sub cmake projects are {cmake_subdirectories}")

    create_main_cmakelists(project_dir_name, cmake_subdirectories)

    parsed_directories = parse_directories(project_description['directories'], project_dir_name)
    create_plumbing(project_dir_name, cmake_subdirectories, parsed_directories)
    create_cpp_project(project_file_name, parsed_directories)
