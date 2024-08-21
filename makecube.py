#!/usr/bin/env python3
import os
import yaml
import sys
import glob
from pathlib import Path

from scripts.modules.setup_utils import setup_project_structure
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

# Load the configuration file
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Paths and parameters from config
container_base_path = config['paths']['container_base_path']
base_data_dir = config['paths']['base_data_dir']
input_ms = config['general']['input_ms']
wsclean_output_dir = config['paths']['wsclean_output_directory']
mstransform_output_dir = config['paths']['mstransform_output_directory']
wsclean_container = config['paths']['wsclean_container']
mstransform_container = config['paths']['casa_container']
kern_container = config['paths']['kern_container']
casa_container = config['paths']['casa_container']
log_file = config['paths']['log_file']

total_numchans = config['general']['total_numchans']
numchans = config['general']['numchans']
num_wsclean_runs = total_numchans // numchans
numpix = config['general']['numpix']
pixscale = config['general']['pixscale']
chanbasename = config['general']['chanbasename']
cubebasename = config['general']['cubebasename']
email_address = config['general']['email_address']
imfitorder = config['general']['imfitorder']
extensions_to_delete_r1 = config['general']['extensions_to_delete_r1']
extensions_to_delete_r2 = config['general']['extensions_to_delete_r2']

# Ensure the WSClean output directory exists
os.makedirs(wsclean_output_dir, exist_ok=True)

# create the bash executable
bash_script = 'mstransform.sh' #os.path.join(outputs, 'mstransform.sh')
loging_file = 'mstransform.log' #os.path.join(outputs, 'mstransform.log')

# name of the submit file
submit_file = 'submit_jobs.sh'
# Open file for writing
# f = open(bash_script,'w')
# write header information
# f.write('#!/bin/bash\n')


# Run CASA from script
mstransform_cmd = f"singularity exec {Path(container_base_path, casa_container)} casa -c {os.path.join(modules, 'mstransform_utils.py')} {Path(base_data_dir, input_ms)} {numchans} {num_wsclean_runs} --nologger --log2term --nogui\n"

# write the slurm file
write_slurm(bash_filename = bash_script,
                jobname = 'split_ms',
                logfile = loging_file,
                email_address = email_address,
                cmd = mstransform_cmd) 

# f.write(mstransform_cmd + '\n')

# Submit the first job and capture its job ID
# job_id_1 = os.popen(f"sbatch {bash_script} | awk '{{print $4}}'").read().strip()

# ------------------------------------------------------------------------------

# Generate and run mstransform command
# mstransform_cmd = generate_mstransform_cmd(
#                     mstransform_container,
#                     batch_dir_name,
#                     os.path.join(batch_dir_name, '.ms'),
#                     numchans,
#                     start_chan,
#                     end_chan)
#                     # config['mstransform']['script'],
#                     # config['mstransform']['output_format'],
#                     # config['mstransform']['field_id'],
#                     # config['mstransform']['spw'],
#                     # config['mstransform']['outframe'])
                                                    
#-------------------------------------------------------------------------------

# Process each batch
# for batch_i in range(1, num_wsclean_runs + 1):
#     start_chan = (batch_i - 1) * numchans
#     end_chan = batch_i * numchans - 1
#     batch_dir_name = f'batch_{batch_i:02d}_chans{start_chan:05d}-{end_chan:05d}'
    
#     os.makedirs(batch_dir_name, exist_ok=True)
    
#     # Generate WSClean command
#     wsclean_cmd = generate_wsclean_cmd(
#         wsclean_container,
#         os.path.join(wsclean_output_dir, chanbasename),
#         numpix,
#         pixscale,
#         start_chan,
#         end_chan,
#         numchans,
#         ms_file,
#         log_file,
#         config['wsclean']['memory'],
#         config['wsclean']['weight'],
#         config['wsclean']['niter'],
#         config['wsclean']['auto_threshold'],
#         config['wsclean']['auto_mask'],
#         config['wsclean']['gain'],
#         config['wsclean']['mgain']
#     )
    
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

#     # Spawn 10 independent jobs after the third job completes
#     for i in range(10):
#         # Submit each independent job
#         independent_job_id = os.popen(f"sbatch --dependency=afterok:{job_id_1} job_script_{i+2}.sh | awk '{{print $4}}'").read().strip()
        
#         # Submit a dependent job that depends on the completion of the corresponding independent job
#         dependent_job_id = os.popen(f"sbatch --dependency=afterok:{independent_job_id} dependent_job_script_{i+2}.sh | awk '{{print $4}}'").read().strip()
        
#         print(f"Independent job {i+4} submitted with job ID: {independent_job_id}")
#         print(f"Dependent job {i+4} submitted with job ID: {dependent_job_id}")