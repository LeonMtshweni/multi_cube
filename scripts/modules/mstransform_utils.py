import sys

input_ms = sys.argv[1]
numchans = sys.argv[2]
num_wsclean_runs = sys.argv[3]
print(input_ms, type(input_ms))
print(numchans, type(numchans))
print(num_wsclean_runs, type(num_wsclean_runs))
# get flag summart from CASA flagdata
for item, element in enumerate(range(num_wsclean_runs)):
    mstransform(vis = input_ms,
            outputvis = f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.ms",
            nchan = numchans,
            spw = f"{0:item}")