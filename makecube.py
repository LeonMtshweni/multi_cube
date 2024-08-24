#!/usr/bin/env python3
import os
import yaml
import sys
import glob
from pathlib import Path

from scripts.modules.setup_utils import setup_project_structure
from scripts.modules.setup_utils import setup_msdir_structure
from scripts.modules.setup_utils import setup_output_structure
from scripts.modules.setup_utils import count_inclusive
from scripts.modules.wsclean_utils import generate_wsclean_cmd
from scripts.modules.bash_utils import write_slurm
from scripts.modules.stack_fits import stack_these_fits
from scripts.modules.cleanup_utils import clean_up_batch_directory
# from scripts.modules.casa_utils import generate_mstransform_cmd


def main():

    # Create the output directories
    setup_project_structure()


    # Get the parent directory
    # parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    current_dir = Path.cwd()

    # Potentially add a try/except statement here
    # Define relative paths
    msdir = os.path.join(current_dir, 'msdir')
    outputs = os.path.join(current_dir, 'outputs')
    inputs = os.path.join(current_dir, 'inputs')
    modules = os.path.join(current_dir, 'scripts/modules')
    job_files = os.path.join(current_dir, 'job_files')
    log_files = os.path.join(current_dir, 'log_files')


    # Load the configuration file
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    #-------------------------------------------------------------------------------
    # PATH CONFIG PARAMETERS
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
    #-------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------
    # GENERAL CONFIG PARAMATERS
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
    job_id_1 = os.popen(f"sbatch {bash_script} | awk '{{print $4}}'").read().strip()

    #-------------------------------------------------------------------------------

    # Create the batch file directories in the msdir directory
    setup_output_structure(num_wsclean_runs, numchans, outputs)

    # Calculate the number of channels per run
    channels_per_run = numchans // num_wsclean_runs
    remainder_channels = numchans % num_wsclean_runs

    start_channel = 1

    # create list to hold job ids
    job_ids = list()

    # get flag summart from CASA flagdata
    for item, element in enumerate(range(num_wsclean_runs)):

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
            chanbasename = Path(Path(outputs, f"wsclean_{item}_chans{start_channel}-{end_channel}"), chanbasename),
            numpix = numpix,
            pixscale = pixscale,
            start_chan = start_channel,
            end_chan = end_channel,
            chans_out = numchans,
            ms_file = str(Path(Path(msdir, f"batch_{item}_chans{start_channel}-{end_channel}"), f"batch_{item}_chans{start_channel}-{end_channel}.ms")),
            log_file = os.path.join(log_files, f"batch_{item}_chans{start_channel}-{end_channel}.log"),
            memory = config['wsclean']['memory'],
            weight = config['wsclean']['weight'],
            niter = config['wsclean']['niter'],
            auto_threshold = config['wsclean']['auto_threshold'],
            auto_mask = config['wsclean']['auto_mask'],
            gain = config['wsclean']['gain'],
            mgain = config['wsclean']['mgain'])

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
        independent_job_id = os.popen(f"sbatch --dependency=afterok:{job_id_1} {itemised_bash_file} | awk '{{print $4}}'").read().strip()
        # save job ids for future job dependency
        job_ids.append(independent_job_id)

        # Set the start channel for the next run
        start_channel = end_channel

    #-------------------------------------------------------------------------------

    # Calculate the number of channels per run
    channels_per_run = numchans // num_wsclean_runs
    remainder_channels = numchans % num_wsclean_runs

    start_channel = 1

    # get flag summart from CASA flagdata
    for item, element in enumerate(range(num_wsclean_runs)):

        # create the bash executable
        loging_file = os.path.join(log_files, f"fitstoool_{item}_chans{start_channel}-{end_channel}.log")

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run

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
        itemised_bash_file_ii = str(Path(job_files, f"fitstool_{item}.sh"))
        
        # numbered bash file from previous jobs
        itemised_bash_file = str(Path(job_files, f"wsclean_{item}.sh"))

        # spawn jobs - fitstool
        dependent_job_id_ii = os.popen(f"sbatch --dependency=afterok:{itemised_bash_file} {itemised_bash_file_ii}").read().strip()

        # Set the start channel for the next run
        start_channel = end_channel

    #-------------------------------------------------------------------------------

    # # Calculate the number of channels per run
    # channels_per_run = numchans // num_wsclean_runs
    # remainder_channels = numchans % num_wsclean_runs

    # start_channel = 1

    # # get flag summart from CASA flagdata
    # for item, element in enumerate(range(num_wsclean_runs)):

    #     # Calculate the end channel for this run
    #     end_channel = start_channel + channels_per_run

    #     # Distribute the remainder channels
    #     if item < remainder_channels:
    #         end_channel += 1

    #     imcontsub_cmd = 'singularity exec ~/containers/casa-1.7.0.simg casa -c casa_imcontsub.py --logfile logfile-imcontsub.log --nogui mycube=%s imfitorder=%i'%(batch_cubename,imfitorder)

    #     # write the slurm file
    #     write_slurm(bash_filename = os.path.join(job_files, f"imcontsub_{item}.sh"),
    #                     jobname = f"imcontsub_{item}",
    #                     logfile = loging_file,
    #                     email_address = email_address,
    #                     cmd = imcontsub_cmd,
    #                     time = wall_time,
    #                     partition = partition,
    #                     ntasks = ntasks,
    #                     nodes = nodes,
    #                     cpus = cpus,
    #                     mem = mem)

    #     # numbered bash file from current jobs
    #     itemised_bash_file_iii = str(Path(job_files, f"imcontsub_{item}.sh"))
        
    #     # numbered bash file from previous jobs
    #     itemised_bash_file_ii = str(Path(job_files, f"fitstool_{item}.sh"))

    #     # spawn jobs - imcontsub casa
    #     dependent_job_id_iii = os.popen(f"sbatch --dependency=afterok:{itemised_bash_file_ii} {itemised_bash_file_iii}").read().strip()

    #     # Set the start channel for the next run
    #     start_channel = end_channel

if __name__ == '__main__':
    main()