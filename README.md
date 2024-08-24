# multi_cube

A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum subtracted ms file.

Requirements
------------
This tool requires slurm as jobs are submited in unison. I developed and tested with Python 3.12.1. on the [ILIFU](https://www.ilifu.ac.za/) research cloud instrastucture (hosted by [IDIA](https://idia.ac.za/)). Add info about requirements.txt

Installation
------------

### Setting up an environment

It is recommended that you make use of a [virtual environment](https://docs.python.org/3/library/venv.html) to install and rup multi_cube, for obvious reasons, i.e.:
```
python3 -m venv .venv
source .venv/bin/activate
```
Once you've created and activated your virtual environmen, simply clone the repo into your preferred location:

```
cd example_dir
git clone https://github.com/LeonMtshweni/multi_cube.git
cd multi_cube/
```

Usage
------------

Perusal of the config file is required for the operation of multi_cube. It is assumed that the user has a calibrated, continuum subtracted ms file.

Running the following command will automatically run all the components of multi_cube, i.e. splitting the ms file into a user specified number of smaller files with the same band width, imaging all of the various ms files, and stacking them into a cube.

Run

```
$ python makecube.py

```