def generate_mstransform_cmd(casa_container, input_ms, output_dir, numchans, start_chan, end_chan):
    """
    Generate the mstransform command.
    
    Parameters:
    - container: Path to the Singularity container for mstransform.
    - input_ms: Path to the input measurement set.
    - output_dir: Directory where output will be saved.
    - script: Path to the mstransform script.
    - output_format: Output format for the transformed data.
    - field_id: Field ID to be used in transformation.
    - spw: Spectral window ID.
    - outframe: Output frame.

    Returns:
    - cmd: The mstransform command as a string.
    """
    mstransform_cmd = (
        f"singularity exec {casa_container} casa mstranform"
        f"vis = {input_ms}"
        f"outputvis = {output_dir}"
        f"mode = 'channel'"
        f"nchan = {numchans}"
        f"start = '856MHz'"
        f"width = '1'"
        f"restfreq = '1.420405752GHz'"
        f"outframe = 'bary'"
    )
    return mstransform_cmd


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