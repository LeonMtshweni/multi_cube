# multi_cube

A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum subtracted ms file.

Requirements
------------
This tool is designed to leverage [Slurm Workload Manager](https://slurm.schedmd.com/documentation.html) for efficient job scheduling, allowing for simultaneous submission of multiple jobs. Development and testing were conducted using Python 3.12.1 on the [ILIFU](https://www.ilifu.ac.za/) research cloud infrastructure, hosted by [IDIA](https://idia.ac.za/). To ensure proper environment setup, dependencies are listed in requirements.txt."

Installation
------------

### Setting up an environment

It is recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) when installing and running `multi_cube` for isolation and dependency management. To set up the environment:
```
python3 -m venv .venv
source .venv/bin/activate
```
After creating and activating your virtual environment, clone the repository into your desired directory:
```
cd example_dir
git clone https://github.com/LeonMtshweni/multi_cube.git
cd multi_cube/
```

Usage
------------

To operate `multi_cube`, you must review and configure the settings in the provided configuration file in the config directory. It is also assumed that you have a calibrated, continuum-subtracted MS file.

Executing the following command will trigger the full `multi_cube` workflow, which includes splitting the MS file into a user-defined number of smaller files with equal bandwidth, imaging each of these files, and finally stacking them into bandwidth selected data cubes.

Run

```
$ python makecube.py

```