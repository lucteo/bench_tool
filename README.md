# bench_tool

Bench_tool is a small script that helps you perform small benchmarks for testing the performance of your applications. The applications can be written in any language, provided there is a Makefile that is able to build the application. It measures both the CPU time and the memory usage.

Version: 1.1

Copyright (c) 2015, Lucian Radu Teodorescu.


## Using the bench_tool

To use this tool one must carefully arrange the tests/programs in a specified folder structure, providing enough information on how the programs should be run. If the proper folder structure is followed, the tool will run smoothly without any additional input from the user.

There are three main concepts that the user needs to know when using this tool:
- **tests**: these are independents sets of things that should be benchmarked in isolation; different tests will not have any connection between them; each test will be represented by a directory
- **programs**; the actual executables that will be run in order to do the benchmark measurements; a test typically contains multiple programs; the list of programs is specified in a file named `programs.in` for each test directory
- **run arguments**: this will contain the list of parameters that need to be applied to the programs when they are executed; a test will typically contain one or more sets of run arguments; the run arguments are specified in a file named `args.in` for each test directory

### Folder structure

To use the tool, certain folder structure rules may be followed. Here is a typical folder structure for a benchmark consisting of different tests:
- **bench_tool**
  - **results**
    - **tmp**
      - ...
    - results_testA.csv
    - results_testA.log
    - results_testB.csv
    - results_testB.log
  - **tests**
    - **testA**
      - args.in
      - programs.in
      - prog1.c
      - prog1.out
      - prog2.cpp
      - prog2.out
      - Makefile
    - **testB**
      - args.in
      - programs.in
      - prog1.c
      - prog1.out
      - prog2.cpp
      - prog2.out
      - Makefile
  - bench_tool.py
  - config.py

#### The `tests` folder

The **tests** folder is the folder in which the tests and programs should be placed. The tool is able to run multiple tests, each containing a set of programs to be tested. Different tests typically consists of different sets of programs, so the measurements are aggregated per test.

The tests in the example folder are `testA` and `testB`. To add a new test, create a new folder inside the `tests` folder.

Each test folder should contain at least two files: `programs.in` and `args.in`. The first contains the programs that will be invoked for the test and the latter contains the set of arguments needed.

Each line of the `programs.in` file will contain a program to be invoked. This does not need to be an executable, it can also be a command line. For example, to invoke a Java program, one can add a line that looks as following: `java -server -Xss15500k -classpath src/main MainProgram`. The format of the file should look like the following:

    ./progam1.out
    ./progam2.out
    # A comment line starts with '#' (must be first character, no spaces allowed before it)
    complex command line
    program_name:command

As seen, from the previous examples one can add comments if the first character of the line is `#`. Also, if the command line becomes too complex one can give names to programs.

Similarly, int the `args.in` file one needs to specify the running arguments of the programs, one set of arguments per line. Comments are also possible with the `#` characters, but names cannot be given to argument sets.

For each test the tool will try to *build* the programs before running them. For this it will invoke a `make` command in the test directory, so therefore a `Makefile` file needs to be provided. Based on the configuration parameters, the tool will typically invoke `make clean` before `make`.

If there is only one test in the benchmark, the user may choose not to create a dedicated test folder, and put the test data (`run` folder, programs and makefile) directly under the main `tests` folder.

#### The `results` folder

The **results** folder will contain the results of the benchmark execution. It will contain the compilation logs, the execution logs and the timing results.

The benchmark will record both the execution time and the maximum memory usage.

For each test _X_, the aggregated timing results will be put in the `results_X.csv` file. This file will contain the average of execution of each program with each set of arguments for multiple runs, together with the standard deviation (both for execution time and memory). The execution time and used memory for each program run will be placed in the `results_X.log` file

The compilation log can be found in file `tmp/comp_testName.log`.
The output for each program execution (each program x each argument set x number of runs) will be placed in the `tmp` folder as well, inside files ending in `.run.log`.


#### Configuration file

Near the `bench_tool.py` script, there is a special script called `config.py` containing configuration parameters. One can set here the number of program run repetitions, the timeout for each program execution and whether to perform a `make clean` before building the programs.

### Ignoring tests, programs and run arguments

To ignore a test from running in the benchmark, simply rename the test and make it start with a dot (e.g., `.testA`). The tool will not consider the test at all.

Similarly, one can ignore programs (ending with `.out`) and run arguments files (the `run/*.run` files).


### Running the benchmark

After creating the test folders, setting up the programs, creating the proper makefiles and creating the run argument files, one would want to run the benchmark for all the tests. For this the main script needs to be executed:

    python ./bench_tool.py

After running this command, for each test all the programs will be built and then run, producing the timing and memory results.

## Requirements

Python 2.7 is required

## Changes

#### Version 1.1
- programs to be executed are read from a filename, instead of requiring executables with .out extensions (e.g, no need to create a `.out` file for Python scripts)
- run arguments are read from a file, one line per set of arguments, instead of reading from multiple files
- added option to express memory in MB instead of KB
- bug fixes:
  - flush the files before executing commands
  - fixed bug with out of order display of results
  - better display of results


## License

Copyright (c) 2015, Lucian Radu Teodorescu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
