import numpy as np

def build_bins():
    fluxmin = 1E2 / 4.0
    fluxmax = 1E5 / 4.0
    nbins = 9

    ledges = 10 ** np.linspace(np.log10(fluxmin),
                            np.log10(fluxmax),
                            nbins + 1)[:-1]

    bin_diff = np.diff(np.log10(ledges))[0]
    redges = 10 ** (np.log10(ledges) + bin_diff)

    return ledges, redges

