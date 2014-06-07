DATE := 2014/06/07
EXT := png
PLOTSDIR := plots
PLOTS := $(PLOTSDIR)/04-flux-vs-rms.$(EXT) \
	$(PLOTSDIR)/00-overscan-levels.$(EXT) \
	$(PLOTSDIR)/01-dark-levels.$(EXT) \
	$(PLOTSDIR)/02-dark-correlation.$(EXT) \
	$(PLOTSDIR)/05-rms-vs-time.$(EXT)

GENEVA := $(HOME)/storage/Geneva/

all: index.html

index.html: view/build_html.py $(PLOTS)
	python $< -o $@

# Plots
$(PLOTSDIR)/04-flux-vs-rms.$(EXT): photometry/flux_vs_rms.py data/pre-sysrem.fits data/post-sysrem.fits
	python $< --pre-sysrem $(word 2,$^) --post-sysrem $(word 3,$^) -o $@

$(PLOTSDIR)/05-rms-vs-time.$(EXT): photometry/rms_vs_time.py data/pre-sysrem.fits data/post-sysrem.fits
	python $< --pre-sysrem $(word 2,$^) --post-sysrem $(word 3,$^) -o $@

$(PLOTSDIR)/00-overscan-levels.$(EXT): reduction/plot_overscan_levels.py data/extracted-bias-levels.csv
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/01-dark-levels.$(EXT): reduction/plot_dark_current.py data/extracted-dark-current.csv
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/02-dark-correlation.$(EXT): reduction/plot_dark_current_correlation.py data/extracted-dark-current.csv
	python $< $(word 2,$^) -o $@

# Data
data/pre-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/data/pipeline-output.fits $@

data/post-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/output/working-output.fits $@

data/bias-frames-list.txt: scripts/build_bias_list.sh
	sh $< $@ $(DATE)

data/dark-frames-list.txt: scripts/build_dark_list.sh
	sh $< $@ $(DATE)

data/extracted-dark-current.csv: reduction/extract_dark_current.py data/dark-frames-list.txt
	python $< $(word 2,$^) -o $@

data/extracted-bias-levels.csv: reduction/extract_overscan.py data/bias-frames-list.txt
	python $< $(word 2,$^) -o $@

# Viewing
view: index.html
	firefox $<

# clean


# phony
.PHONY: clean clean-plots destroy

clean-plots:
	rm plots/*.$(EXT) | true

destroy:
	$(MAKE) clean-plots
	rm data/*.fits data/*.txt data/*.csv | true

