# bench_tool

Bench_tool is a small script that helps you perform small benchmarks for testing the performance of your applications. The applications can be written in any language, provided there is a Makefile that is able to build the application. It measures both the CPU time and the memory usage.

Version: 1.0

Copyright (c) 2015, Lucian Radu Teodorescu.


## Using the bench_tool

To use this tool one must carefully arrange the tests/programs in a specified folder structure, providing enough information on how the programs should be run. If the proper folder structure is followed, the tool will run smoothly without any additional input from the user.

There are three main concepts that the user needs to know when using this tool:
- **tests**: these are independents sets of things that should be benchmarked in isolation; different tests will not have any connection between them
- **programs**; the actual executables that will be run in order to do the benchmark measurements; a test typically contains multiple programs
- **run arguments**: this will contain the list of parameters that need to be applied to the programs when they are executed; a test will typically contain one or more sets of run arguments

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
      - run
        - args1.run
        - args2.run
      - prog1.c
      - prog1.out
      - prog2.cpp
      - prog2.out
      - Makefile
    - **testB**
      - run
        - args1.run
        - args2.run
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

Each test folder should contain a sub-folder named `run` in which at least one file with the `.run` extension exists. In our example, each test have two such files named `args1.run` and `args2.run`. These files should contain the list of arguments passed when executing the programs. For example, if the `args1.run` and `args2.run` contain the content `60000` and `70000`, each program of from the test will be run twice with the arguments `60000` and `70000`.

The programs for each test should be placed directly under the test folder. They do not need to follow a specific convention. To build the programs the bench_tool will invoke `make` command in the test folder, so therefore a `Makefile` file needs to be provided. Each compiled program needs to be executable and have the `.out` extension. In fact, the bench_tool will consider all the files ending in `.out` as being the programs to be run for a particular test.

In conclusion, to create a test, one needs to create a folder for the test, put all the programs in the test folder, create a `Makefile` to compile the programs and provide some `run/???.run` files describing the arguments that need to be applied when running the programs.

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

## License

Copyright (c) 2015, Lucian Radu Teodorescu

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
