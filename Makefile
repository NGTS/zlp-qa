EXT = png

PLOTS := $(PLOTSDIR)/04-flux-vs-rms.$(EXT) \
	$(PLOTSDIR)/00-overscan-levels.$(EXT) \
	$(PLOTSDIR)/01-dark-levels.$(EXT) \
	$(PLOTSDIR)/02-dark-correlation.$(EXT) \
	$(PLOTSDIR)/05-rms-vs-time.$(EXT) \
	$(PLOTSDIR)/06-match-with-2mass.$(EXT) \
	$(PLOTSDIR)/07-separation-vs-magnitude.$(EXT) \
	$(PLOTSDIR)/08-separation-vs-position.$(EXT) \
	$(PLOTSDIR)/09-extracted-astrometric-parameters.$(EXT) \
	$(PLOTSDIR)/10-match-region.$(EXT) \
	$(PLOTSDIR)/11-vector-matches.$(EXT) \
	$(PLOTSDIR)/12-catalogue-misses.$(EXT) \
	$(PLOTSDIR)/13-sysrem-basis-functions.$(EXT)

all: index.html check-root-dir

index.html: view/build_html.py $(PLOTS) templates/index.html
	python $< -o $@ --extension $(EXT)

check-root-dir:
ifndef ROOTDIR
	$(error ROOTDIR is undefined)
endif

check-plots-dir:
ifndef PLOTSDIR
	$(error PLOTSDIR is undefined)
endif
