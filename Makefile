PLOTSDIR := plots
PLOTS := $(PLOTSDIR)/fluxvsrms.png $(PLOTSDIR)/bias-levels.png
GENEVA := $(HOME)/storage/Geneva/

all: $(PLOTS) index.html

index.html: view/build_html.py $(PLOTS)
	python $< -o $@

# Plots
$(PLOTSDIR)/fluxvsrms.png: photometry/flux-vs-rms.py data/pre-sysrem.fits data/post-sysrem.fits
	python $< --pre-sysrem $(word 2,$^) --post-sysrem $(word 3,$^) -o $@

$(PLOTSDIR)/bias-levels.png: reduction/plot-bias-levels.py data/bias-frames-list.txt
	python $< $(word 2,$^) -o $@

# Data
data/pre-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/data/pipeline-output.fits $@

data/post-sysrem.fits:
	cp /home/astro/phsnag/work/NGTS/ZLP/debugging-sysrem/output/working-output.fits $@

data/bias-frames-list.txt: scripts/build_bias_list.sh
	sh $< $@
