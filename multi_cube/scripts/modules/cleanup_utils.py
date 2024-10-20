import os

def remove_files(directory, extensions):
    """
    Remove files in the specified directory with the given extensions.
    
    Parameters:
    - directory: Directory path where files are to be removed.
    - extensions: List of file extensions (patterns) to delete.
    """
    for ext in extensions:
        pattern = os.path.join(directory, ext)
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"Removed file: {file}")
            except Exception as e:
                print(f"Failed to remove file {file}: {e}")

def clean_up_batch_directory(directory, extensions_r1, extensions_r2):
    """
    Perform cleanup tasks for the batch directory.
    
    Parameters:
    - directory: Directory path to clean up.
    - extensions_r1: List of file extensions to remove in the first cleanup phase.
    - extensions_r2: List of file extensions to remove in the second cleanup phase.
    """
    # Remove unwanted files
    remove_files(directory, extensions_r1)

    # Optionally remove additional files
    remove_files(directory, extensions_r2)
