EXT := pdf
PLOTSDIR := plots
PLOTS := $(PLOTSDIR)/fluxvsrms.$(EXT) $(PLOTSDIR)/overscan-levels.$(EXT) $(PLOTSDIR)/dark-levels.$(EXT) $(PLOTSDIR)/dark-correlation.$(EXT)
GENEVA := $(HOME)/storage/Geneva/

all: $(PLOTS) index.html

index.html: view/build_html.py $(PLOTS)
	python $< -o $@

# Plots
$(PLOTSDIR)/fluxvsrms.$(EXT): photometry/flux_vs_rms.py data/pre-sysrem.fits data/post-sysrem.fits
	python $< --pre-sysrem $(word 2,$^) --post-sysrem $(word 3,$^) -o $@

$(PLOTSDIR)/overscan-levels.$(EXT): reduction/plot_overscan_levels.py data/extracted-bias-levels.csv
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/dark-levels.$(EXT): reduction/plot_dark_current.py data/extracted-dark-current.csv
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/dark-correlation.$(EXT): reduction/plot_dark_current_correlation.py data/extracted-dark-current.csv
	python $< $(word 2,$^) -o $@


# Data
data/pre-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/data/pipeline-output.fits $@

data/post-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/output/working-output.fits $@

data/bias-frames-list.txt: scripts/build_bias_list.sh
	sh $< $@

data/dark-frames-list.txt: scripts/build_dark_list.sh
	sh $< $@

data/extracted-dark-current.csv: reduction/extract_dark_current.py data/dark-frames-list.txt
	python $< $(word 2,$^) -o $@

data/extracted-bias-levels.csv: reduction/extract_overscan.py data/bias-frames-list.txt
	python $< $(word 2,$^) -o $@

# Viewing
view: view-plots

view-plots: $(PLOTS)
	xv $(PLOTS) &
