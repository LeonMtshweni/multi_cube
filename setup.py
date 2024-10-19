from setuptools import setup, find_packages

setup(
    name="multi-cube",  # Your package name on PyPI
    version="0.1",  # Initial version
    packages=find_packages(),  # Automatically find the packages
    description="A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum subtracted ms file.",
    long_description=open("README.md").read(),  # Long description from your README
    long_description_content_type="A convenience tool that orchestrates the parallel generation of FITS cubes from a continuum subtracted ms file. User modifies the configuration file multi_cube/config/config.yml",  # The README format
    author="Leon K.B. Mtshweni",
    author_email="leonkb.m.astro@gmail.com",
    url="https://github.com/yourusername/multi-cube",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust if using another license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python version requirement

    entry_points={
        'console_scripts': [
            'multi_cube=scripts.makecube:main'
        ],
    },
)
