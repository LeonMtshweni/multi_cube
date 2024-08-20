import os

def create_directories(directories):
    """
    Create directories if they do not already exist.
    
    Parameters:
    - directories: List of directory paths to create.
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_project_structure():
    """
    Set up the project structure by creating necessary directories in the parent directory.
    """
    # Define directories to create
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    directories = [
        os.path.join(parent_dir, 'msdir'),
        os.path.join(parent_dir, 'outputs'),
        os.path.join(parent_dir, 'inputs')
    ]
    
    # Create directories
    create_directories(directories)