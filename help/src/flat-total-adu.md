# Flat total adu

This plot shows a histogram of the total number of ADU in a region 256x256 pixels in the centre of the frame. It is computed by summing the individual flat frames (after bias and dark correction) that are used to compute the master flat frame. A vertical line marks the median in the region, and further statistics are printed to the plot title.

The uncertainty in the flat fielding is approximately the 1/sqrt(f) where f is the total number electrons. This plot goes some way to estimating this value.
