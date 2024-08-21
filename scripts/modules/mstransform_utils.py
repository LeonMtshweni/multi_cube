import sys

input_ms = sys.argv[1]
numchans = sys.argv[2]
num_wsclean_runs = sys.argv[3]
print(input_ms, input_ms.dtype)
print(numchans, numchans.dtype)
print(num_wsclean_runs, num_wsclean_runs.dtype)
# get flag summart from CASA flagdata
for item, element in enumerate(range(num_wsclean_runs)):
    mstransform(vis = input_ms,
            outputvis = f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.ms",
            nchan = numchans,
            spw = f"{0:item}")