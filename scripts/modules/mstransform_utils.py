import sys
from pathlib import Path

input_ms = sys.argv[1] # input ms file
numchans = int(sys.argv[2]) # total number of channels
num_wsclean_runs = int(sys.argv[3]) # number of runs
msdir = Path(sys.argv[4])

# Calculate the number of channels per run
channels_per_run = numchans // num_wsclean_runs
remainder_channels = numchans % num_wsclean_runs

start_channel = 1

# get flag summart from CASA flagdata
for item, element in enumerate(range(num_wsclean_runs)):

    # Calculate the end channel for this run
    end_channel = start_channel + channels_per_run

    # Distribute the remainder channels
    if item < remainder_channels:
        end_channel += 1
    
    mstransform(vis = input_ms,
                datacolumn = "data",
                outputvis = str(Path(Path(msdir, f"batch_{item}_chans{start_channel}-{end_channel}"), f"batch_{item}_chans{start_channel}-{end_channel}.ms")),
                nchan = numchans,
                spw = f"0:{start_channel}~{end_channel}")
    
    # Set the start channel for the next run
    start_channel = end_channel