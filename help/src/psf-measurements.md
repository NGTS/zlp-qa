# PSF measurements

The analysis stacks the 100 brightest non-saturated stars, using the astrometric solution to align with high accuracy, onto a super sampled grid. This is repeated in nine regions of the chip to quantify spatial terms. It measures the semi-major (a), semi-minor (b) and rotation (theta) of the combined stacked image.

The panels are:

* *FWHM* - the average of the a and b terms for each region
* *a*, *b*, *theta* - measurements as described above
* *e* - eccentricity as computed by `1 - sqrt(b / a) ** 2`

At the moment it is slightly confusing as all 9 regions are plotted. This should improve soon.
