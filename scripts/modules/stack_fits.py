import os
from pathlib import Path

def stack_these_fits(kern_container, batch_cubename, batch_dir_name, chanbasename):
    """Generate the FitsTool command."""
    return (
        f"singularity exec {kern_container} fitstool.py "
        f"--stack {batch_cubename}:FREQ {Path(batch_cubename)}*-image.fits"
    )