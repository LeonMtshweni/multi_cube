#!/usr/bin/env python3
import os
import yaml

# Load the configuration file
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Parameters from config
myms = config['general']['input_ms'] 
total_numchans = config['general']['total_numchans']
numchans = config['general']['numchans']
num_wsclean_runs = total_numchans // numchans
numpix = config['general']['numpix']
pixscale = config['general']['pixscale']
chanbasename = config['general']['chanbasename']
cubebasename = config['general']['cubebasename']
imfitorder = config['general']['imfitorder']
extensions_to_delete_r1 = config['general']['extensions_to_delete_r1']
extensions_to_delete_r2 = config['general']['extensions_to_delete_r2']