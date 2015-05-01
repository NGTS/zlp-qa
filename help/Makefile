SOURCES := $(wildcard src/*.md)
OUTPUTS := $(subst src,build,$(SOURCES:.md=.html))

all: $(OUTPUTS)

build/%.html: src/%.md
	pandoc -s $< -o $@

print-%:
	@echo '$*=$($*)'
