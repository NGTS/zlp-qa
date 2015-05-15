<!-- Add mathjax source and configure to use single dollar signs for inline equations -->
<script src='//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML'></script>



# Field rotation

Shown is a time series of the field rotation as computed by the astrometric solution.

The computation of angle is taken from [the astrometry.net source code](https://github.com/dstndstn/astrometry.net/blob/9a085ee2a35c6da12144c5f32fa5970938ff1b2d/util/sip.c#L550-L559). In summary:

$$
\begin{eqnarray}
\mathrm{parity} &=& \mathrm{sign} \left\vert CD \right\vert \\
A &=& \mathrm{parity} * \mathrm{CD}_{11} + \mathrm{CD}_{22} \\
T &=& \mathrm{parity} * \mathrm{CD}_{21} + \mathrm{CD}_{12} \\
\theta &=& \arctan \frac{A}{T}
\end{eqnarray}
$$

The displacement at 1024 pixels $D$ is then computed as $D = \theta R$ where $\theta$ is the peak to peak rotation of the time series in radians, and $R = 1024$.
