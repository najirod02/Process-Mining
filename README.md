# Process Mining and Management Project

### Author
Student: Dorijan Di Zepp 

Email: dorijan.dizepp@studenti.unitn.it

ID number: 257827 

## Table of content

Here a simple list of the content you can find in this readme:
- [Introduction](#introduction)
- [Setup](#setup)
- [Run the code](#run-the-code)

## Introduction

In this project we aim at measuring how much variable - in terms of variety of behaviour - are event logs. Computing the variability of a log can indeed be rather useful, for instance, to decide for (a procedural or a declarative) model discovery, or to decide which prediction technique to apply.

We have to define three python functions, each taking as input an event log and returning a measure of its variability:
- `compute_variant_variablity`: returning the number of variants of the event log
- `compute_edit_distance_variability`: returning the average edit distance between pairs of
traces
- `compute_my_variability`: returning a measure of the variability of the log that you can define
by yourself. You can take into account the only control flow or also look at the variability of
the event payloads

We have to use the function mentioned before on 4 log files:
- BPI Challenge 2011
- Concept drift
- Concept drift type 1
- Concept drift type 2

## Setup

This repository contains both the log files and the script `project.py`. The script performs an analysis of the event logs.

With the latest version of python (Python 3.3 or higher), you need to `create a virutal environment` before installing the dependencises.<br/>
If you have a lower version then you can skip this part about venv and directly go to the [list of modules](#modules-list).

This command will create a folder for the virutal environment.

```bash
python3 -m venv path_to_repo/venv
```

To `activate the new environment` simply type:

```bash
 source venv/bin/activate
```

### Modules list
With the environment activated (if needed), you can install the required dependencies:
```bash
pip install pm4py
pip install rapidfuzz
pip install tqdm
```

[`rapidFuzz`](https://pypi.org/project/RapidFuzz/) is a fast string matching library for Python and C++ while [`tqdm`](https://pypi.org/project/tqdm/) is a simple library for displaying progress bars, useful for monitoring long computations, especially for large log files.
Last but not least, [`pm4py`](https://pypi.org/project/pm4py/) is a python library that supports process mining algorithms in python.

If you want to deactivate the venv:
```bash
deactivate
```
I suggest to leave it activated as long as you are working on the project and/or testing as this allows the correct functioning of the 
script.

## Run the code
To execute the analysis, simply run the following command in your terminal:

```bash
python3 project.py
```

Make sure that the `venv is activated`.

The results will be both printed on the terminal and in an output file called `output_results.txt`

The log files to be read are already defined inside the code in the main function. In case you want to add/remove a file to analyse or to simply change the path of one of them you can modify the list following the structure:
```python
logs = {
    "Log name": "path_to_file.xes"
}
```