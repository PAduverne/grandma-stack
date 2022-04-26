# grandma-stack
Tool for stacking astronomical image

## Installation

1. Install Sextractor

2. Install Scamp

3. Install stdpipe 
    * Clone the [project](https://gitlab.in2p3.fr/icare/stdpipe)
    * Go into the stdpipe repertory
    * Run : pip install .

4. Install the tool
    * Clone the [project](https://github.com/PAduverne/grandma-stack)
    * Go into the grandma-stack repertory
    * Run : pip install .

## Running

1. Put the flat images in a repertory named flat
2. Put the bias images in a repertory named dark
3. Put the raw images to stackin a repertory named : raw

Arguments: \
--images : Path to the repertory containing the flat, bias and raw images \
--ra : Radial ascension of the target \
--dec : Declination of the target \
--outname : name of the output image \
--astrometry : Whether refining the astrometry using Scamp (Default : True)