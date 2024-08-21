import sys

input_ms = sys.argv[1]
numchans = sys.argv[2]
num_wsclean_runs = sys.argv[3]

# get flag summart from CASA flagdata
for item, element in enumerate(range(num_wsclean_runs)):
    mstransform(vis = input_ms,
            outputvis = f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.ms",
            nchan = numchans,
            spw = f"{0:item}")