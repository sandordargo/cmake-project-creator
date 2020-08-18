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
- has main or executable? if not is it a library? can it be both?
- optional binary/library names
DONE - v2: nested folders
DONE - v2: multiple libs
DONE - shared/static
- depend on other internal lib - check in cmake, how to!
- depend on conan libs
- optional compiler
- optional unit test pack
'''


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--description',
                        default="sample-v3.json",
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


def create_plumbing(path, subdirs):
    runtest = " ; ".join(
        f"./{sd}/bin/{project_dir_name}_{sd.split('/')[-2] if '/' in sd else sd}_test" for sd in subdirs if
        'test' in sd)
    runtest = "(" + runtest + ")"

    with open(f'{path}/runTests.sh', "w") as runTests:
        runTests.write(

            f"""
    CURRENT_DIR=`pwd`
    cd build && rm -rf * && conan install .. -s compiler.libcxx=libstdc++11 && cmake .. && make && {runtest}
    cd $CURRENT_DIR
                    """
        )
    st = os.stat(f'{path}/runTests.sh')
    os.chmod(f'{path}/runTests.sh', st.st_mode | stat.S_IEXEC)

    with open(f'{path}/conanfile.txt', "w") as conanfile:
        conanfile.write(
            """
[requires]
gtest/1.8.1

[generators]
cmake
            """
        )


def collect_subdirectories(directories, name="", paths=None):
    print("begin", name, directories)
    if not paths:
        paths = []
    for dir in directories:
        print('d', dir)
        if 'type' in dir and dir['type'] in ["source", "tests"]:
            paths.append(os.path.join(name, dir['name']))
            print('a', paths)
        if 'subdirectories' in dir:
            paths = collect_subdirectories(dir['subdirectories'], os.path.join(name, dir['name']), paths)
    return paths


def create_main_cmakelists(path, projectname, subdirs):
    includes = ""
    for sd in subdirs:
        includes += f'add_subdirectory("{sd}")' + "\n"

    with open(f'{path}/CMakeLists.txt', "w") as cmake:
        content = f"""

    cmake_minimum_required(VERSION 3.10)
    project({projectname})

    set(CMAKE_CXX_STANDARD 17)

    {includes}
    """
        cmake.write(content)


def iterate_on_dirs(directories, relative_root):
    for dir in directories:
        rel_path = os.path.join(relative_root, dir['name'])

        if dir["type"] == "intermediate":
            print("nothing to do")
            iterate_on_dirs(dir['subdirectories'], rel_path)
            continue
        directory_factory.make(dir["type"], rel_path).create(dir, project_file_name)


if __name__ == "__main__":
    arguments = parse_arguments()

    with open(arguments.description) as json_file:
        project_description = json.load(json_file)

    project_dir_name = project_description['projectName']
    project_file_name = project_description['projectName'].capitalize()
    if arguments.cleanup:
        try:
            shutil.rmtree(project_dir_name)
        except:
            pass

    os.makedirs(os.path.join(project_dir_name, 'build'))

    subdirs = collect_subdirectories(project_description['directories'])
    create_plumbing(project_dir_name, subdirs)
    print(subdirs)
    create_main_cmakelists(project_dir_name, project_description['projectName'], subdirs)

    iterate_on_dirs(project_description['directories'], project_dir_name)
