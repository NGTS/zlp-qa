# Dark levels

This plot only shows the following information for the dark frames. The dark current is computed by

1. Computing the prescan and overscan means with 3-&sigma; clipping
1. Interpolate the bias level between these two values
1. Subtract from the imaging region
1. Compute the 3-&sigma; cliped mean of the remaining signal

The remaining panels have the same descriptions as the previous plot. [See the help file for this plot for more information.](/help/overscan-levels.html)
