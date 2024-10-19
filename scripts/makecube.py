#!/usr/bin/env python3
import os
import argparse
import yaml
import sys
import glob
from pathlib import Path
import shutil  # For copying the default config file

from scripts.modules.setup_utils import setup_project_structure
from scripts.modules.setup_utils import setup_msdir_structure
from scripts.modules.setup_utils import setup_output_structure
from scripts.modules.setup_utils import count_inclusive
from scripts.modules.wsclean_utils import generate_wsclean_cmd
from scripts.modules.bash_utils import write_slurm
from scripts.modules.bash_utils import write_slurm_striped_down
from scripts.modules.remove_unwanted import generate_rm_commands
from scripts.modules.stack_fits import stack_these_fits
from scripts.modules.cleanup_utils import clean_up_batch_directory

# Get the directory of the installed package (where the default config file is located)
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the default config file within the package
DEFAULT_CONFIG_PATH = os.path.join(PACKAGE_DIR, 'config/config.yaml')

def generate_default_config(config_path):
    """Copy the default config file to the specified location."""
    if os.path.exists(config_path):
        print(f"Configuration file {config_path} already exists.")
    else:
        print(f"Copying the default config file to {config_path}...")
        shutil.copy(DEFAULT_CONFIG_PATH, config_path)
        print(f"Default config file copied to {config_path}. Please modify it before running the script.")

