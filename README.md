# Astronomy-Scripts
Compilation of scripts used for my Astronomy USRA with Ingrid Stairs

# RMfit.py
This script performs a PSRchive rotation measure fit. Data must not be frequency scrunched. It must be Time scrunched and calibrated. It will generate a file called rmfitdata.txt, it will output a file with the extension rm_scrunch.

# fit2resanalyzer.ipynb
This is a notebook that uses the fit2res.c tarball (which must be compiled first, you can see the executable path I have in my code) made by Ingrid. My notebook takes two template files, orthogonalizes them, then outputs the basis coefficients for a few bin regions of interest. Data should be fully calibrated (will run faster with data already being F T and P scrunched) (takes in ascii file inputs, run colrm.py on ascii files to remove zeros)

# Pulsewidthcalc.py
Pulse width variability. I align the data and fit a Gaussian to it, then based off the Gaussian I can guess where the half width half max will occur, I choose the closest x value to where the guess is, then I choose 10 points on either side of that x value. Then I make a loop where I choose 11 random points in that list of 21 and fit a line to them. Wherever the fit line crosses the half amplitude of the pulse is where i say is the width. Do this on both side of a pulse, then subtract the x values where it found the half amplitude. Then I take the mean of the widths. Its like a monte carlo pulse width calculator, (its good but it can be finicky if your pulses are very abnormal like mine) (This file is old and may not work immediately) Data must be scrunched and fully processed. Generates files named convergence.txt and failed_files.txt (you may have to play with parameters for this to work properly)

# colrm.py
PSRchive ascii conversion adds two columns composed of zeros in the first two spaces of the data. This file removes those so fit2resanalyzer can be run. Only works on ascii (less the file first to see if the zeros exist, or else actual data will be deleted)
