import os
from pathlib import Path

def create_directories(directories):
    """
    Create directories if they do not already exist.
    
    Parameters:
    - directories: List of directory paths to create.
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # print(f"Created directory: {directory}")

def setup_project_structure():
    """
    Set up the project structure by creating necessary directories in the parent directory.
    """
    # Define directories to create
    # site_package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    
    # directories = [
    #     os.path.join(config_dir, 'msdir'),
    #     os.path.join(config_dir, 'outputs'), 
    #     os.path.join(config_dir, 'inputs'),
    #     os.path.join(config_dir, 'job_files'),
    #     os.path.join(config_dir, 'log_files')
    # ]

    # Create directories
    # create_directories(directories)

def setup_msdir_structure(num_wsclean_runs, numchans, msdir):
    """
    Set up the msdir structure by creating necessary directories in the msdir directory.
    """
    # Create an empty list to hold the batch directory names
    directories = list()

    # Calculate the number of channels per run
    channels_per_run = numchans // num_wsclean_runs
    remainder_channels = numchans % num_wsclean_runs

    start_channel = 0

    for item, element in enumerate(range(num_wsclean_runs)):

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run

        # Distribute the remainder channels
        if item < remainder_channels:
            end_channel += 1

        directory = Path(msdir, f"batch_{item}_chans{start_channel}-{end_channel}")

        directories.append(directory)

        # Set the start channel for the next run
        start_channel = end_channel

    # Create directories
    create_directories(directories)

def setup_output_structure(num_wsclean_runs, numchans, output):
    """
    Set up the outputs structure by creating necessary directories in the output directory.
    """
    # Create an empty list to hold the batch directory names
    directories = list()

    # Calculate the number of channels per run
    channels_per_run = numchans // num_wsclean_runs
    remainder_channels = numchans % num_wsclean_runs

    start_channel = 0

    for item, element in enumerate(range(num_wsclean_runs)):

        # Calculate the end channel for this run
        end_channel = start_channel + channels_per_run

        # Distribute the remainder channels
        if item < remainder_channels:
            end_channel += 1

        directory = Path(output, f"batch_{item}_chans{start_channel}-{end_channel}")

        directories.append(directory)

        # Set the start channel for the next run
        start_channel = end_channel

    # Create directories
    create_directories(directories)

# Inclusive count
def count_inclusive(start, end):
    return abs(end - start) + 1

# Exclusive count
def count_exclusive(start, end):
    return max(0, abs(end - start) - 1)