def main():

    # Set up argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="Tool to generate FITS cubes from a continuum-subtracted ms file.")
    
    # Add the --get-config argument for generating the config file
    parser.add_argument(
        '-g', '--get-config',
        action='store_true',
        help='Generate the default configuration file in the current directory.'
    )

    # Add the --config argument (or -c) for specifying the path to the config file
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=os.path.join(os.getcwd(), 'multi_cube_config.yml'),  # Default to the current working directory
        help='Path to the configuration file (default: ./multi_cube_config.yml)'
    )

    # Parse the arguments
    args = parser.parse_args()

    # If --get-config is specified, generate the default config file and exit
    if args.get_config:
        generate_default_config(args.config)
        sys.exit(0)

    # Get the config file path from the command-line argument
    config_path = args.config

    # Check if the config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found.")
        print("Please run 'make_cube --get-config' to generate the default config file.")
        sys.exit(1)

    # Load the configuration file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Create the output directories
    setup_project_structure()

    current_dir = Path.cwd()

    # Define relative paths
    msdir = os.path.join(current_dir, 'msdir')
    outputs = os.path.join(current_dir, 'outputs')
    inputs = os.path.join(current_dir, 'inputs')
    modules = os.path.join(current_dir, 'scripts/modules')
    job_files = os.path.join(current_dir, 'job_files')
    log_files = os.path.join(current_dir, 'log_files')

    #-------------------------------------------------------------------------------
    # PATH CONFIG PARAMETERS (from the config file)
    container_base_path = config['paths']['container_base_path']
    container_base_path_ii = config['paths']['container_base_path_ii']
    base_data_dir = config['paths']['base_data_dir']
    input_ms = config['general']['input_ms']
    wsclean_output_dir = config['paths']['wsclean_output_directory']
    mstransform_output_dir = config['paths']['mstransform_output_directory']
    wsclean_container = config['paths']['wsclean_container']
    mstransform_container = config['paths']['casa_container']
    kern_container = config['paths']['kern_container']
    casa_container = config['paths']['casa_container']
    log_file = config['paths']['log_file']
    #-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    # WSCLEAN CONFIG PARAMETERS
    numpix = config['wsclean']['numpix']
    pixscale = config['wsclean']['pixscale']
    chanbasename = config['wsclean']['chanbasename']
    cubebasename = config['wsclean']['cubebasename']
    datacolumn = config['wsclean']['datacolumn']
    #-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    # GENERAL CONFIG PARAMETERS
    numchans = config['general']['numchans']
    num_wsclean_runs = config['general']['num_wsclean_runs']
    imfitorder = config['general']['imfitorder']
    extensions_to_delete_r1 = config['general']['extensions_to_delete_r1']
    extensions_to_delete_r2 = config['general']['extensions_to_delete_r2']
    #-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    # SLURM RESOURCE ALLOCATION
    wall_time = config['compute']['time']
    partition = config['compute']['partition']
    ntasks = config['compute']['ntasks']
    nodes = config['compute']['nodes']
    cpus = config['compute']['cpus']
    mem = config['compute']['mem']
    email_address = config['compute']['email_address']
    #-------------------------------------------------------------------------------
    # STEP 1 : SPLIT MS FILE

    # Ensure the WSClean output directory exists
    os.makedirs(wsclean_output_dir, exist_ok=True)

    # create the bash executable
    bash_script = os.path.join(job_files, 'mstransform.sh')
    loging_file = os.path.join(log_files, 'mstransform.log')

    # Create the batch file directories in the msdir directory
    setup_msdir_structure(num_wsclean_runs, numchans, msdir)

    # Run CASA from script
    mstransform_cmd = f"singularity exec {Path(container_base_path_ii, casa_container)} casa -c {os.path.join(modules, 'mstransform_utils.py')} {Path(base_data_dir, input_ms)} {numchans} {num_wsclean_runs} {msdir} --nologger --log2term --nogui\n"

    # write the slurm file
    write_slurm(bash_filename = bash_script,
                    jobname = 'split_ms',
                    logfile = loging_file,
                    email_address = email_address,
                    cmd = mstransform_cmd,
                    time = wall_time,
                    partition = partition,
                    ntasks = ntasks,
                    nodes = nodes,
                    cpus = cpus,
                    mem = mem)

    # f.write(mstransform_cmd + '\n')

    # Submit the first job and capture its job ID
    split_ms_job_id = os.popen(f"sbatch {bash_script}").read().strip()

    # Extract the id from the submit message
    split_ms_job_id = split_ms_job_id.split()[-1]

    print(f"\033[5;35m>>> Submitted the wsclean job with id: {split_ms_job_id} and name: split_ms\033[0m")

    #-------------------------------------------------------------------------------
    # STEP 0 : DEFINE THE SIZE OF EACH MS FILE, IN NUMBER OF CHANNELS PER BATCH FILE

    channels_per_run = numchans // num_wsclean_runs
    remainder_channels = numchans % num_wsclean_runs

    #-------------------------------------------------------------------------------
    # STEP 2 : MAKE IMAGES

    # Create the batch file directories in the msdir directory
    setup_output_structure(num_wsclean_runs, numchans, outputs)

    start_channel = 0

    # create list to hold job ids
    wsclean_job_ids = list()

    # get flag summart from CASA flagdata
    for item in range(num_wsclean_runs):

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run

        # Distribute the remainder channels
        if item < remainder_channels:
            end_channel += 1

        # compute the number of channels to output in each wsclean run
        numchans = count_inclusive(start_channel, end_channel)
            
        # Generate WSClean command
        wsclean_cmd = generate_wsclean_cmd(
            wsclean_container = Path(container_base_path, wsclean_container),
            chanbasename = Path(Path(outputs, f"batch_{item}_chans{start_channel}-{end_channel}"), chanbasename),
            numpix = numpix,
            pixscale = pixscale,
            start_chan = 0,
            end_chan = channels_per_run + 1,
            chans_out = 3,
            ms_file = str(Path(Path(msdir, f"batch_{item}_chans{start_channel}-{end_channel}"), f"batch_{item}_chans{start_channel}-{end_channel}.ms")),
            log_file = os.path.join(log_files, f"batch_{item}_chans{start_channel}-{end_channel}.log"),
            memory = config['wsclean']['memory'],
            weight = config['wsclean']['weight'],
            niter = config['wsclean']['niter'],
            auto_threshold = config['wsclean']['auto_threshold'],
            auto_mask = config['wsclean']['auto_mask'],
            gain = config['wsclean']['gain'],
            mgain = config['wsclean']['mgain'],
            datacolumn = datacolumn,
            rm_dir = Path(outputs, f"batch_{item}_chans{start_channel}-{end_channel}"))

        # write the slurm file
        write_slurm(bash_filename = os.path.join(job_files, f"wsclean_{item}.sh"),
                        jobname = f"wsclean_{item}",
                        logfile = loging_file,
                        email_address = email_address,
                        cmd = wsclean_cmd,
                        time = wall_time,
                        partition = partition,
                        ntasks = ntasks,
                        nodes = nodes,
                        cpus = cpus,
                        mem = mem)
        
        # numbered bash file
        itemised_bash_file = str(Path(job_files, f"wsclean_{item}.sh"))
        
        # Submit each independent job
        wsclean_job_id = os.popen(f"sbatch --dependency=afterok:{split_ms_job_id} {itemised_bash_file}").read().strip()

        # Extract the job id from the submit text
        wsclean_job_id = wsclean_job_id.split()[-1]

        print(f"\033[5;35m>>> Submitted the wsclean job with id: {wsclean_job_id} and name: wsclean_{item}\033[0m")

        # save job ids for future job dependency
        wsclean_job_ids.append(wsclean_job_id)

        # Set the start channel for the next run
        start_channel = end_channel

    #-------------------------------------------------------------------------------
    # STEP 3 : DELETE UNWANTED FILES

    # # initialise the starting channel
    # initial_channel = 1

    # # create list to hold job ids
    # rm_job_ids = list()

    # # get flag summart from CASA flagdata
    # for item, wsclean_job_id in zip(range(num_wsclean_runs), wsclean_job_ids):

    #     # Calculate the end channel for this run
    #     final_channel = initial_channel + channels_per_run

    #     # create the bash executable
    #     loging_file = os.path.join(log_files, f"rm_{item}_chans{initial_channel}-{final_channel}.log")

    #     # Distribute the remainder channels
    #     if item < remainder_channels:
    #         final_channel += 1

    #     # name of the directory containing the base fits images
    #     batch_dir_name = Path(outputs, f"batch_{item}_chans{initial_channel}-{final_channel}")

    #     # List of patterns to glob
    #     patterns = ['*-psf.fits', '*-model.fits', '*-residual.fits', '*-dirty.fits', '*-MFS-*.fits']

    #     # Glob all patterns in one line - this is the full paths to the files to delete
    #     matching_files = [file for pattern in patterns for file in glob.glob(os.path.join(batch_dir_name, pattern))]

    #     # Generate the commands
    #     rm_cmd = generate_rm_commands(matching_files)
            
    #     # write the slurm file
    #     write_slurm_striped_down(bash_filename = os.path.join(job_files, f"rm_{item}.sh"),
    #                     jobname = f"rm_{item}",
    #                     logfile = loging_file,
    #                     email_address = email_address,
    #                     cmd = rm_cmd,
    #                     time = '00:30:00',
    #                     partition = "Main",
    #                     ntasks = '1',
    #                     nodes = '1',
    #                     cpus = '1',
    #                     mem = '4GB')

    #     # numbered bash file from current jobs
    #     rm_bash_file = str(Path(job_files, f"rm_{item}.sh"))

    #     # spawn jobs - fitstool
    #     rm_job_id = os.popen(f"sbatch --dependency=afterok:{wsclean_job_id} {rm_bash_file}").read().strip()    

    #     # save job ids for future job dependency
    #     rm_job_ids.append(rm_job_id)

    #     # Set the start channel for the next run
    #     initial_channel = final_channel

    #-------------------------------------------------------------------------------
    # STEP 4 : STACK IMAGES

    start_channel = 0

    # create list to hold job ids
    fitstool_job_ids = list()

    # get flag summart from CASA flagdata
    for item, wsclean_job_id in zip(range(num_wsclean_runs), wsclean_job_ids):

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run
        
        # create the bash executable
        loging_file = os.path.join(log_files, f"fitstoool_{item}_chans{start_channel}-{end_channel}.log")

        # Distribute the remainder channels
        if item < remainder_channels:
            end_channel += 1

        # name of the directory containing the base fits images
        batch_dir_name = Path(outputs, f"batch_{item}_chans{start_channel}-{end_channel}")

        # Name of the output cube
        batch_cubename = Path(batch_dir_name, f"cube_{input_ms}_batch_{item}_chans{start_channel}-{end_channel}.fits")

        # generate command for fitstool.py
        stack_cmd = stack_these_fits(kern_container, batch_cubename, batch_dir_name, chanbasename)

        # write the slurm file
        write_slurm(bash_filename = os.path.join(job_files, f"fitstool_{item}.sh"),
                        jobname = f"fitstool_{item}",
                        logfile = loging_file,
                        email_address = email_address,
                        cmd = stack_cmd,
                        time = wall_time,
                        partition = partition,
                        ntasks = ntasks,
                        nodes = nodes,
                        cpus = cpus,
                        mem = mem)

        # numbered bash file from current jobs
        fitstool_bash_file = str(Path(job_files, f"fitstool_{item}.sh"))

        # spawn jobs - fitstool
        fitstool_job_id = os.popen(f"sbatch --dependency=afterok:{wsclean_job_id} {fitstool_bash_file}").read().strip()

        # Extract the job ID from the output
        fitstool_job_id = fitstool_job_id.split()[-1]

        print(f"\033[5;35m>>> Submitted the fitstool job with id: {fitstool_job_id} and name: fitstool_{item}033[0m")

        # save job ids for future job dependency
        fitstool_job_ids.append(fitstool_job_id)

        # Set the start channel for the next run
        start_channel = end_channel

    #-------------------------------------------------------------------------------
    # STEP 5 : SUBTRACT

    start_channel = 0

    # create list to hold job ids
    imcontsub_job_ids = list()

    # # get flag summart from CASA flagdata
    for item, fitstool_job_id in zip(range(num_wsclean_runs), fitstool_job_ids):

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run

        # create the bash executable
        loging_file = os.path.join(log_files, f"imcontsub_{item}_chans{start_channel}-{end_channel}.log")

        # Distribute the remainder channels
        if item < remainder_channels:
            end_channel += 1

        # name of the directory containing the base fits images
        batch_dir_name = Path(outputs, f"batch_{item}_chans{start_channel}-{end_channel}")

        # Name of the output cube
        batch_cubename = Path(batch_dir_name, f"cube_{input_ms}_batch_{item}_chans{start_channel}-{end_channel}.fits")

        imcontsub_cmd = f"singularity exec {Path(container_base_path_ii, casa_container)} casa -c {os.path.join(modules, 'casa_imcontsub.py')} --logfile {loging_file} --nogui mycube={batch_cubename} imfitorder={imfitorder}" 

        # write the slurm file
        write_slurm(bash_filename = os.path.join(job_files, f"imcontsub_{item}.sh"),
                        jobname = f"imcontsub_{item}",
                        logfile = loging_file,
                        email_address = email_address,
                        cmd = imcontsub_cmd,
                        time = wall_time,
                        partition = partition,
                        ntasks = ntasks,
                        nodes = nodes,
                        cpus = cpus,
                        mem = mem)

        # numbered bash file from current jobs
        imcontsub_bash_file = str(Path(job_files, f"imcontsub_{item}.sh"))

        # spawn jobs - imcontsub casa
        imcontsub_job_id = os.popen(f"sbatch --dependency=afterok:{fitstool_job_id} {imcontsub_bash_file}").read().strip()

        # Extract the job ID from the output
        imcontsub_job_id = imcontsub_job_id.split()[-1]

        print(f"\033[5;35m>>> Submitted the imcontsub job with id: {imcontsub_job_id} and name: imcontsub_{item}\033[0m")

        # save job ids for future job dependency
        imcontsub_job_ids.append(imcontsub_job_id)

        # Set the start channel for the next run
        start_channel = end_channel

if __name__ == '__main__':
    main()