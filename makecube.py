#!/usr/bin/env python3
import os
import yaml
import sys
import glob
from pathlib import Path

from scripts.modules.setup_utils import setup_project_structure
from scripts.modules.setup_utils import setup_msdir_structure
from scripts.modules.wsclean_utils import generate_wsclean_cmd
from scripts.modules.bash_utils import write_slurm
from scripts.modules.cleanup_utils import clean_up_batch_directory
# from scripts.modules.casa_utils import generate_mstransform_cmd

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

for item, element in enumerate(range(num_wsclean_runs)):
        
    # Generate WSClean command
    wsclean_cmd = generate_wsclean_cmd(
        wsclean_container = Path(container_base_path, wsclean_container),
        chanbasename = chanbasename,
        numpix = numpix,
        pixscale = pixscale,
        start_chan = item*numchans,
        end_chan = (item+1)*numchans,
        chans_out = num_wsclean_runs,
        ms_file = str(Path(Path(msdir, f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}"), f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.ms")),
        log_file = os.path.join(log_files, f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.log"),
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

#     print(wsclean_cmd)
#     os.system(wsclean_cmd)

#     # Clean up unwanted files
#     clean_up_batch_directory(batch_dir_name, extensions_to_delete_r1, extensions_to_delete_r2)

#     # Create the cube
#     batch_cubename = os.path.join(batch_dir_name, cubebasename.replace('.fits', f'_{batch_dir_name}.fits'))
#     glue_cube_cmd = (
#         f"{config['fitstool']['stack_cmd'].format(kern_container=kern_container)} {batch_cubename}:FREQ "
#         f"{os.path.join(batch_dir_name, chanbasename)}*-image.fits"
#     )
#     print(glue_cube_cmd)
#     os.system(glue_cube_cmd)

#     # Perform continuum subtraction
#     imcontsub_cmd = (
#         f"singularity exec {casa_container} casa -c {config['casa']['script']} "
#         f"--logfile {config['casa']['log_file']} {config['casa']['nogui']} "
#         f"mycube={batch_cubename} imfitorder={imfitorder}"
#     )
#     print(imcontsub_cmd)
#     os.system(imcontsub_cmd)

# Spawn n independent jobs after the first job completes
# for item in range(num_wsclean_runs):
#     # Submit each independent job
#     independent_job_id = os.popen(f"sbatch --dependency=afterok:{job_id_1} job_script_{item+2}.sh | awk '{{print $4}}'").read().strip()
    
#         # Submit a dependent job that depends on the completion of the corresponding independent job
#         dependent_job_id = os.popen(f"sbatch --dependency=afterok:{independent_job_id} dependent_job_script_{i+2}.sh | awk '{{print $4}}'").read().strip()
        
#         print(f"Independent job {i+4} submitted with job ID: {independent_job_id}")
#         print(f"Dependent job {i+4} submitted with job ID: {dependent_job_id}")