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
    python3 run_noisy.py <case> <column> <queries>
    ```

    where,
    case = name of the case you are running it for. 
    Eg: obl_wn_nullfrac for "oblivious with noisy nullfrac"
    (by "oblivious" we mean that the whole System Catalog is erased)
    For now use: nnf_<epsilon>, replacing <epsilon> with your choice of epsilon in the range 10 to 0.01.

    column = Name of the column of pg_statistic to be noised
    Eg: nullfrac
    Note: Only strings in the following list should be used for this argument: [nullfrac, correl]

    queries = comma-separated list of queries, no spaces
    Eg: 1a,2a

    Example:
    ```
    python3 run_noisy.py obl_wn_nullfrac nullfrac 1a,2a
    ```

    This will create the following:
    1. A sub-directory called <case>_runs containing text files of query runtimes
    2. A subdirectory called plans, with more subdirecties of the form <case>/run, which contain text files for the query plan for that run

# Tasks
1. Run the run_noisy.py code, either using the run_noisy.sh (note that this can take upto 7 days to finish) script or a different script you wrote or manually
2. Push the results to Github

# Task update




