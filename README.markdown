Quality assessment for the pipeline
===================================

The main scripts are kept in the `photometry` and `astrometry` directories. These and only these shall be put on ngtshead and run with the pipeline. All other directories are for testing, development and debugging purposes.

The idea is for each command to almost be piped a lá unix shell commands, but reading in a fits file from stdin may be inefficient so an alternative shall be used:

``` bash
python script.py -o <output> <input>... 
```

As this will be automated, no script should take external parameters.

Photometry
----------

Input data: 

* collapsed fits file
  * before and after sysrem
* for Tom's code, probably raw images :smile:

Astrometry
----------

Input data:

* solved images

Catalogue
---------

* master stacked image
* master catalogue
* 2MASS reference catalogue
