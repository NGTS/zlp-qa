DATE := 2014/06/06
EXT := png
PLOTSDIR := plots
PLOTS := $(PLOTSDIR)/04-flux-vs-rms.$(EXT) \
	$(PLOTSDIR)/00-overscan-levels.$(EXT) \
	$(PLOTSDIR)/01-dark-levels.$(EXT) \
	$(PLOTSDIR)/02-dark-correlation.$(EXT) \
	$(PLOTSDIR)/05-rms-vs-time.$(EXT) \
	$(PLOTSDIR)/06-match-with-2mass.$(EXT) \
	$(PLOTSDIR)/07-separation-vs-magnitude.$(EXT) \
	$(PLOTSDIR)/08-separation-vs-position.$(EXT) \
	$(PLOTSDIR)/09-extracted-astrometric-parameters.$(EXT)

GENEVA := $(HOME)/storage/Geneva/

REFERENCE := data/2mass-reference.csv

all: index.html

index.html: view/build_html.py $(PLOTS) templates/index.html
	python $< -o $@ --extension $(EXT)

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

$(PLOTSDIR)/06-match-with-2mass.$(EXT): astrometry/plot_2mass_match.py data/input-catalogue-match.fits
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/07-separation-vs-magnitude.$(EXT): astrometry/plot_separation_vs_magnitude.py data/input-catalogue-match.fits
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/08-separation-vs-position.$(EXT): astrometry/plot_separation_vs_position.py data/input-catalogue-match.fits
	python $< $(word 2,$^) -o $@

$(PLOTSDIR)/09-extracted-astrometric-parameters.$(EXT): astrometry/plot_astrometric_parameters.py data/astrometric-extraction.csv
	python $< $(word 2,$^) -o $@

# Data
data/pre-sysrem.fits:
	ln -sv /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/data/pipeline-output.fits $@

data/post-sysrem.fits:
	ln -sv /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/output/working-output.fits $@

data/bias-frames-list.txt: scripts/build_bias_list.sh
	sh $< $@ $(DATE)

data/dark-frames-list.txt: scripts/build_dark_list.sh
	sh $< $@ $(DATE)

data/science-images-list.txt: scripts/build_science_list.sh
	sh $< $@

data/extracted-dark-current.csv: reduction/extract_dark_current.py data/dark-frames-list.txt
	python $< $(word 2,$^) -o $@

data/extracted-bias-levels.csv: reduction/extract_overscan.py data/bias-frames-list.txt
	python $< $(word 2,$^) -o $@

data/input-catalogue.fits:
	scp ngtshead.astro:/ngts/pipedev/InputCatalogue/output/SimonTest6/SimonTest6_dither_NG190335+491133/catfile.fits $@

data/input-catalogue-match.fits: astrometry/match_with_2mass.py data/input-catalogue.fits $(REFERENCE) astrometry/stilts.jar
	python $< --catalogue $(word 2,$^) --2mass $(word 3,$^) -o $@

data/astrometric-extraction.csv: astrometry/extract_wcs_parameters.py data/science-images-list.txt
	python $< $(word 2,$^) -o $@

$(REFERENCE): astrometry/fetch_2mass.py data/input-catalogue.fits astrometry/stilts.jar
	python $< $(word 2,$^) -o $@

astrometry/stilts.jar:
	cp /home/astro/phsnag/work//NGTS/ZLP/wcsfit-localfits/stilts.jar $@

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
	rm astrometry/stilts.jar | true

