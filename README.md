
<img align="left" width="100" height="100" src="./abism/res/bato_chico.gif">

# ABISM: Adaptive Background Interferometric Strehl Meter

[![github-actions](https://github.com/tinmarino/abism/workflows/CI%20ABISM/badge.svg)](https://github.com/tinmarino/abism/actions)

A graphical user interface (GUI) to measure the Strehl ratio of astronomical images,
i.e. the quality of adaptive optics system on optical telescopes.

===

* [Quickstart](#quickstart)
* [Details](#details)
* [Links](#links)
* [Credits](#credits)


# Quickstart

```bash
# Install Abism
pip3 install -U git+https://github.com/tinmarino/abism  # or just `pip install abism` for non-developers

# Download a test image
wget https://github.com/tinmarino/abism/wiki/crowded.fits

# Launch the GUI
abism crowded.fits
```

# Details

On the following image, we have a Strehl ratio 50%.
Notice the warning that we are reaching the non-linearity detector limit.
We did not take time to measure the systematic error if intensity is reaching a non linear level, it is very detector dependant.


<img align="center" width=80% src="./abism/doc/abism_v0.900.png">


# Links

* [Paper 2016](https://www.eso.org/sci/libraries/SPIE2016/9909-303.pdf)
* [Slide 2012](https://tinmarino.github.io/?show=abism_slide)


# Credits

__License__: do whatever you want with the code

__Authors__: [Julien Girard](https://www.juliengirard.space), [Martin Tourneboeuf](https://tinmarino.github.io)
