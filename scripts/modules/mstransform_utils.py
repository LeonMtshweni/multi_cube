import sys

input_ms = sys.argv[3]
output_ms = sys.argv[4]
numchans = sys.argv[5]

# get flag summart from CASA flagdata
mstransform(vis = input_ms,
            outputvis = output_ms,
            mode = 'channel',
            nchan = numchans,
            # start = '856MHz',
            width = '1',
            # restfreq = '1.420405752GHz',
            outframe = 'bary')