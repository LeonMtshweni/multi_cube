# multi_cube

A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum subtracted ms file.

Requirements
------------
This tool is designed to leverage [Slurm Workload Manager](https://slurm.schedmd.com/documentation.html) for efficient job scheduling, allowing for simultaneous submission of multiple jobs. Development and testing were conducted using Python 3.12.1 on the [ILIFU](https://www.ilifu.ac.za/) research cloud infrastructure, hosted by [IDIA](https://idia.ac.za/). To ensure proper environment setup, dependencies are listed in requirements.txt."

Installation
------------

### Setting up an environment

It is recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) to ensure isolation and proper dependency management when installing and running `multi_cube`. To set up the environment:

```
python3 -m venv .venv
source .venv/bin/activate
```
This will create and activate a virtual environment in your current directory.

Installing from PyPI

Once your environment is set up, you can install multi_cube directly from PyPI:

```
pip install multi-cube
```
This will install the latest version of the package along with its dependencies.

Installing from Source

If you’d like to work with the source code directly, clone the repository and install it locally. First, clone the repository into your desired directory:

```
cd <desired_directory>
git clone https://<yourtoken>@github.com/LeonMtshweni/multi_cube.git
cd multi_cube/
```

### Usage
------------

`multi_cube` is a tool designed to generate FITS cubes from a continuum-subtracted measurement set (MS) file. Below are the steps to configure and run the tool.

#### 1. Generate a Default Configuration File

To get started, you need to generate a default configuration file. This file contains all the necessary parameters and paths that `multi_cube` uses during execution. Run the following command to generate the config file in your current working directory:

```
multi_cube –get-config
```
This will create a file named `multi_cube_config.yml` in the current directory. The configuration file contains several parameters, including paths, imaging options, and Slurm resource allocation settings.

#### 2. Customize the Configuration File

Once the configuration file is generated, you need to customize it according to your data and computing environment. Open the `multi_cube_config.yml` file in a text editor and modify the following key parameters:

- **Paths**: Set the correct paths to your MS files, output directories, and any containers (e.g., WSClean or CASA).
- **WSClean Settings**: Customize WSClean parameters such as pixel scale, image size, data column, and the number of channels to image.
- **Slurm Settings**: Set the required Slurm resource allocation, including `ntasks`, `cpus`, `mem`, and job `partition`.

Make sure you have a calibrated, continuum-subtracted MS file before proceeding.

#### 3. Run the Workflow

After configuring the settings, run the workflow by executing the `multi_cube` tool from the command line. The tool will split your MS file into user-defined bandwidth segments, image each segment, and then stack the images to create a data cube.

```
multi_cube –config multi_cube_config.yml
```
This command will:
- Split the MS file into smaller chunks.
- Image each chunk using WSClean or CASA.
- Stack the resulting images into a single FITS cube.

#### 4. Monitor the Workflow

The tool is designed to leverage the Slurm workload manager for efficient job scheduling. You can monitor the jobs using standard Slurm commands, such as:
```
squeue -u <your_username>
```
