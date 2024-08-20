import os

def generate_wsclean_cmd(wsclean_container, chanbasename, numpix, pixscale, start_chan, end_chan, numchans, ms_file, log_file, memory, weight, niter, auto_threshold, auto_mask, gain, mgain):
    """Generate the WSClean command."""
    return (
        f"singularity exec {wsclean_container} wsclean "
        f"-name {os.path.join(chanbasename)} "
        f"-mem {memory} "
        f"-weight {weight} "
        f"-size {numpix} {numpix} "
        f"-scale {pixscale} "
        f"-channel-range {start_chan} {end_chan} "
        f"-channels-out {numchans} "
        f"-data-column DATA "
        f"-no-dirty "
        f"-niter {niter} "
        f"-auto-threshold {auto_threshold} "
        f"-auto-mask {auto_mask} "
        f"-no-update-model-required "
        f"-gain {gain} "
        f"-mgain {mgain} "
        f"-local-rms {ms_file} "
        f"> {log_file}"
    )
