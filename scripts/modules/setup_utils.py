import os

def create_directories(directories):
    """
    Create directories if they do not already exist.
    
    Parameters:
    - directories: List of directory paths to create.
    """
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")

def setup_project_structure():
    """
    Set up the project structure by creating necessary directories one level above the current directory.
    """
    # Define the base directory as one level above the current working directory
    base_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))

    # Define the directories to create, relative to the base directory
    directories = [
        os.path.join(base_dir, 'msdir'),
        os.path.join(base_dir, 'outputs'),
        os.path.join(base_dir, 'inputs')
    ]

    # Create the directories
    create_directories(directories)

if __name__ == "__main__":
    setup_project_structure()
