from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, 'r') as req_file:
        return req_file.read().splitlines()

setup(
    name="multi-cube",  # Your package name on PyPI
    version="0.4.3",  # Initial version
    packages=find_packages(),  # Automatically find the packages
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    description="A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum-subtracted ms file.",
    long_description=open("README.md").read(),  # Long description from your README
    long_description_content_type="text/markdown",  # Specify the correct content type for the README
    author="Leon K.B. Mtshweni",
    author_email="leonkb.m.astro@gmail.com",
    url="https://github.com/LeonMtshweni/multi-cube",  # Update this URL to your actual GitHub repository
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust if using another license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # Minimum Python version requirement

    # Automatically install dependencies from requirements.txt
    install_requires=parse_requirements('requirements.txt'),

    entry_points={
        'console_scripts': [
            'multi_cube=multi_cube.scripts.makecube:main'  # This maps the command 'multi_cube' to the 'main' function in 'scripts.makecube'
        ],
    },
)
