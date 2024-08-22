import sys
from pathlib import Path

input_ms = sys.argv[1]
numchans = int(sys.argv[2])
num_wsclean_runs = int(sys.argv[3])
msdir = Path(sys.argv[4])

print(input_ms, type(input_ms))
print(numchans, type(numchans))
print(num_wsclean_runs, type(num_wsclean_runs))
# get flag summart from CASA flagdata
for item, element in enumerate(range(num_wsclean_runs)):
    mstransform(vis = input_ms,
                datacolumn = "data",
                outputvis = str(Path(Path(msdir, f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}"), f"batch_{item}_chans{item*numchans}-{(item+1)*numchans}.ms")),
                nchan = numchans,
                spw = f"0:{item*numchans}")