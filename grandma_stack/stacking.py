#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 00:10:44 2022

@authors: S.Karpov
"""

import matplotlib.pyplot as plt
plt.rc('image', interpolation='bicubic', origin='lower', cmap = 'hot')
rcParams = plt.rcParams.copy()

import glob, argparse, os
import reproject
import numpy as np
from astropy.wcs import WCS
from astropy.io import fits as fits
from stdpipe import astrometry, photometry, catalogs, pipeline
from astropy.coordinates import SkyCoord
import warnings
from astropy.wcs import FITSFixedWarning
from astropy.io.fits.verify import VerifyWarning
warnings.simplefilter(action='ignore', category=FITSFixedWarning)
warnings.simplefilter(action='ignore', category=VerifyWarning)


"""Little script for image stacking for GRANDMA collaboration."""

def main():
    """Main function stacking images"""


    parser = argparse.ArgumentParser(description="Correct for FLAT and BIAS"
                                     "and stack the images")

    parser.add_argument("--images",
                        required=True,
                        type=str,
                        help="Path to the images. ")

    parser.add_argument("--ra",
                        required=True,
                        type=float,
                        help="Radial ascension of the image target.")

    parser.add_argument("--dec",
                        dest="dec",
                        required=True,
                        type=float,
                        help="Declination of the images target")

    parser.add_argument("--outname",
                        required=True,
                        help="Name of the stacked images.")

    parser.add_argument("--astrometry",
                        action='store_true',
                        default=True,
                        help="Refine astrometry with Scamp.")

    args = parser.parse_args()

    # Using the coordinate of the target to find star in PS for astrometry
    target = SkyCoord(args.ra, args.dec, unit='deg')
    cat = catalogs.get_cat_vizier(target.ra.deg, target.dec.deg,
                                  0.2, 'ps1', filters={'gmag':'<22'})

    # Finding the flats, darks and raw images
    dark_path = os.path.join(args.images, 'dark/*.fit*')
    dark_files = sorted(glob.glob(dark_path))

    flat_path = os.path.join(args.images, 'flat/*.fit*')
    flat_files = sorted(glob.glob(flat_path))

    raw_path = os.path.join(args.images, 'raw/*.fit*')
    raw = sorted(glob.glob(raw_path))

    # Creating dark
    darks = []
    for filename in dark_files:
        # header = fits.getheader(filename)
        image = fits.getdata(filename).astype(np.double)
        darks.append(image)
    dark = np.median(darks, axis=0)

    # Creating flat
    flats = []
    for filename in flat_files:
        # header = fits.getheader(filename)
        image = fits.getdata(filename).astype(np.double)
        image -= dark
        image /= np.median(image)
        flats.append(image)
    flat = np.median(flats, axis=0)

    # Base settings
    _tmpdir = os.path.join(args.images, 'tmp')
    if not os.path.exists(_tmpdir):
        os.mkdir(_tmpdir) # Create tmp dir for the analysis

    initial_aper = 5
    bg_size = 256
    minarea = 5

    wcs0 = None
    images = []

    for filename in raw:
        # Opening raw images
        header = fits.getheader(filename)

        # Sutracting dark
        image = fits.getdata(filename).astype(np.double)
        image -= dark

        # Correcting flat
        image /= flat

        # Getting astrometric information from raw images
        header['CD1_1'] = float(header['CD1_1'])
        header['CD1_2'] = float(header['CD1_2'])
        header['CD2_1'] = float(header['CD2_1'])
        header['CD2_2'] = float(header['CD2_2'])

        wcs = WCS(header)

        # Masking infinite valued pixels
        mask = ~np.isfinite(image)
        # mask |= image > 50000

        # Grabbing gain from header
        try:
            gain = float(header.get('GAIN'))
        except Exception:
            gain = 1. # Set to 1 if not given in header

        print(image)
        print(mask)
        print(_tmpdir)
        # Extract objects
        obj, segm = photometry.get_objects_sextractor(image, mask=mask, r0=0.5,
                                                      aper=initial_aper, gain=gain,
                                                      extra={'BACK_SIZE':bg_size},
                                                      extra_params=['NUMBER'],
                                                      checkimages=['SEGMENTATION'],
                                                      _tmpdir=_tmpdir, minarea=minarea)

        if args.astrometry :
            pixscale = astrometry.get_pixscale(wcs=wcs)
            wcs = pipeline.refine_astrometry(obj, cat, 5*pixscale,
                                              wcs=wcs, order=3,
                                              method='scamp',
                                              cat_col_mag='rmag',
                                              cat_col_mag_err='e_rmag',
                                              verbose=True)

        if wcs0 is None:
            wcs0 = wcs
            header0 = header.copy()
            astrometry.clear_wcs(header0)
            header0 += wcs0.to_header(relax=True)

            image1 = image.copy()
        else:
            image1,fp = reproject.reproject_interp((image, wcs), wcs0, image.shape)
            image1[fp<0.5] = np.nan

        images.append(image1)

    simage = np.sum(images, axis=0)
    # smask = np.isnan(simage)
    if (args.outname.split('.')[-1] != 'fit') or (args.outname.plit('.')[-1] != 'fits'):
        science_image = os.path.join(args.images, args.outname + '.fits')
    else:
        science_image = os.path.join(args.images, args.outname)
    fits.writeto(science_image, simage, header0, overwrite=True)

    return 0
    # bg = sep.Background(simage, smask)
    # simage -= bg.back()

    # fits.writeto('/tmp/simage.fits', simage, header0, overwrite=True)
if __name__ == "__main__":
    main()
