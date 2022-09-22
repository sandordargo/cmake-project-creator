[![Actions Status](https://github.com/sandordargo/cmake-project-creator/workflows/PythonCi/badge.svg)](https://github.com/sandordargo/cmake-project-creator/actions)

## Cmake Project Creator

Cmake Project Creator helps you generate a new C++ project. Instead of writing the Cmakefiles and creating all the folders by hand, you can either
* generate a project from an already existing description
* write a new description file yourself

## Requirements

## How to use it?

Call `./create_cmake_project.py --help` to print the help message.

Briefly, you can call the project_creator with one of the predefined options, or you can pass in your own project description.

You should also pass in the path with `-p` or `--path` where your new project should be generated. If it's not passed then the project will be created under the generated_projects directory.

Once a project is generated, navigate to the root of the freshly created project and call `./runTest.sh` to launch the build and the unit tests - if any. Where a test directory is defined, a failing unit test is generated. 

## Predefined schemas

You have the following predefined schemas shipped with project_creator. 

### The `single` directory project

Invoke this with `-d examples/single.json`. It will create a project with one include, one source and one test folder. GTest will be included for unit testing through Conan.

```
myProject
|_ include
|_ src
|_ test

``` 

### The `single` directory project with compiler options

Invoke this with `-d examples/single_with_compiler_options.json`. Like the `single.json`, it will create a project with one include, one source and one test folder. More than that, it will define the following compiler options on a project level: `-Wall -Wextra -Wpedantic -Werror`.

```
myProject
|_ include
|_ src
|_ test

``` 

### The `dual` directory project

Invoke the tool with `-d examples/dual.json` and the following project will be generated:

```
myProject
|_ executable
    |_ include
    |_ src
    |_ test
|_ library
    |_ include
    |_ src
    |_ test
```

The `executable` sub-directory will include `library` sub-directory as a dependency and will also have a `main.cpp` as such an executable. The `library` is just a static library. 

GTest will be included for unit testing through Conan.

### The `nested_dual` directory project

Invoke the tool with `-d examples/nested_dual.json` and the following project will be generated:

```
myProject
|_ common_root
    |_ executable
        |_ include
        |_ src
        |_ test
    |_ library
        |_ include
        |_ src
        |_ test
```

The `executable` sub-directory will include `library` sub-directory as a dependency and will also have a `main.cpp` as such an executable. The `library` is just a static library.

So what is the difference compared to the `dual` project? Not much, it's just that the subdirectories are nested in a new common root. This is more to show you an example, how it is possible. You can check the description in `examples/nested_dual.json`. 

GTest will be included for unit testing through Conan.

## How to write new project descriptions?

First of all, project descriptions are written in JSON format.

In the root of the JSON, you'll have to specify the `projectName` attribute, which will be used both for the directory name where the project will be created and evidently it will be the name of the Cmake project.
Then you have to specify an array of `directories`.


### The root elements

There are two mandatory elements:
- `projectName` setting the project name
- `directories` describing the directory structure of the project

The following items are optional:
- `c++Standard` setting the standard to compile against. If missing, it defaults to *17*. Possible values are: *98*, *11*, *14*, *17*, *20*.
- `compilerOptions` setting extra compiler options. This field takes an array of strings, for example: `"compilerOptions": ["-Wall", "-Wextra", "-Wpedantic", "-Werror"]`.

### Directory object

Each object in the `directories` must specify a `name` attribute, a `type` attribute and/or subdirectories.

#### Mandatory elements

The `name` attribute defines the directory name.

The `type` attribute can take the following values:
- `source` indicating that it will contain implementation files
- `header` indicating that it will contain header files
- `test` indicating that it will contain unit test code
- `intermediate` indicating that it will only contain other subdirectories  

In the subdirectories array, you can list the other `directory` objects to be put nested in the given `directory`.

#### Optional elements

A directory object can have the following optional elements:

- `library` indicating whether a given component should be delivered as a library. Only `source` type directories should use this option. Its values can be `null`, `STATIC` or `SHARED`
- `executable` indicating whether a given component should have an executable, if set to `true`, a `main.cpp` will be generated. Only `source` type directories should use this option.
- `include` indicating whether a given `source` component has a corresponding `include` counterpart or not. Only `source` type directories should use this option.
- `dependencies` array containing all the dependencies of the given component

### Dependency objects

The `dependency` object is to describe a dependency of the enclosing component. It has 2 mandatory attributes and 1 optional:

#### Mandatory elements
- `type` indicating whether the dependency is of another directory of the project (`internal`) or if it's an external one. Among external ones, for the time being, only `conan` is supported. 
- `name` indicating the name of the dependency, in case of internal ones it should be the relative path of the depended directory including the project root. (E.g. `common_root/executable/library`)

#### Optional elements
- `version` is optional and has no role for `internal` dependencies, but for `conan` type dependencies it indicates the version of the component we want to include and the format must follow the Conan syntax. You can both use specific versions or [version ranges](https://docs.conan.io/en/latest/versioning/version_ranges.html) 

## How to contribute?

In any case, please check the Github issues, maybe there is already an item, already a discussion concerning your idea. If that's not the case, open an issue and let's discuss it there.

In terms of coding guidelines, I follow the [PEP 8 Style guide for Pyhon](https://www.python.org/dev/peps/pep-0008/). Tests are must be provided.
