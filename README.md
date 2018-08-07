# ConTest 

ConTest (**Con**colic **Test**ing) is a tool 
that adaptively reduces the search space of concolic testing.
The tool is implemented on top of [CREST][crest], 
a publicly available concolic testing tool for C.

## Install ConTest. 
You need to install [Ubuntu 16.04.5(64 bit)][ubuntu].
Then follow the steps:
```sh
$ sudo apt-get install ocaml libboost-all-dev default-jre #(if not installed) 
$ git clone https://github.com/kupl/ConTest.git
$ cd ConTest/cil
$ ./configure
$ make
$ cd ../src
$ make
```

## Compile a benchmark.
Please read **README\_ConTest** file located in each benchmark directory. 
In **README\_ConTest** file, we explain how to compile each benchmark.
For instance, we can compile tree-1.6.0 as follows:
```sh
$ cd ~/ConTest/benchmarks/tree-1.6.0 
# vi README_ConTest
$ make
```

If you want to run another benchmark (e.g., sed-1.17), read the **README_ConTest** file in the directory:
```sh
$ cd ConTest/benchmarks/sed-1.17 
$ vi README_ConTest
```

## Run ConTest.
ConTest, a tool for peforming template-guided concolic testing via online learning, is run on an instrumented program. 
For instance, we can run our tool for **grep-2.2** as follows:
```sh
$ screen 
# Initially, each benchmark should be compiled with ConTest:
$ cd ConTest/benchmarks/grep-2.2
$ ./configure
$ cd src
$ make
# Run a script
$ cd ~/ConTest/scripts
$ python ConTest.py pgm_config/grep.json CGS 20000 
```

Each argument of the last command means:
-	**pgm_config/grep.json** : a json file to describe the benchmark.
-	**CGS** : A search heuristic (e.g., CFDS (Control-Flow Directed Search), CGS (Context-Guided Search), Gen (Generational Search), Random Branch Search)
-	**20000** : Time budget (sec)

If the script successfully ends, you can see the following command:
```sh
#############################################
################Time Out!!!!!################
#############################################
```
Then, you can calculate the number of covered branches in time budget (i.e. 20000 seconds) as follows:
```sh
$ cd ~/ConTest/experiments/AllLogs__0704__sed-1.17__CFDS
$ python ~/ConTest/scripts/print_branches.py CFDS
```

We run **ConTest** on a linux machine with two Intel Xeon Processor E5-2630 and 192GB RAM.

[crest]: https://github.com/jburnim/crest
[ubuntu]: https://www.ubuntu.com/download/alternative-downloads
