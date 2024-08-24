from setuptools import setup, find_packages

setup(
    name="multi_cube",
    version="0.1.0",
    description='SIP takes a SoFiA generated source catalog and produce images for publication or quick inspection. Images include HI contours overlaid on multiwavelength images, HI moment maps, pixel-by-pixel SNR maps, pv-diagrams with SoFiA mask, and spectra with and without noise.',
    url='https://github.com/LeonMtshweni/multi_cube',
    author='Leon Mtshweni',
    author_email='leon.mtshweni@tuks.co.za',
    packages=find_packages(),
    install_requires=[
        # all packages used native to python installation
    ],
    entry_points={
        'console_scripts': [
            'multi_cube=multi_cube.makecube:main',
        ],
    },
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
