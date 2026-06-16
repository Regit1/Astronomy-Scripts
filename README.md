# Astronomy-Scripts
Compilation of scripts used for my Astronomy USRA with Ingrid Stairs

# RMfit.py
This script performs a PSRchive rotation measure fit. Data must not be frequency scrunched. It must be Time scrunched and calibrated. It will generate a file called rmfitdata.txt, it will output a file with the extension rm_scrunch.

# fit2resanalyzer.ipynb
This is a notebook that uses the fit2res.c tarball (which must be compiled first, you can see the executable path I have in my code) made by Ingrid. My notebook takes two template files, orthogonalizes them, then outputs the basis coefficients for a few bin regions of interest. Data should be fully calibrated (will run faster with data already being F T and P scrunched) (takes in ascii file inputs, run colrm.py on ascii files to remove zeros)

# colrm.py
PSRchive ascii conversion adds two columns composed of zeros in the first two spaces of the data. This file removes those so fit2resanalyzer can be run. Only works on ascii (less the file first to see if the zeros exist, or else actual data will be deleted)
