# Introduction
This repository contains python scripts to run JOB benchmark queries after adding different levels of noise to the System Catalog.
Paper explaining what JOB is: [How Good Are Query Optimizers, Really?](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)

# Prerequisites
1. Install Postgres
2. Download JOB data and setup Postgres database using instructions on the following page:
https://github.com/viktorleis/job

# How to Use
** Read the following list in its entirety before

1. Run restore.sh.

2. Run the script run_noise.py using the following format:
    ```
    python3 run_noisy.py <case> <column> <epsilon> <queries>
    ```

    where,
    case = name of the case you are running it for. 
    Eg: obl_wn_nullfrac for "oblivious with noisy nullfrac"
    (by "oblivious" we mean that the whole System Catalog is erased)
    For now use: nnf_<epsilon>, replacing <epsilon> with your choice of epsilon in the range 10 to 0.01.

    column = Name of the column of pg_statistic to be noised
    Eg: nullfrac
    Note: Only strings in the following list should be used for this argument: [nullfrac, correl]

    epsilon = choice of epsilon in the range 10 to 0.01

    queries = comma-separated list of queries, no spaces
    Eg: 1a,2a

    Example:
    ```
    python3 run_noisy.py obl_wn_nullfrac nullfrac 0.1 1a,2a
    ```

    This will create the following:
    1. A sub-directory called <case>_runs containing text files of query runtimes
    2. A subdirectory called plans, with more subdirecties of the form <case>/run, which contain text files for the query plan for that run

    Note: Skip epsilon=0.1 because those experiments have already been run.

# Plotting Bars
1. The main function reads the runtimes from different files. To also include bars for other epsilons, hard-code path to those files and add more y variable lists.
2. Need to manually add "labels" to the x variable list for new bars. Right now the middle bar is labeled DP. New names can beof the form DP_{epsilon}.
3. Manually add parameters and a call to the plot() function for more y variables

# Task update




